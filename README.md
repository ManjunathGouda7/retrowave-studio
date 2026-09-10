# 📼 Retro Image Generator

Transform your photos into stunning **80s & 90s retro masterpieces** with 80 authentic filters, realistic analog film science, iconic camera date stamps, film borders, and looping animated GIFs!

---

## ✨ Features

- 🕹️ **20 × 80s filters** — Neon Glow, Vaporwave, Synthwave, Miami Vice, VHS, Mall Glamour Portrait, Arcade
- 📼 **20 × 90s filters** — Sepia, Polaroid, Grunge, Y2K, Disposable Camera, Tamagotchi, Blockbuster
- 🎞️ **20 × Retro filters** — Kodachrome 64, Technicolor 3-Strip, Cyanotype, Daguerreotype, Duotone, Noir
- 📺 **10 × Glitch filters** — RGB split, Datamosh, CRT aperture grille, Tracking error, Pixel sort
- 🎨 **10 × Artistic filters** — Oil paint, Pencil sketch, Comic book, Mosaic tiles, Stained glass

### 🔬 High-Fidelity Analog Film Engine
- **Exposure-Weighted Film Grain**: Authentic silver-halide grain concentrated in midtones, tapering off in deep shadows and highlights.
- **Film Halation**: Warm CineStill / 80s movie reddish glow around bright lights and high-contrast edges.
- **Radial Chromatic Aberration**: True optical lens distortion that splits colors radially toward corners with zero center distortion.
- **Smooth S-Curve Tone Response**: Analog film exposure curves that preserve highlight roll-off and lift shadow blacks.

### 🏷️ Iconic Retro Overlays
- 📅 **7-Segment LED Date Stamp**: Procedural glowing orange camera timestamps (e.g. `'89 10 24` or `'94 12 25`).
- 🖼️ **Polaroid 600 Frame**: Classic white instant photo border with authentic bottom chin and drop shadow.
- 🎞️ **35mm Filmstrip Border**: Real negative film rebate with sprocket holes and orange frame numbers.
- 📺 **VHS On-Screen Display (OSD)**: Glowing green `PLAY ▶`, `SP 0:24:18`, `CH 03` overlays.
- 🎞️ **Looping Animated GIFs**: Generate animated retro loops (VHS tracking jitter, pulsing neon, or CRT scan roll).

---

## 🚀 Installation

```bash
git clone <this-repo>
cd "Retro Image Generator"
pip install -r requirements.txt
```

---

## 🖥️ Usage

### Interactive Web UI (Streamlit)
```bash
streamlit run app.py
```
*Features live before/after previews, finishing touch toggles (date stamps, frames, light leaks, halation), batch ZIP downloads, and an animated retro GIF generator.*

### Command Line Interface (CLI)

```bash
# List all 80 filters categorized
python main.py --list

# Apply a single filter
python main.py photo.jpg --filter 80s_vaporwave

# Apply filter with glowing 7-segment date stamp and Polaroid frame
python main.py photo.jpg -f 90s_polaroid --date-stamp "'94 12 25" --polaroid

# Apply Kodachrome with 35mm negative filmstrip border
python main.py photo.jpg -f retro_kodachrome --date-stamp "'89 10 24" --film-border

# Generate a looping retro animated GIF
python main.py photo.jpg -f 80s_vhs --gif

# Apply all filters in a category
python main.py photo.jpg --all-80s
python main.py photo.jpg --all-90s

# Apply EVERY filter (80 images!)
python main.py photo.jpg --all
```

---

## 📂 Adding Your Own Filter

```python
# filters/my_custom.py
from .base import BaseFilter, register_filter
from utils.effects import add_halation, add_grain

@register_filter
class MyFilter(BaseFilter):
    name = "custom_my_filter"
    category = "80s"
    description = "My cool custom filter"
    is_80s = True

    def apply(self, img):
        # Your image processing logic here
        out = add_halation(img, threshold=180, strength=0.4)
        out = add_grain(out, amount=0.08)
        return self._blend(img, out)
```

Then register it in `filters/__init__.py`.