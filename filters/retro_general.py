"""20 General retro filters."""
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from .base import BaseFilter, register_filter
from utils.effects import add_grain, add_vignette, glow, apply_film_curve, add_halation, chromatic_aberration


@register_filter
class Sepia(BaseFilter):
    name = "retro_sepia"
    category = "retro"
    description = "Classic sepia"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        r = np.clip(gray * 1.07 + 24, 0, 255)
        g = np.clip(gray * 0.95 + 12, 0, 255)
        b = np.clip(gray * 0.74, 0, 255)
        return self._blend(img, Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8)))


@register_filter
class BlackWhite(BaseFilter):
    name = "retro_bw"
    category = "retro"
    description = "High contrast B&W"

    def apply(self, img):
        out = img.convert("L").convert("RGB")
        out = ImageEnhance.Contrast(out).enhance(1.3)
        return self._blend(img, out)


@register_filter
class Cyanotype(BaseFilter):
    name = "retro_cyanotype"
    category = "retro"
    description = "Blue cyanotype print"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        r = np.clip(gray * 0.3, 0, 255)
        g = np.clip(gray * 0.6 + 20, 0, 255)
        b = np.clip(gray * 0.9 + 40, 0, 255)
        return self._blend(img, Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8)))


@register_filter
class Daguerreotype(BaseFilter):
    name = "retro_daguerreotype"
    category = "retro"
    description = "Antique daguerreotype"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        r = np.clip(gray * 0.85 + 30, 0, 255)
        g = np.clip(gray * 0.75 + 25, 0, 255)
        b = np.clip(gray * 0.6 + 20, 0, 255)
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        out = add_vignette(out, 0.6)
        return self._blend(img, out)


@register_filter
class Kodachrome(BaseFilter):
    name = "retro_kodachrome"
    category = "retro"
    description = "Kodachrome film"

    def apply(self, img):
        # Kodachrome 64: rich punchy reds, saturated yellows, deep rich blacks, warm halation
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.12 + 4, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.02, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.90 - 4, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=8.0, highlight_compress=10.0, s_contrast=1.28)
        out = add_halation(out, threshold=190, strength=0.35, radius=10)
        out = add_grain(out, 0.05)
        return self._blend(img, out)


@register_filter
class OldPhoto(BaseFilter):
    name = "retro_old_photo"
    category = "retro"
    description = "Old yellowed photo"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr = arr * 0.85 + 25
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.15, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.75, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = add_grain(out, 0.08)
        return self._blend(img, out)


@register_filter
class CrossProcess(BaseFilter):
    name = "retro_cross_process"
    category = "retro"
    description = "Cross-processed colors"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Cool shadows, warm highlights
        lum = arr.mean(axis=2, keepdims=True) / 255
        cool = np.array([30, 60, 120])
        warm = np.array([255, 220, 130])
        toned = cool * (1 - lum) + warm * lum
        mixed = arr * 0.55 + toned * 0.45
        out = Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.3)
        return self._blend(img, out)


@register_filter
class Lomo(BaseFilter):
    name = "retro_lomo"
    category = "retro"
    description = "Lomography style"

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(1.8)
        out = ImageEnhance.Contrast(out).enhance(1.3)
        out = add_vignette(out, 0.7)
        return self._blend(img, out)


@register_filter
class Technicolor(BaseFilter):
    name = "retro_technicolor"
    category = "retro"
    description = "Golden age Technicolor"

    def apply(self, img):
        # 3-strip Technicolor: vibrant rich saturation, punchy warm primaries
        out = ImageEnhance.Color(img).enhance(1.8)
        out = ImageEnhance.Contrast(out).enhance(1.2)
        arr = np.array(out).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.12 + 6, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.04, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.94 - 4, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=6.0, highlight_compress=12.0, s_contrast=1.22)
        out = add_halation(out, threshold=185, strength=0.4, radius=12)
        return self._blend(img, out)


@register_filter
class Faded(BaseFilter):
    name = "retro_faded"
    category = "retro"
    description = "Faded vintage"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr = arr * 0.75 + 45
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(0.9)
        return self._blend(img, out)


@register_filter
class Silver(BaseFilter):
    name = "retro_silver"
    category = "retro"
    description = "Silver gelatin print"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        gray = np.clip(gray * 1.05 + 5, 0, 255)
        r = np.clip(gray * 0.98, 0, 255)
        g = gray
        b = np.clip(gray * 1.05, 0, 255)
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.15)
        return self._blend(img, out)


@register_filter
class Golden(BaseFilter):
    name = "retro_golden"
    category = "retro"
    description = "Golden hour"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.2 + 20, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05 + 10, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.8, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Brightness(out).enhance(1.05)
        return self._blend(img, out)


@register_filter
class Noir(BaseFilter):
    name = "retro_noir"
    category = "retro"
    description = "Film noir B&W"

    def apply(self, img):
        out = img.convert("L").convert("RGB")
        out = ImageEnhance.Contrast(out).enhance(1.6)
        out = add_vignette(out, 0.6)
        return self._blend(img, out)


@register_filter
class FadedColor(BaseFilter):
    name = "retro_faded_color"
    category = "retro"
    description = "Washed out color"

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(0.5)
        out = ImageEnhance.Contrast(out).enhance(0.85)
        arr = np.array(out).astype(np.float32) + 40
        return self._blend(img, Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))


@register_filter
class Emulsion(BaseFilter):
    name = "retro_emulsion"
    category = "retro"
    description = "Lifted blacks emulsion lift"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr = arr * 0.7 + 60
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Color(out).enhance(1.2)
        out = add_grain(out, 0.08)
        return self._blend(img, out)


@register_filter
class Infrared(BaseFilter):
    name = "retro_infrared"
    category = "retro"
    description = "Infrared film look"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]
        arr[:, :, 0] = np.clip(b, 0, 255)
        arr[:, :, 1] = np.clip(g, 0, 255)
        arr[:, :, 2] = np.clip(r, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Color(out).enhance(1.3)
        return self._blend(img, out)


@register_filter
class Duotone(BaseFilter):
    name = "retro_duotone"
    category = "retro"
    description = "Two-color duotone"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32) / 255
        dark = np.array([40, 20, 90])
        light = np.array([255, 180, 60])
        out = dark * (1 - gray[..., None]) + light * gray[..., None]
        return self._blend(img, Image.fromarray(out.astype(np.uint8)))


@register_filter
class OldFashioned(BaseFilter):
    name = "retro_old_fashioned"
    category = "retro"
    description = "Old-timey look"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        r = np.clip(gray * 1.1 + 20, 0, 255)
        g = np.clip(gray * 0.9 + 15, 0, 255)
        b = np.clip(gray * 0.7 + 5, 0, 255)
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        out = add_vignette(out, 0.55)
        out = add_grain(out, 0.1)
        return self._blend(img, out)


@register_filter
class BleachBypass(BaseFilter):
    name = "retro_bleach_bypass"
    category = "retro"
    description = "Bleach bypass high contrast"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        color = np.array(img).astype(np.float32)
        # Overlay gray over color
        result = np.where(gray[..., None] > 128,
                          255 - (255 - color) * (255 - (gray[..., None] * 2 - 255)) / 255,
                          color * (gray[..., None] * 2) / 255)
        out = Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.4)
        return self._blend(img, out)


@register_filter
class Nostalgia(BaseFilter):
    name = "retro_nostalgia"
    category = "retro"
    description = "Warm nostalgic glow"

    def apply(self, img):
        out = img.filter(ImageFilter.GaussianBlur(1))
        out = ImageEnhance.Color(out).enhance(1.3)
        arr = np.array(out).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1 + 15, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.9, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = glow(out, radius=8, strength=0.3)
        return self._blend(img, out)