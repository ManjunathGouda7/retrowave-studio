"""Data models and enums for the asynchronous job queue."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    GIF = "gif"


class JobResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    job_type: JobType
    status: JobStatus
    progress: int = Field(0, ge=0, le=100, description="Completion percentage (0 to 100)")
    current_step: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class JobListResponse(BaseModel):
    total_jobs: int
    jobs: List[JobResponse]
