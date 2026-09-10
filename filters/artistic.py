"""Artistic filters."""
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from .base import BaseFilter, register_filter


@register_filter
class OilPaint(BaseFilter):
    name = "art_oil"
    category = "artistic"
    description = "Oil painting effect"

    def apply(self, img):
        out = img.filter(ImageFilter.ModeFilter(size=7))
        out = ImageEnhance.Color(out).enhance(1.5)
        return self._blend(img, out)


@register_filter
class Watercolor(BaseFilter):
    name = "art_watercolor"
    category = "artistic"
    description = "Watercolor painting"

    def apply(self, img):
        out = img.filter(ImageFilter.MedianFilter(size=5))
        out = ImageEnhance.Color(out).enhance(1.4)
        out = ImageEnhance.Brightness(out).enhance(1.15)
        out = out.filter(ImageFilter.GaussianBlur(0.5))
        return self._blend(img, out)


@register_filter
class Sketch(BaseFilter):
    name = "art_sketch"
    category = "artistic"
    description = "Pencil sketch"

    def apply(self, img):
        gray = img.convert("L")
        inverted = ImageOps.invert(gray)
        blurred = inverted.filter(ImageFilter.GaussianBlur(10))
        sketch = np.array(gray).astype(np.float32)
        blur = np.array(blurred).astype(np.float32)
        result = np.clip(sketch * 255 / (255 - blur + 1), 0, 255).astype(np.uint8)
        out = Image.fromarray(result).convert("RGB")
        return self._blend(img, out)


@register_filter
class Comic(BaseFilter):
    name = "art_comic"
    category = "artistic"
    description = "Comic book style"

    def apply(self, img):
        out = ImageOps.posterize(img, 3)
        out = ImageEnhance.Color(out).enhance(2.0)
        out = ImageEnhance.Contrast(out).enhance(1.4)
        return self._blend(img, out)


@register_filter
class NeonOutlineArt(BaseFilter):
    name = "art_neon_outline"
    category = "artistic"
    description = "Neon outlines"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        edges = np.abs(np.gradient(gray)[0]) + np.abs(np.gradient(gray)[1])
        edges = np.clip(edges * 3, 0, 255).astype(np.uint8)
        base = np.array(img).astype(np.float32) * 0.2
        neon = np.stack([edges, edges // 4, edges], axis=2)
        out = np.clip(base + neon, 0, 255).astype(np.uint8)
        return self._blend(img, Image.fromarray(out))


@register_filter
class Mosaic(BaseFilter):
    name = "art_mosaic"
    category = "artistic"
    description = "Mosaic tiles"

    def apply(self, img):
        w, h = img.size
        small = img.resize((w // 15, h // 15), Image.LANCZOS)
        mosaic = small.resize((w, h), Image.NEAREST)
        # Add grid lines
        arr = np.array(mosaic)
        arr[::15, :] = [40, 40, 40]
        arr[:, ::15] = [40, 40, 40]
        return self._blend(img, Image.fromarray(arr))


@register_filter
class StainedGlass(BaseFilter):
    name = "art_stained_glass"
    category = "artistic"
    description = "Stained glass"

    def apply(self, img):
        out = img.filter(ImageFilter.ModeFilter(size=9))
        out = ImageEnhance.Color(out).enhance(2.2)
        arr = np.array(out)
        gray = np.array(out.convert("L"))
        edges = np.abs(np.gradient(gray.astype(float))[0]) + np.abs(np.gradient(gray.astype(float))[1])
        edges = np.clip(edges * 4, 0, 255).astype(np.uint8)
        arr[edges > 40] = [10, 10, 10]
        return self._blend(img, Image.fromarray(arr))


@register_filter
class PixelArt(BaseFilter):
    name = "art_pixel"
    category = "artistic"
    description = "8-bit pixel art"

    def apply(self, img):
        w, h = img.size
        small = img.resize((w // 12, h // 12), Image.LANCZOS)
        small = ImageOps.posterize(small, 3)
        pixel = small.resize((w, h), Image.NEAREST)
        return self._blend(img, pixel)


@register_filter
class AbstractWaves(BaseFilter):
    name = "art_abstract_waves"
    category = "artistic"
    description = "Abstract waves overlay"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        wave = (np.sin(xx / 30) + np.sin(yy / 30)) * 30
        arr = np.clip(arr + wave[..., None], 0, 255)
        return self._blend(img, Image.fromarray(arr.astype(np.uint8)))


@register_filter
class Trippy(BaseFilter):
    name = "art_trippy"
    category = "artistic"
    description = "Psychedelic trippy"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        r = np.sin(xx / 10 + yy / 10) * 60
        g = np.sin(xx / 12 + 2) * 60
        b = np.sin(yy / 14 + 4) * 60
        tint = np.stack([r, g, b], axis=2)
        out = np.clip(arr + tint, 0, 255).astype(np.uint8)
        out = ImageEnhance.Color(Image.fromarray(out)).enhance(1.5)
        return self._blend(img, out)