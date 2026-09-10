"""Telemetry and analytics endpoints for Retrowave Studio enterprise operations."""
import time
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter
from api.jobs.manager import job_manager

router = APIRouter(prefix="/api/v1/analytics", tags=["Enterprise Analytics & Telemetry"])

# In-memory metrics tracker
SERVER_START_TIME = time.time()


@router.get("", summary="Retrieve real-time service metrics and usage telemetry")
def get_analytics() -> Dict[str, Any]:
    """Return real-time usage telemetry, job statistics, and active workers."""
    jobs = job_manager.list_jobs(limit=500)

    total_jobs = len(jobs)
    video_jobs = sum(1 for j in jobs if j.job_type == "video")
    image_jobs = sum(1 for j in jobs if j.job_type == "image")
    batch_jobs = sum(1 for j in jobs if j.job_type == "batch")

    completed = sum(1 for j in jobs if j.status == "completed")
    processing = sum(1 for j in jobs if j.status == "processing")
    queued = sum(1 for j in jobs if j.status == "queued")
    failed = sum(1 for j in jobs if j.status == "failed")

    # Count popular filters
    filter_counts: Dict[str, int] = {}
    for j in jobs:
        fname = (j.metadata or {}).get("filter_name")
        if fname:
            filter_counts[fname] = filter_counts.get(fname, 0) + 1

    top_filters = sorted(filter_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    uptime_seconds = int(time.time() - SERVER_START_TIME)

    return {
        "status": "online",
        "uptime_seconds": uptime_seconds,
        "total_jobs_submitted": total_jobs,
        "breakdown_by_type": {
            "video": video_jobs,
            "image": image_jobs,
            "batch": batch_jobs,
        },
        "breakdown_by_status": {
            "completed": completed,
            "processing": processing,
            "queued": queued,
            "failed": failed,
        },
        "top_filters": [{"name": k, "usage_count": v} for k, v in top_filters],
        "active_subscribers": sum(len(qs) for qs in job_manager.subscribers.values()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
