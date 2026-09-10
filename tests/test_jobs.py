"""
Automated tests for asynchronous job queue and WebSocket streaming.
"""
import io
import os
import sys
import time
import cv2
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)


def test_submit_and_poll_image_job():
    """Verify asynchronous image job submission, polling, and artifact download."""
    img = Image.new("RGB", (100, 100), color=(120, 80, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    # 1. Submit job (HTTP 202 Accepted)
    response = client.post(
        "/api/v1/jobs/image",
        files={"file": ("test.jpg", buf, "image/jpeg")},
        data={"filter_name": "cyber_neon", "intensity": "1.0", "date_stamp": "'89 10 24"}
    )
    assert response.status_code == 202
    job_data = response.json()
    job_id = job_data["job_id"]
    assert job_id is not None
    assert job_data["status"] in ("queued", "processing", "completed")

    # 2. Poll until completed (timeout 10s)
    completed = False
    for _ in range(20):
        time.sleep(0.3)
        poll_res = client.get(f"/api/v1/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] == "completed":
            completed = True
            assert poll_data["progress"] == 100
            assert poll_data["download_url"] is not None
            break

    assert completed, "Image job did not complete within timeout"

    # 3. Download finished artifact
    dl_res = client.get(f"/api/v1/jobs/{job_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "image/jpeg"
    assert len(dl_res.content) > 1000


def test_submit_and_poll_video_job():
    """Verify asynchronous video job submission, polling, and artifact download."""
    # Create small synthetic test video (12 frames)
    w, h = 160, 120
    temp_video = "tests_sample_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(temp_video, fourcc, 12, (w, h))
    for i in range(12):
        frame = np.full((h, w, 3), (i * 15, 100, 180), dtype=np.uint8)
        writer.write(frame)
    writer.release()

    with open(temp_video, "rb") as vf:
        video_bytes = vf.read()

    if os.path.exists(temp_video):
        os.remove(temp_video)

    # 1. Submit video job (HTTP 202)
    response = client.post(
        "/api/v1/jobs/video",
        files={"file": ("test.mp4", io.BytesIO(video_bytes), "video/mp4")},
        data={
            "filter_name": "cyber_blade_runner",
            "intensity": "0.9",
            "fps": "12",
            "preview": "true",
            "time_effects": "pulse,timestamp"
        }
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # 2. Poll until completed
    completed = False
    for _ in range(30):
        time.sleep(0.4)
        poll_res = client.get(f"/api/v1/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] == "completed":
            completed = True
            assert poll_data["progress"] == 100
            break

    assert completed, "Video job did not complete within timeout"

    # 3. Download finished video
    dl_res = client.get(f"/api/v1/jobs/{job_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "video/mp4"
    assert len(dl_res.content) > 1000


def test_list_jobs():
    """Verify listing recent jobs endpoint."""
    response = client.get("/api/v1/jobs?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


def test_cancel_job():
    """Verify job cancellation."""
    img = Image.new("RGB", (60, 60), color=(10, 20, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    # Submit job
    response = client.post(
        "/api/v1/jobs/image",
        files={"file": ("test.jpg", buf, "image/jpeg")},
        data={"filter_name": "cyber_neon"}
    )
    job_id = response.json()["job_id"]

    # Cancel job
    del_res = client.delete(f"/api/v1/jobs/{job_id}")
    # Might be 200 or 400 if already finished immediately
    assert del_res.status_code in (200, 400)


def test_websocket_streaming():
    """Verify WebSocket connection and real-time streaming event delivery."""
    img = Image.new("RGB", (80, 80), color=(20, 180, 220))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    # Submit job
    response = client.post(
        "/api/v1/jobs/image",
        files={"file": ("test.jpg", buf, "image/jpeg")},
        data={"filter_name": "dreamy_bubblegum"}
    )
    job_id = response.json()["job_id"]

    # Connect to WebSocket
    with client.websocket_connect(f"/ws/jobs/{job_id}") as websocket:
        # Receive first event
        data = websocket.receive_json()
        assert "job_id" in data
        assert data["job_id"] == job_id
        assert "status" in data
        assert "progress" in data
