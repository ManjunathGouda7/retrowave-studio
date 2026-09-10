"""
Retro Image & Video Studio - Modern Streamlit Web Application
110 Authentic Retro Filters across 8 Categories + Full Dynamic Video Studio Pipeline.
"""
import io
import os
import tempfile
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
from utils.video_processor import VideoProcessor

st.set_page_config(
    page_title="Retrowave Studio - Retro Image & Video Engine",
    page_icon="📼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Retro Synthwave CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Syne:wght@700;800&family=Inter:wght@400;600;700&family=VT323&display=swap');
    
    /* Global App Background */
    .stApp {
        background-color: #07090e;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(255, 0, 127, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 85% 20%, rgba(0, 240, 255, 0.07) 0%, transparent 40%),
            linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 48px 48px, 48px 48px;
        color: #f3f4f6;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(14, 18, 29, 0.9) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
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
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }
    
    /* Neon Styled Buttons */
    .stButton button, .stDownloadButton button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.65rem 1.4rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(255, 0, 127, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(255, 0, 127, 0.55) !important;
    }

    /* Modern Radio Group */
    div[data-testid="stRadio"] > div {
        background: rgba(14, 18, 29, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 6px;
        border-radius: 12px;
    }

    /* Glass Cards */
    div[data-testid="stExpander"] {
        background: rgba(17, 22, 37, 0.72) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="retro-title">📼 RETROWAVE STUDIO</div>', unsafe_allow_html=True)
st.markdown('<div class="retro-sub">110 Retro Filters • Cyberpunk, Horror, Dreamy & 80s/90s • Full Video Processing Engine</div>', unsafe_allow_html=True)

# Top navigation: Image Studio vs Video Studio
studio_mode = st.radio(
    "Select Studio",
    ["📷 Retro Image Studio", "🎬 Dynamic Video Studio"],
    horizontal=True,
    label_visibility="collapsed"
)

CATEGORIES = ["80s", "90s", "retro", "glitch", "artistic", "cyberpunk", "horror", "dreamy"]

# -------------------------------------------------------------
# 📷 RETRO IMAGE STUDIO
# -------------------------------------------------------------
if studio_mode == "📷 Retro Image Studio":
    with st.sidebar:
        st.markdown("### ⚙️ Image Settings")
        uploaded = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png", "bmp", "webp"])

        if uploaded:
            st.image(uploaded, caption="Original Preview", use_container_width=True)

        intensity = st.slider("Filter Intensity", 0.0, 1.0, 1.0, 0.05)

        st.markdown("---")
        st.markdown("### 🎨 Filter Category")
        category = st.selectbox("Category", CATEGORIES, format_func=lambda c: f"{c.upper()} ({sum(1 for _, cl in FILTER_REGISTRY.items() if cl.category == c)} filters)")

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

        # Finishing Touches Panel
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

    def process_image_filter(img: Image.Image, name: str, intens: float) -> Image.Image:
        cls = FILTER_REGISTRY[name]
        filtered = cls(intensity=intens).apply(img)
        return apply_finishing_touches(filtered)

    if uploaded:
        img = Image.open(uploaded).convert("RGB")

        if mode == "Single Filter" and filter_name:
            with st.spinner(f"Applying {filter_name}..."):
                result = process_image_filter(img, filter_name, intensity)

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
            st.subheader(f"🎨 Generating all {len(filters_in_cat)} filters in '{category.upper()}'...")
            cols = st.columns(4)
            results = {}
            progress = st.progress(0)
            for i, (name, _) in enumerate(filters_in_cat):
                try:
                    out = process_image_filter(img, name, intensity)
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
        st.subheader("📊 Filter Library Overview (110 Total)")
        stat_cols = st.columns(4)
        for i, cat in enumerate(CATEGORIES):
            n = sum(1 for _, c in FILTER_REGISTRY.items() if c.category == cat)
            stat_cols[i % 4].metric(cat.upper(), f"{n} Filters")

    else:
        st.info("👈 Upload an image from the sidebar to begin editing!")

# -------------------------------------------------------------
# 🎬 DYNAMIC VIDEO STUDIO
# -------------------------------------------------------------
else:
    st.subheader("🎬 Retro Video Studio Pipeline")
    st.markdown("Transform video clips into authentic vintage broadcasts, VHS tapes, cyberpunk anime, or found footage horrors.")

    col_v1, col_v2 = st.columns([1, 2])

    with col_v1:
        st.markdown("### 1. Upload Video")
        video_file = st.file_uploader(
            "Choose a Video File",
            type=["mp4", "mov", "avi", "mkv", "webm", "gif"],
            help="Supports clips up to 3 minutes. Videos are automatically downscaled to 720p for fast rendering."
        )

        st.markdown("### 2. Video & Filter Settings")
        v_category = st.selectbox("Filter Category", CATEGORIES, index=5, key="v_cat")
        v_filters_in_cat = [(n, c) for n, c in sorted(FILTER_REGISTRY.items()) if c.category == v_category]
        
        v_filter_name = st.selectbox(
            "Filter",
            [n for n, _ in v_filters_in_cat],
            format_func=lambda n: f"{n} — {FILTER_REGISTRY[n].description}",
            key="v_filter"
        )
        v_intensity = st.slider("Filter Intensity", 0.0, 1.0, 1.0, 0.05, key="v_int")
        v_fps = st.select_slider("Target Frame Rate (FPS)", options=[8, 12, 15, 24], value=12)

        st.markdown("### 3. Dynamic Time-Based Effects")
        c_pulse = st.checkbox("💓 Pulse (Rhythmic Brightness)", value=False)
        c_strobe = st.checkbox("⚡ Strobe (Rapid Flashing)", value=False)
        c_chroma = st.checkbox("🌈 Chromatic Cycle (Rainbow Hue Rotate)", value=False)
        c_wobble = st.checkbox("📼 VHS Wobble (Tracking Sync Jitter)", value=True)
        c_time = st.checkbox("🔴 Blinking Timestamp (REC ● 00:00:00)", value=True)
        c_zoom = st.checkbox("💥 Zoom Punch (Periodic Rhythmic Beat)", value=False)
        c_glitch = st.checkbox("⚡ Glitch Interval (Periodic RGB Bursts)", value=False)
        c_burn = st.checkbox("🔥 Film Burn (Occasional Light Flares)", value=False)
        
        watermark_text = st.text_input("Optional Watermark", value="")

    active_time_effects = []
    if c_pulse: active_time_effects.append("pulse")
    if c_strobe: active_time_effects.append("strobe")
    if c_chroma: active_time_effects.append("chromatic_cycle")
    if c_wobble: active_time_effects.append("vhs_wobble")
    if c_time: active_time_effects.append("timestamp")
    if c_zoom: active_time_effects.append("zoom_punch")
    if c_glitch: active_time_effects.append("glitch_interval")
    if c_burn: active_time_effects.append("film_burn")

    with col_v2:
        if video_file:
            # Save uploaded video to temp file
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=Path(video_file.name).suffix)
            tfile.write(video_file.read())
            tfile.flush()
            tfile_path = tfile.name

            try:
                v_info = VideoProcessor.get_video_info(tfile_path)
                st.info(f"📊 **Source Video**: {v_info['width']}×{v_info['height']} • {v_info['fps']:.1f} FPS • {v_info['duration']:.1f}s ({v_info['total_frames']} frames)")
            except Exception as e:
                st.error(f"Could not read video metadata: {e}")
                v_info = None

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                do_preview = st.button("⚡ Generate 3-Second Quick Preview", use_container_width=True)
            with btn_col2:
                do_full = st.button("🚀 Render Full Video", use_container_width=True)

            if do_preview or do_full:
                is_prev = do_preview
                cls = FILTER_REGISTRY[v_filter_name]
                f_obj = cls(intensity=v_intensity)

                p_bar = st.progress(0)
                status_box = st.empty()

                def web_progress(cur, tot):
                    p_bar.progress(cur / max(tot, 1))
                    status_box.text(f"Processing frame {cur}/{tot} ({int(cur/max(tot,1)*100)}%)...")

                out_mp4_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                out_gif_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name

                with st.spinner("Rendering retro frames with time-based effects..."):
                    res = VideoProcessor.process_video(
                        input_path=tfile_path,
                        filter_obj=f_obj,
                        output_mp4=out_mp4_tmp,
                        output_gif=out_gif_tmp,
                        target_fps=v_fps,
                        is_preview=is_prev,
                        time_effects=active_time_effects,
                        watermark=watermark_text if watermark_text else None,
                        progress_callback=web_progress
                    )

                status_box.success(f"✅ Finished rendering {res['frames_processed']} frames at {res['fps']} FPS ({res['duration']:.1f}s)!")

                tab_v1, tab_v2 = st.tabs(["🎥 MP4 Video Playback", "🎞️ Animated GIF"])
                with tab_v1:
                    with open(out_mp4_tmp, "rb") as mf:
                        mp4_bytes = mf.read()
                    st.video(mp4_bytes)
                    st.download_button(
                        "⬇️ Download MP4 Video",
                        mp4_bytes,
                        file_name=f"retro_{Path(video_file.name).stem}_{v_filter_name}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

                with tab_v2:
                    with open(out_gif_tmp, "rb") as gf:
                        gif_bytes = gf.read()
                    st.image(gif_bytes, use_container_width=True)
                    st.download_button(
                        "⬇️ Download Animated GIF",
                        gif_bytes,
                        file_name=f"retro_{Path(video_file.name).stem}_{v_filter_name}.gif",
                        mime="image/gif",
                        use_container_width=True
                    )

        else:
            st.info("👈 Upload a video clip on the left to get started!")
            st.markdown("""
            ### 🎬 Video Studio Features:
            - **110 Unique Retro Filters**: Apply any aesthetic from Cyberpunk, Horror, Dreamy, 80s, 90s, Retro, Glitch, and Artistic.
            - **8 Dynamic Time Effects**:
              - 💓 **Pulse**: Gentle rhythmic breathing brightness
              - ⚡ **Strobe**: High-energy flashing
              - 🌈 **Chromatic Cycle**: Continuous rainbow hue rotation
              - 📼 **VHS Wobble**: Rolling horizontal tracking lines
              - 🔴 **Blinking Timestamp**: Vintage video camera OSD
              - 💥 **Zoom Punch**: Rhythmic zoom beat snap
              - ⚡ **Glitch Burst**: Periodic RGB channel separation
              - 🔥 **Film Burn**: Warm flare leaks
            - **Dual Export**: Export both high-efficiency MP4 video and looping animated GIFs.
            """)