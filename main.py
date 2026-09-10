#!/usr/bin/env python3
"""
Retro Image Generator - CLI
Usage:
    python main.py input.jpg --filter 80s_vaporwave
    python main.py input.jpg --filter 90s_polaroid --date-stamp "'94 12 25" --polaroid
    python main.py input.jpg --filter 80s_vhs --gif
    python main.py input.jpg --all-80s
    python main.py --list
"""
import argparse
import os
import sys
from pathlib import Path
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
from utils.effects import add_light_leak, add_grain

# Ensure safe UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def list_filters():
    print("\n🎨 Available Filters:\n")
    categories = {}
    for name, cls in sorted(FILTER_REGISTRY.items()):
        categories.setdefault(cls.category, []).append((name, cls.description))
    for cat, items in categories.items():
        print(f"\n📁 {cat.upper()} ({len(items)} filters)")
        print("─" * 60)
        for name, desc in items:
            print(f"  • {name:30s} → {desc}")
    print(f"\n✨ Total Available: {len(FILTER_REGISTRY)} filters across {len(categories)} categories.\n")


def apply_filter(
    input_path: str,
    filter_name: str,
    intensity: float = 1.0,
    date_stamp: str = None,
    polaroid: bool = False,
    film_border: bool = False,
    vhs_osd: bool = False,
    light_leak: bool = False,
    grain: float = 0.0,
    gif: bool = False,
):
    if filter_name not in FILTER_REGISTRY:
        print(f"❌ Unknown filter: {filter_name}")
        return None
    img = Image.open(input_path).convert("RGB")
    cls = FILTER_REGISTRY[filter_name]
    f = cls(intensity=intensity)
    
    os.makedirs("output", exist_ok=True)
    base = Path(input_path).stem

    if gif:
        out_path = f"output/{base}_{filter_name}_animated.gif"
        gif_bytes = create_retro_gif(img, f, anim_type="vhs_jitter")
        with open(out_path, "wb") as gf:
            gf.write(gif_bytes)
        print(f"🎞️ Animated GIF Saved: {out_path}")
        return out_path

    result = f.apply(img)

    # Optional Finishing Touches
    if light_leak:
        result = add_light_leak(result, intensity=0.45)
    if grain > 0:
        result = add_grain(result, amount=grain)
    if date_stamp:
        result = draw_date_stamp(result, date_str=date_stamp)
    if vhs_osd:
        result = add_vhs_osd(result)
    if polaroid:
        result = add_polaroid_border(result)
    elif film_border:
        result = add_filmstrip_border(result)

    out_path = f"output/{base}_{filter_name}.jpg"
    result.save(out_path, quality=95)
    print(f"✅ Saved: {out_path}")
    return out_path


def apply_all_in_category(input_path: str, category: str, intensity: float = 1.0, **kwargs):
    imgs = [name for name, cls in FILTER_REGISTRY.items() if cls.category == category]
    if not imgs:
        print(f"❌ No filters in category: {category}")
        return
    print(f"🎨 Applying {len(imgs)} {category} filters...")
    for name in imgs:
        apply_filter(input_path, name, intensity, **kwargs)


def apply_all(input_path: str, intensity: float = 1.0, **kwargs):
    print(f"🎨 Applying ALL {len(FILTER_REGISTRY)} filters...")
    for name in FILTER_REGISTRY:
        try:
            apply_filter(input_path, name, intensity, **kwargs)
        except Exception as e:
            print(f"⚠️  {name}: {e}")


def main():
    p = argparse.ArgumentParser(description="Retro Image Generator - CLI")
    p.add_argument("input", nargs="?", help="Input image path")
    p.add_argument("--filter", "-f", help="Filter name")
    p.add_argument("--all", "-a", action="store_true", help="Apply all filters")
    p.add_argument("--all-80s", action="store_true", help="Apply all 80s filters")
    p.add_argument("--all-90s", action="store_true", help="Apply all 90s filters")
    p.add_argument("--all-glitch", action="store_true", help="Apply all glitch filters")
    p.add_argument("--all-retro", action="store_true", help="Apply all retro filters")
    p.add_argument("--all-artistic", action="store_true", help="Apply all artistic filters")
    p.add_argument("--intensity", "-i", type=float, default=1.0, help="Filter intensity (0.0 to 1.0)")
    p.add_argument("--list", "-l", action="store_true", help="List all filters")
    
    # Finishing touches
    p.add_argument("--date-stamp", "-d", nargs="?", const="'89 10 24", help="Add retro 7-segment date stamp (e.g. \"'89 10 24\")")
    p.add_argument("--polaroid", action="store_true", help="Encase in a classic Polaroid 600 frame")
    p.add_argument("--film-border", action="store_true", help="Add 35mm film negative border with sprockets")
    p.add_argument("--vhs-osd", action="store_true", help="Add VHS on-screen display overlay")
    p.add_argument("--light-leak", action="store_true", help="Add warm camera light leak")
    p.add_argument("--grain", type=float, default=0.0, help="Add extra film grain (e.g. 0.1)")
    p.add_argument("--gif", action="store_true", help="Generate looping retro animated GIF")
    
    args = p.parse_args()

    if args.list:
        list_filters()
        return

    if not args.input:
        p.print_help()
        return

    if not os.path.exists(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    extra_kwargs = {
        "date_stamp": args.date_stamp,
        "polaroid": args.polaroid,
        "film_border": args.film_border,
        "vhs_osd": args.vhs_osd,
        "light_leak": args.light_leak,
        "grain": args.grain,
        "gif": args.gif,
    }

    if args.filter:
        apply_filter(args.input, args.filter, args.intensity, **extra_kwargs)
    elif args.all:
        apply_all(args.input, args.intensity, **extra_kwargs)
    elif args.all_80s:
        apply_all_in_category(args.input, "80s", args.intensity, **extra_kwargs)
    elif args.all_90s:
        apply_all_in_category(args.input, "90s", args.intensity, **extra_kwargs)
    elif args.all_glitch:
        apply_all_in_category(args.input, "glitch", args.intensity, **extra_kwargs)
    elif args.all_retro:
        apply_all_in_category(args.input, "retro", args.intensity, **extra_kwargs)
    elif args.all_artistic:
        apply_all_in_category(args.input, "artistic", args.intensity, **extra_kwargs)
    else:
        p.print_help()


if __name__ == "__main__":
    main()