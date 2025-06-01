#!/usr/bin/env python
"""API routes for audio processing functionality.

This module provides FastAPI routes for audio processing, including:
- Audio file upload
- Transcription
- Speaker diarization
- Combined processing
- Chunked processing for large files
"""

import os
import tempfile
import asyncio
import aiofiles
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from loguru import logger
import time
import json

from src.ai.audio_processor import AudioProcessor
from src.ai.audio_chunker import AudioChunker
from config.settings import settings

# Create router
router = APIRouter(prefix="/api/audio", tags=["audio"])

# Initialize audio processor and chunker (will be lazy-loaded when needed)
audio_processor = None
audio_chunker = None


class ProcessingResult(BaseModel):
    """Model for audio processing results."""
    job_id: str
    status: str
    message: str


class TranscriptionSegment(BaseModel):
    """Model for a transcription segment."""
    start: float
    end: float
    text: str


class SpeakerSegment(BaseModel):
    """Model for a speaker segment."""
    start: float
    end: float
    speaker: str


class AlignedSegment(BaseModel):
    """Model for an aligned transcript segment with speaker."""
    start: float
    end: float
    speaker: str
    text: str


class ProcessingResponse(BaseModel):
    """Model for complete processing response."""
    transcription: str
    segments: List[TranscriptionSegment]
    speaker_segments: List[SpeakerSegment]
    aligned_transcript: List[AlignedSegment]


class ProcessingOptions(BaseModel):
    """Model for audio processing options."""
    use_chunking: bool = False
    chunk_duration: Optional[int] = None  # in seconds
    max_workers: Optional[int] = None  # for parallel processing


class UploadResult(BaseModel):
    """Model for file upload results."""
    upload_id: str
    filename: str
    file_size: int
    content_type: str
    status: str
    message: str


class UploadProgress(BaseModel):
    """Model for upload progress tracking."""
    upload_id: str
    filename: str
    bytes_uploaded: int
    total_bytes: int
    progress_percent: float
    status: str
    upload_speed_mbps: Optional[float] = None
    estimated_time_remaining: Optional[int] = None  # seconds


class MultipleUploadResult(BaseModel):
    """Model for multiple file upload results."""
    uploads: List[UploadResult]
    total_files: int
    successful_uploads: int
    failed_uploads: int


class FileValidationError(BaseModel):
    """Model for file validation errors."""
    filename: str
    error: str
    error_code: str


def get_processor():
    """Lazy-load the audio processor."""
    global audio_processor
    if audio_processor is None:
        audio_processor = AudioProcessor(
            whisper_model_size=settings.WHISPER_MODEL,
            hf_token=settings.HF_TOKEN
        )
    return audio_processor


def get_chunker():
    """Lazy-load the audio chunker."""
    global audio_chunker
    if audio_chunker is None:
        # Initialize with the same processor to avoid loading models multiple times
        processor = get_processor()
        audio_chunker = AudioChunker(
            audio_processor=processor,
            chunk_duration=settings.CHUNK_DURATION,
            max_workers=settings.MAX_WORKERS
        )
    return audio_chunker


# Global dictionary to store upload progress
upload_progress = {}

# Supported audio file types
SUPPORTED_AUDIO_TYPES = {
    'audio/wav', 'audio/wave', 'audio/x-wav',
    'audio/mpeg', 'audio/mp3',
    'audio/mp4', 'audio/m4a',
    'audio/webm',
    'audio/ogg',
    'audio/flac',
    'audio/aac',
    'video/mp4',  # MP4 video files often contain audio
    'video/webm'  # WebM video files
}

SUPPORTED_EXTENSIONS = {
    '.wav', '.mp3', '.mp4', '.m4a', '.webm', '.ogg', '.flac', '.aac'
}


def validate_audio_file(file: UploadFile) -> Optional[FileValidationError]:
    """Validate an uploaded audio file."""
    try:
        # Check file size
        if hasattr(file, 'size') and file.size:
            max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
            if file.size > max_size:
                return FileValidationError(
                    filename=file.filename,
                    error=f"File size {file.size / 1024 / 1024:.1f}MB exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB",
                    error_code="FILE_TOO_LARGE"
                )
        
        # Check file extension
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in SUPPORTED_EXTENSIONS:
                return FileValidationError(
                    filename=file.filename,
                    error=f"File extension '{file_ext}' not supported. Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}",
                    error_code="UNSUPPORTED_FORMAT"
                )
        
        # Check MIME type
        if file.content_type and file.content_type not in SUPPORTED_AUDIO_TYPES:
            # Try to guess MIME type from filename
            if file.filename:
                guessed_type, _ = mimetypes.guess_type(file.filename)
                if guessed_type not in SUPPORTED_AUDIO_TYPES:
                    return FileValidationError(
                        filename=file.filename,
                        error=f"Content type '{file.content_type}' not supported. Supported types: {', '.join(SUPPORTED_AUDIO_TYPES)}",
                        error_code="UNSUPPORTED_MIME_TYPE"
                    )
        
        # Check filename
        if not file.filename or len(file.filename.strip()) == 0:
            return FileValidationError(
                filename="<unknown>",
                error="Filename is required",
                error_code="MISSING_FILENAME"
            )
        
        # Check for potentially dangerous filenames
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in file.filename for char in dangerous_chars):
            return FileValidationError(
                filename=file.filename,
                error="Filename contains potentially dangerous characters",
                error_code="INVALID_FILENAME"
            )
        
        return None
        
    except Exception as e:
        logger.error(f"Error validating file {file.filename}: {str(e)}")
        return FileValidationError(
            filename=file.filename or "<unknown>",
            error=f"Validation error: {str(e)}",
            error_code="VALIDATION_ERROR"
        )


def generate_upload_id() -> str:
    """Generate a unique upload ID."""
    return f"upload_{int(time.time())}_{os.urandom(4).hex()}"


async def save_uploaded_file(file: UploadFile, upload_id: str) -> Path:
    """Save an uploaded file with progress tracking."""
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate safe filename
    safe_filename = f"{upload_id}_{file.filename}"
    file_path = upload_dir / safe_filename
    
    # Initialize progress tracking
    file_size = getattr(file, 'size', 0)
    upload_progress[upload_id] = {
        'filename': file.filename,
        'total_bytes': file_size,
        'bytes_uploaded': 0,
        'status': 'uploading',
        'start_time': time.time(),
        'progress_percent': 0.0
    }
    
    try:
        chunk_size = 8192  # 8KB chunks
        bytes_uploaded = 0
        start_time = time.time()
        
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(chunk_size):
                await f.write(chunk)
                bytes_uploaded += len(chunk)
                
                # Update progress
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                if file_size > 0:
                    progress_percent = (bytes_uploaded / file_size) * 100
                else:
                    progress_percent = 0.0
                
                # Calculate upload speed
                upload_speed_mbps = None
                estimated_time_remaining = None
                if elapsed_time > 0:
                    speed_bps = bytes_uploaded / elapsed_time
                    upload_speed_mbps = (speed_bps * 8) / (1024 * 1024)  # Convert to Mbps
                    
                    if file_size > 0 and speed_bps > 0:
                        remaining_bytes = file_size - bytes_uploaded
                        estimated_time_remaining = int(remaining_bytes / speed_bps)
                
                upload_progress[upload_id].update({
                    'bytes_uploaded': bytes_uploaded,
                    'progress_percent': progress_percent,
                    'upload_speed_mbps': upload_speed_mbps,
                    'estimated_time_remaining': estimated_time_remaining
                })
        
        # Mark as completed
        upload_progress[upload_id].update({
            'status': 'completed',
            'progress_percent': 100.0,
            'bytes_uploaded': bytes_uploaded
        })
        
        logger.info(f"Successfully saved file {file.filename} as {file_path}")
        return file_path
        
    except Exception as e:
        # Mark as failed
        upload_progress[upload_id].update({
            'status': 'failed',
            'error': str(e)
        })
        logger.error(f"Error saving file {file.filename}: {str(e)}")
        # Clean up partial file
        if file_path.exists():
            file_path.unlink()
        raise


@router.post("/upload-audio", response_model=UploadResult)
async def upload_single_audio_file(
    file: UploadFile = File(..., description="Audio file to upload")
):
    """Upload a single audio file with validation and progress tracking.
    
    This endpoint accepts a single audio file upload and performs validation
    before saving it to the server. The file can then be processed using
    the /process endpoint with the returned upload_id.
    
    Supported formats: WAV, MP3, MP4, M4A, WebM, OGG, FLAC, AAC
    Maximum file size: Configurable (default 500MB)
    """
    try:
        # Validate the file
        validation_error = validate_audio_file(file)
        if validation_error:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": validation_error.error,
                    "error_code": validation_error.error_code,
                    "filename": validation_error.filename
                }
            )
        
        # Generate upload ID
        upload_id = generate_upload_id()
        
        # Save the file
        file_path = await save_uploaded_file(file, upload_id)
        
        # Get file info
        file_size = file_path.stat().st_size
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        logger.info(f"Successfully uploaded file {file.filename} with upload_id {upload_id}")
        
        return UploadResult(
            upload_id=upload_id,
            filename=file.filename,
            file_size=file_size,
            content_type=content_type,
            status="completed",
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-multiple", response_model=MultipleUploadResult)
async def upload_multiple_audio_files(
    files: List[UploadFile] = File(..., description="Multiple audio files to upload")
):
    """Upload multiple audio files with validation and progress tracking.
    
    This endpoint accepts multiple audio file uploads and performs validation
    on each file before saving them to the server. Files can then be processed
    using the /process endpoint with their respective upload_ids.
    
    Each file is validated independently, so some files may succeed while others fail.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Reasonable limit for multiple uploads
        raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files allowed per request")
    
    results = []
    successful_uploads = 0
    failed_uploads = 0
    
    for file in files:
        try:
            # Validate the file
            validation_error = validate_audio_file(file)
            if validation_error:
                results.append(UploadResult(
                    upload_id="",
                    filename=file.filename,
                    file_size=0,
                    content_type=file.content_type or "",
                    status="failed",
                    message=f"Validation failed: {validation_error.error}"
                ))
                failed_uploads += 1
                continue
            
            # Generate upload ID
            upload_id = generate_upload_id()
            
            # Save the file
            file_path = await save_uploaded_file(file, upload_id)
            
            # Get file info
            file_size = file_path.stat().st_size
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
            
            results.append(UploadResult(
                upload_id=upload_id,
                filename=file.filename,
                file_size=file_size,
                content_type=content_type,
                status="completed",
                message="File uploaded successfully"
            ))
            successful_uploads += 1
            
            logger.info(f"Successfully uploaded file {file.filename} with upload_id {upload_id}")
            
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
            results.append(UploadResult(
                upload_id="",
                filename=file.filename,
                file_size=0,
                content_type=file.content_type or "",
                status="failed",
                message=f"Upload failed: {str(e)}"
            ))
            failed_uploads += 1
    
    return MultipleUploadResult(
        uploads=results,
        total_files=len(files),
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads
    )


@router.get("/upload-progress/{upload_id}", response_model=UploadProgress)
async def get_upload_progress(upload_id: str):
    """Get the progress of a file upload.
    
    This endpoint returns real-time progress information for an ongoing
    or completed file upload, including upload speed and estimated time remaining.
    """
    if upload_id not in upload_progress:
        raise HTTPException(status_code=404, detail=f"Upload {upload_id} not found")
    
    progress_data = upload_progress[upload_id]
    
    return UploadProgress(
        upload_id=upload_id,
        filename=progress_data['filename'],
        bytes_uploaded=progress_data['bytes_uploaded'],
        total_bytes=progress_data['total_bytes'],
        progress_percent=progress_data['progress_percent'],
        status=progress_data['status'],
        upload_speed_mbps=progress_data.get('upload_speed_mbps'),
        estimated_time_remaining=progress_data.get('estimated_time_remaining')
    )


@router.delete("/upload/{upload_id}")
async def delete_uploaded_file(upload_id: str):
    """Delete an uploaded file and its progress tracking data.
    
    This endpoint removes the uploaded file from the server and cleans up
    any associated progress tracking data.
    """
    try:
        # Find the file
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_files = list(upload_dir.glob(f"{upload_id}_*"))
        
        if not upload_files:
            raise HTTPException(status_code=404, detail=f"Upload {upload_id} not found")
        
        # Delete the file(s)
        deleted_files = []
        for file_path in upload_files:
            if file_path.exists():
                file_path.unlink()
                deleted_files.append(str(file_path.name))
        
        # Clean up progress tracking
        if upload_id in upload_progress:
            del upload_progress[upload_id]
        
        logger.info(f"Deleted upload {upload_id}, files: {deleted_files}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Upload {upload_id} deleted successfully",
                "deleted_files": deleted_files
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting upload {upload_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/process", response_model=ProcessingResult)
async def process_audio(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    upload_id: Optional[str] = Form(None),
    whisper_model: Optional[str] = Form(None),
    use_chunking: bool = Form(False),
    chunk_duration: Optional[int] = Form(None),
    max_workers: Optional[int] = Form(None),
    processor: AudioProcessor = Depends(get_processor),
    chunker: AudioChunker = Depends(get_chunker)
):
    """Process an audio file for transcription and speaker diarization.
    
    This endpoint can process audio in two ways:
    1. Direct file upload (provide 'file' parameter)
    2. Process previously uploaded file (provide 'upload_id' parameter)
    
    The processing generates:
    - Transcription
    - Speaker diarization
    - Aligned transcript with speakers
    
    For large files, chunking can be enabled to split the audio into smaller segments
    and process them in parallel.
    
    Processing happens in the background, and results can be retrieved later.
    """
    # Validate input parameters
    if not file and not upload_id:
        raise HTTPException(
            status_code=400,
            detail="Either 'file' or 'upload_id' must be provided"
        )
    
    if file and upload_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both 'file' and 'upload_id'. Choose one method."
        )
    
    # Generate a unique job ID
    job_id = f"job_{os.urandom(8).hex()}"
    
    try:
        if upload_id:
            # Process from previously uploaded file
            upload_dir = Path(settings.UPLOAD_DIR)
            upload_files = list(upload_dir.glob(f"{upload_id}_*"))
            
            if not upload_files:
                raise HTTPException(
                    status_code=404,
                    detail=f"Upload {upload_id} not found. Make sure the file was uploaded successfully."
                )
            
            file_path = upload_files[0]  # Use the first matching file
            logger.info(f"Processing previously uploaded file: {file_path}")
            
        else:
            # Process from direct file upload
            # Create temp directory for processing if it doesn't exist
            temp_dir = Path(settings.UPLOAD_DIR)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Save uploaded file to temp directory
            file_path = temp_dir / f"{job_id}_{file.filename}"
            
            # Write file content
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"Saved uploaded file to {file_path}")
        
        # Prepare processing options
        processing_options = {
            "use_chunking": use_chunking,
            "chunk_duration": chunk_duration,
            "max_workers": max_workers,
            "whisper_model": whisper_model
        }
        
        # Add background task for processing
        background_tasks.add_task(
            process_audio_background,
            file_path,
            job_id,
            processing_options
        )
        
        return ProcessingResult(
            job_id=job_id,
            status="processing",
            message="Audio processing started in the background"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-upload/{upload_id}", response_model=ProcessingResult)
async def process_uploaded_file(
    upload_id: str,
    background_tasks: BackgroundTasks,
    whisper_model: Optional[str] = Form(None),
    use_chunking: bool = Form(False),
    chunk_duration: Optional[int] = Form(None),
    max_workers: Optional[int] = Form(None)
):
    """Process a previously uploaded audio file by upload_id.
    
    This is a convenience endpoint that's equivalent to calling /process
    with the upload_id parameter.
    """
    return await process_audio(
        background_tasks=background_tasks,
        file=None,
        upload_id=upload_id,
        whisper_model=whisper_model,
        use_chunking=use_chunking,
        chunk_duration=chunk_duration,
        max_workers=max_workers
    )


async def process_audio_background(file_path: Path, job_id: str, options: Dict[str, Any]):
    """Process audio file in the background."""
    try:
        # Extract options
        use_chunking = options.get("use_chunking", False)
        chunk_duration = options.get("chunk_duration")
        max_workers = options.get("max_workers")
        whisper_model = options.get("whisper_model")
        
        # Prepare processing kwargs
        whisper_kwargs = {}
        if whisper_model:
            whisper_kwargs["model"] = whisper_model
        
        # Create results directory
        results_dir = Path(settings.CHUNK_DIR) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        output_path = results_dir / f"{job_id}.json"
        
        # Process based on chunking option
        if use_chunking:
            logger.info(f"Processing {file_path} with chunking")
            
            # Get chunker with custom settings if provided
            chunker = get_chunker()
            if chunk_duration:
                chunker.chunk_duration = chunk_duration
            if max_workers:
                chunker.max_workers = max_workers
            
            # Process with chunking
            results = await chunker.process_audio(
                file_path,
                whisper_kwargs=whisper_kwargs
            )
            
            # Save results
            chunker.save_results(results, output_path)
        else:
            logger.info(f"Processing {file_path} without chunking")
            
            # Get processor
            processor = get_processor()
            
            # Process without chunking
            results = processor.process_audio(
                file_path,
                whisper_kwargs=whisper_kwargs
            )
            
            # Save results
            processor.save_results(results, output_path)
        
        logger.success(f"Background processing completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {str(e)}")


@router.get("/status/{job_id}", response_model=ProcessingResult)
async def get_processing_status(job_id: str):
    """Get the status of an audio processing job."""
    # Check if results file exists
    results_dir = Path(settings.CHUNK_DIR) / "results"
    results_file = results_dir / f"{job_id}.json"
    
    if results_file.exists():
        return ProcessingResult(
            job_id=job_id,
            status="completed",
            message="Processing completed successfully"
        )
    
    # Check if job is still in progress (file exists in uploads)
    uploads_dir = Path(settings.UPLOAD_DIR)
    upload_files = list(uploads_dir.glob(f"{job_id}_*"))
    
    if upload_files:
        return ProcessingResult(
            job_id=job_id,
            status="processing",
            message="Audio processing is still in progress"
        )
    
    # Job not found
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


@router.get("/results/{job_id}", response_model=ProcessingResponse)
async def get_processing_results(job_id: str):
    """Get the results of a completed audio processing job."""
    import json
    
    # Check if results file exists
    results_dir = Path(settings.CHUNK_DIR) / "results"
    results_file = results_dir / f"{job_id}.json"
    
    if not results_file.exists():
        raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found")
    
    try:
        # Load results from file
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)
        
        # Convert to response model
        return ProcessingResponse(
            transcription=results["transcription"]["text"],
            segments=[
                TranscriptionSegment(
                    start=segment["start"],
                    end=segment["end"],
                    text=segment["text"]
                )
                for segment in results["transcription"]["segments"]
            ],
            speaker_segments=[
                SpeakerSegment(
                    start=segment["start"],
                    end=segment["end"],
                    speaker=segment["speaker"]
                )
                for segment in results["speaker_segments"]
            ],
            aligned_transcript=[
                AlignedSegment(
                    start=segment["start"],
                    end=segment["end"],
                    speaker=segment["speaker"],
                    text=segment["text"]
                )
                for segment in results["aligned_transcript"]
            ]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving results for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
