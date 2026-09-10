"""Glitch/VHS/CRT filters."""
import numpy as np
from PIL import Image, ImageEnhance
from .base import BaseFilter, register_filter
from utils.effects import chromatic_aberration, scanlines, add_grain, add_vignette


@register_filter
class RGBSplit(BaseFilter):
    name = "glitch_rgb_split"
    category = "glitch"
    description = "RGB channel split"

    def apply(self, img):
        return self._blend(img, chromatic_aberration(img, shift=10))


@register_filter
class Datamosh(BaseFilter):
    name = "glitch_datamosh"
    category = "glitch"
    description = "Datamosh effect"

    def apply(self, img):
        arr = np.array(img).copy()
        h, w = arr.shape[:2]
        for _ in range(20):
            y = np.random.randint(0, h - 40)
            block_h = np.random.randint(5, 40)
            shift = np.random.randint(-50, 50)
            arr[y:y+block_h] = np.roll(arr[y:y+block_h], shift, axis=1)
        out = Image.fromarray(arr)
        out = add_grain(out, 0.1)
        return self._blend(img, out)


@register_filter
class VHS(BaseFilter):
    name = "glitch_vhs"
    category = "glitch"
    description = "VHS tape look"

    def apply(self, img):
        out = chromatic_aberration(img, shift=5)
        out = scanlines(out, spacing=3, darkness=0.25)
        out = add_grain(out, 0.12)
        out = add_vignette(out, 0.3)
        out = ImageEnhance.Color(out).enhance(1.3)
        return self._blend(img, out)


@register_filter
class CRT(BaseFilter):
    name = "glitch_crt"
    category = "glitch"
    description = "CRT monitor"

    def apply(self, img):
        out = scanlines(img, spacing=2, darkness=0.3)
        out = chromatic_aberration(out, shift=2)
        out = add_vignette(out, 0.4)
        out = ImageEnhance.Brightness(out).enhance(1.1)
        return self._blend(img, out)


@register_filter
class PixelSort(BaseFilter):
    name = "glitch_pixel_sort"
    category = "glitch"
    description = "Pixel sorting glitch"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        lum = arr.mean(axis=2)
        for y in range(0, h, 5):
            row = lum[y]
            threshold = np.percentile(row, 90)
            mask = row > threshold
            if mask.sum() > 2:
                idx = np.where(mask)[0]
                start, end = idx[0], idx[-1]
                segment = arr[y, start:end+1]
                order = np.argsort(segment.mean(axis=1))
                arr[y, start:end+1] = segment[order]
        return self._blend(img, Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))


@register_filter
class StaticNoise(BaseFilter):
    name = "glitch_static"
    category = "glitch"
    description = "TV static overlay"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        noise = np.random.randint(0, 255, arr.shape[:2])
        noise_rgb = np.stack([noise] * 3, axis=2).astype(np.float32)
        out = arr * 0.75 + noise_rgb * 0.25
        return self._blend(img, Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))


@register_filter
class TearGlitch(BaseFilter):
    name = "glitch_tear"
    category = "glitch"
    description = "Screen tearing"

    def apply(self, img):
        arr = np.array(img).copy()
        h, w = arr.shape[:2]
        for _ in range(10):
            y = np.random.randint(0, h)
            height = np.random.randint(2, 10)
            shift = np.random.randint(-80, 80)
            arr[y:y+height] = np.roll(arr[y:y+height], shift, axis=1)
        out = Image.fromarray(arr)
        out = chromatic_aberration(out, shift=3)
        return self._blend(img, out)


@register_filter
class ScanlineHeavy(BaseFilter):
    name = "glitch_scanline_heavy"
    category = "glitch"
    description = "Heavy scanlines"

    def apply(self, img):
        out = scanlines(img, spacing=2, darkness=0.5)
        out = ImageEnhance.Brightness(out).enhance(1.2)
        return self._blend(img, out)


@register_filter
class Corrupted(BaseFilter):
    name = "glitch_corrupted"
    category = "glitch"
    description = "Corrupted file"

    def apply(self, img):
        arr = np.array(img).copy()
        h, w = arr.shape[:2]
        for _ in range(8):
            y = np.random.randint(0, h)
            height = np.random.randint(10, 60)
            arr[y:y+height] = np.random.randint(0, 256, (min(height, h-y), w, 3), dtype=np.uint8)
        out = Image.fromarray(arr)
        return self._blend(img, out)


@register_filter
class TrackingError(BaseFilter):
    name = "glitch_tracking"
    category = "glitch"
    description = "VHS tracking error"

    def apply(self, img):
        arr = np.array(img).copy()
        h, w = arr.shape[:2]
        for _ in range(3):
            y = np.random.randint(0, h - 100)
            band = np.random.randint(30, 100)
            for i in range(0, w, 20):
                shift = np.random.randint(-15, 15)
                arr[y:y+band, i:i+20] = np.roll(arr[y:y+band, i:i+20], shift, axis=1)
        out = Image.fromarray(arr)
        out = add_grain(out, 0.15)
        return self._blend(img, out)