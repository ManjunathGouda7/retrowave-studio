"""
Cyberpunk retro-futuristic filters (10 filters).
Aesthetic: Neon-drenched dystopias, high-contrast holograms, neural grids, and cybernetic color palettes.
"""
import math
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps
from .base import BaseFilter, register_filter
from utils.effects import (
    add_grain,
    add_vignette,
    chromatic_aberration,
    scanlines,
    glow,
    add_halation,
    apply_film_curve,
)


@register_filter
class CyberpunkNeon(BaseFilter):
    name = "cyber_neon"
    category = "cyberpunk"
    description = "Neon-drenched dystopia, magenta + cyan split with halation"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]) / 255.0
        
        # Deep inky purple shadows, electric hot pink midtones, glowing cyan highlights
        shadows = np.array([50, 10, 80], dtype=np.float32)
        mids = np.array([255, 20, 160], dtype=np.float32)
        highs = np.array([0, 245, 255], dtype=np.float32)
        
        toned = np.where(
            lum[..., None] < 0.5,
            shadows + (mids - shadows) * (lum[..., None] * 2.0),
            mids + (highs - mids) * ((lum[..., None] - 0.5) * 2.0)
        )
        mixed = arr * 0.45 + toned * 0.55
        out = Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8))
        out = add_halation(out, threshold=175, strength=0.55, radius=12)
        out = glow(out, radius=16, strength=0.35, threshold=165)
        out = chromatic_aberration(out, shift=4)
        return self._blend(img, out)


@register_filter
class BladeRunner(BaseFilter):
    name = "cyber_blade_runner"
    category = "cyberpunk"
    description = "Orange/teal moody sci-fi with anamorphic glow"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]) / 255.0
        
        # Deep dystopian teal shadows, radioactive amber highlights
        teal = np.array([10, 75, 100], dtype=np.float32)
        amber = np.array([255, 145, 30], dtype=np.float32)
        toned = teal * (1.0 - lum[..., None]) + amber * lum[..., None]
        
        mixed = arr * 0.4 + toned * 0.6
        out = Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=8.0, highlight_compress=10.0, s_contrast=1.3)
        out = add_halation(out, threshold=170, strength=0.45, radius=14)
        out = add_vignette(out, strength=0.45, smoothness=0.85)
        out = add_grain(out, amount=0.07)
        return self._blend(img, out)


@register_filter
class ChromeDystopia(BaseFilter):
    name = "cyber_chrome_dystopia"
    category = "cyberpunk"
    description = "Metallic silver specular finish with lifted darks"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        # Solarize/metallic reflection curve (sinusoidal luminance response)
        chrome = (np.sin(gray * (math.pi / 64.0)) + 1.0) * 127.5
        arr = np.array(img).astype(np.float32)
        
        # Cool silvery tint: high green/blue, subtle violet shadows
        r = np.clip(chrome * 0.85 + arr[:, :, 0] * 0.15, 0, 255)
        g = np.clip(chrome * 0.95 + arr[:, :, 1] * 0.15 + 10, 0, 255)
        b = np.clip(chrome * 1.05 + arr[:, :, 2] * 0.15 + 25, 0, 255)
        
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.25)
        out = glow(out, radius=10, strength=0.3, threshold=180)
        return self._blend(img, out)


@register_filter
class Hologram(BaseFilter):
    name = "cyber_hologram"
    category = "cyberpunk"
    description = "Cyan-projected translucent hologram with scanlines"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        # Pure electric cyan laser palette
        r = np.clip(gray * 0.15, 0, 255)
        g = np.clip(gray * 0.85 + 40, 0, 255)
        b = np.clip(gray * 1.1 + 60, 0, 255)
        
        holo = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        holo = scanlines(holo, spacing=3, darkness=0.4)
        holo = chromatic_aberration(holo, shift=6)
        holo = glow(holo, radius=12, strength=0.45, threshold=140)
        return self._blend(img, holo)


@register_filter
class ChromaticGlow(BaseFilter):
    name = "cyber_chromatic_glow"
    category = "cyberpunk"
    description = "RGB highlight bloom from bright light sources"

    def apply(self, img):
        out = glow(img, radius=20, strength=0.5, threshold=160)
        out = add_halation(out, threshold=175, strength=0.6, radius=16)
        out = chromatic_aberration(out, shift=8)
        out = ImageEnhance.Color(out).enhance(1.4)
        return self._blend(img, out)


@register_filter
class NeuralNet(BaseFilter):
    name = "cyber_neural_net"
    category = "cyberpunk"
    description = "Edge-detection with electric neon circuitry lines"

    def apply(self, img):
        gray = np.array(img.convert("L"))
        # Sobel gradient edges
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(grad_x, grad_y)
        mag = np.clip(mag * 2.5, 0, 255).astype(np.uint8)
        
        # Colorize edges into electric blue and magenta
        edge_r = np.clip(mag * 1.1, 0, 255).astype(np.uint8)
        edge_g = np.clip(mag * 0.4, 0, 255).astype(np.uint8)
        edge_b = np.clip(mag * 1.4, 0, 255).astype(np.uint8)
        neon_edges = np.stack([edge_r, edge_g, edge_b], axis=2)
        
        # Inky dark background
        base = np.array(img).astype(np.float32) * 0.25
        combined = np.clip(base + neon_edges.astype(np.float32) * 1.2, 0, 255).astype(np.uint8)
        out = Image.fromarray(combined)
        out = glow(out, radius=10, strength=0.4, threshold=140)
        return self._blend(img, out)


@register_filter
class AcidRain(BaseFilter):
    name = "cyber_acid_rain"
    category = "cyberpunk"
    description = "Vertical smear distortion with toxic green color push"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        
        # Toxic green / amber cast
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.65, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.35 + 20, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.7, 0, 255)
        
        # Vertical rain smear streaks
        rng = np.random.RandomState(88)
        for _ in range(40):
            x = rng.randint(0, w - 4)
            streak_len = rng.randint(h // 6, h // 2)
            y = rng.randint(0, h - streak_len)
            arr[y:y+streak_len, x:x+2] = np.clip(arr[y:y+streak_len, x:x+2] * 1.4 + 40, 0, 255)
            
        out = Image.fromarray(arr.astype(np.uint8))
        out = add_vignette(out, strength=0.45)
        out = add_grain(out, amount=0.08)
        return self._blend(img, out)


@register_filter
class NeuralLink(BaseFilter):
    name = "cyber_neural_link"
    category = "cyberpunk"
    description = "Futuristic HUD grid overlay with targeting brackets"

    def apply(self, img):
        out = ImageEnhance.Contrast(img).enhance(1.2)
        out = ImageEnhance.Color(out).enhance(1.3)
        w, h = out.size
        
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        hud_color = (0, 255, 230, 160)
        
        # Subtle cyber grid
        step = max(30, int(min(w, h) * 0.12))
        for x in range(0, w, step):
            draw.line([(x, 0), (x, h)], fill=(0, 255, 230, 40), width=1)
        for y in range(0, h, step):
            draw.line([(0, y), (w, y)], fill=(0, 255, 230, 40), width=1)
            
        # Center targeting reticle brackets
        cx, cy = w // 2, h // 2
        r = max(25, int(min(w, h) * 0.15))
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=15, end=75, fill=hud_color, width=2)
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=105, end=165, fill=hud_color, width=2)
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=195, end=255, fill=hud_color, width=2)
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=285, end=345, fill=hud_color, width=2)
        
        # Corner brackets
        pad = max(15, int(min(w, h) * 0.05))
        blen = max(15, int(min(w, h) * 0.06))
        draw.line([(pad, pad), (pad + blen, pad)], fill=hud_color, width=2)
        draw.line([(pad, pad), (pad, pad + blen)], fill=hud_color, width=2)
        draw.line([(w - pad, pad), (w - pad - blen, pad)], fill=hud_color, width=2)
        draw.line([(w - pad, pad), (w - pad, pad + blen)], fill=hud_color, width=2)
        
        base = out.convert("RGBA")
        combined = Image.alpha_composite(base, overlay).convert("RGB")
        return self._blend(img, combined)


@register_filter
class DataStream(BaseFilter):
    name = "cyber_data_stream"
    category = "cyberpunk"
    description = "Flowing vertical digital rain streaks"

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        
        # Shift overall tint to dark matrix green/cyan
        arr[:, :, 0] *= 0.75
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.25 + 15, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.85 + 20, 0, 255)
        
        # Digital code rain column drops
        rng = np.random.RandomState(42)
        col_step = max(8, w // 40)
        for col in range(4, w - 4, col_step):
            drop_len = rng.randint(h // 4, 3 * h // 4)
            start_y = rng.randint(0, h - drop_len)
            gradient = np.linspace(0.2, 1.8, drop_len)[:, None, None]
            glow_color = np.array([0, 255, 180], dtype=np.float32) * gradient
            arr[start_y:start_y+drop_len, col:col+2] = np.clip(
                arr[start_y:start_y+drop_len, col:col+2] * 0.5 + glow_color, 0, 255
            )
            
        out = Image.fromarray(arr.astype(np.uint8))
        out = scanlines(out, spacing=3, darkness=0.2)
        return self._blend(img, out)


@register_filter
class CyberSamurai(BaseFilter):
    name = "cyber_samurai"
    category = "cyberpunk"
    description = "Aggressive red + black high-contrast duotone"

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32) / 255.0
        # High contrast S-curve
        high_contrast = 1.0 / (1.0 + np.exp(-12.0 * (gray - 0.45)))
        
        # Red and carbon black duotone
        r = np.clip(high_contrast * 255.0, 0, 255)
        g = np.clip(high_contrast * 20.0, 0, 255)
        b = np.clip(high_contrast * 35.0, 0, 255)
        
        samurai = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        samurai = add_halation(samurai, threshold=160, strength=0.5, radius=12)
        samurai = add_vignette(samurai, strength=0.55)
        return self._blend(img, samurai)
