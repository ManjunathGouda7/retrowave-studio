"""
Dreamy, ethereal, and pastel aesthetic filters (10 filters).
Aesthetic: Soft focus glamour, fairy tale warmth, bubblegum pastels, aura bleed, and starry sparkles.
"""
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
from .base import BaseFilter, register_filter
from utils.effects import (
    add_grain,
    add_vignette,
    glow,
    add_halation,
    add_light_leak,
    apply_film_curve,
)


@register_filter
class SoftFocus(BaseFilter):
    name = "dreamy_soft_focus"
    category = "dreamy"
    description = "Gentle blur + pastel lightness"

    def apply(self, img):
        blurred = img.filter(ImageFilter.GaussianBlur(radius=6))
        # Glamour Orton blend
        orton = Image.blend(img, blurred, 0.45)
        bright = ImageEnhance.Brightness(orton).enhance(1.1)
        pastel = ImageEnhance.Color(bright).enhance(0.9)
        out = apply_film_curve(pastel, shadow_lift=18.0, highlight_compress=6.0, s_contrast=1.05)
        return self._blend(img, out)


@register_filter
class Ethereal(BaseFilter):
    name = "dreamy_ethereal"
    category = "dreamy"
    description = "Glow + airy light leaks"

    def apply(self, img):
        out = glow(img, radius=22, strength=0.5, threshold=150)
        out = add_halation(out, threshold=170, strength=0.4, radius=16)
        out = add_light_leak(out, intensity=0.4, position="top_right")
        out = ImageEnhance.Brightness(out).enhance(1.12)
        out = add_vignette(out, strength=0.25, smoothness=0.9)
        return self._blend(img, out)


@register_filter
class PastelDream(BaseFilter):
    name = "dreamy_pastel_dream"
    category = "dreamy"
    description = "Muted pastel palette"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Compress dynamic range and push into whimsical pastels
        arr = arr * 0.75 + 60.0
        # Peach / lavender tint
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.06 + 6, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.98, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.08 + 10, 0, 255)
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(0.92)
        out = add_grain(out, amount=0.04)
        return self._blend(img, out)


@register_filter
class FairyTale(BaseFilter):
    name = "dreamy_fairy_tale"
    category = "dreamy"
    description = "Warm glow + soft vignette"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Golden magical tint: amber highlights, lush warm greens
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1 + 12, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05 + 8, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.9 - 5, 0, 255)
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = glow(out, radius=18, strength=0.45, threshold=160)
        out = add_vignette(out, strength=0.38, smoothness=0.9)
        return self._blend(img, out)


@register_filter
class Bubblegum(BaseFilter):
    name = "dreamy_bubblegum"
    category = "dreamy"
    description = "Pink + soft pink bloom"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Bubblegum pink push
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.25 + 28, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.92 + 5, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.15 + 20, 0, 255)
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Color(out).enhance(1.4)
        out = glow(out, radius=16, strength=0.4, threshold=165)
        out = apply_film_curve(out, shadow_lift=15.0, highlight_compress=8.0, s_contrast=1.15)
        return self._blend(img, out)


@register_filter
class Lullaby(BaseFilter):
    name = "dreamy_lullaby"
    category = "dreamy"
    description = "Sleepy, soft-focus, low contrast"

    def apply(self, img):
        blurred = img.filter(ImageFilter.GaussianBlur(radius=8))
        soft = Image.blend(img, blurred, 0.5)
        
        # Pale lavender low-contrast tone
        arr = np.array(soft).astype(np.float32)
        arr = arr * 0.78 + 45.0
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.08 + 12, 0, 255)
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(0.85)
        out = add_vignette(out, strength=0.3)
        return self._blend(img, out)


@register_filter
class Aura(BaseFilter):
    name = "dreamy_aura"
    category = "dreamy"
    description = "Colorful aura bleed around subjects"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        
        # Extract highlights and saturated edges for aura
        blurred = cv2.GaussianBlur(arr, (0, 0), sigmaX=max(8, min(w, h) // 30))
        # Iridescent rainbow tint map
        y, x = np.ogrid[:h, :w]
        phase = (x / float(w) + y / float(h)) * 2.0 * np.pi
        rainbow = np.stack([
            np.sin(phase) * 0.5 + 0.5,
            np.sin(phase + 2.094) * 0.5 + 0.5,
            np.sin(phase + 4.188) * 0.5 + 0.5
        ], axis=2) * 120.0
        
        aura_layer = np.clip(blurred * 0.4 + rainbow * 0.6, 0, 255).astype(np.uint8)
        aura_img = Image.fromarray(aura_layer)
        out = Image.blend(img, aura_img, 0.35)
        out = ImageEnhance.Color(out).enhance(1.25)
        return self._blend(img, out)


@register_filter
class Starlight(BaseFilter):
    name = "dreamy_starlight"
    category = "dreamy"
    description = "Sparkle overlay on specular highlights"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        h, w = arr.shape[:2]
        
        # Identify brightest specular pixels
        threshold = 215
        stars_mask = (lum > threshold).astype(np.uint8)
        
        # Soft diffuse glow
        out = glow(img, radius=14, strength=0.4, threshold=175)
        draw = ImageDraw.Draw(out)
        
        # Find local peaks for 4-point star glints
        rng = np.random.RandomState(42)
        y_pts, x_pts = np.where(stars_mask > 0)
        
        if len(x_pts) > 0:
            # Sample up to 25 star glints
            sample_count = min(25, len(x_pts))
            indices = rng.choice(len(x_pts), sample_count, replace=False)
            
            glint_len = max(6, int(min(w, h) * 0.025))
            for idx in indices:
                sx, sy = x_pts[idx], y_pts[idx]
                star_color = (255, 255, 240, 220)
                # 4-point star cross lines
                draw.line([(sx - glint_len, sy), (sx + glint_len, sy)], fill=star_color, width=1)
                draw.line([(sx, sy - glint_len), (sx, sy + glint_len)], fill=star_color, width=1)
                draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255, 255))
                
        return self._blend(img, out)


@register_filter
class SunsetCloud(BaseFilter):
    name = "dreamy_sunset_cloud"
    category = "dreamy"
    description = "Orange + pink haze gradient"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        
        # Smooth vertical sunset gradient: purple -> pink -> golden orange
        grad_y = np.linspace(0.0, 1.0, h)[:, None, None]
        top_color = np.array([160, 60, 150]) # twilight magenta
        bot_color = np.array([255, 140, 50]) # golden sunset orange
        gradient = top_color * (1.0 - grad_y) + bot_color * grad_y
        
        mixed = arr * 0.6 + gradient * 0.4
        out = Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8))
        out = glow(out, radius=18, strength=0.35, threshold=160)
        out = apply_film_curve(out, shadow_lift=12.0, highlight_compress=10.0, s_contrast=1.12)
        return self._blend(img, out)


@register_filter
class Melancholy(BaseFilter):
    name = "dreamy_melancholy"
    category = "dreamy"
    description = "Cool blue dreamy tone with gentle nostalgic fade"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Deep nostalgic twilight blue
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.82 + 5, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.92 + 10, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.18 + 25, 0, 255)
        
        out = Image.fromarray(arr.astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=24.0, highlight_compress=15.0, s_contrast=1.08)
        out = add_vignette(out, strength=0.4)
        out = add_grain(out, amount=0.07)
        return self._blend(img, out)
