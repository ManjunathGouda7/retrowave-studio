"""
Retrowave Studio Enterprise REST API.
Production-grade microservice for retro image transformations and dynamic video processing.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import filters
from filters.base import FILTER_REGISTRY
from api.routes import filters as filters_router
from api.routes import images as images_router
from api.routes import videos as videos_router
from api.routes import jobs as jobs_router
from api.routes import websocket as websocket_router
from api.schemas import HealthResponse

app = FastAPI(
    title="Retrowave Studio Enterprise API",
    description="""
    ## 📼 Welcome to Retrowave Studio API
    
    A high-performance RESTful microservice for **110 authentic retro visual filters** and **dynamic video processing**.
    
    ### Key Features:
    * **110 Unique Filters** across 8 categories: Cyberpunk, Horror, Dreamy, 80s, 90s, Retro, Glitch, and Artistic.
    * **Asynchronous Job Queue**: Asynchronous rendering with live progress polling (`/api/v1/jobs/{id}`).
    * **Real-Time WebSockets**: Stream frame-by-frame progress percentages directly via `/ws/jobs/{id}`.
    * **Photographic Film Science**: CineStill halation, exposure-weighted film grain, and S-curves.
    * **Retro Overlays**: Glowing 7-segment camera date stamps, Polaroid frames, 35mm negative filmstrips, and VHS OSD.
    * **Dynamic Video Engine**: Frame-by-frame rendering with 8 temporal effects (Pulse, Strobe, VHS Wobble, Timestamp, Glitch, etc.).
    * **Dual Exports**: Direct MP4 video streaming and looping animated GIFs.
    """,
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for web, mobile, and third-party integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(filters_router.router)
app.include_router(images_router.router)
app.include_router(videos_router.router)
app.include_router(jobs_router.router)
app.include_router(websocket_router.router)


@app.get("/", include_in_schema=False)
def root():
    """Redirect root to interactive OpenAPI docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse, tags=["Health Check"])
def health_check():
    """Service health check endpoint."""
    categories = sorted(list(set(cls.category for cls in FILTER_REGISTRY.values())))
    return HealthResponse(
        status="healthy",
        version="1.1.0",
        service="retrowave-studio-api",
        total_filters=len(FILTER_REGISTRY),
        categories=categories,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
