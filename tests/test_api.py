"""
Automated tests for FastAPI microservice endpoints.
"""
import io
import os
import sys
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

# Ensure root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)


def test_health():
    """Verify health endpoint returns 200 and healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_filters"] == 110
    assert len(data["categories"]) == 8


def test_list_filters():
    """Verify listing all filters returns 110 filters."""
    response = client.get("/api/v1/filters")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 110
    assert len(data["filters"]) == 110


def test_filter_by_category():
    """Verify filtering by specific category."""
    response = client.get("/api/v1/filters?category=cyberpunk")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    for item in data["filters"]:
        assert item["category"] == "cyberpunk"


def test_get_categories():
    """Verify categories summary endpoint."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["total_categories"] == 8
    assert data["total_filters"] == 110


def test_get_filter_detail():
    """Verify retrieving a single filter."""
    response = client.get("/api/v1/filters/cyber_blade_runner")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "cyber_blade_runner"
    assert data["category"] == "cyberpunk"


def test_get_filter_not_found():
    """Verify 404 for nonexistent filter."""
    response = client.get("/api/v1/filters/non_existent_filter_xyz")
    assert response.status_code == 404


def test_process_image_binary():
    """Verify image processing endpoint with binary return."""
    # Create synthetic test image
    img = Image.new("RGB", (120, 90), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/v1/process/image",
        files={"file": ("test.jpg", buf, "image/jpeg")},
        data={
            "filter_name": "cyber_neon",
            "intensity": "0.9",
            "date_stamp": "'89 10 24",
            "polaroid": "true",
            "response_type": "binary"
        }
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert len(response.content) > 1000


def test_process_image_json():
    """Verify image processing endpoint with JSON base64 return."""
    img = Image.new("RGB", (60, 60), color=(200, 50, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/v1/process/image",
        files={"file": ("test.jpg", buf, "image/jpeg")},
        data={
            "filter_name": "horror_grindhouse",
            "intensity": "1.0",
            "response_type": "json"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filter_applied"] == "horror_grindhouse"
    assert len(data["base64_data"]) > 100


def test_process_image_gif():
    """Verify animated GIF generation endpoint."""
    img = Image.new("RGB", (80, 80), color=(50, 180, 120))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/v1/process/image/gif",
        files={"file": ("test.jpg", buf, "image/jpeg")},
        data={
            "filter_name": "dreamy_bubblegum",
            "anim_type": "neon_pulse",
            "num_frames": "4",
            "duration": "100"
        }
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/gif"
    assert len(response.content) > 1000
