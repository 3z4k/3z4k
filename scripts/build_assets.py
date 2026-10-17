#!/usr/bin/env python3
"""Build the profile artwork with Pillow; optionally use the local terminal scenes."""

import argparse
import importlib.util
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W = 960
INK = "#0C1524"
BLUE = "#8ABEFF"
APRICOT = "#FFBF86"
PAPER = "#E6EDF3"
SLATE = "#8DA0B8"
FONT_PATHS = (
    Path("/System/Library/Fonts/Menlo.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
)


def font(size):
    path = next((p for p in FONT_PATHS if p.exists()), None)
    if path is None:
        raise SystemExit("Install Menlo or DejaVu Sans Mono to render the artwork.")
    return ImageFont.truetype(str(path), size)


def shell(height, title):
    im = Image.new("RGB", (W, height), INK)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, W - 2, height - 2), radius=18, outline="#293C54", width=2)
    d.line((1, 47, W - 2, 47), fill="#293C54")
    for x, color in zip((25, 45, 65), ("#FF9B92", "#FFCE86", "#98C6B3")):
        d.ellipse((x - 4, 20, x + 4, 28), fill=color)
    d.text((W // 2, 24), title, font=font(13), fill=SLATE, anchor="mm")
    return im


def save_animation(frames, name, duration):
    # Shared palette avoids color flicker between otherwise identical frames.
    atlas = Image.new("RGB", (W, frames[0].height * 3))
    for i, frame in enumerate((frames[0], frames[len(frames) // 2], frames[-1])):
        atlas.paste(frame, (0, i * frame.height))
    palette = atlas.quantize(colors=128)
    converted = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    converted[0].save(ASSETS / f"{name}.gif", save_all=True,
                      append_images=converted[1:], duration=duration,
                      loop=0, optimize=True, disposal=1)
    frames[0].save(ASSETS / f"{name}.png", optimize=True)


def intro():
    base = shell(414, "~/3z4k  —  a small corner of the internet")
    d = ImageDraw.Draw(base)
    d.text((40, 78), "3z4k", font=font(20), fill=APRICOT)
    d.text((101, 78), "@github:~ $ whoami", font=font(20), fill=PAPER)

    # Rasterize the alias into a real grid of ASCII glyphs.
    mask = Image.new("L", (300, 80))
    md = ImageDraw.Draw(mask)
    md.text((2, -17), "k4z3", font=font(100), fill=255, stroke_width=1)
    mask = mask.resize((67, 16), Image.Resampling.LANCZOS)
    glyphs = []
    for y in range(mask.height):
        for x in range(mask.width):
            if mask.getpixel((x, y)) > 110:
                glyphs.append((x, y, "k4z3"[(x + y) % 4]))
    d.text((43, 312), "tools that work. experiments that move.", font=font(22), fill=PAPER)
    d.text((43, 361), "web tools / discord bots / terminal worlds", font=font(16), fill=SLATE)
    d.text((915, 361), "[ enter ]", font=font(14), fill=APRICOT, anchor="ra")
    glyph_font = font(12)
    frames = []
    for i in range(64):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        # Start with a complete wordmark. One quiet sweep moves across it.
        sweep = (i / 63) * 100 - 15
        for x, y, char in glyphs:
            distance = abs(x - sweep)
            color = APRICOT if distance < 1.8 else PAPER if distance < 4 else BLUE
            draw.text((43 + x * 11, 124 + y * 10), char, font=glyph_font, fill=color)
        if (i // 8) % 2 == 0:
            draw.rectangle((331, 81, 341, 100), fill=APRICOT)
        frames.append(frame)
    save_animation(frames, "intro", 100)


def load_scene(name, path):
    if not path.is_file():
        raise SystemExit(f"Scene source not found: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def gallery(terminal_root):
    aq = load_scene("profile_aquarium", terminal_root / "terminal-aquarium/aquarium.py")
    rd = load_scene("profile_roadster", terminal_root / "terminal-roadster/roadster.py")
    tank = aq.Aquarium(110, 60, count=7)
    scene = rd.Scene(74, 30)
    small = font(10)
    base = shell(378, "~/experiments  —  drawn by code")
    d = ImageDraw.Draw(base)
    d.text((24, 69), "aquarium.py", font=font(16), fill=APRICOT)
    d.text((504, 69), "roadster.py", font=font(16), fill=APRICOT)
    for _ in range(30):
        tank.update(.1)
    frames = []
    for i in range(72):
        tank.update(1 / 6)
        if i in (12, 42):
            tank.feed(.45 if i == 12 else .7)
        canvas = tank.draw()
        pixels = bytes(c for row in canvas.pixels for pixel in row for c in pixel)
        ocean = Image.frombytes("RGB", (110, 60), pixels)
        frame = base.copy()
        frame.paste(ocean.resize((440, 240), Image.Resampling.NEAREST), (24, 100))
        # Keep the text car legible, using the same aspect ratio as the terminal.
        car = Image.new("RGB", (444, 240), rd.BG)
        draw = ImageDraw.Draw(car)
        for (x, y), (char, color) in scene.frame(i / 6).items():
            draw.text((x * 6, y * 8), char, font=small, fill=color)
        frame.paste(car, (496, 100))
        # Captions sit on a solid band underneath both scenes.
        draw = ImageDraw.Draw(frame)
        draw.rectangle((20, 340, 470, 375), fill=INK)
        draw.text((24, 351), "a tiny ocean inside a terminal", font=font(13), fill=SLATE)
        draw.text((504, 351), "a sports car made of characters", font=font(13), fill=SLATE)
        frames.append(frame)
    save_animation(frames, "terminal-lab", 170)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminal-root", type=Path)
    args = parser.parse_args()
    ASSETS.mkdir(exist_ok=True)
    intro()
    if args.terminal_root:
        gallery(args.terminal_root.resolve())
    for path in sorted(ASSETS.iterdir()):
        print(f"{path.relative_to(ROOT)}: {path.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
