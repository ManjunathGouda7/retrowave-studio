# 📼 Retrowave Studio — Retro Image & Video Generator

Transform your photos and video clips into stunning **retro masterpieces** with **110 authentic filters across 8 categories**, realistic analog film science, iconic overlays, and a full **Dynamic Video Processing Studio**!

---

## ✨ 110 Filters Across 8 Categories

- 🌆 **10 × Cyberpunk** — Cyber Neon, Blade Runner, Chrome Dystopia, Hologram, Chromatic Glow, Neural Net, Acid Rain, Neural Link, Data Stream, Cyber Samurai
- 👻 **10 × Horror** — Grindhouse, Found Footage, Night Vision, Blood Moon, Séance, Creepy Doll, Static Scream, Ash Gray, Demon Eye, Silent Hill
- 🌸 **10 × Dreamy** — Soft Focus, Ethereal, Pastel Dream, Fairy Tale, Bubblegum, Lullaby, Aura, Starlight, Sunset Cloud, Melancholy
- 🕹️ **20 × 80s** — Neon Glow, Vaporwave, Synthwave, Miami Vice, VHS, Mall Glamour Portrait, Arcade, Retro TV, Roller Disco
- 📼 **20 × 90s** — Polaroid, Grunge, Y2K, Disposable Camera, Tamagotchi, Blockbuster, CD Case, Slap Bracelet, Soap Opera
- 🎞️ **20 × Retro** — Kodachrome 64, Technicolor 3-Strip, Cyanotype, Daguerreotype, Duotone, Film Noir, Golden Hour
- 📺 **10 × Glitch** — RGB split, Datamosh, CRT aperture grille, Tracking error, Pixel sort, Heavy scanlines
- 🎨 **10 × Artistic** — Oil paint, Pencil sketch, Comic book, Mosaic tiles, Stained glass, Pixel art

---

## 🎬 Video Processing Studio

Process video clips (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.gif`) up to 3 minutes with automatic 720p scaling, selectable FPS (8, 12, 15, 24), and **8 dynamic time-based effects**:

| Effect | Description |
| :--- | :--- |
| **💓 Pulse** | Brightness oscillates rhythmically over time |
| **⚡ Strobe** | High-energy periodic strobe flashing |
| **🌈 Chromatic Cycle** | Continuous rainbow hue rotation in HSV color space |
| **📼 VHS Wobble** | Rolling horizontal tracking glitch and scanline jitter |
| **🔴 Blinking Timestamp** | Vintage camcorder `REC ●` blinking dot with live running timecode |
| **💥 Zoom Punch** | Periodic rhythmic beat zoom-in punch and snap back |
| **⚡ Glitch Interval** | Periodic bursts of RGB channel separation every $N$ frames |
| **🔥 Film Burn** | Occasional warm light leak flares and fades |

---

## 🚀 Installation

```bash
git clone https://github.com/ManjunathGouda7/retrowave-studio.git
cd retrowave-studio
pip install -r requirements.txt
```

---

## 🖥️ Usage

### Interactive Web UI (Streamlit)
```bash
streamlit run app.py
```
*Includes two dedicated studios:*
- **📷 Retro Image Studio**: Before/after split comparison, finishing touches (7-segment date stamps, Polaroid/35mm borders, light leaks, halation), batch category ZIP downloads, and looping animated GIFs.
- **🎬 Dynamic Video Studio**: Multi-format video uploads, 3-second quick previews, time-based effects switches, live progress tracking, and dual MP4/GIF downloads.

---

### Command Line Interface (CLI)

#### 📷 Image Processing
```bash
# List all 110 filters
python main.py --list

# Apply single filter
python main.py photo.jpg --filter cyber_neon

# Add date stamp and Polaroid frame
python main.py photo.jpg -f 90s_polaroid --date-stamp "'94 12 25" --polaroid

# Add Kodachrome with 35mm filmstrip negative border
python main.py photo.jpg -f retro_kodachrome --date-stamp "'89 10 24" --film-border

# Apply all filters in a category
python main.py photo.jpg --all-cyberpunk
python main.py photo.jpg --all-horror
python main.py photo.jpg --all-dreamy
```

#### 🎬 Video Processing
```bash
# Process video with Cyberpunk Blade Runner look at 15 FPS
python main.py video.mp4 --filter cyber_blade_runner --fps 15

# Quick 3-second preview with VHS Wobble and Blinking Timestamp
python main.py video.mp4 --filter horror_found_footage --preview --time-effects vhs_wobble,timestamp

# Export both MP4 and animated GIF with rhythmic pulse and zoom punch
python main.py video.mp4 --filter dreamy_bubblegum --fps 12 --time-effects pulse,zoom_punch --video-format both
```

---

## 📂 Adding Your Own Filter

```python
# filters/my_custom.py
from .base import BaseFilter, register_filter
from utils.effects import add_halation, add_grain

@register_filter
class MyFilter(BaseFilter):
    name = "my_custom_filter"
    category = "cyberpunk"
    description = "Custom dystopian filter"

    def apply(self, img):
        out = add_halation(img, threshold=180, strength=0.45)
        out = add_grain(out, amount=0.08)
        return self._blend(img, out)
```