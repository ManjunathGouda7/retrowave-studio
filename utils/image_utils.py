"""
Retro image overlays and generators:
- Procedural 7-segment digital camera LED date stamp
- Polaroid instant frame with classic chin
- 35mm filmstrip negative border with sprocket perforations
- VHS On-Screen Display (OSD)
- Looping animated retro GIF generator
"""
import io
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# 7-segment display mapping for digits 0-9
SEGMENTS = {
    '0': ('a', 'b', 'c', 'd', 'e', 'f'),
    '1': ('b', 'c'),
    '2': ('a', 'b', 'g', 'e', 'd'),
    '3': ('a', 'b', 'g', 'c', 'd'),
    '4': ('f', 'g', 'b', 'c'),
    '5': ('a', 'f', 'g', 'c', 'd'),
    '6': ('a', 'f', 'e', 'd', 'c', 'g'),
    '7': ('a', 'b', 'c'),
    '8': ('a', 'b', 'c', 'd', 'e', 'f', 'g'),
    '9': ('a', 'b', 'c', 'd', 'f', 'g'),
    '-': ('g',),
}


def _draw_7segment_char(draw: ImageDraw.ImageDraw, char: str, x: float, y: float, w: float, h: float, color: tuple, thickness: int):
    """Draw a single 7-segment LED character procedurally."""
    half_h = h / 2.0
    t = max(2, thickness)
    
    # Segment coordinates
    segs = {
        'a': [(x + t, y), (x + w - t, y)],                             # top
        'b': [(x + w, y + t), (x + w, y + half_h - t/2)],              # top-right
        'c': [(x + w, y + half_h + t/2), (x + w, y + h - t)],          # bottom-right
        'd': [(x + t, y + h), (x + w - t, y + h)],                     # bottom
        'e': [(x, y + half_h + t/2), (x, y + h - t)],                  # bottom-left
        'f': [(x, y + t), (x, y + half_h - t/2)],                      # top-left
        'g': [(x + t, y + half_h), (x + w - t, y + half_h)],          # middle
    }
    
    if char in SEGMENTS:
        for seg in SEGMENTS[char]:
            pts = segs[seg]
            draw.line(pts, fill=color, width=t)
    elif char == "'":
        # Apostrophe (e.g. '89 or '94)
        draw.line([(x + w * 0.4, y), (x + w * 0.2, y + h * 0.3)], fill=color, width=t)
    elif char in ('.', ':'):
        rad = max(2, t // 2)
        if char == '.':
            draw.ellipse([x + w/2 - rad, y + h - t - rad, x + w/2 + rad, y + h - t + rad], fill=color)
        else:
            draw.ellipse([x + w/2 - rad, y + h * 0.3 - rad, x + w/2 + rad, y + h * 0.3 + rad], fill=color)
            draw.ellipse([x + w/2 - rad, y + h * 0.7 - rad, x + w/2 + rad, y + h * 0.7 + rad], fill=color)


def draw_date_stamp(img: Image.Image, date_str: str = "'89 10 24", color: tuple = (255, 120, 20)) -> Image.Image:
    """
    Draw classic glowing orange 7-segment digital date stamp in the bottom-right corner.
    Authentic to 80s/90s compact point-and-shoot film cameras.
    """
    w, h = img.size
    
    # Scale digit sizes proportionally to image dimensions
    char_h = max(18, int(h * 0.038))
    char_w = int(char_h * 0.55)
    thick = max(2, int(char_h * 0.13))
    spacing = int(char_w * 0.35)
    space_w = int(char_w * 0.8)
    margin_x = max(20, int(w * 0.05))
    margin_y = max(20, int(h * 0.05))
    
    # Measure total string width
    total_w = 0
    for ch in date_str:
        if ch == ' ':
            total_w += space_w
        elif ch in ("'", '.', ':'):
            total_w += int(char_w * 0.4) + spacing
        else:
            total_w += char_w + spacing
            
    start_x = w - margin_x - total_w
    start_y = h - margin_y - char_h
    
    # Transparent glow layer
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    
    curr_x = start_x
    for ch in date_str:
        if ch == ' ':
            curr_x += space_w
        elif ch in ("'", '.', ':'):
            cw = int(char_w * 0.4)
            _draw_7segment_char(glow_draw, ch, curr_x, start_y, cw, char_h, color + (255,), thick)
            curr_x += cw + spacing
        else:
            _draw_7segment_char(glow_draw, ch, curr_x, start_y, char_w, char_h, color + (255,), thick)
            curr_x += char_w + spacing
            
    # Apply soft phosphor glow
    bloom = glow_layer.filter(ImageFilter.GaussianBlur(radius=max(2, int(thick * 1.5))))
    
    base = img.convert("RGBA")
    # Composite glow, then sharp digits
    base = Image.alpha_composite(base, bloom)
    base = Image.alpha_composite(base, glow_layer)
    return base.convert("RGB")


def add_polaroid_border(img: Image.Image, border_color: tuple = (246, 244, 238)) -> Image.Image:
    """
    Place the image inside an authentic Polaroid 600 instant film frame
    with white borders, classic bottom chin, and inner drop shadow.
    """
    w, h = img.size
    
    # Polaroid proportions: 7.5% side and top border, 22% bottom chin
    side_border = max(18, int(w * 0.075))
    top_border = side_border
    bottom_chin = max(50, int(h * 0.22))
    
    total_w = w + (side_border * 2)
    total_h = h + top_border + bottom_chin
    
    frame = Image.new("RGB", (total_w, total_h), border_color)
    
    # Inner photo drop shadow for realism
    shadow = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rectangle([4, 4, w + 4, h + 4], fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=4))
    
    frame.paste(shadow, (side_border - 4, top_border - 4), shadow)
    frame.paste(img, (side_border, top_border))
    
    return frame


def add_filmstrip_border(img: Image.Image, brand_text: str = "KODAK 400-5") -> Image.Image:
    """
    Add 35mm film negative borders with sprocket perforations
    and frame numbers along the edges.
    """
    w, h = img.size
    border_h = max(36, int(h * 0.12))
    total_h = h + (border_h * 2)
    
    frame = Image.new("RGB", (w, total_h), (12, 12, 12))
    frame.paste(img, (0, border_h))
    
    draw = ImageDraw.Draw(frame)
    sprocket_w = max(12, int(border_h * 0.45))
    sprocket_h = max(16, int(border_h * 0.6))
    sprocket_gap = max(24, int(sprocket_w * 2.2))
    corner_rad = max(2, sprocket_w // 4)
    
    # Draw sprocket holes along top and bottom borders
    for x in range(sprocket_gap // 2, w - sprocket_w, sprocket_gap):
        # Top sprockets
        top_y = (border_h - sprocket_h) // 2
        draw.rounded_rectangle([x, top_y, x + sprocket_w, top_y + sprocket_h], radius=corner_rad, fill=(240, 240, 240))
        # Bottom sprockets
        bot_y = total_h - border_h + (border_h - sprocket_h) // 2
        draw.rounded_rectangle([x, bot_y, x + sprocket_w, bot_y + sprocket_h], radius=corner_rad, fill=(240, 240, 240))
        
        # Subtle DX code bar & frame numbers in orange
        if (x // sprocket_gap) % 3 == 0:
            frame_num = f"▶ {18 + (x // sprocket_gap)}"
            draw.text((x + sprocket_w + 4, top_y + 2), frame_num, fill=(235, 140, 30))
            draw.text((x + sprocket_w + 4, bot_y + 2), brand_text, fill=(235, 140, 30))
            
    return frame


def add_vhs_osd(img: Image.Image, mode: str = "PLAY ▶", time_code: str = "SP 0:24:18") -> Image.Image:
    """
    Vintage VCR On-Screen Display (OSD) overlay in classic 80s phosphor green.
    """
    w, h = img.size
    font_size = max(16, int(h * 0.04))
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Neon green phosphor color with subtle glow
    color = (40, 255, 120, 240)
    shadow_color = (0, 0, 0, 200)
    
    pos_mode = (max(20, int(w * 0.06)), max(20, int(h * 0.06)))
    pos_time = (max(20, int(w * 0.06)), h - max(40, int(h * 0.1)))
    pos_channel = (w - max(120, int(w * 0.2)), max(20, int(h * 0.06)))
    
    for (px, py), text in [(pos_mode, mode), (pos_time, time_code), (pos_channel, "CH 03")]:
        # Drop shadow
        draw.text((px + 2, py + 2), text, fill=shadow_color)
        draw.text((px, py), text, fill=color)
        
    base = img.convert("RGBA")
    combined = Image.alpha_composite(base, overlay)
    return combined.convert("RGB")


def create_retro_gif(img: Image.Image, filter_obj, anim_type: str = "vhs_jitter", num_frames: int = 8, duration: int = 120) -> bytes:
    """
    Generate a looping animated retro GIF:
    - 'vhs_jitter': realistic VHS tape tracking noise & horizontal slice shifts
    - 'neon_pulse': rhythmic breathing neon glow
    - 'crt_roll': rolling CRT vertical blanking interval scanline bar
    """
    from utils.effects import scanlines, chromatic_aberration, add_grain
    
    # Process base filtered image
    base = filter_obj.apply(img)
    w, h = base.size
    
    frames = []
    
    for i in range(num_frames):
        phase = float(i) / num_frames
        frame = base.copy()
        
        if anim_type == "vhs_jitter":
            # Random tracking jitter per frame
            arr = np.array(frame)
            if np.random.rand() > 0.4:
                slice_y = np.random.randint(0, h - 25)
                slice_h = np.random.randint(4, 25)
                shift = np.random.randint(-15, 16)
                arr[slice_y:slice_y+slice_h] = np.roll(arr[slice_y:slice_y+slice_h], shift, axis=1)
            frame = Image.fromarray(arr)
            frame = chromatic_aberration(frame, shift=np.random.randint(2, 6))
            frame = add_grain(frame, amount=0.08)
            
        elif anim_type == "neon_pulse":
            # Pulsing intensity
            scale = 0.85 + 0.25 * math.sin(phase * 2 * math.pi)
            arr = np.array(frame).astype(np.float32)
            arr[:, :, (0, 2)] = np.clip(arr[:, :, (0, 2)] * scale, 0, 255)
            frame = Image.fromarray(arr.astype(np.uint8))
            frame = add_grain(frame, amount=0.05)
            
        elif anim_type == "crt_roll":
            # Rolling horizontal scan bar
            arr = np.array(frame).astype(np.float32)
            bar_y = int(phase * h)
            bar_h = max(20, h // 10)
            y_indices = (np.arange(bar_y, bar_y + bar_h)) % h
            arr[y_indices] = np.clip(arr[y_indices] * 1.3 + 25, 0, 255)
            frame = Image.fromarray(arr.astype(np.uint8))
            frame = scanlines(frame, spacing=3, darkness=0.25)
            
        frames.append(frame)
        
    buf = io.BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )
    return buf.getvalue()
