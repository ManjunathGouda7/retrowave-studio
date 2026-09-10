"""3D LUT (.cube) generation and export endpoints for video editing suites."""
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field

from filters.base import FILTER_REGISTRY
from utils.lut_generator import LUTGenerator

router = APIRouter(prefix="/api/v1/lut", tags=["3D LUT Engine (.cube)"])


class CustomLUTRequest(BaseModel):
    title: str = Field("RETROWAVE_CUSTOM", description="LUT title shown inside DaVinci/Premiere")
    temperature: float = Field(0.0, ge=-1.0, le=1.0, description="-1.0 (cool cyan) to +1.0 (warm amber)")
    tint: float = Field(0.0, ge=-1.0, le=1.0, description="-1.0 (green) to +1.0 (magenta)")
    contrast: float = Field(1.0, ge=0.2, le=2.5, description="S-curve contrast slope")
    saturation: float = Field(1.0, ge=0.0, le=2.5, description="Color saturation multiplier")
    size: int = Field(33, ge=16, le=65, description="Lattice cube size (default: 33 for standard NLEs)")


@router.get("/filter/{filter_name}", summary="Export 3D .cube LUT for any retro filter")
def export_filter_lut(
    filter_name: str,
    size: int = Query(33, ge=16, le=65, description="3D LUT cube dimension (default: 33)"),
    intensity: float = Query(1.0, ge=0.0, le=1.0, description="Filter strength"),
):
    """
    Generate and download an industry-standard 3D .cube LUT for any of the 110 retro filters.
    Compatible with DaVinci Resolve, Adobe Premiere Pro, Final Cut Pro, and Photoshop.
    """
    if filter_name not in FILTER_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Filter '{filter_name}' not found in registry")

    cube_content = LUTGenerator.generate_cube_from_filter(
        filter_name=filter_name,
        size=size,
        intensity=intensity,
    )

    filename = f"retrowave_{filter_name}.cube"
    return Response(
        content=cube_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/plain; charset=utf-8",
        }
    )


@router.post("/custom", summary="Generate custom 3D .cube LUT from color grading recipe")
def export_custom_lut(request: CustomLUTRequest):
    """
    Generate a 3D .cube LUT from custom color temperature, tint, contrast S-curves, and saturation.
    """
    cube_content = LUTGenerator.generate_custom_recipe_cube(
        temperature=request.temperature,
        tint=request.tint,
        contrast=request.contrast,
        saturation=request.saturation,
        size=request.size,
        title=request.title,
    )

    filename = f"{request.title.lower().replace(' ', '_')}.cube"
    return Response(
        content=cube_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/plain; charset=utf-8",
        }
    )
