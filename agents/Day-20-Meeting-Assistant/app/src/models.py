"""
SQLAlchemy models for Meeting Assistant
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, 
    ForeignKey, Enum, JSON, LargeBinary
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from src.database import Base


class ProcessingStatus(PyEnum):
    """Enum for processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MeetingType(PyEnum):
    """Enum for meeting types"""
    VIRTUAL = "virtual"
    PHYSICAL = "physical"
    HYBRID = "hybrid"


class Meeting(Base):
    """Meeting model - represents a meeting session"""
    
    __tablename__ = "meetings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_type: Mapped[MeetingType] = mapped_column(
        Enum(MeetingType), default=MeetingType.VIRTUAL
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    meeting_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Processing status
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    
    # Meeting metadata
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    participant_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # zoom, teams, meet, etc.
    meeting_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    audio_chunks: Mapped[List["AudioChunk"]] = relationship(
        "AudioChunk", back_populates="meeting", cascade="all, delete-orphan"
    )
    transcripts: Mapped[List["Transcript"]] = relationship(
        "Transcript", back_populates="meeting", cascade="all, delete-orphan"
    )
    speakers: Mapped[List["Speaker"]] = relationship(
        "Speaker", back_populates="meeting", cascade="all, delete-orphan"
    )
    summaries: Mapped[List["MeetingSummary"]] = relationship(
        "MeetingSummary", back_populates="meeting", cascade="all, delete-orphan"
    )
    action_items: Mapped[List["ActionItem"]] = relationship(
        "ActionItem", back_populates="meeting", cascade="all, delete-orphan"
    )


class AudioChunk(Base):
    """Audio chunk model - represents processed audio segments"""
    
    __tablename__ = "audio_chunks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meetings.id"), nullable=False)
    
    # Chunk information
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)  # seconds
    end_time: Mapped[float] = mapped_column(Float, nullable=False)  # seconds
    duration: Mapped[float] = mapped_column(Float, nullable=False)  # seconds
    
    # File information
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    format: Mapped[str] = mapped_column(String(10), nullable=False)  # wav, mp3, etc.
    
    # Processing status
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="audio_chunks")
    transcripts: Mapped[List["Transcript"]] = relationship(
        "Transcript", back_populates="audio_chunk", cascade="all, delete-orphan"
    )


class Speaker(Base):
    """Speaker model - represents identified speakers in meetings"""
    
    __tablename__ = "speakers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meetings.id"), nullable=False)
    
    # Speaker identification
    speaker_label: Mapped[str] = mapped_column(String(50), nullable=False)  # SPEAKER_00, SPEAKER_01, etc.
    speaker_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Human-readable name
    
    # Speaker characteristics (for voice fingerprinting)
    voice_characteristics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Speaking statistics
    total_speaking_time: Mapped[float] = mapped_column(Float, default=0.0)  # seconds
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="speakers")
    transcripts: Mapped[List["Transcript"]] = relationship(
        "Transcript", back_populates="speaker", cascade="all, delete-orphan"
    )


class Transcript(Base):
    """Transcript model - represents transcribed text segments"""
    
    __tablename__ = "transcripts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meetings.id"), nullable=False)
    audio_chunk_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("audio_chunks.id"), nullable=True
    )
    speaker_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("speakers.id"), nullable=True
    )
    
    # Transcript content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 to 1.0
    
    # Timing information
    start_time: Mapped[float] = mapped_column(Float, nullable=False)  # seconds from meeting start
    end_time: Mapped[float] = mapped_column(Float, nullable=False)  # seconds from meeting start
    
    # Word-level data (optional)
    word_timestamps: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="transcripts")
    audio_chunk: Mapped[Optional["AudioChunk"]] = relationship(
        "AudioChunk", back_populates="transcripts"
    )
    speaker: Mapped[Optional["Speaker"]] = relationship("Speaker", back_populates="transcripts")


class MeetingSummary(Base):
    """Meeting summary model - represents AI-generated summaries"""
    
    __tablename__ = "meeting_summaries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meetings.id"), nullable=False)
    
    # Summary content
    summary_type: Mapped[str] = mapped_column(String(50), nullable=False)  # brief, detailed, executive
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Key topics and insights
    key_topics: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    insights: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # AI model information
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="summaries")


class ActionItem(Base):
    """Action item model - represents tasks and decisions from meetings"""
    
    __tablename__ = "action_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meetings.id"), nullable=False)
    
    # Action item content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assignee: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Priority and status
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, urgent
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, in_progress, completed, cancelled
    
    # Context information
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # surrounding discussion
    transcript_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # AI extraction metadata
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extracted_by: Mapped[str] = mapped_column(String(100), nullable=False)  # AI model used
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="action_items")


class ProcessingLog(Base):
    """Processing log model - tracks processing steps and errors"""
    
    __tablename__ = "processing_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("meetings.id"), nullable=True)
    
    # Log information
    process_type: Mapped[str] = mapped_column(String(100), nullable=False)  # transcription, diarization, summarization
    status: Mapped[ProcessingStatus] = mapped_column(Enum(ProcessingStatus), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing and performance
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Error details
    error_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Additional metadata
    process_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )