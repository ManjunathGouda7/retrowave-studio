"""
Retro Image Generator - Modern Streamlit Web Application
High-fidelity analog film simulations, retro aesthetics, vintage overlays, and animated GIF generator.
"""
import io
import zipfile
from pathlib import Path
import streamlit as st
from PIL import Image

import filters
from filters.base import FILTER_REGISTRY
from utils.image_utils import (
    draw_date_stamp,
    add_polaroid_border,
    add_filmstrip_border,
    add_vhs_osd,
    create_retro_gif,
)
from utils.effects import add_light_leak, add_grain, add_halation, scanlines

st.set_page_config(
    page_title="Retro Image Generator",
    page_icon="📼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Retro CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Inter:wght@400;600;700&display=swap');
    
    .retro-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.2rem;
        background: linear-gradient(135deg, #ff007f, #00f0ff, #9d00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 30px rgba(255, 0, 127, 0.3);
    }
    .retro-sub {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stDownloadButton button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 0, 127, 0.4) !important;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="retro-title">📼 RETRO IMAGE GENERATOR</div>', unsafe_allow_html=True)
st.markdown('<div class="retro-sub">80+ Vintage Film Simulations, 80s/90s Aesthetics, Authentic Overlays & Looping GIFs</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Image & Core Settings")
    uploaded = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png", "bmp", "webp"])

    if uploaded:
        st.image(uploaded, caption="Original Preview", use_container_width=True)

    intensity = st.slider("Filter Intensity", 0.0, 1.0, 1.0, 0.05)

    st.markdown("---")
    st.markdown("### 🎨 Filter Category")
    category = st.radio("Category", ["80s", "90s", "retro", "glitch", "artistic"], horizontal=True)

    filters_in_cat = [(n, c) for n, c in sorted(FILTER_REGISTRY.items()) if c.category == category]

    st.markdown("---")
    st.markdown("### 🎬 Processing Mode")
    mode = st.radio("Mode", ["Single Filter", "All in Category", "🎞️ Looping Retro GIF"])

    if mode in ["Single Filter", "🎞️ Looping Retro GIF"]:
        filter_name = st.selectbox(
            "Select Filter",
            [n for n, _ in filters_in_cat],
            format_func=lambda n: f"{n} — {FILTER_REGISTRY[n].description}"
        )
    else:
        filter_name = None

    # Overlays & Finishing Touches
    st.markdown("---")
    with st.expander("✨ Retro Finishing Touches", expanded=False):
        st.markdown("**📅 Camera Date Stamp**")
        enable_date = st.checkbox("Add 7-Segment LED Date Stamp", value=False)
        date_text = st.text_input("Date Stamp Text", value="'89 10 24") if enable_date else None

        st.markdown("**🖼️ Vintage Border & Frame**")
        frame_choice = st.selectbox(
            "Frame Type",
            ["None", "Polaroid 600 Frame", "35mm Filmstrip Negative", "VHS OSD Overlay"]
        )

        st.markdown("**🎞️ Analog Optics & Film Grain**")
        add_leak = st.checkbox("Warm Camera Light Leak", value=False)
        leak_intensity = st.slider("Light Leak Strength", 0.1, 1.0, 0.45) if add_leak else 0.0
        
        extra_grain = st.slider("Extra Film Grain", 0.0, 0.3, 0.0, 0.02)
        enable_halation = st.checkbox("Film Halation (CineStill Red Glow)", value=False)
        enable_crt = st.checkbox("CRT Scanlines", value=False)


def apply_finishing_touches(image: Image.Image) -> Image.Image:
    """Apply selected retro overlays and optical effects."""
    res = image
    if add_leak and leak_intensity > 0:
        res = add_light_leak(res, intensity=leak_intensity)
    if enable_halation:
        res = add_halation(res, threshold=180, strength=0.4, radius=12)
    if extra_grain > 0:
        res = add_grain(res, amount=extra_grain)
    if enable_crt:
        res = scanlines(res, spacing=3, darkness=0.22, aperture_grille=True)
    if enable_date and date_text:
        res = draw_date_stamp(res, date_str=date_text)
    if frame_choice == "VHS OSD Overlay":
        res = add_vhs_osd(res)
    elif frame_choice == "Polaroid 600 Frame":
        res = add_polaroid_border(res)
    elif frame_choice == "35mm Filmstrip Negative":
        res = add_filmstrip_border(res)
    return res


def process_filter(img: Image.Image, name: str, intens: float) -> Image.Image:
    cls = FILTER_REGISTRY[name]
    filtered = cls(intensity=intens).apply(img)
    return apply_finishing_touches(filtered)


# Main Content Area
if uploaded:
    img = Image.open(uploaded).convert("RGB")

    if mode == "Single Filter" and filter_name:
        with st.spinner(f"Applying {filter_name}..."):
            result = process_filter(img, filter_name, intensity)

        tab1, tab2 = st.tabs(["🖼️ Comparison View", "🔍 Full Size"])
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Image")
                st.image(img, use_container_width=True)
            with col2:
                st.subheader(f"✨ {filter_name}")
                st.image(result, use_container_width=True)
        with tab2:
            st.image(result, use_container_width=True)

        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=95)
        st.download_button(
            "⬇️ Download Masterpiece (JPEG)",
            buf.getvalue(),
            file_name=f"retro_{filter_name}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

    elif mode == "🎞️ Looping Retro GIF" and filter_name:
        st.subheader("🎞️ Looping Retro GIF Generator")
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            anim_type = st.selectbox("Animation Style", [
                ("vhs_jitter", "VHS Tape Tracking Jitter"),
                ("neon_pulse", "Neon Breathing Pulse"),
                ("crt_roll", "CRT Vertical Blanking Roll")
            ], format_func=lambda x: x[1])[0]
            frames_count = st.slider("Animation Frames", 6, 16, 8)
            frame_speed = st.slider("Frame Delay (ms)", 60, 200, 110, 10)
            
            gen_gif = st.button("🚀 Generate Animated GIF", use_container_width=True)

        with col_g2:
            if gen_gif:
                with st.spinner("Rendering retro frames & assembling GIF..."):
                    cls = FILTER_REGISTRY[filter_name]
                    filter_obj = cls(intensity=intensity)
                    gif_bytes = create_retro_gif(img, filter_obj, anim_type=anim_type, num_frames=frames_count, duration=frame_speed)
                    st.image(gif_bytes, caption="Animated Looping Retro GIF", use_container_width=True)
                    st.download_button(
                        "⬇️ Download Animated GIF",
                        gif_bytes,
                        file_name=f"retro_{filter_name}_{anim_type}.gif",
                        mime="image/gif",
                        use_container_width=True
                    )
            else:
                st.info("Click **Generate Animated GIF** above to create a looping animation.")

    else:  # All in category
        st.subheader(f"🎨 Generating all {len(filters_in_cat)} filters in category '{category.upper()}'...")
        cols = st.columns(4)
        results = {}
        progress = st.progress(0)
        for i, (name, _) in enumerate(filters_in_cat):
            try:
                out = process_filter(img, name, intensity)
                results[name] = out
                with cols[i % 4]:
                    st.image(out, caption=name, use_container_width=True)
            except Exception as e:
                st.warning(f"{name} failed: {e}")
            progress.progress((i + 1) / len(filters_in_cat))

        # Zip download
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for name, out in results.items():
                b = io.BytesIO()
                out.save(b, format="JPEG", quality=95)
                zf.writestr(f"{name}.jpg", b.getvalue())
        st.download_button(
            f"⬇️ Download All ({len(results)} Images) as ZIP",
            zip_buf.getvalue(),
            file_name=f"{category}_retro_collection.zip",
            mime="application/zip",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("📊 Retro Filter Collection Overview")
    stat_cols = st.columns(5)
    for i, cat in enumerate(["80s", "90s", "retro", "glitch", "artistic"]):
        n = sum(1 for _, c in FILTER_REGISTRY.items() if c.category == cat)
        stat_cols[i].metric(cat.upper(), f"{n} Filters")
    st.success(f"**Total Available: {len(FILTER_REGISTRY)} Authentic Retro Filters**")

else:
    st.info("👈 Upload any photo from the sidebar to begin!")
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        st.markdown("""
        ### 🕹️ 80s Aesthetics (20)
        - **Vaporwave & Synthwave**: Magenta/cyan split-toning
        - **Neon Glow**: Highlight bloom & CineStill halation
        - **Miami Vice**: High-saturation pastel hues
        - **Mall Glamour**: Soft-focus 80s portrait diffusion
        """)
    with col_feat2:
        st.markdown("""
        ### 📼 90s & Analog (40)
        - **Polaroids & Disposables**: Authentic matte blacks & flash falloff
        - **Kodachrome & Technicolor**: 3-strip color response curves
        - **Grunge & Faded**: 90s alternative aesthetic
        - **Cyanotype & Daguerreotype**: Antique photographic processes
        """)
    with col_feat3:
        st.markdown("""
        ### 📺 Glitch & Overlays (20)
        - **Optical Chromatic Aberration**: True corner radial split
        - **7-Segment LED Date Stamps**: Glowing orange point-and-shoot camera dates
        - **Frames**: Polaroid frames & 35mm film negative borders
        - **Looping GIFs**: VHS jitter and CRT scanline animations
        """)