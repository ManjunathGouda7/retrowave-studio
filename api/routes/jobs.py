"""Asynchronous job management and polling endpoints."""
import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from filters.base import FILTER_REGISTRY
from api.jobs.manager import job_manager
from api.jobs.models import JobResponse, JobListResponse

router = APIRouter(prefix="/api/v1/jobs", tags=["Asynchronous Job Queue"])


@router.post("/video", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, summary="Queue video for async processing")
async def queue_video_job(
    file: UploadFile = File(..., description="Video clip file"),
    filter_name: str = Form("cyber_blade_runner"),
    intensity: float = Form(1.0, ge=0.0, le=1.0),
    fps: int = Form(12),
    preview: bool = Form(False, description="Render only first 3 seconds"),
    time_effects: Optional[str] = Form(None, description="Comma-separated: pulse,strobe,vhs_wobble,timestamp,etc."),
    video_format: str = Form("mp4", description="'mp4' or 'gif'"),
    watermark: Optional[str] = Form(None),
):
    """Submit a video clip for asynchronous background rendering. Returns job_id immediately."""
    if filter_name not in FILTER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Filter '{filter_name}' not found")

    suffix = Path(file.filename or "video.mp4").suffix.lower() or ".mp4"
    temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        temp_in.write(content)
        temp_in.flush()
    finally:
        temp_in.close()

    effects_list = [e.strip() for e in time_effects.split(",")] if time_effects else []

    job_id = job_manager.submit_video_job(
        input_path=temp_in.name,
        filter_name=filter_name,
        intensity=intensity,
        fps=fps,
        preview=preview,
        time_effects=effects_list,
        video_format=video_format,
        watermark=watermark,
    )
    job = job_manager.get_job(job_id)
    return job


@router.post("/image", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, summary="Queue image for async processing")
async def queue_image_job(
    file: UploadFile = File(..., description="Image file"),
    filter_name: str = Form("cyber_neon"),
    intensity: float = Form(1.0, ge=0.0, le=1.0),
    date_stamp: Optional[str] = Form(None),
    polaroid: bool = Form(False),
    film_border: bool = Form(False),
    vhs_osd: bool = Form(False),
    light_leak: bool = Form(False),
    grain: float = Form(0.0),
):
    """Submit an image for asynchronous background processing."""
    if filter_name not in FILTER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Filter '{filter_name}' not found")

    suffix = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
    temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        temp_in.write(content)
        temp_in.flush()
    finally:
        temp_in.close()

    job_id = job_manager.submit_image_job(
        input_path=temp_in.name,
        filter_name=filter_name,
        intensity=intensity,
        date_stamp=date_stamp,
        polaroid=polaroid,
        film_border=film_border,
        vhs_osd=vhs_osd,
        light_leak=light_leak,
        grain=grain,
    )
    job = job_manager.get_job(job_id)
    return job


@router.get("", response_model=JobListResponse, summary="List all recent jobs")
def list_jobs(limit: int = 50):
    """List recent background rendering jobs and statuses."""
    jobs = job_manager.list_jobs(limit=limit)
    return JobListResponse(total_jobs=len(jobs), jobs=jobs)


@router.get("/{job_id}", response_model=JobResponse, summary="Poll job status & progress")
def get_job_status(job_id: str):
    """Get the live status and progress percentage (0-100%) of a specific job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job


@router.delete("/{job_id}", summary="Cancel a running or queued job")
def cancel_job(job_id: str):
    """Cancel an active or queued background rendering job."""
    success = job_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Job '{job_id}' could not be cancelled or does not exist")
    return {"status": "cancelled", "job_id": job_id}


@router.get("/{job_id}/download", summary="Download finished media artifact")
def download_job_output(job_id: str):
    """Download the completed processed media file for a finished job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Job is not completed yet (current status: '{job.status}')")

    out_path = job_manager.get_output_path(job_id)
    if not out_path or not os.path.exists(out_path):
        raise HTTPException(status_code=404, detail="Output file not found on server")

    ext = Path(out_path).suffix.lower()
    media_type = "video/mp4" if ext == ".mp4" else ("image/gif" if ext == ".gif" else "image/jpeg")
    return FileResponse(out_path, media_type=media_type, filename=os.path.basename(out_path))
