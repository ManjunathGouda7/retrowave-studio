"""
3D Color Lookup Table (.cube) Generator for Retrowave Studio.
Generates industry-standard 3D LUTs compatible with Adobe Premiere Pro,
DaVinci Resolve, Final Cut Pro, and Photoshop.
"""
import io
import numpy as np
from PIL import Image
from filters.base import FILTER_REGISTRY


class LUTGenerator:
    """Generates industry-standard .cube 3D LUTs from filters or custom color recipes."""

    @staticmethod
    def generate_cube_from_filter(filter_name: str, size: int = 33, intensity: float = 1.0) -> str:
        """
        Sample the filter's transformation across a 3D color cube of dimension size x size x size
        and output a standard .cube text string.
        """
        if filter_name not in FILTER_REGISTRY:
            raise ValueError(f"Filter '{filter_name}' not found in registry.")

        filter_cls = FILTER_REGISTRY[filter_name]
        filter_instance = filter_cls(intensity=intensity)

        # Generate 3D lattice points: size x size x size points in RGB space
        # Standard .cube order: R varies fastest, then G, then B
        grid = np.linspace(0, 255, size, dtype=np.uint8)
        
        # B x G x R array of RGB values
        b_idx, g_idx, r_idx = np.meshgrid(grid, grid, grid, indexing='ij')
        
        # Reshape into a 2D image of dimension (size*size, size, 3) to pass through PIL filter
        # Total pixels: size^3
        total_points = size * size * size
        rgb_flat = np.stack([r_idx.flatten(), g_idx.flatten(), b_idx.flatten()], axis=-1)
        
        # Arrange as an image: width = size * size, height = size
        img_arr = rgb_flat.reshape((size, size * size, 3)).astype(np.uint8)
        img = Image.fromarray(img_arr, mode="RGB")

        # Apply filter
        filtered_img = filter_instance.apply(img)
        filtered_arr = np.array(filtered_img).astype(np.float32) / 255.0
        
        # Reshape back to flat array in standard .cube order
        filtered_points = filtered_arr.reshape((total_points, 3))

        # Build .cube file lines
        lines = [
            f'TITLE "{filter_name.upper()}"',
            f"LUT_3D_SIZE {size}",
            "DOMAIN_MIN 0.0 0.0 0.0",
            "DOMAIN_MAX 1.0 1.0 1.0",
            "",
        ]

        for pt in filtered_points:
            r = max(0.0, min(1.0, float(pt[0])))
            g = max(0.0, min(1.0, float(pt[1])))
            b = max(0.0, min(1.0, float(pt[2])))
            lines.append(f"{r:.6f} {g:.6f} {b:.6f}")

        return "\n".join(lines)

    @staticmethod
    def generate_custom_recipe_cube(
        temperature: float = 0.0,
        tint: float = 0.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        size: int = 33,
        title: str = "RETROWAVE_CUSTOM"
    ) -> str:
        """
        Generate a 3D LUT from custom color grading parameters:
        - temperature: -1.0 (cool cyan) to +1.0 (warm amber)
        - tint: -1.0 (green) to +1.0 (magenta)
        - contrast: 0.5 to 2.0 (S-curve slope)
        - saturation: 0.0 (monochrome) to 2.0 (vivid)
        """
        grid = np.linspace(0.0, 1.0, size, dtype=np.float32)
        b_idx, g_idx, r_idx = np.meshgrid(grid, grid, grid, indexing='ij')

        # Flat coordinates (total_points x 3)
        r = r_idx.flatten()
        g = g_idx.flatten()
        b = b_idx.flatten()

        # 1. Temperature adjustment
        if temperature > 0:
            r = r + temperature * 0.15 * (1.0 - r)
            b = b - temperature * 0.12 * b
        elif temperature < 0:
            t = abs(temperature)
            b = b + t * 0.15 * (1.0 - b)
            r = r - t * 0.12 * r

        # 2. Tint adjustment
        if tint > 0:
            r = r + tint * 0.08 * (1.0 - r)
            b = b + tint * 0.08 * (1.0 - b)
            g = g - tint * 0.08 * g
        elif tint < 0:
            tn = abs(tint)
            g = g + tn * 0.12 * (1.0 - g)
            r = r - tn * 0.06 * r
            b = b - tn * 0.06 * b

        # 3. S-curve contrast
        # Centered sigmoid around 0.5
        r = 0.5 + (r - 0.5) * contrast
        g = 0.5 + (g - 0.5) * contrast
        b = 0.5 + (b - 0.5) * contrast

        # 4. Saturation
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        r = luminance + (r - luminance) * saturation
        g = luminance + (g - luminance) * saturation
        b = luminance + (b - luminance) * saturation

        # Clamp 0.0 to 1.0
        r = np.clip(r, 0.0, 1.0)
        g = np.clip(g, 0.0, 1.0)
        b = np.clip(b, 0.0, 1.0)

        lines = [
            f'TITLE "{title.upper()}"',
            f"LUT_3D_SIZE {size}",
            "DOMAIN_MIN 0.0 0.0 0.0",
            "DOMAIN_MAX 1.0 1.0 1.0",
            "",
        ]

        total = len(r)
        for i in range(total):
            lines.append(f"{r[i]:.6f} {g[i]:.6f} {b[i]:.6f}")

        return "\n".join(lines)
