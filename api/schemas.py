"""Pydantic schemas and models for the Retrowave Studio API."""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class FilterInfo(BaseModel):
    name: str = Field(..., description="Unique filter identifier")
    category: str = Field(..., description="Thematic category (e.g. cyberpunk, 80s, horror)")
    description: str = Field(..., description="Visual aesthetic description")


class CategoryInfo(BaseModel):
    category: str = Field(..., description="Category name")
    count: int = Field(..., description="Number of filters in this category")


class FiltersResponse(BaseModel):
    total: int = Field(..., description="Total number of filters returned")
    filters: List[FilterInfo] = Field(..., description="List of filter objects")


class CategoriesResponse(BaseModel):
    total_categories: int
    total_filters: int
    categories: List[CategoryInfo]


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    service: str = "retrowave-studio-api"
    total_filters: int
    categories: List[str]


class ProcessImageBase64Response(BaseModel):
    success: bool
    filter_applied: str
    intensity: float
    width: int
    height: int
    mime_type: str
    base64_data: str
