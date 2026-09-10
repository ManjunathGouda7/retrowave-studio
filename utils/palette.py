"""Retro color palettes and utilities."""
import numpy as np

# Classic 80s neon palette
NEON_80S = {
    "hot_pink": (255, 20, 147),
    "cyan": (0, 255, 255),
    "electric_purple": (191, 0, 255),
    "yellow": (255, 255, 0),
    "sunset_orange": (255, 100, 50),
    "magenta": (255, 0, 255),
}

# 90s palette
PALETTE_90S = {
    "teal": (0, 128, 128),
    "mauve": (153, 102, 153),
    "mustard": (218, 165, 32),
    "burgundy": (128, 0, 32),
    "forest": (34, 139, 34),
    "denim": (30, 60, 130),
}

# Vaporwave palette
VAPORWAVE = [(255, 113, 206), (1, 205, 254), (185, 103, 255),
             (5, 255, 161), (1, 205, 254), (255, 251, 150)]

# Sepia tone matrix
SEPIA_MATRIX = np.array([
    [0.393, 0.769, 0.189],
    [0.349, 0.686, 0.168],
    [0.272, 0.534, 0.131],
])


def apply_color_matrix(img_array: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Apply a 3x3 color transformation matrix."""
    result = img_array @ matrix.T
    return np.clip(result, 0, 255).astype(np.uint8)