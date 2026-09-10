"""Reusable image effects for analog, retro, and vintage aesthetics."""
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance


def add_grain(img: Image.Image, amount: float = 0.15, colored: bool = False) -> Image.Image:
    """
    Add authentic photographic film grain.
    Real film grain is exposure-dependent: most pronounced in midtones
    and virtually absent in pure whites and deep blacks.
    """
    if amount <= 0:
        return img
    
    arr = np.array(img).astype(np.float32)
    # Perceptual luminance calculation
    lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]) / 255.0
    
    # Parabolic midtone weight curve: peak at midtones (0.5), tapering at 0.0 and 1.0
    weight = np.clip(4.0 * lum * (1.0 - lum), 0.1, 1.0)[..., None]
    
    if colored:
        noise = np.random.normal(0, amount * 255.0, arr.shape).astype(np.float32)
    else:
        mono_noise = np.random.normal(0, amount * 255.0, arr.shape[:2]).astype(np.float32)[..., None]
        noise = np.repeat(mono_noise, 3, axis=2)
    
    arr = np.clip(arr + noise * weight, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def add_vignette(img: Image.Image, strength: float = 0.5, smoothness: float = 0.8) -> Image.Image:
    """Darken edges with smooth optical cosine falloff to prevent banding."""
    if strength <= 0:
        return img
    
    arr = np.array(img).astype(np.float32)
    h, w = arr.shape[:2]
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    max_dist_sq = cx**2 + cy**2
    dist_sq = ((x - cx)**2 + (y - cy)**2) / max_dist_sq
    
    falloff = np.clip(dist_sq ** smoothness, 0.0, 1.0)
    mask = 1.0 - (strength * falloff)
    mask = np.clip(mask, 0.0, 1.0)[..., None]
    
    arr = np.clip(arr * mask, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def chromatic_aberration(img: Image.Image, shift: int = 5) -> Image.Image:
    """
    True optical radial chromatic aberration.
    Scales outward from image center (corners split more than center),
    avoiding harsh horizontal roll wrap-around artifacts.
    """
    if shift <= 0:
        return img
    
    arr = np.array(img)
    h, w = arr.shape[:2]
    cx, cy = w / 2.0, h / 2.0
    
    # Scale factors relative to image size
    scale_factor = (shift / max(w, h)) * 1.5
    scale_r = 1.0 + scale_factor
    scale_b = max(0.9, 1.0 - scale_factor)
    
    mat_r = cv2.getRotationMatrix2D((cx, cy), 0, scale_r)
    mat_b = cv2.getRotationMatrix2D((cx, cy), 0, scale_b)
    
    r = cv2.warpAffine(arr[:, :, 0], mat_r, (w, h), borderMode=cv2.BORDER_REFLECT)
    g = arr[:, :, 1]
    b = cv2.warpAffine(arr[:, :, 2], mat_b, (w, h), borderMode=cv2.BORDER_REFLECT)
    
    result = np.stack([r, g, b], axis=2)
    return Image.fromarray(result)


def scanlines(img: Image.Image, spacing: int = 4, darkness: float = 0.3, aperture_grille: bool = False) -> Image.Image:
    """Add CRT scanlines with sinusoidal falloff and optional phosphor aperture grille."""
    arr = np.array(img).astype(np.float32)
    h, w = arr.shape[:2]
    
    # Smooth sinusoidal scanlines
    y = np.arange(h, dtype=np.float32)[:, None]
    sine_wave = (np.sin(2.0 * np.pi * y / max(spacing, 2)) + 1.0) * 0.5
    scan_mask = 1.0 - (darkness * (1.0 - sine_wave))
    arr = arr * scan_mask[..., None]
    
    if aperture_grille and w > 100:
        # Subtle RGB triad phosphor mask
        x = np.arange(w) % 3
        grille = np.ones((h, w, 3), dtype=np.float32)
        grille[:, x == 0, 0] *= 1.05
        grille[:, x == 0, 1] *= 0.92
        grille[:, x == 0, 2] *= 0.92
        grille[:, x == 1, 1] *= 1.05
        grille[:, x == 1, 0] *= 0.92
        grille[:, x == 1, 2] *= 0.92
        grille[:, x == 2, 2] *= 1.05
        grille[:, x == 2, 0] *= 0.92
        grille[:, x == 2, 1] *= 0.92
        arr = arr * grille
        
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def glow(img: Image.Image, radius: int = 15, strength: float = 0.5, threshold: int = 170) -> Image.Image:
    """
    Highlight bloom glow.
    Applies glow strictly to bright highlights (lum > threshold),
    preserving sharpness and deep contrast in dark and midtone areas.
    """
    if strength <= 0:
        return img
        
    arr = np.array(img).astype(np.float32)
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    
    # Extract highlights with smooth transition
    hl_mask = np.clip((lum - threshold) / max(255 - threshold, 1), 0.0, 1.0)[..., None]
    highlights = arr * hl_mask
    
    hl_img = Image.fromarray(highlights.astype(np.uint8))
    blurred = hl_img.filter(ImageFilter.GaussianBlur(radius=max(1, radius)))
    blurred_arr = np.array(blurred).astype(np.float32)
    
    # Screen blend for natural light addition
    combined = 255.0 - (255.0 - arr) * (255.0 - blurred_arr * strength) / 255.0
    return Image.fromarray(np.clip(combined, 0, 255).astype(np.uint8))


def add_halation(img: Image.Image, threshold: int = 190, strength: float = 0.6, radius: int = 12) -> Image.Image:
    """
    Analog film halation effect (CineStill / 80s movie look).
    Light scatters inside the film base and causes warm reddish-orange halos
    around bright highlights and high-contrast boundaries.
    """
    if strength <= 0:
        return img
        
    arr = np.array(img).astype(np.float32)
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    
    # Identify high luminance regions
    hl_mask = np.clip((lum - threshold) / max(255 - threshold, 1), 0.0, 1.0)
    
    # Blur highlight map
    hl_pil = Image.fromarray((hl_mask * 255).astype(np.uint8))
    blurred_hl = hl_pil.filter(ImageFilter.GaussianBlur(radius=max(2, radius)))
    hl_glow = np.array(blurred_hl).astype(np.float32) / 255.0
    
    # Warm red/orange halation tint
    tint = np.array([255.0, 60.0, 20.0], dtype=np.float32)
    halo = (hl_glow[..., None] * tint) * strength
    
    result = np.clip(arr + halo, 0, 255).astype(np.uint8)
    return Image.fromarray(result)


def apply_film_curve(img: Image.Image, shadow_lift: float = 18.0, highlight_compress: float = 12.0, s_contrast: float = 1.15) -> Image.Image:
    """
    Apply photographic film S-curve tone response.
    Smoothly lifts blacks and rolls off highlights to emulate analog dynamic range.
    """
    # 256-element LUT
    x = np.linspace(0.0, 1.0, 256)
    # S-curve using smooth sigmoid
    k = (s_contrast - 1.0) * 4.0 + 1.0
    curve = 1.0 / (1.0 + np.exp(-k * (x - 0.5) * 6.0))
    # Normalize to 0..1
    curve = (curve - curve[0]) / (curve[-1] - curve[0])
    
    # Lift shadows & compress highlights
    y = curve * (255.0 - shadow_lift - highlight_compress) + shadow_lift
    lut = np.clip(y, 0, 255).astype(np.uint8)
    
    arr = np.array(img)
    arr = cv2.LUT(arr, lut)
    return Image.fromarray(arr)


def add_light_leak(img: Image.Image, intensity: float = 0.5, position: str = "top_right") -> Image.Image:
    """Generate warm, organic camera light leak across an edge or corner."""
    if intensity <= 0:
        return img
        
    arr = np.array(img).astype(np.float32)
    h, w = arr.shape[:2]
    
    # Coordinate grids
    y, x = np.ogrid[:h, :w]
    
    if position == "top_right":
        dist = np.sqrt(((x - w) ** 2 + y ** 2)) / np.sqrt(w**2 + h**2)
    elif position == "top_left":
        dist = np.sqrt((x ** 2 + y ** 2)) / np.sqrt(w**2 + h**2)
    elif position == "left":
        dist = x / float(w)
    else:  # right
        dist = (w - x) / float(w)
        
    leak_mask = np.clip(1.0 - dist * 1.8, 0.0, 1.0) ** 1.5
    
    # Warm golden/magenta light leak gradient
    tint = np.array([255.0, 140.0, 60.0])
    leak_overlay = (leak_mask[..., None] * tint) * intensity
    
    result = np.clip(arr + leak_overlay, 0, 255).astype(np.uint8)
    return Image.fromarray(result)


def add_dust_and_scratches(img: Image.Image, num_specks: int = 35, num_scratches: int = 2) -> Image.Image:
    """Simulate dust particles, slide fibers, and hair scratches found on aged film."""
    arr = np.array(img).copy()
    h, w = arr.shape[:2]
    
    # Deterministic pseudo-randomness based on image shape for stability
    rng = np.random.RandomState(42)
    
    # Small dust specks
    for _ in range(num_specks):
        x = int(rng.randint(0, w))
        y = int(rng.randint(0, h))
        rad = int(rng.randint(1, 3))
        c_val = int(rng.choice([25, 230]))
        cv2.circle(arr, (x, y), rad, (c_val, c_val, c_val), -1)
        
    # Subtle vertical scratches
    for _ in range(num_scratches):
        x = int(rng.randint(0, w))
        y1 = int(rng.randint(0, h // 4))
        y2 = int(rng.randint(3 * h // 4, h))
        shift_x = int(rng.randint(-3, 4))
        cv2.line(arr, (x, y1), (x + shift_x, y2), (220, 220, 220), 1)
        
    return Image.fromarray(arr)