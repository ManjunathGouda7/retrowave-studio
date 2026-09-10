# 📼 Retrowave Studio — Retro Image & Video Generator

Transform your photos and video clips into stunning **retro masterpieces** with **110 authentic filters across 8 categories**, realistic analog film science, iconic overlays, an **Enterprise FastAPI Microservice**, and a full **Dynamic Video Processing Studio**!

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

## 🚀 Interfaces & Architecture

Retrowave Studio offers four distinct interfaces tailored for developers, creators, and enterprise systems:

1. 🌟 **Modern Web Studio (React + Vite)**: Ultra-premium dark cyber synthwave dashboard with an interactive **draggable split-screen slider**, 110-filter explorer, live **WebSocket render HUD**, and real-time job queue monitor.
2. ⚡ **Enterprise REST API (FastAPI)**: High-throughput microservice with interactive Swagger documentation (`/docs`) and real-time WebSocket streaming (`/ws/jobs/{id}`).
3. 🖥️ **Interactive Web UI (Streamlit)**: Streamlit workstation with refreshed dark glassmorphism styling and quick batch downloads.
4. 💻 **Command Line (CLI)**: Scriptable tool for batch photo conversion and automated video rendering.

---

## 🛠️ Installation & Quickstart

```bash
# Clone the repository
git clone https://github.com/ManjunathGouda7/retrowave-studio.git
cd retrowave-studio

# Install Python backend dependencies
pip install -r requirements.txt

# Install frontend dependencies (for dev mode)
cd web && npm install && cd ..
```

---

## 🌟 Modern Web Studio (React + Vite) & FastAPI Microservice

Launch the unified FastAPI server (serves both the Web Studio and REST microservice):

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

* 👉 **Modern Web Studio**: Open **`http://localhost:8000`** in your browser!
* 👉 **Interactive Swagger Docs**: Open **`http://localhost:8000/docs`**
* 👉 **ReDoc Documentation**: Open **`http://localhost:8000/redoc`**

> **Frontend Development Mode**: To run the Vite dev server with instant hot module reloading:
> ```bash
> cd web
> npm run dev
> # Studio opens at http://localhost:3000 (auto-proxies API and WebSockets to :8000)
> ```

### Synchronous REST Endpoints:
- `GET /health` — Service health check and loaded categories.
- `GET /api/v1/filters` — List all 110 filters (supports `?category=cyberpunk` filter).
- `GET /api/v1/categories` — List all 8 categories with filter counts.
- `POST /api/v1/process/image` — Transform image with retro filters, date stamps, Polaroid/35mm frames.
- `POST /api/v1/process/image/gif` — Generate multi-frame looping animated GIF.
- `POST /api/v1/process/video` — Synchronous video processing with time-based effects.

### ⚡ Phase 2: Distributed Job Queue & WebSockets:
- `POST /api/v1/jobs/video` — Submit asynchronous video render job (`202 Accepted`).
- `POST /api/v1/jobs/image` — Submit asynchronous image transformation job (`202 Accepted`).
- `GET /api/v1/jobs/{id}` — Poll job status, progress percentage (0-100%), and current step.
- `GET /api/v1/jobs` — List recent queued, processing, and completed jobs.
- `DELETE /api/v1/jobs/{id}` — Cancel a queued or active rendering task.
- `GET /api/v1/jobs/{id}/download` — Download rendered MP4/GIF/JPEG artifact.
- `WS /ws/jobs/{id}` — **Real-time WebSocket event stream** broadcasting live render progress directly to frontend clients.

```javascript
// Example: Connect to real-time WebSocket progress stream
const ws = new WebSocket("ws://localhost:8000/ws/jobs/" + jobId);
ws.onmessage = (event) => {
  const job = JSON.parse(event.data);
  console.log(`Progress: ${job.progress}% - ${job.current_step}`);
};
```

---

## 🖥️ Interactive Web UI (Streamlit)

```bash
streamlit run app.py
```
*Includes two dedicated creative studios:*
- **📷 Retro Image Studio**: Before/after split comparison, finishing touches (7-segment date stamps, Polaroid/35mm borders, light leaks, halation), batch category ZIP downloads, and looping animated GIFs.
- **🎬 Dynamic Video Studio**: Multi-format video uploads, 3-second quick previews, time-based effects switches, live progress tracking, and dual MP4/GIF downloads.

---

## 💻 Command Line Interface (CLI)

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

## 🐳 Docker Deployment
 
Run the entire enterprise suite (API, Web UI, and Redis) containerized:
 
```bash
# Build and run API, Web UI, and Redis services
docker-compose up --build
 
# API & Swagger UI: http://localhost:8000/docs
# Streamlit Web UI: http://localhost:8501
# Redis Message Broker: localhost:6379
```

---

## 🧪 Testing

Run the automated test suite with pytest:

```bash
python -m pytest tests/ -v
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