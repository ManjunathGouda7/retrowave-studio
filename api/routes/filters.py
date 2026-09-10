"""Endpoints for querying filters and categories."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from collections import Counter

from filters.base import FILTER_REGISTRY
from api.schemas import FilterInfo, FiltersResponse, CategoriesResponse, CategoryInfo

router = APIRouter(prefix="/api/v1", tags=["Filters & Categories"])


@router.get("/filters", response_model=FiltersResponse, summary="List all filters")
def list_filters(category: Optional[str] = Query(None, description="Filter by category (e.g. cyberpunk, 80s, horror, dreamy)")):
    """Return all available retro filters, optionally filtered by category."""
    items = []
    for name, cls in sorted(FILTER_REGISTRY.items()):
        if category and cls.category.lower() != category.lower():
            continue
        items.append(FilterInfo(
            name=name,
            category=cls.category,
            description=cls.description
        ))
    return FiltersResponse(total=len(items), filters=items)


@router.get("/categories", response_model=CategoriesResponse, summary="List all categories")
def list_categories():
    """Return all categories with filter counts."""
    counts = Counter(cls.category for cls in FILTER_REGISTRY.values())
    cat_items = [
        CategoryInfo(category=cat, count=cnt)
        for cat, cnt in sorted(counts.items())
    ]
    return CategoriesResponse(
        total_categories=len(cat_items),
        total_filters=len(FILTER_REGISTRY),
        categories=cat_items
    )


@router.get("/filters/{name}", response_model=FilterInfo, summary="Get filter details")
def get_filter(name: str):
    """Get metadata for a specific filter."""
    if name not in FILTER_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Filter '{name}' not found")
    cls = FILTER_REGISTRY[name]
    return FilterInfo(
        name=name,
        category=cls.category,
        description=cls.description
    )
