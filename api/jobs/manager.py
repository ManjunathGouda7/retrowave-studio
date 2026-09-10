"""
Thread-safe Asynchronous Job Manager with WebSocket Event Broadcasting.
Handles concurrent background workers, progress tracking, and event streaming.
"""
import asyncio
import io
import os
import shutil
import tempfile
import threading
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict, List, Optional
from PIL import Image

from filters.base import FILTER_REGISTRY
from utils.video_processor import VideoProcessor
from utils.effects import add_grain, add_light_leak
from utils.image_utils import (
    draw_date_stamp,
    add_polaroid_border,
    add_filmstrip_border,
    add_vhs_osd,
)
from api.jobs.models import JobStatus, JobType, JobResponse


def _dump_job(job_res: JobResponse) -> dict:
    if hasattr(job_res, "model_dump"):
        return job_res.model_dump()
    return job_res.dict()


class JobManager:
    """Singleton job queue manager."""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="retrowave_worker")
        self.jobs: Dict[str, dict] = {}
        self.lock = threading.Lock()
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        self.output_dir = os.path.join(os.getcwd(), "output", "jobs")
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _broadcast(self, job_id: str, data: dict):
        """Broadcast state update to all active WebSocket listeners for this job."""
        with self.lock:
            queues = list(self.subscribers.get(job_id, []))
        for q in queues:
            try:
                q.put_nowait(data)
            except Exception:
                pass

    def subscribe(self, job_id: str) -> asyncio.Queue:
        """Register a WebSocket client queue for a specific job."""
        q = asyncio.Queue()
        with self.lock:
            if job_id not in self.subscribers:
                self.subscribers[job_id] = []
            self.subscribers[job_id].append(q)
            # Send current state if job already exists
            if job_id in self.jobs:
                current_state = _dump_job(self._format_job_response(self.jobs[job_id]))
                q.put_nowait(current_state)
        return q

    def unsubscribe(self, job_id: str, q: asyncio.Queue):
        """Unregister a WebSocket client queue."""
        with self.lock:
            if job_id in self.subscribers and q in self.subscribers[job_id]:
                self.subscribers[job_id].remove(q)
                if not self.subscribers[job_id]:
                    del self.subscribers[job_id]

    def _format_job_response(self, job: dict) -> JobResponse:
        return JobResponse(
            job_id=job["id"],
            job_type=job["type"],
            status=job["status"],
            progress=job["progress"],
            current_step=job.get("current_step"),
            created_at=job["created_at"],
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            download_url=f"/api/v1/jobs/{job['id']}/download" if job["status"] == JobStatus.COMPLETED else None,
            error_message=job.get("error"),
            metadata=job.get("metadata", {})
        )

    def get_job(self, job_id: str) -> Optional[JobResponse]:
        """Retrieve job status."""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
            return self._format_job_response(job)

    def list_jobs(self, limit: int = 50) -> List[JobResponse]:
        """List all recent jobs."""
        with self.lock:
            sorted_jobs = sorted(self.jobs.values(), key=lambda j: j["created_at"], reverse=True)
            return [self._format_job_response(j) for j in sorted_jobs[:limit]]

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False
            if job["status"] in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                return False
            job["status"] = JobStatus.CANCELLED
            job["cancelled"] = True
            job["completed_at"] = self._get_timestamp()
            job["current_step"] = "Cancelled by user"

        self._broadcast(job_id, _dump_job(self._format_job_response(job)))
        return True

    def get_output_path(self, job_id: str) -> Optional[str]:
        """Get output file path for completed job."""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job or job["status"] != JobStatus.COMPLETED:
                return None
            return job.get("output_file")

    def submit_video_job(
        self,
        input_path: str,
        filter_name: str,
        intensity: float = 1.0,
        fps: int = 12,
        preview: bool = False,
        time_effects: list = None,
        video_format: str = "mp4",
        watermark: str = None,
    ) -> str:
        """Submit asynchronous video processing job."""
        job_id = str(uuid.uuid4())
        ext = ".gif" if video_format == "gif" else ".mp4"
        output_file = os.path.join(self.output_dir, f"{job_id}_{filter_name}{ext}")

        job = {
            "id": job_id,
            "type": JobType.VIDEO,
            "status": JobStatus.QUEUED,
            "progress": 0,
            "current_step": "Queued in worker pool",
            "created_at": self._get_timestamp(),
            "started_at": None,
            "completed_at": None,
            "input_file": input_path,
            "output_file": output_file,
            "error": None,
            "cancelled": False,
            "metadata": {
                "filter_name": filter_name,
                "fps": fps,
                "preview": preview,
                "time_effects": time_effects or [],
                "format": video_format
            }
        }

        with self.lock:
            self.jobs[job_id] = job

        self.executor.submit(
            self._execute_video_task,
            job_id,
            input_path,
            output_file,
            filter_name,
            intensity,
            fps,
            preview,
            time_effects,
            video_format,
            watermark
        )
        return job_id

    def _execute_video_task(
        self,
        job_id: str,
        input_path: str,
        output_file: str,
        filter_name: str,
        intensity: float,
        fps: int,
        preview: bool,
        time_effects: list,
        video_format: str,
        watermark: str,
    ):
        """Worker thread for video execution."""
        with self.lock:
            job = self.jobs[job_id]
            if job.get("cancelled"):
                return
            job["status"] = JobStatus.PROCESSING
            job["started_at"] = self._get_timestamp()
            job["current_step"] = "Initializing video frames"
        self._broadcast(job_id, _dump_job(self._format_job_response(job)))

        def progress_cb(current_frame, total_frames):
            with self.lock:
                if job.get("cancelled"):
                    return
                pct = int((current_frame / max(total_frames, 1)) * 100)
                job["progress"] = min(99, max(1, pct))
                job["current_step"] = f"Rendering frame {current_frame}/{total_frames} ({pct}%)"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))

        try:
            cls = FILTER_REGISTRY[filter_name]
            filter_obj = cls(intensity=intensity)

            mp4_out = output_file if video_format == "mp4" else None
            gif_out = output_file if video_format == "gif" else None

            VideoProcessor.process_video(
                input_path=input_path,
                filter_obj=filter_obj,
                output_mp4=mp4_out,
                output_gif=gif_out,
                target_fps=fps,
                is_preview=preview,
                time_effects=time_effects,
                watermark=watermark,
                progress_callback=progress_cb,
            )

            with self.lock:
                if job.get("cancelled"):
                    return
                job["status"] = JobStatus.COMPLETED
                job["progress"] = 100
                job["completed_at"] = self._get_timestamp()
                job["current_step"] = "Render completed successfully"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))

        except Exception as e:
            with self.lock:
                job["status"] = JobStatus.FAILED
                job["error"] = str(e)
                job["completed_at"] = self._get_timestamp()
                job["current_step"] = f"Failed: {str(e)}"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))

    def submit_image_job(
        self,
        input_path: str,
        filter_name: str,
        intensity: float = 1.0,
        date_stamp: str = None,
        polaroid: bool = False,
        film_border: bool = False,
        vhs_osd: bool = False,
        light_leak: bool = False,
        grain: float = 0.0,
    ) -> str:
        """Submit asynchronous image transformation job."""
        job_id = str(uuid.uuid4())
        output_file = os.path.join(self.output_dir, f"{job_id}_{filter_name}.jpg")

        job = {
            "id": job_id,
            "type": JobType.IMAGE,
            "status": JobStatus.QUEUED,
            "progress": 0,
            "current_step": "Queued in worker pool",
            "created_at": self._get_timestamp(),
            "started_at": None,
            "completed_at": None,
            "input_file": input_path,
            "output_file": output_file,
            "error": None,
            "cancelled": False,
            "metadata": {"filter_name": filter_name}
        }

        with self.lock:
            self.jobs[job_id] = job

        self.executor.submit(
            self._execute_image_task,
            job_id,
            input_path,
            output_file,
            filter_name,
            intensity,
            date_stamp,
            polaroid,
            film_border,
            vhs_osd,
            light_leak,
            grain
        )
        return job_id

    def _execute_image_task(
        self,
        job_id: str,
        input_path: str,
        output_file: str,
        filter_name: str,
        intensity: float,
        date_stamp: str,
        polaroid: bool,
        film_border: bool,
        vhs_osd: bool,
        light_leak: bool,
        grain: float,
    ):
        """Worker thread for image execution."""
        with self.lock:
            job = self.jobs[job_id]
            if job.get("cancelled"):
                return
            job["status"] = JobStatus.PROCESSING
            job["started_at"] = self._get_timestamp()
            job["progress"] = 25
            job["current_step"] = "Applying retro filter"
        self._broadcast(job_id, _dump_job(self._format_job_response(job)))

        try:
            img = Image.open(input_path).convert("RGB")
            cls = FILTER_REGISTRY[filter_name]
            result = cls(intensity=intensity).apply(img)

            with self.lock:
                job["progress"] = 65
                job["current_step"] = "Compositing finishing overlays"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))

            if light_leak:
                result = add_light_leak(result, intensity=0.45)
            if grain > 0:
                result = add_grain(result, amount=grain)
            if date_stamp:
                result = draw_date_stamp(result, date_str=date_stamp)
            if vhs_osd:
                result = add_vhs_osd(result)
            if polaroid:
                result = add_polaroid_border(result)
            elif film_border:
                result = add_filmstrip_border(result)

            result.save(output_file, format="JPEG", quality=95)

            with self.lock:
                job["status"] = JobStatus.COMPLETED
                job["progress"] = 100
                job["completed_at"] = self._get_timestamp()
                job["current_step"] = "Image processed successfully"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))

        except Exception as e:
            with self.lock:
                job["status"] = JobStatus.FAILED
                job["error"] = str(e)
                job["completed_at"] = self._get_timestamp()
                job["current_step"] = f"Failed: {str(e)}"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))

    def submit_batch_job(
        self,
        input_zip_path: str,
        filter_name: str,
        intensity: float = 1.0,
        date_stamp: str = None,
        polaroid: bool = False,
        film_border: bool = False,
        vhs_osd: bool = False,
        light_leak: bool = False,
        grain: float = 0.0,
    ) -> str:
        """Submit asynchronous batch media processing job (ZIP archive)."""
        job_id = str(uuid.uuid4())
        output_file = os.path.join(self.output_dir, f"{job_id}_batch_{filter_name}.zip")

        job = {
            "id": job_id,
            "type": JobType.BATCH,
            "status": JobStatus.QUEUED,
            "progress": 0,
            "current_step": "Queued in worker pool",
            "created_at": self._get_timestamp(),
            "started_at": None,
            "completed_at": None,
            "input_file": input_zip_path,
            "output_file": output_file,
            "error": None,
            "cancelled": False,
            "metadata": {"filter_name": filter_name}
        }

        with self.lock:
            self.jobs[job_id] = job

        self.executor.submit(
            self._execute_batch_task,
            job_id,
            input_zip_path,
            output_file,
            filter_name,
            intensity,
            date_stamp,
            polaroid,
            film_border,
            vhs_osd,
            light_leak,
            grain
        )
        return job_id

    def _execute_batch_task(
        self,
        job_id: str,
        input_zip_path: str,
        output_file: str,
        filter_name: str,
        intensity: float,
        date_stamp: str,
        polaroid: bool,
        film_border: bool,
        vhs_osd: bool,
        light_leak: bool,
        grain: float,
    ):
        """Worker thread for batch archive execution."""
        with self.lock:
            job = self.jobs[job_id]
            if job.get("cancelled"):
                return
            job["status"] = JobStatus.PROCESSING
            job["started_at"] = self._get_timestamp()
            job["progress"] = 5
            job["current_step"] = "Extracting batch archive"
        self._broadcast(job_id, _dump_job(self._format_job_response(job)))

        temp_dir = tempfile.mkdtemp(prefix=f"batch_{job_id}_")
        try:
            with zipfile.ZipFile(input_zip_path, 'r') as zf:
                all_files = [f for f in zf.namelist() if not f.startswith('__MACOSX/') and not f.startswith('.')]
                image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
                image_files = [f for f in all_files if f.lower().endswith(image_extensions)]

                if not image_files:
                    raise ValueError("No valid image files (.jpg, .png, .webp) found in ZIP archive.")

                total_images = len(image_files)
                processed_files = []

                cls = FILTER_REGISTRY[filter_name]
                filter_obj = cls(intensity=intensity)

                for idx, fname in enumerate(image_files, 1):
                    with self.lock:
                        if job.get("cancelled"):
                            return
                        pct = int((idx / total_images) * 90)
                        job["progress"] = max(5, pct)
                        job["current_step"] = f"Processing image {idx}/{total_images}: {os.path.basename(fname)}"
                    self._broadcast(job_id, _dump_job(self._format_job_response(job)))

                    with zf.open(fname) as file_handle:
                        img_bytes = file_handle.read()
                        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

                    res = filter_obj.apply(img)
                    if light_leak:
                        res = add_light_leak(res, intensity=0.45)
                    if grain > 0:
                        res = add_grain(res, amount=grain)
                    if date_stamp:
                        res = draw_date_stamp(res, date_str=date_stamp)
                    if vhs_osd:
                        res = add_vhs_osd(res)
                    if polaroid:
                        res = add_polaroid_border(res)
                    elif film_border:
                        res = add_filmstrip_border(res)

                    base_name = os.path.splitext(os.path.basename(fname))[0]
                    out_img_name = f"{base_name}_{filter_name}.jpg"
                    out_img_path = os.path.join(temp_dir, out_img_name)
                    res.save(out_img_path, format="JPEG", quality=95)
                    processed_files.append((out_img_path, out_img_name))

            # Pack into output zip
            with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as out_zip:
                for full_path, arc_name in processed_files:
                    out_zip.write(full_path, arc_name)

            with self.lock:
                job["status"] = JobStatus.COMPLETED
                job["progress"] = 100
                job["completed_at"] = self._get_timestamp()
                job["current_step"] = f"Batch complete ({total_images} images processed)"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))

        except Exception as e:
            with self.lock:
                job["status"] = JobStatus.FAILED
                job["error"] = str(e)
                job["completed_at"] = self._get_timestamp()
                job["current_step"] = f"Failed: {str(e)}"
            self._broadcast(job_id, _dump_job(self._format_job_response(job)))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# Global singleton instance
job_manager = JobManager()
