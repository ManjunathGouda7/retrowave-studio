"""20 Classic 80s style filters."""
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from .base import BaseFilter, register_filter
from utils.effects import add_grain, add_vignette, chromatic_aberration, scanlines, glow, add_halation, apply_film_curve
from utils.palette import NEON_80S


@register_filter
class NeonGlow80s(BaseFilter):
    name = "80s_neon_glow"
    category = "80s"
    description = "Neon glow with vibrant pinks and cyans"
    is_80s = True

    def apply(self, img):
        img_boost = ImageEnhance.Color(img).enhance(1.8)
        img_boost = ImageEnhance.Contrast(img_boost).enhance(1.25)
        arr = np.array(img_boost).astype(np.float32)
        # Push toward neon palette with smooth curve
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.25 + 25, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.15 + 30, 0, 255)
        result = Image.fromarray(arr.astype(np.uint8))
        result = add_halation(result, threshold=175, strength=0.5, radius=14)
        result = glow(result, radius=18, strength=0.35, threshold=160)
        return self._blend(img, result)


@register_filter
class Vaporwave(BaseFilter):
    name = "80s_vaporwave"
    category = "80s"
    description = "Vaporwave aesthetic - pink/cyan palette"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = arr.mean(axis=2, keepdims=True) / 255.0
        shadow = np.array([75, 30, 115])
        mid = np.array([255, 95, 175])
        high = np.array([85, 225, 255])
        result = np.where(lum < 0.5,
                          shadow + (mid - shadow) * (lum * 2.0),
                          mid + (high - mid) * ((lum - 0.5) * 2.0))
        out = Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
        out = add_halation(out, threshold=180, strength=0.4, radius=12)
        out = add_grain(out, 0.08)
        return self._blend(img, out)


@register_filter
class RetroSunset(BaseFilter):
    name = "80s_retro_sunset"
    category = "80s"
    description = "Orange/pink sunset gradient"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h = arr.shape[0]
        grad = np.linspace(0, 1, h)[:, None, None]
        # Top: purple, middle: orange, bottom: yellow
        overlay = np.zeros_like(arr)
        overlay[:h//2] = np.array([180, 30, 120]) * (1 - grad[:h//2]) + np.array([255, 100, 50]) * grad[:h//2]
        overlay[h//2:] = np.array([255, 100, 50]) * (1 - grad[h//2:]) + np.array([255, 220, 100]) * grad[h//2:]
        blended = arr * 0.6 + overlay * 0.4
        return self._blend(img, Image.fromarray(blended.astype(np.uint8)))


@register_filter
class MiamiVice(BaseFilter):
    name = "80s_miami_vice"
    category = "80s"
    description = "Miami Vice pink & teal"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.4 + 20, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.9, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.2 + 30, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.4)
        return self._blend(img, out)


@register_filter
class Synthwave(BaseFilter):
    name = "80s_synthwave"
    category = "80s"
    description = "Synthwave with magenta & cyan"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = arr.mean(axis=2, keepdims=True) / 255.0
        shadows = np.array([120, 0, 180])
        highlights = np.array([0, 255, 255])
        toned = shadows * (1.0 - lum) + highlights * lum
        mixed = arr * 0.45 + toned * 0.55
        out = Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8))
        out = add_halation(out, threshold=185, strength=0.45, radius=10)
        out = add_grain(out, 0.08)
        return self._blend(img, out)


@register_filter
class Arcade(BaseFilter):
    name = "80s_arcade"
    category = "80s"
    description = "Arcade cabinet colors"
    is_80s = True

    def apply(self, img):
        img = ImageEnhance.Color(img).enhance(2.2)
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = ImageEnhance.Brightness(img).enhance(1.1)
        return self._blend(Image.open.__self__ if False else img, img)


@register_filter
class Chrome80s(BaseFilter):
    name = "80s_chrome"
    category = "80s"
    description = "Chrome/metallic look"
    is_80s = True

    def apply(self, img):
        gray = img.convert("L")
        arr = np.array(gray).astype(np.float32)
        # Posterize into metallic bands
        bands = (arr // 32) * 32
        r = np.clip(bands + 40, 0, 255)
        g = np.clip(bands + 20, 0, 255)
        b = np.clip(bands + 60, 0, 255)
        result = np.stack([r, g, b], axis=2).astype(np.uint8)
        out = Image.fromarray(result)
        out = ImageEnhance.Contrast(out).enhance(1.3)
        return self._blend(img, out)


@register_filter
class Holographic(BaseFilter):
    name = "80s_holographic"
    category = "80s"
    description = "Holographic rainbow sheen"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        x = np.linspace(0, 2 * np.pi, w)[None, :]
        y = np.linspace(0, 2 * np.pi, h)[:, None]
        r = np.sin(x + y) * 60 + 100
        g = np.sin(x + y + 2) * 60 + 100
        b = np.sin(x + y + 4) * 60 + 100
        tint = np.stack([r, g, b], axis=2)
        out = np.clip(arr * 0.6 + tint * 0.4, 0, 255).astype(np.uint8)
        return self._blend(img, Image.fromarray(out))


@register_filter
class Grid80s(BaseFilter):
    name = "80s_grid"
    category = "80s"
    description = "Retro grid overlay"
    is_80s = True

    def apply(self, img):
        arr = np.array(img)
        h, w = arr.shape[:2]
        # Add perspective grid lines
        overlay = arr.copy()
        for i in range(0, w, 40):
            overlay[:, i:i+2] = [255, 0, 150]
        for j in range(0, h, 40):
            overlay[j:j+2, :] = [0, 255, 255]
        result = Image.blend(img, Image.fromarray(overlay), 0.35)
        return self._blend(img, result)


@register_filter
class Pixelated80s(BaseFilter):
    name = "80s_pixelated"
    category = "80s"
    description = "Chunky 8-bit pixels"
    is_80s = True

    def apply(self, img):
        w, h = img.size
        small = img.resize((w // 8, h // 8), Image.NEAREST)
        pixelated = small.resize((w, h), Image.NEAREST)
        pixelated = ImageEnhance.Color(pixelated).enhance(1.5)
        return self._blend(img, pixelated)


@register_filter
class Poster80s(BaseFilter):
    name = "80s_poster"
    category = "80s"
    description = "80s poster art"
    is_80s = True

    def apply(self, img):
        from PIL import ImageOps
        out = ImageOps.posterize(img, 3)
        out = ImageEnhance.Color(out).enhance(1.8)
        out = ImageEnhance.Contrast(out).enhance(1.3)
        return self._blend(img, out)


@register_filter
class VHS80s(BaseFilter):
    name = "80s_vhs"
    category = "80s"
    description = "VHS tape distortion"
    is_80s = True

    def apply(self, img):
        out = chromatic_aberration(img, shift=5)
        out = scanlines(out, spacing=3, darkness=0.22, aperture_grille=True)
        out = add_grain(out, 0.09)
        out = add_vignette(out, 0.35)
        out = ImageEnhance.Color(out).enhance(1.25)
        return self._blend(img, out)


@register_filter
class TrapperKeeper(BaseFilter):
    name = "80s_trapper_keeper"
    category = "80s"
    description = "Trapper Keeper binder style"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Triangle pattern overlay
        h, w = arr.shape[:2]
        for i in range(0, w, 100):
            arr[:, i:i+2] = [255, 100, 200]
        # Bright saturated colors
        arr = np.clip(arr * 1.4, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        return self._blend(img, out)


@register_filter
class NeonOutline(BaseFilter):
    name = "80s_neon_outline"
    category = "80s"
    description = "Neon edge detection"
    is_80s = True

    def apply(self, img):
        edges = img.convert("L").filter(ImageFilter.FIND_EDGES)
        edge_arr = np.array(edges).astype(np.float32) / 255
        base = np.array(img).astype(np.float32) * 0.3
        neon = np.stack([
            edge_arr * 255,
            edge_arr * 50,
            edge_arr * 255
        ], axis=2)
        out = np.clip(base + neon, 0, 255).astype(np.uint8)
        return self._blend(img, Image.fromarray(out))


@register_filter
class SunsetGradient80s(BaseFilter):
    name = "80s_sunset_gradient"
    category = "80s"
    description = "Deep sunset gradient"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h = arr.shape[0]
        grad = np.linspace(0, 1, h)[:, None, None]
        grad_rgb = np.concatenate([
            grad * 255,                            # R
            grad * 100,                            # G
            (1 - grad) * 180 + 50                  # B
        ], axis=2)
        out = arr * 0.5 + grad_rgb * 0.5
        return self._blend(img, Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))


@register_filter
class Geometric80s(BaseFilter):
    name = "80s_geometric"
    category = "80s"
    description = "Memphis style geometric"
    is_80s = True

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(1.8)
        arr = np.array(out).astype(np.float32)
        h, w = arr.shape[:2]
        # Random colored shapes
        np.random.seed(80)
        for _ in range(15):
            x, y = np.random.randint(0, w), np.random.randint(0, h)
            size = np.random.randint(30, 100)
            color = np.random.choice([0, 1, 2])
            c = [[255, 0, 150], [0, 255, 255], [255, 255, 0]][color]
            x2, y2 = min(w, x + size), min(h, y + size)
            arr[y:y+3, x:x2] = c
            arr[y:y2, x:x+3] = c
            arr[y2-3:y2, x:x2] = c
            arr[y:y2, x2-3:x2] = c
        return self._blend(img, Image.fromarray(arr.astype(np.uint8)))


@register_filter
class RetroTV(BaseFilter):
    name = "80s_retro_tv"
    category = "80s"
    description = "Old CRT TV look"
    is_80s = True

    def apply(self, img):
        out = scanlines(img, spacing=2, darkness=0.2)
        out = chromatic_aberration(out, shift=2)
        out = add_vignette(out, 0.5)
        out = ImageEnhance.Color(out).enhance(1.4)
        out = glow(out, radius=5, strength=0.3)
        return self._blend(img, out)


@register_filter
class Aerobics(BaseFilter):
    name = "80s_aerobics"
    category = "80s"
    description = "Bright workout video aesthetic"
    is_80s = True

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(2.2)
        out = ImageEnhance.Brightness(out).enhance(1.2)
        out = ImageEnhance.Contrast(out).enhance(1.1)
        return self._blend(img, out)


@register_filter
class RollerDisco(BaseFilter):
    name = "80s_roller_disco"
    category = "80s"
    description = "Roller disco sparkle"
    is_80s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Add sparkles
        h, w = arr.shape[:2]
        np.random.seed(42)
        for _ in range(200):
            x, y = np.random.randint(0, w), np.random.randint(0, h)
            size = np.random.randint(2, 6)
            brightness = np.random.randint(200, 256)
            arr[y:y+size, x:x+size] = np.minimum(arr[y:y+size, x:x+size] + brightness, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Color(out).enhance(1.5)
        return self._blend(img, out)


@register_filter
class MallPortrait80s(BaseFilter):
    name = "80s_mall_portrait"
    category = "80s"
    description = "80s glamour mall portrait with soft focus & warm glow"
    is_80s = True

    def apply(self, img):
        blurred = img.filter(ImageFilter.GaussianBlur(radius=6))
        diffused = Image.blend(img, blurred, 0.35)
        arr = np.array(diffused).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.07 + 10, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.02 + 5, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.95, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = add_halation(out, threshold=175, strength=0.35, radius=10)
        out = add_vignette(out, strength=0.3, smoothness=0.9)
        out = add_grain(out, amount=0.06)
        return self._blend(img, out)