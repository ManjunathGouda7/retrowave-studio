"""Endpoints for image processing and animated GIF generation."""
import base64
import io
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from PIL import Image

from filters.base import FILTER_REGISTRY
from utils.effects import add_grain, add_light_leak, add_halation
from utils.image_utils import (
    draw_date_stamp,
    add_polaroid_border,
    add_filmstrip_border,
    add_vhs_osd,
    create_retro_gif,
)
from api.schemas import ProcessImageBase64Response

router = APIRouter(prefix="/api/v1/process", tags=["Image Processing"])


@router.post("/image", summary="Apply retro filter & overlays to an image")
async def process_image(
    file: UploadFile = File(..., description="Source image file (JPG, PNG, WebP)"),
    filter_name: str = Form("cyber_neon", description="Name of the retro filter (from /api/v1/filters)"),
    intensity: float = Form(1.0, ge=0.0, le=1.0, description="Filter strength (0.0 to 1.0)"),
    date_stamp: Optional[str] = Form(None, description="Optional glowing 7-segment date stamp (e.g. \"'89 10 24\")"),
    polaroid: bool = Form(False, description="Encase inside Polaroid 600 frame"),
    film_border: bool = Form(False, description="Add 35mm film negative border with sprockets"),
    vhs_osd: bool = Form(False, description="Add vintage VCR On-Screen Display"),
    light_leak: bool = Form(False, description="Add warm camera light flare"),
    grain: float = Form(0.0, ge=0.0, le=0.5, description="Extra film grain intensity"),
    response_type: str = Form("binary", description="'binary' for JPEG stream or 'json' for base64"),
):
    """Process an uploaded image through any of the 110 retro filters with finishing overlays."""
    if filter_name not in FILTER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Filter '{filter_name}' not found. Check GET /api/v1/filters")

    try:
        content = await file.read()
        pil_img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    cls = FILTER_REGISTRY[filter_name]
    filter_obj = cls(intensity=intensity)
    result = filter_obj.apply(pil_img)

    # Apply optional finishing overlays
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

    buf = io.BytesIO()
    result.save(buf, format="JPEG", quality=95)
    jpeg_bytes = buf.getvalue()

    if response_type == "json":
        b64_str = base64.b64encode(jpeg_bytes).decode("utf-8")
        return ProcessImageBase64Response(
            success=True,
            filter_applied=filter_name,
            intensity=intensity,
            width=result.width,
            height=result.height,
            mime_type="image/jpeg",
            base64_data=b64_str
        )

    return Response(
        content=jpeg_bytes,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"inline; filename=retro_{filter_name}.jpg"}
    )


@router.post("/image/gif", summary="Generate looping animated retro GIF from image")
async def process_image_to_gif(
    file: UploadFile = File(..., description="Source image file"),
    filter_name: str = Form("cyber_neon", description="Name of the retro filter"),
    intensity: float = Form(1.0, ge=0.0, le=1.0),
    anim_type: str = Form("vhs_jitter", description="Animation style: 'vhs_jitter', 'neon_pulse', or 'crt_roll'"),
    num_frames: int = Form(8, ge=4, le=24, description="Number of animation frames"),
    duration: int = Form(120, ge=40, le=500, description="Frame duration in milliseconds"),
):
    """Generate a multi-frame looping animated retro GIF."""
    if filter_name not in FILTER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Filter '{filter_name}' not found")

    try:
        content = await file.read()
        pil_img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    cls = FILTER_REGISTRY[filter_name]
    filter_obj = cls(intensity=intensity)

    try:
        gif_bytes = create_retro_gif(
            img=pil_img,
            filter_obj=filter_obj,
            anim_type=anim_type,
            num_frames=num_frames,
            duration=duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GIF generation failed: {str(e)}")

    return Response(
        content=gif_bytes,
        media_type="image/gif",
        headers={"Content-Disposition": f"attachment; filename=retro_{filter_name}_{anim_type}.gif"}
    )
