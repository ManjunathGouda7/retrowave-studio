"""
Video processing pipeline for Retro Image Generator.
Features:
- Multi-format support: MP4, MOV, AVI, MKV, WEBM, GIF
- Auto-downscaling to max 720p
- Configurable target FPS (8, 12, 15, 24)
- 8 Dynamic time-based effects (Pulse, Strobe, Chromatic Cycle, VHS Wobble, Timestamp, Zoom Punch, Glitch Interval, Film Burn)
- 3-Second Quick Preview generator
- MP4 & Looping GIF output
- Watermark support
"""
import math
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from utils.effects import chromatic_aberration, scanlines, add_light_leak, add_grain


def apply_time_effects(
    frame_img: Image.Image,
    frame_idx: int,
    total_frames: int,
    fps: float,
    effects: list = None,
    watermark: str = None
) -> Image.Image:
    """Apply dynamic, frame-varying time effects to a processed video frame."""
    if not effects and not watermark:
        return frame_img

    effects = [e.lower() for e in (effects or [])]
    t = float(frame_idx) / max(fps, 1.0)
    w, h = frame_img.size
    result = frame_img

    # 1. Pulse: Brightness oscillates rhythmically (1.5 Hz)
    if "pulse" in effects:
        scale = 1.0 + 0.22 * math.sin(t * 2.0 * math.pi * 1.5)
        result = ImageEnhance.Brightness(result).enhance(scale)

    # 2. Strobe: Rapid rhythmic flashing
    if "strobe" in effects:
        # Flash every 4 frames
        if (frame_idx % 4) == 0:
            result = ImageEnhance.Brightness(result).enhance(1.45)
        elif (frame_idx % 4) == 2:
            result = ImageEnhance.Brightness(result).enhance(0.75)

    # 3. Chromatic Cycle: Hue rotates over time (Rainbow cycle)
    if "chromatic_cycle" in effects:
        arr_rgb = np.array(result)
        arr_hsv = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
        # Shift hue by time
        hue_shift = (t * 50.0) % 180.0
        arr_hsv[:, :, 0] = (arr_hsv[:, :, 0] + hue_shift) % 180.0
        cycled_rgb = cv2.cvtColor(arr_hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        result = Image.fromarray(cycled_rgb)

    # 4. VHS Wobble: Rolling scanlines & horizontal tracking sync jitter
    if "vhs_wobble" in effects:
        arr = np.array(result)
        # Rolling horizontal tracking glitch bar
        bar_y = int(((t * 1.2) % 1.0) * h)
        bar_h = max(10, h // 16)
        y_slice = np.arange(bar_y, bar_y + bar_h) % h
        shift = int(12 * math.sin(t * 10.0))
        arr[y_slice] = np.roll(arr[y_slice], shift, axis=1)
        result = Image.fromarray(arr)
        result = scanlines(result, spacing=3, darkness=0.2)

    # 5. Zoom Punch: Rhythmic beat zoom-in pulse & snap back
    if "zoom_punch" in effects:
        # Beats every 1.0 second
        beat_phase = (t % 1.0)
        if beat_phase < 0.25:
            zoom_scale = 1.0 + 0.12 * math.sin(beat_phase * 4.0 * math.pi)
            crop_w = int(w / zoom_scale)
            crop_h = int(h / zoom_scale)
            x1 = (w - crop_w) // 2
            y1 = (h - crop_h) // 2
            cropped = result.crop((x1, y1, x1 + crop_w, y1 + crop_h))
            result = cropped.resize((w, h), Image.BILINEAR)

    # 6. Glitch Interval: Burst of RGB split every N frames
    if "glitch_interval" in effects:
        period = int(fps * 1.5)
        rem = frame_idx % max(period, 1)
        if rem < 3: # 3-frame glitch burst
            result = chromatic_aberration(result, shift=10)
            arr = np.array(result)
            slice_y = int((t * 300) % (h - 20))
            arr[slice_y:slice_y+15] = np.roll(arr[slice_y:slice_y+15], 25, axis=1)
            result = Image.fromarray(arr)

    # 7. Film Burn: Periodic warm flare flash and fade
    if "film_burn" in effects:
        period_burn = int(fps * 2.5)
        rem_b = frame_idx % max(period_burn, 1)
        if rem_b < 4:
            burn_intensity = 0.75 * (1.0 - rem_b / 4.0)
            result = add_light_leak(result, intensity=burn_intensity, position="top_right")

    # 8. Timestamp Overlay: Blinking REC ● + running timecode
    if "timestamp" in effects:
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font_size = max(14, int(h * 0.035))
        
        # Blinking REC indicator (blinks every 0.5 sec)
        blink = (int(t * 2) % 2) == 0
        rec_text = "REC "
        draw.text((20, 20), rec_text, fill=(240, 240, 240, 230))
        if blink:
            draw.ellipse([70, 24, 82, 36], fill=(255, 30, 30, 240))
            
        # Running Timecode: 00:MM:SS:FF
        total_secs = int(t)
        mins = total_secs // 60
        secs = total_secs % 60
        frames_part = frame_idx % int(max(fps, 1))
        tc_str = f"00:{mins:02d}:{secs:02d}:{frames_part:02d}"
        
        draw.text((20, h - 35), tc_str, fill=(40, 255, 120, 230))
        
        base = result.convert("RGBA")
        result = Image.alpha_composite(base, overlay).convert("RGB")

    # Optional Watermark
    if watermark:
        draw_wm = ImageDraw.Draw(result)
        draw_wm.text((w - 140, h - 25), str(watermark), fill=(220, 220, 220))

    return result


class VideoProcessor:
    """Processes video files with filters and dynamic temporal effects."""

    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Extract metadata from video file."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / max(fps, 1.0)
        cap.release()

        return {
            "fps": fps,
            "total_frames": total_frames,
            "width": w,
            "height": h,
            "duration": duration,
        }

    @staticmethod
    def remux_audio(input_path: str, video_path: str):
        """Extract audio from source input and remux into output video using ffmpeg if available."""
        import subprocess
        import shutil
        ffmpeg_exe = shutil.which("ffmpeg")
        if not ffmpeg_exe or not os.path.exists(video_path):
            return

        temp_audio = video_path + ".temp_audio.m4a"
        temp_muxed = video_path + ".temp_muxed.mp4"
        try:
            cmd_extract = [
                ffmpeg_exe, "-y", "-i", input_path, "-vn", "-c:a", "copy", temp_audio
            ]
            res_ext = subprocess.run(cmd_extract, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res_ext.returncode != 0 or not os.path.exists(temp_audio) or os.path.getsize(temp_audio) == 0:
                return

            cmd_mux = [
                ffmpeg_exe, "-y", "-i", video_path, "-i", temp_audio,
                "-c:v", "copy", "-c:a", "aac", "-shortest", temp_muxed
            ]
            res_mux = subprocess.run(cmd_mux, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res_mux.returncode == 0 and os.path.exists(temp_muxed) and os.path.getsize(temp_muxed) > 0:
                os.replace(temp_muxed, video_path)
        except Exception:
            pass
        finally:
            for p in (temp_audio, temp_muxed):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    @staticmethod
    def process_video(
        input_path: str,
        filter_obj,
        output_mp4: str = None,
        output_gif: str = None,
        target_fps: int = 12,
        max_duration: float = 180.0,
        is_preview: bool = False,
        time_effects: list = None,
        watermark: str = None,
        progress_callback=None,
    ) -> dict:
        """
        Process video frame-by-frame with target FPS, downscaling, and effects.
        """
        info = VideoProcessor.get_video_info(input_path)
        cap = cv2.VideoCapture(input_path)
        
        orig_fps = info["fps"]
        orig_w, orig_h = info["width"], info["height"]
        
        # Calculate scaling to max 720p (1280x720) preserving aspect ratio
        max_dim = 720
        if max(orig_w, orig_h) > max_dim:
            if orig_w >= orig_h:
                out_w = max_dim
                out_h = int(orig_h * (max_dim / orig_w))
            else:
                out_h = max_dim
                out_w = int(orig_w * (max_dim / orig_h))
        else:
            out_w, out_h = orig_w, orig_h

        # Frame dimensions must be even for video codecs
        out_w = (out_w // 2) * 2
        out_h = (out_h // 2) * 2

        # Preview limits duration to 3 seconds
        limit_duration = 3.0 if is_preview else min(info["duration"], max_duration)
        max_output_frames = int(limit_duration * target_fps)

        # Sampling step
        frame_interval = max(1, int(round(orig_fps / target_fps)))
        
        # Video Writer for MP4
        writer = None
        if output_mp4:
            os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_mp4, fourcc, target_fps, (out_w, out_h))

        processed_frames_pil = []
        frame_count_in = 0
        frame_count_out = 0

        try:
            while cap.isOpened() and frame_count_out < max_output_frames:
                ret, frame_bgr = cap.read()
                if not ret:
                    break

                # Sample frames to hit target FPS
                if (frame_count_in % frame_interval) == 0:
                    # Resize frame
                    if (out_w, out_h) != (orig_w, orig_h):
                        frame_bgr = cv2.resize(frame_bgr, (out_w, out_h), interpolation=cv2.INTER_AREA)

                    # BGR to RGB PIL
                    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)

                    # 1. Apply core image filter
                    filtered_pil = filter_obj.apply(frame_pil)

                    # 2. Apply time-based dynamic effects
                    final_pil = apply_time_effects(
                        filtered_pil,
                        frame_idx=frame_count_out,
                        total_frames=max_output_frames,
                        fps=target_fps,
                        effects=time_effects,
                        watermark=watermark
                    )

                    # Write MP4
                    if writer:
                        out_bgr = cv2.cvtColor(np.array(final_pil), cv2.COLOR_RGB2BGR)
                        writer.write(out_bgr)

                    # Collect for GIF
                    if output_gif:
                        processed_frames_pil.append(final_pil)

                    frame_count_out += 1

                    if progress_callback:
                        progress_callback(frame_count_out, max_output_frames)

                frame_count_in += 1

        finally:
            cap.release()
            if writer:
                writer.release()

        # Attempt to preserve and remux original audio if ffmpeg is available
        if output_mp4 and os.path.exists(output_mp4):
            VideoProcessor.remux_audio(input_path, output_mp4)

        # Generate animated GIF if requested
        if output_gif and processed_frames_pil:
            os.makedirs(os.path.dirname(os.path.abspath(output_gif)), exist_ok=True)
            duration_ms = int(1000.0 / target_fps)
            processed_frames_pil[0].save(
                output_gif,
                format="GIF",
                save_all=True,
                append_images=processed_frames_pil[1:],
                duration=duration_ms,
                loop=0,
                optimize=True
            )

        return {
            "frames_processed": frame_count_out,
            "fps": target_fps,
            "width": out_w,
            "height": out_h,
            "mp4_path": output_mp4,
            "gif_path": output_gif,
            "duration": frame_count_out / float(target_fps)
        }
