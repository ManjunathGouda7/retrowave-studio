"""Base filter class - all filters inherit from this."""
from abc import ABC, abstractmethod
from PIL import Image
import numpy as np


class BaseFilter(ABC):
    name = "base"
    category = "general"
    description = "Base filter"
    is_80s = False
    is_90s = False

    def __init__(self, intensity: float = 1.0):
        self.intensity = max(0.0, min(1.0, intensity))

    @abstractmethod
    def apply(self, img: Image.Image) -> Image.Image:
        """Apply filter to a PIL Image and return new PIL Image."""
        pass

    def _blend(self, original: Image.Image, filtered: Image.Image) -> Image.Image:
        """Blend based on intensity."""
        return Image.blend(original, filtered, self.intensity)

    def __call__(self, img: Image.Image) -> Image.Image:
        return self.apply(img)


FILTER_REGISTRY = {}


def register_filter(cls):
    """Decorator to register filters."""
    FILTER_REGISTRY[cls.name] = cls
    return cls


def get_filters_by_category(category=None):
    if category:
        return {k: v for k, v in FILTER_REGISTRY.items() if v.category == category}
    return FILTER_REGISTRY