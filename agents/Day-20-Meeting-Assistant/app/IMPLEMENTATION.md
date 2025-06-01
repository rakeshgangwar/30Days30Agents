# Meeting Assistant Implementation Documentation

## Executive Summary

This document outlines the implementation strategy for a comprehensive meeting assistant capable of recording, transcribing, and analyzing both virtual and physical meetings. The solution leverages open-source technologies for privacy, accuracy, and cost-effectiveness.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Core Components](#core-components)
4. [Implementation Plan](#implementation-plan)
5. [Privacy & Security](#privacy--security)
6. [Deployment Strategy](#deployment-strategy)
7. [Performance Considerations](#performance-considerations)
8. [Future Enhancements](#future-enhancements)

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services   │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Browser Ext  │ │◄──►│ │   API       │ │◄──►│ │  Whisper    │ │
│ │(Virtual)    │ │    │ │ Gateway     │ │    │ │(Transcribe) │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Desktop App  │ │◄──►│ │Audio Proc   │ │◄──►│ │Pyannote.ai  │ │
│ │(Physical)   │ │    │ │Service      │ │    │ │(Diarization)│ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│                 │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│                 │    │ │  Storage    │ │    │ │   BART      │ │
│                 │    │ │  Service    │ │    │ │(Summary)    │ │
│                 │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

```
Frontend Layer:
├── Browser Extension (Virtual Meetings)
│   ├── Content Script (Meeting Detection)
│   ├── Audio Capture Module
│   └── Platform Integrations (Zoom, Teams, Meet)
└── Progressive Web App (Physical Meetings - Universal)
    ├── Cross-Platform PWA (iOS, Android, Windows, macOS, Linux)
    │   ├── Web Audio API Recording
    │   ├── File Upload & Management
    │   ├── Offline Storage (IndexedDB)
    │   ├── Service Worker (Background Sync)
    │   ├── Responsive UI (Mobile/Desktop)
    │   └── Native App-like Experience

Backend Layer:
├── API Gateway (FastAPI)
├── Audio Processing Service
├── File Management Service
├── Integration Service
└── Notification Service

AI Processing Layer:
├── Speech-to-Text (Whisper)
├── Speaker Diarization (Pyannote.audio)
├── LLM Processing Hub
│   ├── OpenRouter (Cloud LLMs - GPT-4, Claude, etc.)
│   └── Ollama (Local LLMs - Llama, Mistral, etc.)
└── Audio Chunking Service (10-15 min segments)

Data Layer:
├── PostgreSQL (Metadata)
├── File System/S3 (Audio Files)
└── Redis (Caching/Sessions)
```

## Technology Stack

### Recommended Stack (Primary)

**Speech Processing:**
- **OpenAI Whisper**: State-of-the-art speech recognition with 99% accuracy on clear audio
- **Pyannote.audio**: Advanced speaker diarization with 90% accuracy in standard conditions
- **SpeechBrain**: Backup for advanced speech processing needs

**LLM Processing & NLP:**
- **OpenRouter**: Cloud-based LLM access (GPT-4, Claude, Gemini, etc.) for high-quality summarization
- **Ollama**: Local LLM inference (Llama 3.1, Mistral, CodeLlama) for offline processing
- **LiteLLM**: Unified interface for multiple LLM providers
- **spaCy**: For entity recognition and text preprocessing

**Backend:**
- **FastAPI**: High-performance API framework
- **PostgreSQL**: Robust metadata storage
- **Redis**: Caching and session management
- **Celery**: Background task processing

**Frontend:**
- **Browser Extension**: Vanilla JS with Web APIs for virtual meetings
- **Progressive Web App**: React.js with TypeScript - single app for all platforms (mobile/desktop)
- **Web Dashboard**: Integrated into PWA for unified experience

**Infrastructure:**
- **Docker**: Containerization
- **nginx**: Reverse proxy and load balancing
- **AWS/GCP**: Cloud deployment (optional)

### Alternative Stack (Lightweight)

**For Resource-Constrained Environments:**
- **Vosk**: Lightweight speech recognition
- **Basic diarization**: Speaker clustering algorithms
- **Flask**: Simpler backend framework
- **SQLite**: Local database storage

## Core Components

### 1. Audio Capture Module

**Virtual Meetings (Browser Extension):**
```javascript
// Content script for meeting detection and audio capture
class MeetingAudioCapture {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
    }

    async startCapture() {
        const stream = await navigator.mediaDevices.getDisplayMedia({
            audio: true,
            video: false
        });
        
        this.mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        
        this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
        };
        
        this.mediaRecorder.start(1000); // 1-second chunks
        this.isRecording = true;
    }

    async uploadAudio() {
        const audioBlob = new Blob(this.audioChunks, {
            type: 'audio/webm;codecs=opus'
        });
        
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('meeting_id', this.meetingId);
        
        await fetch('/api/upload-audio', {
            method: 'POST',
            body: formData
        });
    }
}
```

**Progressive Web App (PWA) - Universal Recording Application:**
```javascript
// Enhanced PWA for universal recording and file upload (Mobile + Desktop)
class UniversalMeetingRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.currentMeetingId = null;
        this.chunkSize = 15 * 60 * 1000; // 15 minutes in milliseconds
        this.isOnline = navigator.onLine;
        this.offlineQueue = [];
        
        // Setup offline/online handlers
        this.setupOfflineHandlers();
        
        // Setup service worker for background sync
        this.registerServiceWorker();
    }

    async startRecording(meetingId) {
        this.currentMeetingId = meetingId;
        
        try {
            // Enhanced audio constraints for better quality
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    // Mobile-specific optimizations
                    ...(this.isMobile() && {
                        latency: 0.1,
                        volume: 1.0
                    })
                }
            });
            
            // Choose optimal codec based on platform
            const mimeType = this.getBestMimeType();
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: mimeType,
                audioBitsPerSecond: 128000
            });
            
            // Chunked recording for real-time processing
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push({
                        data: event.data,
                        timestamp: Date.now(),
                        chunkId: this.audioChunks.length
                    });
                    
                    // Auto-upload chunks if online
                    if (this.isOnline) {
                        this.uploadChunk(event.data, this.audioChunks.length - 1);
                    }
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.handleRecordingStop();
            };
            
            // Start recording with chunked intervals
            this.mediaRecorder.start(this.chunkSize);
            this.isRecording = true;
            
            // Update UI
            this.updateRecordingUI(true);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Failed to start recording. Please check microphone permissions.');
        }
    }

    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Stop all tracks to release microphone
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }

    async handleRecordingStop() {
        // Create final audio blob from all chunks
        const audioBlob = new Blob(
            this.audioChunks.map(chunk => chunk.data),
            { type: this.getBestMimeType() }
        );
        
        // Save to IndexedDB for offline access
        await this.saveToOfflineStorage(audioBlob);
        
        // Upload final recording if online
        if (this.isOnline) {
            await this.uploadFile(audioBlob, this.currentMeetingId);
        } else {
            this.queueForOfflineUpload(audioBlob);
        }
        
        this.updateRecordingUI(false);
        this.audioChunks = [];
    }

    async uploadChunk(chunkData, chunkId) {
        const formData = new FormData();
        formData.append('audio', chunkData);
        formData.append('meeting_id', this.currentMeetingId);
        formData.append('chunk_id', chunkId);
        formData.append('is_chunk', 'true');
        
        try {
            const response = await fetch('/api/upload-audio-chunk', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status}`);
            }
            
            const result = await response.json();
            this.updateChunkProgress(chunkId, 'uploaded');
            
        } catch (error) {
            console.error('Chunk upload failed:', error);
            this.updateChunkProgress(chunkId, 'failed');
        }
    }

    async uploadFile(file, meetingId) {
        const formData = new FormData();
        formData.append('audio', file);
        formData.append('meeting_id', meetingId);
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // Progress tracking
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    this.updateUploadProgress(percentComplete);
                }
            });
            
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    const result = JSON.parse(xhr.responseText);
                    this.showSuccess('Audio uploaded successfully!');
                    resolve(result);
                } else {
                    this.showError(`Upload failed: ${xhr.status}`);
                    reject(new Error(`Upload failed: ${xhr.status}`));
                }
            });
            
            xhr.addEventListener('error', () => {
                this.showError('Upload failed. Please try again.');
                reject(new Error('Upload failed'));
            });
            
            xhr.open('POST', '/api/upload-audio');
            xhr.send(formData);
        });
    }

    // Multi-file upload support
    async uploadMultipleFiles(files, meetingId) {
        const validFiles = Array.from(files).filter(file =>
            file.type.startsWith('audio/') ||
            file.type.startsWith('video/') ||
            file.name.match(/\.(mp3|wav|m4a|webm|ogg|flac|aac)$/i)
        );
        
        if (validFiles.length === 0) {
            this.showError('No valid audio files found.');
            return;
        }
        
        this.showInfo(`Uploading ${validFiles.length} files...`);
        
        const uploadPromises = validFiles.map((file, index) =>
            this.uploadFileWithRetry(file, meetingId, index)
        );
        
        try {
            const results = await Promise.all(uploadPromises);
            this.showSuccess(`Successfully uploaded ${results.length} files!`);
            return results;
        } catch (error) {
            this.showError('Some files failed to upload. Please try again.');
            throw error;
        }
    }

    async uploadFileWithRetry(file, meetingId, index, retries = 3) {
        for (let attempt = 1; attempt <= retries; attempt++) {
            try {
                return await this.uploadFile(file, meetingId);
            } catch (error) {
                if (attempt === retries) {
                    throw error;
                }
                await this.delay(1000 * attempt); // Exponential backoff
            }
        }
    }

    // Drag and drop with enhanced UX
    setupDragAndDrop(dropZoneId) {
        const dropZone = document.getElementById(dropZoneId);
        if (!dropZone) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('dragover');
            }, false);
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', async (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                await this.uploadMultipleFiles(files, this.currentMeetingId);
            }
        }, false);
    }

    // Offline storage using IndexedDB
    async saveToOfflineStorage(audioBlob) {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('MeetingAssistantDB', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                const db = request.result;
                const transaction = db.transaction(['recordings'], 'readwrite');
                const store = transaction.objectStore('recordings');
                
                const recordingData = {
                    id: this.currentMeetingId,
                    audio: audioBlob,
                    timestamp: Date.now(),
                    uploaded: false
                };
                
                store.put(recordingData);
                transaction.oncomplete = () => resolve();
                transaction.onerror = () => reject(transaction.error);
            };
            
            request.onupgradeneeded = () => {
                const db = request.result;
                if (!db.objectStoreNames.contains('recordings')) {
                    db.createObjectStore('recordings', { keyPath: 'id' });
                }
            };
        });
    }

    // Service Worker registration for background sync
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered:', registration);
                
                // Enable background sync
                if ('sync' in window.ServiceWorkerRegistration.prototype) {
                    registration.sync.register('background-upload');
                }
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    // Utility methods
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    getBestMimeType() {
        const supportedTypes = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/wav'
        ];
        
        return supportedTypes.find(type => MediaRecorder.isTypeSupported(type)) || 'audio/webm';
    }

    setupOfflineHandlers() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.syncOfflineUploads();
            this.showInfo('Back online! Syncing recordings...');
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showInfo('Offline mode. Recordings will sync when connection is restored.');
        });
    }

    async syncOfflineUploads() {
        // Implement background sync for offline uploads
        if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({
                command: 'SYNC_UPLOADS'
            });
        }
    }

    // UI Helper methods
    updateRecordingUI(isRecording) {
        const recordButton = document.getElementById('record-button');
        const statusIndicator = document.getElementById('status-indicator');
        
        if (recordButton) {
            recordButton.textContent = isRecording ? 'Stop Recording' : 'Start Recording';
            recordButton.classList.toggle('recording', isRecording);
        }
        
        if (statusIndicator) {
            statusIndicator.textContent = isRecording ? 'Recording...' : 'Ready';
            statusIndicator.classList.toggle('active', isRecording);
        }
    }

    updateUploadProgress(percent) {
        const progressBar = document.getElementById('upload-progress');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }
        
        if (progressText) {
            progressText.textContent = `Uploading... ${percent}%`;
        }
    }

    updateChunkProgress(chunkId, status) {
        const chunkElement = document.getElementById(`chunk-${chunkId}`);
        if (chunkElement) {
            chunkElement.className = `chunk-status ${status}`;
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showNotification(message, type) {
        // Create or update notification element
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            document.body.appendChild(notification);
        }
        
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 5000);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    queueForOfflineUpload(audioBlob) {
        this.offlineQueue.push({
            audioBlob,
            meetingId: this.currentMeetingId,
            timestamp: Date.now()
        });
    }
}

// Service Worker for background sync (sw.js)
const SW_CACHE_NAME = 'meeting-assistant-v1';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/manifest.json'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(SW_CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

self.addEventListener('sync', (event) => {
    if (event.tag === 'background-upload') {
        event.waitUntil(syncOfflineUploads());
    }
});

async function syncOfflineUploads() {
    // Implement offline upload sync logic
    const db = await openDB();
    const recordings = await getUnuploadedRecordings(db);
    
    for (const recording of recordings) {
        try {
            await uploadRecording(recording);
            await markAsUploaded(db, recording.id);
        } catch (error) {
            console.error('Failed to sync recording:', error);
        }
    }
}
```

### 2. Enhanced Audio Processing Pipeline with Chunking

```python
# Enhanced audio processing service with chunking and LLM integration
import whisper
from pyannote.audio import Pipeline
import ffmpeg
import asyncio
import os
from typing import List, Dict, Any
import json
from datetime import timedelta

class AudioProcessor:
    def __init__(self):
        # Load models
        self.whisper_model = whisper.load_model("medium")
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token="your_hf_token"
        )
        self.llm_service = LLMService()
        self.chunk_duration = 15 * 60  # 15 minutes in seconds
    
    async def process_audio(self, audio_file_path, meeting_id):
        """Complete audio processing pipeline with chunking"""
        try:
            # 1. Preprocess and get audio info
            processed_audio, duration = await self._preprocess_audio(audio_file_path)
            
            # 2. Split audio into chunks if longer than threshold
            if duration > self.chunk_duration:
                chunks = await self._split_audio_into_chunks(processed_audio, meeting_id)
                return await self._process_chunks_parallel(chunks, meeting_id)
            else:
                return await self._process_single_audio(processed_audio, meeting_id)
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            raise
    
    async def _process_chunks_parallel(self, chunks: List[Dict], meeting_id: str):
        """Process multiple audio chunks in parallel"""
        chunk_results = []
        
        # Process chunks in parallel (limited concurrency to manage resources)
        semaphore = asyncio.Semaphore(3)  # Process max 3 chunks simultaneously
        
        async def process_chunk_wrapper(chunk_info):
            async with semaphore:
                return await self._process_single_audio(
                    chunk_info['path'],
                    meeting_id,
                    chunk_info['start_time']
                )
        
        tasks = [process_chunk_wrapper(chunk) for chunk in chunks]
        chunk_results = await asyncio.gather(*tasks)
        
        # Combine results from all chunks
        return await self._combine_chunk_results(chunk_results, meeting_id)
    
    async def _process_single_audio(self, audio_path: str, meeting_id: str, start_offset: float = 0):
        """Process a single audio file or chunk"""
        # 1. Transcribe with Whisper
        transcript_result = await self._transcribe_audio(audio_path)
        
        # 2. Perform speaker diarization
        diarization_result = await self._diarize_speakers(audio_path)
        
        # 3. Align transcript with speakers
        aligned_transcript = await self._align_transcript_speakers(
            transcript_result, diarization_result, start_offset
        )
        
        return {
            'transcript': aligned_transcript,
            'start_offset': start_offset,
            'audio_path': audio_path
        }
    
    async def _combine_chunk_results(self, chunk_results: List[Dict], meeting_id: str):
        """Combine results from multiple chunks"""
        # Combine all transcripts
        full_transcript = []
        for chunk in chunk_results:
            full_transcript.extend(chunk['transcript'])
        
        # Sort by timestamp
        full_transcript.sort(key=lambda x: x['start'])
        
        # Generate summary and action items using LLM
        summary = await self.llm_service.generate_summary(full_transcript)
        action_items = await self.llm_service.extract_action_items(full_transcript)
        
        # Store and return results
        result = {
            'meeting_id': meeting_id,
            'transcript': full_transcript,
            'summary': summary,
            'action_items': action_items,
            'speakers': list(set([seg['speaker'] for seg in full_transcript])),
            'processing_method': 'chunked'
        }
        
        await self._store_results(result)
        return result
    
    async def _preprocess_audio(self, audio_path):
        """Convert audio to standard format and get duration"""
        output_path = audio_path.replace('.webm', '.wav')
        
        # Get audio duration
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['streams'][0]['duration'])
        
        (
            ffmpeg
            .input(audio_path)
            .output(output_path, acodec='pcm_s16le', ac=1, ar=16000)
            .overwrite_output()
            .run()
        )
        
        return output_path, duration
    
    async def _split_audio_into_chunks(self, audio_path: str, meeting_id: str):
        """Split audio into chunks for efficient processing"""
        # Get audio duration
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['streams'][0]['duration'])
        
        chunks = []
        chunk_count = int(duration // self.chunk_duration) + 1
        
        os.makedirs(f"chunks/{meeting_id}", exist_ok=True)
        
        for i in range(chunk_count):
            start_time = i * self.chunk_duration
            end_time = min((i + 1) * self.chunk_duration, duration)
            
            chunk_path = f"chunks/{meeting_id}/chunk_{i:03d}.wav"
            
            # Extract chunk using ffmpeg
            (
                ffmpeg
                .input(audio_path, ss=start_time, t=end_time - start_time)
                .output(chunk_path, acodec='pcm_s16le', ac=1, ar=16000)
                .overwrite_output()
                .run()
            )
            
            chunks.append({
                'path': chunk_path,
                'start_time': start_time,
                'end_time': end_time,
                'chunk_id': i
            })
        
        return chunks
    
    async def _transcribe_audio(self, audio_path):
        """Transcribe audio using Whisper"""
        result = self.whisper_model.transcribe(
            audio_path,
            task="transcribe",
            language="en"
        )
        return result["segments"]
    
    async def _diarize_speakers(self, audio_path):
        """Perform speaker diarization"""
        diarization = self.diarization_pipeline(audio_path)
        
        speakers = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        
        return speakers
    
    async def _align_transcript_speakers(self, transcript_segments, speaker_segments, start_offset: float = 0):
        """Align Whisper transcript with speaker diarization"""
        aligned = []
        
        for segment in transcript_segments:
            segment_start = segment["start"] + start_offset
            segment_end = segment["end"] + start_offset
            
            # Find overlapping speaker
            for speaker_seg in speaker_segments:
                speaker_start = speaker_seg["start"] + start_offset
                speaker_end = speaker_seg["end"] + start_offset
                
                if (speaker_start <= segment_start <= speaker_end or
                    speaker_start <= segment_end <= speaker_end):
                    
                    aligned.append({
                        "start": segment_start,
                        "end": segment_end,
                        "text": segment["text"].strip(),
                        "speaker": speaker_seg["speaker"]
                    })
                    break
            else:
                # No speaker found, assign unknown
                aligned.append({
                    "start": segment_start,
                    "end": segment_end,
                    "text": segment["text"].strip(),
                    "speaker": "UNKNOWN"
                })
        
        return aligned

# LLM Service for OpenRouter and Ollama integration
import httpx
import ollama
from typing import Optional

class LLMService:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.ollama_client = ollama.Client()
        self.use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        
    async def generate_summary(self, transcript: List[Dict]) -> str:
        """Generate meeting summary using LLM"""
        # Prepare transcript text
        transcript_text = self._format_transcript_for_llm(transcript)
        
        prompt = f"""
        Please provide a comprehensive summary of the following meeting transcript:
        
        {transcript_text}
        
        Include:
        1. Main topics discussed
        2. Key decisions made
        3. Important points raised by each speaker
        4. Overall meeting outcome
        
        Keep the summary concise but informative (300-500 words).
        """
        
        if self.use_local or not self.openrouter_api_key:
            return await self._generate_with_ollama(prompt)
        else:
            return await self._generate_with_openrouter(prompt)
    
    async def extract_action_items(self, transcript: List[Dict]) -> List[Dict]:
        """Extract action items using LLM"""
        transcript_text = self._format_transcript_for_llm(transcript)
        
        prompt = f"""
        Please extract all action items from the following meeting transcript.
        Return them as a JSON array where each item has:
        - "task": The task description
        - "assignee": Who is responsible (if mentioned)
        - "deadline": When it should be completed (if mentioned)
        - "priority": High/Medium/Low (your assessment)
        
        Transcript:
        {transcript_text}
        
        Return only the JSON array, no other text.
        """
        
        if self.use_local or not self.openrouter_api_key:
            response = await self._generate_with_ollama(prompt)
        else:
            response = await self._generate_with_openrouter(prompt)
        
        # Parse JSON response
        try:
            import json
            action_items = json.loads(response.strip())
            return action_items if isinstance(action_items, list) else []
        except json.JSONDecodeError:
            # Fallback to regex extraction if JSON parsing fails
            return await self._fallback_action_extraction(transcript_text)
    
    async def _generate_with_openrouter(self, prompt: str, model: str = "anthropic/claude-3.5-sonnet") -> str:
        """Generate response using OpenRouter API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.3
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"OpenRouter API error: {e}")
                # Fallback to local model
                return await self._generate_with_ollama(prompt)
    
    async def _generate_with_ollama(self, prompt: str, model: str = "llama3.1:8b") -> str:
        """Generate response using local Ollama"""
        try:
            response = await asyncio.to_thread(
                self.ollama_client.generate,
                model=model,
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 2000}
            )
            return response["response"]
        except Exception as e:
            print(f"Ollama error: {e}")
            # Ultimate fallback to simple extraction
            return await self._fallback_summary_generation(prompt)
    
    def _format_transcript_for_llm(self, transcript: List[Dict]) -> str:
        """Format transcript for LLM processing"""
        formatted_lines = []
        for segment in transcript:
            timestamp = self._format_timestamp(segment["start"])
            speaker = segment["speaker"]
            text = segment["text"]
            formatted_lines.append(f"[{timestamp}] {speaker}: {text}")
        
        return "\n".join(formatted_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    async def _fallback_action_extraction(self, transcript_text: str) -> List[Dict]:
        """Fallback regex-based action item extraction"""
        import re
        
        action_patterns = [
            r"(.*?)\s+(will|should|must|needs? to|has to|assigned to)\s+(.*?)(?:\.|$)",
            r"(action item|todo|task|follow up|next step):\s*(.*?)(?:\.|$)",
            r"(.*?)\s+by\s+(next week|tomorrow|friday|monday|end of week)(.*?)(?:\.|$)"
        ]
        
        action_items = []
        for pattern in action_patterns:
            matches = re.finditer(pattern, transcript_text, re.IGNORECASE)
            for match in matches:
                action_text = match.group(0).strip()
                if len(action_text) > 10:
                    action_items.append({
                        "task": action_text,
                        "assignee": "Not specified",
                        "deadline": "Not specified",
                        "priority": "Medium"
                    })
        
        return action_items[:10]
    
    async def _fallback_summary_generation(self, prompt: str) -> str:
        """Ultimate fallback summary generation"""
        return "Summary generation temporarily unavailable. Please check LLM service configuration."
    
    async def _generate_summary(self, aligned_transcript):
        """Generate meeting summary"""
        full_text = " ".join([seg["text"] for seg in aligned_transcript])
        
        # Split into chunks if too long
        max_chunk_length = 1024
        chunks = [full_text[i:i+max_chunk_length] 
                 for i in range(0, len(full_text), max_chunk_length)]
        
        summaries = []
        for chunk in chunks:
            if len(chunk.strip()) > 50:  # Skip very short chunks
                summary = self.summarizer(
                    chunk,
                    max_length=150,
                    min_length=30,
                    do_sample=False
                )
                summaries.append(summary[0]["summary_text"])
        
        return " ".join(summaries)
    
    async def _extract_action_items(self, aligned_transcript):
        """Extract action items using NLP"""
        import re
        
        action_patterns = [
            r"(.*?)\s+(will|should|must|needs? to|has to|assigned to)\s+(.*?)(?:\.|$)",
            r"(action item|todo|task|follow up|next step):\s*(.*?)(?:\.|$)",
            r"(.*?)\s+by\s+(next week|tomorrow|friday|monday|end of week)(.*?)(?:\.|$)"
        ]
        
        action_items = []
        full_text = " ".join([seg["text"] for seg in aligned_transcript])
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                action_text = match.group(0).strip()
                if len(action_text) > 10:  # Filter very short items
                    action_items.append({
                        "text": action_text,
                        "confidence": 0.8  # Simple confidence score
                    })
        
        # Remove duplicates
        unique_actions = []
        for action in action_items:
            if not any(action["text"].lower() in existing["text"].lower() 
                      for existing in unique_actions):
                unique_actions.append(action)
        
        return unique_actions[:10]  # Limit to top 10
```

### 3. Enhanced API Layer with File Upload Support

```python
# FastAPI backend service
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, Meeting, Transcript
import uuid
import os

app = FastAPI(title="Meeting Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_processor = AudioProcessor()

@app.post("/api/meetings")
async def create_meeting(
    title: str,
    meeting_type: str,  # "virtual" or "physical"
    db: Session = Depends(get_db)
):
    meeting_id = str(uuid.uuid4())
    meeting = Meeting(
        id=meeting_id,
        title=title,
        meeting_type=meeting_type,
        status="created"
    )
    db.add(meeting)
    db.commit()
    
    return {"meeting_id": meeting_id, "status": "created"}

@app.post("/api/upload-audio")
async def upload_audio(
    background_tasks: BackgroundTasks,
    meeting_id: str,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save uploaded audio file
    file_path = f"uploads/{meeting_id}_{audio.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await audio.read()
        buffer.write(content)
    
    # Update meeting status
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting:
        meeting.status = "processing"
        meeting.audio_file_path = file_path
        db.commit()
    
    # Process audio in background
    background_tasks.add_task(
        process_meeting_audio, 
        meeting_id, 
        file_path
    )
    
    return {"status": "uploaded", "message": "Processing started"}

async def process_meeting_audio(meeting_id: str, audio_file_path: str):
    """Background task for audio processing"""
    try:
        result = await audio_processor.process_audio(audio_file_path, meeting_id)
        
        # Update database with results
        db = next(get_db())
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = "completed"
            meeting.summary = result["summary"]
            
            # Store transcript
            transcript = Transcript(
                meeting_id=meeting_id,
                content=result["transcript"],
                action_items=result["action_items"]
            )
            db.add(transcript)
            db.commit()
        
    except Exception as e:
        print(f"Error processing meeting {meeting_id}: {e}")
        # Update status to failed
        db = next(get_db())
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = "failed"
            db.commit()

@app.get("/api/meetings/{meeting_id}")
async def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        return {"error": "Meeting not found"}
    
    transcript = db.query(Transcript).filter(
        Transcript.meeting_id == meeting_id
    ).first()
    
    return {
        "meeting": meeting,
        "transcript": transcript.content if transcript else None,
        "action_items": transcript.action_items if transcript else None
    }

@app.get("/api/meetings")
async def list_meetings(db: Session = Depends(get_db)):
    meetings = db.query(Meeting).order_by(Meeting.created_at.desc()).all()
    return {"meetings": meetings}
```

### 4. Enhanced Database Schema

```python
# Enhanced database models with chunking and file upload support
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    meeting_type = Column(String, nullable=False)  # "virtual" or "physical"
    platform = Column(String)  # "zoom", "teams", "meet", "mobile", "desktop", "upload"
    status = Column(String, default="created")  # created, processing, completed, failed
    audio_file_path = Column(Text)  # Can store multiple paths separated by semicolon
    summary = Column(Text)
    processing_method = Column(String)  # "single", "chunked", "multiple_files"
    error_message = Column(Text)  # Store error details if processing fails
    total_duration = Column(Float)  # Total audio duration in seconds
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    transcripts = relationship("Transcript", back_populates="meeting")
    audio_chunks = relationship("AudioChunk", back_populates="meeting")
    speakers = relationship("Speaker", back_populates="meeting")

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    content = Column(JSON)  # Array of speaker segments with timestamps
    action_items = Column(JSON)  # Array of action items with metadata
    speakers = Column(JSON)  # List of identified speakers
    confidence_score = Column(Float)  # Overall confidence in transcription
    language_detected = Column(String)  # Detected language
    word_count = Column(Integer)  # Total word count
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="transcripts")

class AudioChunk(Base):
    __tablename__ = "audio_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    chunk_id = Column(Integer, nullable=False)  # Sequential chunk number
    file_path = Column(String, nullable=False)
    start_time = Column(Float)  # Start time in seconds
    end_time = Column(Float)  # End time in seconds
    duration = Column(Float)  # Chunk duration
    status = Column(String, default="uploaded")  # uploaded, processing, processed, failed
    transcript_data = Column(JSON)  # Chunk-specific transcript
    error_message = Column(Text)
    processing_time = Column(Float)  # Time taken to process in seconds
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="audio_chunks")

class Speaker(Base):
    __tablename__ = "speakers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    speaker_id = Column(String, nullable=False)  # From diarization (e.g., "SPEAKER_00")
    assigned_name = Column(String)  # User-assigned name
    total_speaking_time = Column(Float)  # Total speaking time in seconds
    word_count = Column(Integer)  # Total words spoken
    first_appearance = Column(Float)  # When speaker first appears (seconds)
    last_appearance = Column(Float)  # When speaker last appears (seconds)
    confidence_score = Column(Float)  # Confidence in speaker identification
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="speakers")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    job_type = Column(String, nullable=False)  # "transcription", "diarization", "summarization"
    status = Column(String, default="queued")  # queued, running, completed, failed
    priority = Column(Integer, default=5)  # 1 (highest) to 10 (lowest)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    result_data = Column(JSON)  # Store job results
    created_at = Column(DateTime, server_default=func.now())

class UploadSession(Base):
    __tablename__ = "upload_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    session_type = Column(String, nullable=False)  # "single", "chunked", "multiple"
    total_files = Column(Integer)
    uploaded_files = Column(Integer, default=0)
    total_size = Column(Integer)  # Total size in bytes
    uploaded_size = Column(Integer, default=0)  # Uploaded size in bytes
    status = Column(String, default="active")  # active, completed, failed, cancelled
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String)  # For future user management
    preferred_llm = Column(String, default="openrouter")  # "openrouter" or "ollama"
    openrouter_model = Column(String, default="anthropic/claude-3.5-sonnet")
    ollama_model = Column(String, default="llama3.1:8b")
    auto_process = Column(Boolean, default=True)
    chunk_size_minutes = Column(Integer, default=15)
    language_preference = Column(String, default="en")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

# Database migration script
def create_tables(engine):
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def upgrade_existing_tables(engine):
    """Add new columns to existing tables for backward compatibility"""
    from sqlalchemy import text
    
    migration_queries = [
        # Add new columns to meetings table
        "ALTER TABLE meetings ADD COLUMN IF NOT EXISTS platform VARCHAR",
        "ALTER TABLE meetings ADD COLUMN IF NOT EXISTS processing_method VARCHAR",
        "ALTER TABLE meetings ADD COLUMN IF NOT EXISTS error_message TEXT",
        "ALTER TABLE meetings ADD COLUMN IF NOT EXISTS total_duration FLOAT",
        
        # Add new columns to transcripts table
        "ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS speakers JSON",
        "ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS confidence_score FLOAT",
        "ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS language_detected VARCHAR",
        "ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS word_count INTEGER",
        
        # Add new columns to speakers table
        "ALTER TABLE speakers ADD COLUMN IF NOT EXISTS assigned_name VARCHAR",
        "ALTER TABLE speakers ADD COLUMN IF NOT EXISTS total_speaking_time FLOAT",
        "ALTER TABLE speakers ADD COLUMN IF NOT EXISTS word_count INTEGER",
        "ALTER TABLE speakers ADD COLUMN IF NOT EXISTS first_appearance FLOAT",
        "ALTER TABLE speakers ADD COLUMN IF NOT EXISTS last_appearance FLOAT",
        "ALTER TABLE speakers ADD COLUMN IF NOT EXISTS confidence_score FLOAT",
    ]
    
    with engine.connect() as conn:
        for query in migration_queries:
            try:
                conn.execute(text(query))
                conn.commit()
            except Exception as e:
                print(f"Migration warning: {query} - {e}")
```

## Enhanced Implementation Plan

### Phase 1: Core Backend with LLM Integration (Weeks 1-5)

**Week 1-2: Foundation & Environment Setup**
- Set up development environment with GPU support
- Install and configure Whisper + Pyannote.audio
- Set up OpenRouter API integration
- Install and configure Ollama for local LLM processing
- Create enhanced database schema with chunking support
- Implement basic audio chunking algorithm

**Week 3-4: Enhanced Audio Processing Pipeline**
- Build chunked audio processing system (10-15 min segments)
- Implement parallel chunk processing with Celery
- Create LLM service with OpenRouter/Ollama fallback
- Develop intelligent summarization and action item extraction
- Add audio preprocessing and format conversion

**Week 5: API Development & File Upload**
- Build enhanced FastAPI backend with file upload support
- Implement chunked upload endpoints
- Create real-time processing progress tracking
- Add multiple file upload support
- Implement background task management

### Phase 2: Universal Progressive Web Application (Weeks 6-8)

**Week 6-7: PWA Core Development**
- Build responsive PWA with React.js + TypeScript
- Implement Web Audio API for cross-platform recording
- Create adaptive UI components for mobile and desktop
- Add offline storage with IndexedDB
- Implement service worker for background sync
- Build intuitive meeting management interface

**Week 8: Enhanced PWA Features & Optimization**
- Add drag-and-drop file upload with progress tracking
- Implement chunked recording with real-time upload
- Create offline queue and automatic sync capabilities
- Add PWA manifest for native app-like installation
- Optimize performance for mobile devices
- Implement push notifications for processing updates

### Phase 3: Browser Extension & Virtual Meeting Integration (Weeks 11-13)

**Week 11-12: Browser Extension Development**
- Develop meeting detection logic for major platforms
- Implement audio capture from virtual meetings
- Add platform-specific integrations (Zoom, Teams, Meet, WebEx)
- Create popup interface for recording controls
- Implement automatic meeting join and recording

**Week 13: Integration Testing & Optimization**
- Cross-platform testing and bug fixes
- Performance optimization for large audio files
- Memory usage optimization for mobile devices
- Integration testing between all platforms

### Phase 4: Advanced AI Features & Intelligence (Weeks 14-16)

**Week 14: Enhanced AI Processing**
- Fine-tune LLM prompts for better summarization
- Implement sentiment analysis and mood tracking
- Add topic clustering and key insight extraction
- Develop meeting quality scoring algorithms
- Create speaker identification and naming system

**Week 15: Real-time Features**
- Implement live transcription during recording
- Add real-time speaker identification
- Create instant summary generation
- Develop live action item detection
- Add real-time collaboration features

**Week 16: Analytics & Insights**
- Build meeting analytics dashboard
- Implement trend analysis and insights
- Create meeting efficiency metrics
- Add comparative analysis features
- Develop recommendation system

### Phase 5: Enterprise Features & Production (Weeks 17-20)

**Week 17-18: Enterprise Features**
- Implement multi-tenant architecture
- Add role-based access control
- Create team collaboration features
- Build integration APIs for third-party systems
- Add compliance and audit features

**Week 19: Testing & Security**
- Comprehensive security audit
- Performance testing under load
- User acceptance testing
- Privacy compliance verification
- Documentation completion

**Week 20: Production Deployment**
- Production environment setup
- Monitoring and logging implementation
- User onboarding system
- Launch preparation and marketing materials
- Post-launch support system

### Key Milestones & Deliverables

**Milestone 1 (Week 5): Core Processing Engine**
- ✅ Audio chunking and parallel processing
- ✅ LLM integration with OpenRouter/Ollama
- ✅ Enhanced API with file upload support
- ✅ Database schema with chunking support

**Milestone 2 (Week 10): Cross-Platform Applications**
- ✅ Mobile app for iOS/Android
- ✅ Desktop app for Windows/Mac/Linux
- ✅ Progressive Web App
- ✅ File upload and management system

**Milestone 3 (Week 13): Browser Integration**
- ✅ Browser extension for virtual meetings
- ✅ Platform integrations (Zoom, Teams, Meet)
- ✅ Automatic meeting detection and recording
- ✅ Cross-platform compatibility testing

**Milestone 4 (Week 16): AI Intelligence**
- ✅ Advanced summarization and insights
- ✅ Real-time transcription and processing
- ✅ Speaker identification and analytics
- ✅ Meeting quality scoring

**Milestone 5 (Week 20): Production Launch**
- ✅ Enterprise-ready features
- ✅ Security and compliance
- ✅ Production deployment
- ✅ User onboarding and support

### Resource Requirements

**Development Team:**
- 2 Backend Developers (Python/FastAPI)
- 2 Frontend Developers (React Native/Electron)
- 1 AI/ML Engineer (LLM integration)
- 1 DevOps Engineer (Deployment/Infrastructure)
- 1 QA Engineer (Testing/Security)

**Infrastructure:**
- GPU-enabled servers for AI processing
- Cloud storage for audio files
- CDN for global distribution
- Database cluster for scalability
- Monitoring and logging systems

**Third-Party Services:**
- OpenRouter API credits
- Cloud hosting (AWS/GCP/Azure)
- Domain and SSL certificates
- App store developer accounts
- Analytics and monitoring tools

## Privacy & Security

### Data Protection Principles

1. **Local Processing First**: Process audio locally when possible to minimize data transmission
2. **Encryption**: Encrypt all stored audio files and transcripts
3. **Minimal Data Collection**: Only collect necessary metadata
4. **User Consent**: Explicit consent for recording and processing
5. **Data Retention**: Configurable retention policies

### Security Implementation

```python
# Encryption service for sensitive data
from cryptography.fernet import Fernet
import os
import base64

class EncryptionService:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def encrypt_file(self, file_path):
        """Encrypt audio file"""
        with open(file_path, "rb") as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        encrypted_path = f"{file_path}.encrypted"
        
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)
        
        # Remove original file
        os.remove(file_path)
        return encrypted_path
    
    def decrypt_file(self, encrypted_path):
        """Decrypt audio file for processing"""
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        original_path = encrypted_path.replace(".encrypted", "")
        
        with open(original_path, "wb") as f:
            f.write(decrypted_data)
        
        return original_path

# Privacy compliance middleware
@app.middleware("http")
async def privacy_middleware(request: Request, call_next):
    # Log data access
    if request.url.path.startswith("/api/"):
        # Implement audit logging
        pass
    
    response = await call_next(request)
    
    # Add privacy headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response
```

### Consent Management

```python
# Consent tracking system
class ConsentManager:
    def __init__(self, db_session):
        self.db = db_session
    
    def record_consent(self, meeting_id, participant_email, consent_type):
        """Record participant consent"""
        consent = Consent(
            meeting_id=meeting_id,
            participant_email=participant_email,
            consent_type=consent_type,  # "recording", "transcription", "ai_processing"
            granted_at=datetime.utcnow(),
            ip_address=request.remote_addr
        )
        self.db.add(consent)
        self.db.commit()
    
    def verify_consent(self, meeting_id, required_consents):
        """Verify all required consents are obtained"""
        consents = self.db.query(Consent).filter(
            Consent.meeting_id == meeting_id
        ).all()
        
        consent_types = {c.consent_type for c in consents}
        return all(consent in consent_types for consent in required_consents)
```

## Performance Considerations

### Resource Optimization

**CPU/GPU Usage:**
- Use GPU acceleration for Whisper (CUDA support)
- Implement model quantization for edge devices
- Background processing for non-real-time operations

**Memory Management:**
- Stream processing for large audio files
- Chunked processing to prevent memory overflow
- Model caching and warm-up strategies

**Storage Optimization:**
- Audio compression (OPUS codec)
- Transcript compression for storage
- Automated cleanup of temporary files

### Scalability Strategies

```python
# Horizontal scaling with Celery
from celery import Celery
import redis

# Configure Celery for distributed processing
celery_app = Celery(
    'meeting_assistant',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task
def process_audio_segment(audio_chunk_path, meeting_id, segment_id):
    """Process individual audio segments in parallel"""
    processor = AudioProcessor()
    return processor.process_chunk(audio_chunk_path, meeting_id, segment_id)

# Load balancing for multiple workers
class AudioProcessingQueue:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def add_processing_job(self, meeting_id, audio_path):
        """Add job to processing queue"""
        job_data = {
            'meeting_id': meeting_id,
            'audio_path': audio_path,
            'priority': 'normal',
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.redis_client.lpush('audio_processing_queue', json.dumps(job_data))
    
    def get_queue_status(self):
        """Get current queue status"""
        queue_length = self.redis_client.llen('audio_processing_queue')
        return {'pending_jobs': queue_length}
```

## Deployment Strategy

### Development Environment Setup

```bash
# Environment setup script using uv
#!/bin/bash

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project with uv
uv init meeting-assistant
cd meeting-assistant

# Add core AI dependencies
uv add torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
uv add git+https://github.com/openai/whisper.git
uv add pyannote.audio
uv add transformers datasets accelerate optimum

# Add backend dependencies
uv add fastapi uvicorn[standard]
uv add sqlalchemy alembic psycopg2-binary
uv add redis celery
uv add python-multipart aiofiles
uv add cryptography python-jose[cryptography]
uv add httpx ollama

# Add development dependencies
uv add --dev pytest pytest-asyncio pytest-cov
uv add --dev black isort flake8 mypy
uv add --dev pre-commit

# Add optional dependencies for specific features
uv add pyaudio soundfile librosa ffmpeg-python  # Audio processing
uv add spacy nltk textblob  # NLP utilities
uv add streamlit gradio  # Optional web interfaces

# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install ffmpeg postgresql redis-server

# Setup database
sudo -u postgres createdb meeting_assistant
sudo -u postgres createuser meeting_user --pwprompt

# Setup environment variables
echo "DATABASE_URL=postgresql://meeting_user:password@localhost/meeting_assistant" > .env
echo "REDIS_URL=redis://localhost:6379/0" >> .env
echo "OPENROUTER_API_KEY=your_openrouter_api_key" >> .env
echo "HF_TOKEN=your_huggingface_token" >> .env
echo "USE_LOCAL_LLM=false" >> .env

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running the Application

```bash
# Start the backend API
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (in another terminal)
uv run celery -A main.celery_app worker --loglevel=info

# Start Celery beat scheduler (for periodic tasks)
uv run celery -A main.celery_app beat --loglevel=info

# Run database migrations
uv run alembic upgrade head

# Run tests
uv run pytest

# Code formatting and linting
uv run black .
uv run isort .
uv run flake8 .
uv run mypy .
```

### Docker Configuration

```dockerfile
# Dockerfile for backend service using uv
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock first for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application using uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://meeting_user:password@db:5432/meeting_assistant
      - REDIS_URL=redis://redis:6379/0
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - HF_TOKEN=${HF_TOKEN}
      - USE_LOCAL_LLM=${USE_LOCAL_LLM}
    volumes:
      - ./uploads:/app/uploads
      - ./models:/app/models
    depends_on:
      - db
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  celery_worker:
    build: .
    command: uv run celery -A main.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://meeting_user:password@db:5432/meeting_assistant
      - REDIS_URL=redis://redis:6379/0
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - HF_TOKEN=${HF_TOKEN}
      - USE_LOCAL_LLM=${USE_LOCAL_LLM}
    volumes:
      - ./uploads:/app/uploads
      - ./models:/app/models
    depends_on:
      - db
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=meeting_assistant
      - POSTGRES_USER=meeting_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Production Deployment

```yaml
# Kubernetes deployment configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meeting-assistant-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: meeting-assistant-backend
  template:
    metadata:
      labels:
        app: meeting-assistant-backend
    spec:
      containers:
      - name: backend
        image: meeting-assistant:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: 1
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis_url
```

## Future Enhancements

### Planned Features

1. **Real-time Processing**
   - Live transcription during meetings
   - Real-time speaker identification
   - Instant summary generation

2. **Advanced AI Features**
   - Sentiment analysis and mood tracking
   - Topic clustering and analysis
   - Automatic agenda extraction
   - Meeting quality scoring

3. **Integration Ecosystem**
   - Calendar integration (Google, Outlook)
   - CRM integration (Salesforce, HubSpot)
   - Project management tools (Jira, Asana)
   - Communication platforms (Slack, Teams)

4. **Mobile Applications**
   - Native iOS/Android apps
   - Offline processing capabilities
   - Voice commands and controls

5. **Enterprise Features**
   - Multi-tenant architecture
   - Role-based access control
   - Advanced analytics dashboard
   - Compliance reporting

### Technology Roadmap

**Q1 2024: Foundation**
- Core transcription and diarization
- Basic web interface
- Browser extension MVP

**Q2 2024: Intelligence**
- Advanced summarization
- Action item extraction
- Speaker identification

**Q3 2024: Integration**
- Platform integrations
- API ecosystem
- Mobile applications

**Q4 2024: Enterprise**
- Multi-tenant support
- Advanced analytics
- Compliance features

## Summary of Enhanced Features

### Key Enhancements from Original Plan

**1. Advanced LLM Integration**
- **OpenRouter Integration**: Access to cutting-edge models (GPT-4, Claude, Gemini) for superior summarization
- **Ollama Fallback**: Local LLM processing for offline scenarios and privacy-conscious users
- **Intelligent Switching**: Automatic fallback from cloud to local processing based on availability
- **Custom Prompting**: Specialized prompts for meeting-specific tasks (summaries, action items, insights)

**2. Intelligent Audio Chunking**
- **Smart Segmentation**: 10-15 minute audio chunks for optimal processing efficiency
- **Parallel Processing**: Multiple chunks processed simultaneously for faster results
- **Memory Optimization**: Prevents memory overflow on large meeting recordings
- **Real-time Processing**: Chunks can be processed as they're recorded for live transcription

**3. Universal Progressive Web Application**
- **Single PWA**: Works seamlessly on mobile, desktop, and web browsers
- **Web Audio API**: Native-quality audio recording across all platforms
- **Offline-First**: IndexedDB storage with background sync capabilities
- **App-Like Experience**: PWA manifest for installation on any device
- **Responsive Design**: Adaptive UI optimized for both mobile and desktop

**4. Enhanced File Upload & Management**
- **Multiple File Support**: Upload and process multiple audio files for a single meeting
- **Drag & Drop Interface**: Intuitive file upload with progress tracking
- **Chunked Upload**: Large files uploaded in segments for reliability
- **Format Support**: Wide range of audio formats (WAV, MP3, M4A, WEBM, etc.)

**5. Real-time Processing Capabilities**
- **Live Transcription**: Real-time transcription during recording
- **Progress Tracking**: Real-time updates on processing status
- **Streaming Results**: Live transcript updates as chunks are processed
- **Background Processing**: Non-blocking processing with status updates

### Technical Innovations

**Hybrid AI Architecture:**
```mermaid
graph TD
    A[Audio Input] --> B[Chunking Service]
    B --> C[Whisper Transcription]
    B --> D[Pyannote Diarization]
    C --> E[LLM Processing Hub]
    D --> E
    E --> F{Internet Available?}
    F -->|Yes| G[OpenRouter API]
    F -->|No| H[Local Ollama]
    G --> I[Enhanced Summary]
    H --> I
    I --> J[Final Results]
```

**Simplified Architecture:**
```mermaid
graph LR
    A[Backend API] --> B[Browser Extension]
    A --> C[Progressive Web App]
    B --> D[Virtual Meetings]
    C --> E[Physical Meetings - Universal]
    C --> F[File Upload & Management]
    C --> G[Meeting Dashboard]
```

### Competitive Advantages

**1. Privacy-First Approach**
- Local processing option with Ollama
- No mandatory cloud data transmission
- User-controlled data retention policies
- Encrypted storage and transmission

**2. Superior Accuracy**
- Whisper: 99% transcription accuracy on clear audio
- Pyannote: 90% speaker diarization accuracy
- Advanced LLMs: Higher quality summaries than traditional NLP

**3. Flexible Deployment**
- Self-hosted or cloud deployment options
- Hybrid processing (cloud + local)
- Scalable architecture from single user to enterprise

**4. Comprehensive Platform Support**
- All major virtual meeting platforms
- Cross-platform mobile and desktop apps
- Browser-based universal access
- File upload for any audio source

**5. Advanced Intelligence**
- Context-aware summarization
- Intelligent action item extraction
- Speaker identification and analytics
- Meeting quality insights

### Implementation Roadmap Summary

| Phase | Duration | Key Deliverables | Primary Focus |
|-------|----------|------------------|---------------|
| **Phase 1** | Weeks 1-5 | Core backend, LLM integration, chunking | Foundation & AI |
| **Phase 2** | Weeks 6-10 | Mobile, desktop, and web applications | Cross-platform apps |
| **Phase 3** | Weeks 11-13 | Browser extension, virtual meeting integration | Virtual meetings |
| **Phase 4** | Weeks 14-16 | Advanced AI features, real-time processing | Intelligence layer |
| **Phase 5** | Weeks 17-20 | Enterprise features, production deployment | Launch ready |

### Success Metrics & KPIs

**Technical Performance:**
- Transcription accuracy: >95% for clear audio
- Speaker diarization accuracy: >90%
- Processing time: <1.5x audio duration (with chunking)
- System uptime: >99.9%
- Mobile app responsiveness: <2s load time

**User Experience:**
- User satisfaction score: >4.5/5
- Task completion rate: >90%
- Support ticket volume: <5% of active users
- Feature adoption rate: >70% for core features

**Business Metrics:**
- Development cost: ~$200K-300K for MVP
- Time to market: 20 weeks for full-featured product
- Scalability: Support 1000+ concurrent users
- Market differentiation: Unique hybrid AI approach

## Conclusion

This enhanced implementation plan delivers a next-generation meeting assistant that combines the best of open-source AI technology with modern software architecture. The solution addresses the key requirements you specified:

**✅ Virtual Meeting Support**: Browser extension with platform integrations
**✅ Physical Meeting Support**: Cross-platform mobile and desktop applications
**✅ File Upload Capability**: Multiple format support with drag-and-drop interface
**✅ Advanced LLM Integration**: OpenRouter for cloud processing, Ollama for local processing
**✅ Intelligent Audio Chunking**: 10-15 minute segments for optimal processing efficiency

The modular, privacy-first architecture ensures the solution can scale from individual users to enterprise deployments while maintaining competitive accuracy and performance. By leveraging cutting-edge open-source tools (Whisper, Pyannote) with modern LLM capabilities, this meeting assistant will deliver superior results compared to existing commercial solutions.

The 20-week implementation timeline provides a realistic path to a production-ready system that can compete with established players like Otter.ai, Fireflies.ai, and Rev.com, while offering unique advantages in privacy, flexibility, and cross-platform support.

**Next Steps:**
1. **Technical Validation**: Set up proof-of-concept with Whisper + Pyannote + OpenRouter/Ollama
2. **Architecture Review**: Validate technical decisions with development team
3. **Resource Planning**: Finalize team composition and infrastructure requirements
4. **Development Kickoff**: Begin Phase 1 implementation with core backend development

This implementation plan provides a solid foundation for building a competitive, feature-rich meeting assistant that can capture significant market share while maintaining user trust through transparent, privacy-focused design.