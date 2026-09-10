# Multi-stage production container for Retrowave Studio
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PORT=8000

# Install required system libraries for OpenCV and FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose ports for both FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Healthcheck for FastAPI microservice
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command starts FastAPI microservice
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
