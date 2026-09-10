"""20 Classic 90s style filters."""
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from .base import BaseFilter, register_filter
from utils.effects import add_grain, add_vignette, scanlines, apply_film_curve, add_halation, chromatic_aberration


@register_filter
class Sepia90s(BaseFilter):
    name = "90s_sepia"
    category = "90s"
    description = "Classic sepia tone"
    is_90s = True

    def apply(self, img):
        # 90s chocolate/platinum warm sepia with lifted matte blacks
        gray = np.array(img.convert("L")).astype(np.float32)
        r = np.clip(gray * 1.05 + 28, 0, 255)
        g = np.clip(gray * 0.92 + 18, 0, 255)
        b = np.clip(gray * 0.82 + 8, 0, 255)
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=12.0, highlight_compress=8.0, s_contrast=1.1)
        out = add_grain(out, 0.07)
        return self._blend(img, out)


@register_filter
class Polaroid90s(BaseFilter):
    name = "90s_polaroid"
    category = "90s"
    description = "Faded Polaroid look"
    is_90s = True

    def apply(self, img):
        # Authentic Polaroid emulsion: lifted matte shadows, creamy highlights, slight green-cyan shadow shift
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.04 + 6, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.01 + 4, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.96 - 2, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=24.0, highlight_compress=16.0, s_contrast=1.12)
        out = add_halation(out, threshold=195, strength=0.3, radius=10)
        out = add_grain(out, 0.06)
        out = add_vignette(out, strength=0.25, smoothness=0.9)
        return self._blend(img, out)


@register_filter
class Grunge90s(BaseFilter):
    name = "90s_grunge"
    category = "90s"
    description = "Nirvana-style grunge"
    is_90s = True

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(0.65)
        out = apply_film_curve(out, shadow_lift=10.0, highlight_compress=18.0, s_contrast=1.35)
        out = add_grain(out, 0.14)
        out = add_vignette(out, 0.45)
        return self._blend(img, out)


@register_filter
class Y2K(BaseFilter):
    name = "90s_y2k"
    category = "90s"
    description = "Y2K chrome & cyan"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.8, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.1 + 20, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.3 + 30, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Brightness(out).enhance(1.15)
        return self._blend(img, out)


@register_filter
class Disposable90s(BaseFilter):
    name = "90s_disposable"
    category = "90s"
    description = "Disposable camera look"
    is_90s = True

    def apply(self, img):
        # 90s single-use camera: sharp center flash, warm amber cast, optical corner falloff
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.06 + 8, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.02 + 4, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.94, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = apply_film_curve(out, shadow_lift=14.0, highlight_compress=10.0, s_contrast=1.2)
        out = add_vignette(out, strength=0.38, smoothness=0.85)
        out = chromatic_aberration(out, shift=3)
        out = add_grain(out, 0.09)
        return self._blend(img, out)


@register_filter
class Blockbuster(BaseFilter):
    name = "90s_blockbuster"
    category = "90s"
    description = "Blockbuster VHS blue/yellow"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        lum = arr.mean(axis=2, keepdims=True) / 255
        blue = np.array([30, 60, 150])
        yellow = np.array([255, 220, 100])
        toned = blue * (1 - lum) + yellow * lum
        mixed = arr * 0.4 + toned * 0.6
        out = Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8))
        out = scanlines(out, spacing=3, darkness=0.15)
        return self._blend(img, out)


@register_filter
class Faded90s(BaseFilter):
    name = "90s_faded"
    category = "90s"
    description = "Faded photo from a drawer"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr = arr * 0.7 + 60
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.1, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(0.85)
        return self._blend(img, out)


@register_filter
class Filmstrip90s(BaseFilter):
    name = "90s_filmstrip"
    category = "90s"
    description = "Filmstrip borders"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32) * 0.9 + 20
        h, w = arr.shape[:2]
        # Top & bottom filmstrip holes
        hole_color = np.array([15, 15, 15])
        for i in range(0, w, 60):
            arr[:15, i:i+30] = hole_color
            arr[h-15:, i:i+30] = hole_color
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Color(out).enhance(1.2)
        return self._blend(img, out)


@register_filter
class Lomo90s(BaseFilter):
    name = "90s_lomo"
    category = "90s"
    description = "Lomography saturated"
    is_90s = True

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(1.9)
        out = ImageEnhance.Contrast(out).enhance(1.4)
        out = add_vignette(out, 0.7)
        return self._blend(img, out)


@register_filter
class CDCase90s(BaseFilter):
    name = "90s_cd_case"
    category = "90s"
    description = "CD case holographic"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        x = np.linspace(0, 6 * np.pi, w)[None, :, None]
        y = np.linspace(0, 6 * np.pi, h)[:, None, None]
        hue = (np.sin(x + y) + 1) / 2
        rainbow = np.concatenate([
            np.sin(hue * 6.28) * 100 + 155,
            np.sin(hue * 6.28 + 2) * 100 + 155,
            np.sin(hue * 6.28 + 4) * 100 + 155
        ], axis=2)
        out = arr * 0.6 + rainbow * 0.4
        out = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        return self._blend(img, out)


@register_filter
class OldNewspaper(BaseFilter):
    name = "90s_newspaper"
    category = "90s"
    description = "Newspaper print"
    is_90s = True

    def apply(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        # Halftone-ish
        dots = ((np.arange(gray.shape[1])[None, :] + np.arange(gray.shape[0])[:, None]) % 4 == 0)
        gray[dots] = np.clip(gray[dots] * 1.2, 0, 255)
        r = np.clip(gray * 1.05 + 15, 0, 255)
        g = np.clip(gray * 1.02 + 10, 0, 255)
        b = np.clip(gray * 0.85 + 5, 0, 255)
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        return self._blend(img, out)


@register_filter
class GrungeColor(BaseFilter):
    name = "90s_grunge_color"
    category = "90s"
    description = "Color grunge"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Darken random patches
        h, w = arr.shape[:2]
        np.random.seed(90)
        for _ in range(30):
            x, y = np.random.randint(0, w), np.random.randint(0, h)
            size = np.random.randint(20, 80)
            arr[y:y+size, x:x+size] *= np.random.uniform(0.5, 0.9)
        out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        out = ImageEnhance.Color(out).enhance(0.85)
        return self._blend(img, out)


@register_filter
class TeenMagazine(BaseFilter):
    name = "90s_teen_mag"
    category = "90s"
    description = "Tiger Beat magazine look"
    is_90s = True

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(1.6)
        out = ImageEnhance.Brightness(out).enhance(1.15)
        arr = np.array(out).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.15, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.1, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = add_grain(out, 0.05)
        return self._blend(img, out)


@register_filter
class OldVHS90s(BaseFilter):
    name = "90s_old_vhs"
    category = "90s"
    description = "Aged VHS tape"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        # Warp/tracking lines
        h, w = arr.shape[:2]
        for _ in range(5):
            y = np.random.randint(0, h)
            arr[y:y+3] = np.roll(arr[y:y+3], np.random.randint(-20, 20), axis=1)
        arr = arr * 0.85 + 20
        out = Image.fromarray(arr.astype(np.uint8))
        out = scanlines(out, spacing=4, darkness=0.2)
        out = add_grain(out, 0.15)
        return self._blend(img, out)


@register_filter
class CassetteTape(BaseFilter):
    name = "90s_cassette"
    category = "90s"
    description = "Cassette tape sleeve"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        arr = arr * 0.9 + 10
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.95, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.85, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Contrast(out).enhance(1.15)
        return self._blend(img, out)


@register_filter
class SoapOpera(BaseFilter):
    name = "90s_soap_opera"
    category = "90s"
    description = "Soap opera dreamy soft"
    is_90s = True

    def apply(self, img):
        out = img.filter(ImageFilter.GaussianBlur(2))
        out = ImageEnhance.Brightness(out).enhance(1.15)
        out = ImageEnhance.Color(out).enhance(1.4)
        return self._blend(img, out)


@register_filter
class Hypercolor(BaseFilter):
    name = "90s_hypercolor"
    category = "90s"
    description = "Hypercolor shirt gradient"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h = arr.shape[0]
        grad = np.linspace(0, 1, h)[:, None, None]
        tint = np.concatenate([
            (1 - grad) * 220 + grad * 50,
            grad * 200 + (1 - grad) * 50,
            255 - grad * 150
        ], axis=2)
        out = arr * 0.55 + tint * 0.45
        return self._blend(img, Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))


@register_filter
class SlapBracelet(BaseFilter):
    name = "90s_slap_bracelet"
    category = "90s"
    description = "Neon 90s colors"
    is_90s = True

    def apply(self, img):
        out = ImageEnhance.Color(img).enhance(2.0)
        arr = np.array(out).astype(np.float32)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.2, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.9, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
        out = ImageEnhance.Brightness(out).enhance(1.1)
        return self._blend(img, out)


@register_filter
class Tamagotchi(BaseFilter):
    name = "90s_tamagotchi"
    category = "90s"
    description = "LCD handheld screen"
    is_90s = True

    def apply(self, img):
        arr = np.array(img.convert("L")).astype(np.float32)
        # Posterize to 4 levels (LCD look)
        levels = np.array([60, 120, 180, 240])
        idx = np.digitize(arr, [90, 150, 210])
        lcd = levels[idx]
        r = np.zeros_like(lcd)
        g = lcd * 0.9
        b = lcd * 0.4
        out = Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
        return self._blend(img, out)


@register_filter
class Trapper90s(BaseFilter):
    name = "90s_trapper"
    category = "90s"
    description = "Trapper Keeper 90s style"
    is_90s = True

    def apply(self, img):
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        # Diagonal stripes overlay
        yy, xx = np.mgrid[0:h, 0:w]
        stripe = ((xx + yy) // 40) % 2
        overlay = np.where(stripe[..., None], np.array([255, 200, 50]), np.array([50, 100, 200]))
        arr = arr * 0.5 + overlay * 0.5
        out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        out = ImageEnhance.Color(out).enhance(1.4)
        return self._blend(img, out)