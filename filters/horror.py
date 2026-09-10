"""
Horror, occult, and psychological thriller filters (10 filters).
Aesthetic: Grindhouse exploitation film, found footage VHS, night vision, fog, and chilling monochrome.
"""
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
from .base import BaseFilter, register_filter
from utils.effects import (
    add_grain,
    add_vignette,
    chromatic_aberration,
    scanlines,
    glow,
    add_dust_and_scratches,
    apply_film_curve,
)


@register_filter
class Grindhouse(BaseFilter):
    name = "horror_grindhouse"
    category = "horror"
    description = "Scratchy, damaged 70s exploitation film with dirt & scratches"

    def apply(self, img):
        # Yellowed, aged, sun-baked exploitation film print
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.15 + 15, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05 + 8, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.72 - 10, 0, 255)
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=20.0, highlight_compress=18.0, s_contrast=1.35)
        out = add_dust_and_scratches(out, num_specks=65, num_scratches=5)
        out = add_grain(out, amount=0.18)
        out = add_vignette(out, strength=0.55, smoothness=0.8)
        return self._blend(img, out)


@register_filter
class FoundFootage(BaseFilter):
    name = "horror_found_footage"
    category = "horror"
    description = "Shaky degraded VHS tape with green-tinted low-light noise"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Sickly green-gray shadow tint
        arr[:, :, 0] *= 0.8
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.1 + 15, 0, 255)
        arr[:, :, 2] *= 0.85
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = chromatic_aberration(out, shift=5)
        out = scanlines(out, spacing=2, darkness=0.28)
        out = add_grain(out, amount=0.16)
        out = add_vignette(out, strength=0.6, smoothness=0.75)
        return self._blend(img, out)


@register_filter
class NightVision(BaseFilter):
    name = "horror_night_vision"
    category = "horror"
    description = "Military phosphor green night-vision with center gain bloom"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        # Bright phosphor green mapping
        r = np.clip(gray * 0.15, 0, 255)
        g = np.clip(gray * 1.25 + 30, 0, 255)
        b = np.clip(gray * 0.25 + 10, 0, 255)
        
        nv = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        nv = add_grain(nv, amount=0.22)
        nv = glow(nv, radius=12, strength=0.4, threshold=150)
        nv = add_vignette(nv, strength=0.75, smoothness=0.65)
        return self._blend(img, nv)


@register_filter
class BloodMoon(BaseFilter):
    name = "horror_blood_moon"
    category = "horror"
    description = "Deep crimson wash with crushed shadow contrast"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]) / 255.0
        
        # Deep blood red wash
        r = np.clip(lum * 255.0 + 30.0, 0, 255)
        g = np.clip(lum * 35.0, 0, 255)
        b = np.clip(lum * 40.0, 0, 255)
        
        blood = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        blood = apply_film_curve(blood, shadow_lift=0.0, highlight_compress=15.0, s_contrast=1.45)
        blood = add_vignette(blood, strength=0.65)
        blood = add_grain(blood, amount=0.1)
        return self._blend(img, blood)


@register_filter
class Seance(BaseFilter):
    name = "horror_seance"
    category = "horror"
    description = "Ghostly translucent white fog and overexposed spectral highlights"

    def apply(self, img):
        # Desaturate heavily, overexpose highlights, add ghostly fog
        desat = ImageEnhance.Color(img).enhance(0.2)
        bright = ImageEnhance.Brightness(desat).enhance(1.25)
        
        # Spectral white fog glow
        fog = glow(bright, radius=25, strength=0.65, threshold=120)
        fog = apply_film_curve(fog, shadow_lift=35.0, highlight_compress=0.0, s_contrast=0.95)
        fog = add_grain(fog, amount=0.08)
        fog = add_vignette(fog, strength=0.4)
        return self._blend(img, fog)


@register_filter
class CreepyDoll(BaseFilter):
    name = "horror_creepy_doll"
    category = "horror"
    description = "Sickly desaturated skin tones, heavy vignette, gritty grain"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Pull color toward cold sickly porcelain
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.75 + 15, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.78 + 15, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.88 + 25, 0, 255)
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.3)
        out = add_vignette(out, strength=0.7, smoothness=0.7)
        out = add_grain(out, amount=0.15)
        return self._blend(img, out)


@register_filter
class StaticScream(BaseFilter):
    name = "horror_static_scream"
    category = "horror"
    description = "Heavy TV static noise with high-frequency jitter"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        
        # Heavy monochrome and color noise burst
        noise = np.random.normal(0, 45, (h, w, 3))
        noisy_arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        
        out = Image.fromarray(noisy_arr)
        out = chromatic_aberration(out, shift=7)
        out = scanlines(out, spacing=2, darkness=0.35)
        out = ImageEnhance.Contrast(out).enhance(1.35)
        return self._blend(img, out)


@register_filter
class AshGray(BaseFilter):
    name = "horror_ash_gray"
    category = "horror"
    description = "Bleak, cold washed-out horror aesthetic"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        # Pale icy blue-ash tone
        r = np.clip(gray * 0.88 + 8, 0, 255)
        g = np.clip(gray * 0.92 + 12, 0, 255)
        b = np.clip(gray * 0.98 + 22, 0, 255)
        
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=22.0, highlight_compress=25.0, s_contrast=1.1)
        out = add_grain(out, amount=0.1)
        out = add_vignette(out, strength=0.5)
        return self._blend(img, out)


@register_filter
class DemonEye(BaseFilter):
    name = "horror_demon_eye"
    category = "horror"
    description = "Dark claustrophobic vignette with sinister red contrast push"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]) / 255.0
        
        # Crush shadows into black, ignite highlights into blood red
        r = np.clip(arr[:, :, 0] * 1.35 + (lum * 60.0), 0, 255)
        g = np.clip(arr[:, :, 1] * 0.55, 0, 255)
        b = np.clip(arr[:, :, 2] * 0.55, 0, 255)
        
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.4)
        out = add_vignette(out, strength=0.82, smoothness=0.6)
        out = add_grain(out, amount=0.1)
        return self._blend(img, out)


@register_filter
class SilentHill(BaseFilter):
    name = "horror_silent_hill"
    category = "horror"
    description = "Dense oppressive fog overlay with industrial rust/decay tones"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        
        # Rust and grimy brown-yellow undertones
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05 + 15, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.95 + 10, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.7 - 5, 0, 255)
        
        rust = Image.fromarray(arr.astype(np.uint8))
        rust = ImageEnhance.Contrast(rust).enhance(0.85)
        
        # Dense fog blur layer
        fog = rust.filter(ImageFilter.GaussianBlur(radius=max(6, min(w, h) // 40)))
        blended_fog = Image.blend(rust, fog, 0.45)
        
        out = apply_film_curve(blended_fog, shadow_lift=30.0, highlight_compress=15.0, s_contrast=1.0)
        out = add_grain(out, amount=0.12)
        out = add_vignette(out, strength=0.6, smoothness=0.8)
        return self._blend(img, out)
