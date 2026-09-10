"""Endpoints for video processing with dynamic time effects."""
import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from filters.base import FILTER_REGISTRY
from utils.video_processor import VideoProcessor

router = APIRouter(prefix="/api/v1/process", tags=["Video Processing"])


def cleanup_temp_files(*paths):
    """Background task to remove temporary processed video files."""
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass


@router.post("/video", summary="Process a video clip with retro filter and time effects")
async def process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video file (MP4, MOV, AVI, WEBM, MKV)"),
    filter_name: str = Form("cyber_blade_runner", description="Retro filter name"),
    intensity: float = Form(1.0, ge=0.0, le=1.0),
    fps: int = Form(12, description="Target frame rate: 8, 12, 15, or 24"),
    preview: bool = Form(True, description="If True, only renders first 3 seconds for speed"),
    time_effects: Optional[str] = Form(None, description="Comma-separated: pulse,strobe,chromatic_cycle,vhs_wobble,timestamp,zoom_punch,glitch_interval,film_burn"),
    video_format: str = Form("mp4", description="'mp4' or 'gif'"),
    watermark: Optional[str] = Form(None, description="Optional watermark overlay text"),
):
    """Process an uploaded video clip frame-by-frame with dynamic temporal effects."""
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

    cls = FILTER_REGISTRY[filter_name]
    filter_obj = cls(intensity=intensity)

    effects_list = [e.strip() for e in time_effects.split(",")] if time_effects else []

    temp_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name if video_format == "mp4" else None
    temp_gif = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name if video_format == "gif" else None

    try:
        res = VideoProcessor.process_video(
            input_path=temp_in.name,
            filter_obj=filter_obj,
            output_mp4=temp_mp4,
            output_gif=temp_gif,
            target_fps=fps,
            is_preview=preview,
            time_effects=effects_list,
            watermark=watermark,
        )
    except Exception as e:
        cleanup_temp_files(temp_in.name, temp_mp4, temp_gif)
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

    # Schedule cleanup of temp input file
    background_tasks.add_task(cleanup_temp_files, temp_in.name)

    if video_format == "mp4" and temp_mp4 and os.path.exists(temp_mp4):
        background_tasks.add_task(cleanup_temp_files, temp_mp4)
        return FileResponse(
            temp_mp4,
            media_type="video/mp4",
            filename=f"retro_{Path(file.filename or 'video').stem}_{filter_name}.mp4"
        )
    elif video_format == "gif" and temp_gif and os.path.exists(temp_gif):
        background_tasks.add_task(cleanup_temp_files, temp_gif)
        return FileResponse(
            temp_gif,
            media_type="image/gif",
            filename=f"retro_{Path(file.filename or 'video').stem}_{filter_name}.gif"
        )
    else:
        cleanup_temp_files(temp_in.name, temp_mp4, temp_gif)
        raise HTTPException(status_code=500, detail="Output video file could not be generated")
