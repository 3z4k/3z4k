#!/usr/bin/env python3
"""Render an ASCII Himalayan landscape with a name rising behind the ridgeline."""

from pathlib import Path
import math
import random

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
WIDTH, HEIGHT = 1120, 560
BG = (8, 19, 28)
FONT_PATHS = (Path('/System/Library/Fonts/Menlo.ttc'),
              Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
FONT_PATH = next((p for p in FONT_PATHS if p.exists()), None)
if FONT_PATH is None:
    raise SystemExit('Menlo or DejaVu Sans Mono is required.')


def font(size):
    return ImageFont.truetype(str(FONT_PATH), size)


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def ridge(points, x):
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        if ax <= x <= bx:
            return ay + (by - ay) * (x - ax) / (bx - ax)
    return points[-1][1]


def make_landscape():
    im = Image.new('RGBA', (WIDTH, HEIGHT))
    d = ImageDraw.Draw(im)
    layers = [
        ([(0,29),(13,20),(24,26),(37,12),(49,25),(60,18),(74,27),
          (88,21),(101,10),(115,26),(129,17),(145,29),(159,23)],
         (63,106,125), (205,230,230)),
        ([(0,34),(12,27),(25,34),(42,22),(57,34),(77,18),(96,35),
          (115,27),(136,34),(151,23),(159,30)],
         (35,75,94), (118,167,183)),
        ([(0,37),(18,33),(36,39),(61,30),(82,39),(105,32),(128,40),
          (145,34),(159,37)],
         (17,43,59), (55,92,110)),
    ]
    char_font = font(12)
    for index, (points, shade, snow) in enumerate(layers):
        # Every layer has an opaque silhouette: the name really passes behind it.
        top = [(x * 7, 130 + ridge(points, x) * 9) for x in range(160)]
        d.polygon(top + [(WIDTH, 521), (0, 521)], fill=(*BG,255))
        for x in range(160):
            h = ridge(points, x)
            slope = ridge(points, min(159, x + 1)) - ridge(points, max(0, x - 1))
            for y in range(math.ceil(h), 44):
                depth = y - h
                seed = (x * 7919 + y * 104729 + index * 31) % 101
                if depth < 1.2:
                    char = '/' if slope < -.25 else '\\' if slope > .25 else '^'
                    color = snow
                elif depth < (5.4 if index == 0 else 2.8) and h < (24 if index == 0 else 26):
                    char = '/\\^:'[seed % 4]
                    color = mix(shade, snow, .55 + .4 * (seed / 101))
                else:
                    char = '/:.'[seed % 3] if seed < 70 else ' '
                    color = mix(shade, snow, .12 if slope < 0 else .01)
                if char != ' ':
                    d.text((x * 7, 130 + y * 9), char, font=char_font, fill=(*color,255))
    return im


def name_points():
    f = font(160)
    box = f.getbbox('Kaze Kylan')
    mask = Image.new('L', (box[2]-box[0], box[3]-box[1]))
    ImageDraw.Draw(mask).text((-box[0],-box[1]), 'Kaze Kylan', font=f, fill=255, stroke_width=1)
    mask = mask.resize((138,17), Image.Resampling.LANCZOS)
    return [(x,y,'/\\:+='[(x+y*3)%5]) for y in range(17)
            for x in range(138) if mask.getpixel((x,y)) > 90]


def main():
    OUT.mkdir(exist_ok=True)
    base = Image.new('RGB', (WIDTH,HEIGHT), BG)
    d = ImageDraw.Draw(base)
    d.text((34,28), '$ nepal --quiet', font=font(14), fill=(133,171,181))
    d.text((1086,28), 'himalaya / 3z4k', font=font(14), fill=(133,171,181), anchor='ra')
    rng = random.Random(25)
    for _ in range(42):
        x,y = rng.randrange(24,1095),rng.randrange(64,292)
        d.text((x,y), '.', font=font(10), fill=(34,62,76))
    landscape = make_landscape()
    points = name_points()
    f = font(11)
    def render(t):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        progress = min(1,max(0,t/7.5))
        eased = progress*progress*(3-2*progress)
        top = round(363 - 286*eased)
        opacity = 1 if t < 10 else max(0,1-(t-10)/1.8)
        for x,y,char in points:
            color = mix((218,172,151),(189,221,225),y/16)
            draw.text((77+x*7,top+y*8),char,font=f,fill=mix(BG,color,opacity))
        frame.paste(landscape,(0,0),landscape)
        draw = ImageDraw.Draw(frame)
        # A small double-pennon Nepal flag marks the tallest rear peak.
        fx,fy = 707,199
        draw.line((fx,fy-14,fx,226),fill=(154,181,192),width=1)
        wave = round(math.sin(t*1.1))
        flag = [(fx+1,fy-14),(fx+30,fy+wave),(fx+8,fy+wave),
                (fx+28,fy+15+wave),(fx+1,fy+15)]
        draw.polygon(flag,fill=(193,45,68),outline=(101,144,192),width=2)
        draw.ellipse((fx+5,fy-6,fx+9,fy-2),fill=(234,235,224))
        draw.ellipse((fx+6,fy+6,fx+10,fy+10),fill=(234,235,224))
        draw.rectangle((0,524,WIDTH,HEIGHT),fill=BG)
        draw.text((34,537),'quietly making things.',font=font(13),fill=(133,171,181))
        draw.text((1086,537),'from nepal, with curiosity.',font=font(13),fill=(133,171,181),anchor='ra')
        return frame
    frames = [render(i/8) for i in range(96)]
    poster = render(8.5)
    atlas = Image.new('RGB',(WIDTH,HEIGHT*3))
    for i,frame in enumerate((frames[0],frames[32],poster)):
        atlas.paste(frame,(0,i*HEIGHT))
    palette = atlas.quantize(colors=128)
    quantized = [f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    # GIF delays use 10 ms units: alternating delays average exactly 8 fps.
    quantized[0].save(OUT/'himalaya.gif',save_all=True,append_images=quantized[1:],
                      duration=[120,130]*48,loop=0,optimize=True,disposal=1)
    poster.save(OUT/'himalaya.png',optimize=True)
    print(f"Rendered 12-second reveal: {(OUT/'himalaya.gif').stat().st_size//1024} KiB")


if __name__ == '__main__':
    main()
