"""
Automated test suite for Phase 4: 3D LUT Generator, Batch Queue, Analytics & Security.
"""
import io
import os
import sys
import time
import zipfile
import pytest
from PIL import Image
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)


def test_export_filter_lut():
    """Verify downloading 3D .cube LUT for an authentic retro filter."""
    res = client.get("/api/v1/lut/filter/cyber_neon?size=17")
    assert res.status_code == 200
    assert "retrowave_cyber_neon.cube" in res.headers.get("content-disposition", "")
    content = res.text
    assert 'TITLE "CYBER_NEON"' in content
    assert "LUT_3D_SIZE 17" in content
    assert "DOMAIN_MIN 0.0 0.0 0.0" in content


def test_export_custom_lut():
    """Verify generating custom color grading .cube LUT."""
    payload = {
        "title": "NEON_SUNSET",
        "temperature": 0.45,
        "tint": -0.2,
        "contrast": 1.25,
        "saturation": 1.4,
        "size": 17,
    }
    res = client.post("/api/v1/lut/custom", json=payload)
    assert res.status_code == 200
    assert "neon_sunset.cube" in res.headers.get("content-disposition", "")
    content = res.text
    assert 'TITLE "NEON_SUNSET"' in content
    assert "LUT_3D_SIZE 17" in content


def test_analytics_endpoint():
    """Verify analytics telemetry endpoint returns expected metrics."""
    res = client.get("/api/v1/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "uptime_seconds" in data
    assert "breakdown_by_type" in data
    assert "breakdown_by_status" in data


def test_submit_and_poll_batch_job():
    """Verify submitting a ZIP archive of images to the batch queue and downloading result."""
    # Create an in-memory zip archive with 2 small test images
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        img1 = Image.new("RGB", (64, 64), color="blue")
        img2 = Image.new("RGB", (64, 64), color="magenta")
        b1, b2 = io.BytesIO(), io.BytesIO()
        img1.save(b1, format="JPEG")
        img2.save(b2, format="JPEG")
        zf.writestr("test1.jpg", b1.getvalue())
        zf.writestr("test2.jpg", b2.getvalue())

    zip_buffer.seek(0)

    # Submit batch job
    files = {"file": ("test_batch.zip", zip_buffer.getvalue(), "application/zip")}
    data = {
        "filter_name": "retro_kodachrome",
        "intensity": "0.85",
        "grain": "0.05",
    }
    res = client.post("/api/v1/jobs/batch", files=files, data=data)
    assert res.status_code == 202
    job_info = res.json()
    job_id = job_info["job_id"]
    assert job_info["job_type"] == "batch"

    # Poll until completed
    max_wait = 10
    start = time.time()
    completed = False

    while time.time() - start < max_wait:
        poll_res = client.get(f"/api/v1/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] == "completed":
            completed = True
            assert poll_data["progress"] == 100
            break
        elif poll_data["status"] == "failed":
            pytest.fail(f"Batch job failed: {poll_data.get('error_message')}")
        time.sleep(0.3)

    assert completed, "Batch job did not complete within timeout"

    # Download batch result ZIP
    dl_res = client.get(f"/api/v1/jobs/{job_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/zip"

    # Verify returned zip contains the processed images
    with zipfile.ZipFile(io.BytesIO(dl_res.content), "r") as result_zip:
        names = result_zip.namelist()
        assert len(names) == 2
        assert any("test1_retro_kodachrome.jpg" in n for n in names)
        assert any("test2_retro_kodachrome.jpg" in n for n in names)


def test_api_key_auth(monkeypatch):
    """Verify API key authentication when RETROWAVE_API_KEY is configured."""
    monkeypatch.setenv("RETROWAVE_API_KEY", "test-secret-key-123")

    # Protected endpoint without header should return 401
    res = client.get("/api/v1/filters")
    assert res.status_code == 401

    # Protected endpoint with valid header should return 200
    res2 = client.get("/api/v1/filters", headers={"X-API-Key": "test-secret-key-123"})
    assert res2.status_code == 200
    assert res2.headers.get("X-RateLimit-Tier") == "enterprise"

    # Public/docs/health endpoints should still be accessible without key
    res3 = client.get("/health")
    assert res3.status_code == 200
