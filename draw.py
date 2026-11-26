#!/usr/bin/env python3
"""Draw the 26 November 2026 front page (1024x1024 PNG).

Fresh code written for this entry. Flat vector-style pictograms drawn
with Pillow only; no photographs, no copied artwork. Run:
    python3 draw.py [--variant A|B|C] [--out PATH]
Default: variant A, written beside this script as entry.png.
"""
import argparse
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (180, 35, 24)
RULE = (26, 26, 26)
MUTED = (68, 62, 52)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, box, lines, fnt, fill, align="center", leading=None):
    x0, y0, x1, y1 = box
    if leading is None:
        leading = int(fnt.size * 1.18)
    total = leading * len(lines)
    y = y0 + max(0, (y1 - y0 - total) // 2)
    for line in lines:
        w = draw.textlength(line, font=fnt)
        x = x0 + (x1 - x0 - w) // 2 if align == "center" else x0
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def render_pic(pic, size):
    """Render a pictogram into its own image so it can never spill
    outside its panel, whatever coordinates it uses."""
    layer = Image.new("RGB", size, (255, 255, 255))
    ld = ImageDraw.Draw(layer)
    pic(ld, (0, 0, size[0], size[1]))
    return layer


def panel(draw, box, headline, sub, pic, head_size=28, sub_size=20):
    """A bordered panel: picture on top, headline + sub below it."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(255, 253, 247), outline=INK, width=3)
    pic_h = int((y1 - y0) * 0.58)
    # Paste the pictogram clipped to its own box via the canvas image.
    pic_img = render_pic(pic, (x1 - x0 - 6, pic_h - 3))
    draw._image.paste(pic_img, (x0 + 3, y0 + 3))
    draw.line([(x0, y0 + pic_h), (x1, y0 + pic_h)], fill=INK, width=3)
    cap = (x0 + 12, y0 + pic_h + 10, x1 - 12, y1 - 8)
    hf = font(SANS, head_size)
    lines = wrap(draw, headline, hf, cap[2] - cap[0])
    lh = int(head_size * 1.16)
    y = cap[1]
    for line in lines:
        draw.text((cap[0], y), line, font=hf, fill=INK)
        y += lh
    if sub:
        sf = font(SANS_REG, sub_size)
        slines = wrap(draw, sub, sf, cap[2] - cap[0])
        y += 2
        for line in slines:
            draw.text((cap[0], y), line, font=sf, fill=MUTED)
            y += int(sub_size * 1.2)


# ---------------------------------------------------------------- pictures

def cairo_pic(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(43, 43, 58))
    for fx, fy in [(0.12, 0.12), (0.34, 0.07), (0.58, 0.14), (0.82, 0.08), (0.94, 0.18)]:
        d.ellipse([x0 + fx * w - 3, y0 + fy * h - 3, x0 + fx * w + 3, y0 + fy * h + 3],
                  fill=(240, 240, 220))
    horizon = y0 + int(h * 0.66)
    d.rectangle([x0, horizon, x1, y1], fill=(70, 68, 66))
    d.rectangle([x0, horizon, x1, horizon + 5], fill=(200, 190, 160))
    for i, bh in enumerate([0.10, 0.16, 0.09, 0.14, 0.12]):
        bx = x0 + int(w * (0.04 + i * 0.19))
        d.rectangle([bx, horizon - int(h * bh), bx + int(w * 0.13), horizon], fill=(58, 58, 74))
    # tanker: tank + cab + wheels, sized to the box
    tw, th = int(w * 0.42), int(h * 0.20)
    tx, ty = x0 + int(w * 0.16), horizon - th - 6
    d.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=th // 2, fill=(196, 196, 190),
                        outline=INK, width=3)
    d.rectangle([tx + tw, ty + th // 3, tx + tw + int(w * 0.12), ty + th],
                fill=(180, 60, 40), outline=INK, width=3)
    d.rectangle([tx + tw + int(w * 0.02), ty + th // 2, tx + tw + int(w * 0.10), ty + th - 6],
                fill=(180, 220, 235))
    for wx in (tx + int(tw * 0.14), tx + int(tw * 0.78), tx + tw + int(w * 0.05)):
        d.ellipse([wx, ty + th - 6, wx + int(w * 0.06), ty + th + int(h * 0.07)], fill=INK)
    # flames above the tank, capped inside the box
    fx = tx + int(tw * 0.18)
    for (dx, fw, fh, col) in [(0, 0.13, 0.30, (230, 90, 20)), (0.09, 0.10, 0.38, (245, 160, 30)),
                              (0.18, 0.13, 0.28, (230, 90, 20)), (0.06, 0.07, 0.20, (250, 210, 80))]:
        d.polygon([(fx + dx * w, ty), (fx + dx * w + fw * w / 2, ty - fh * h),
                   (fx + dx * w + fw * w, ty)], fill=col)
    # smoke, rising to the right of the flames so they stay visible
    for (dx, dy, r) in [(0.60, 0.12, 0.055), (0.66, 0.06, 0.07), (0.73, 0.02, 0.06)]:
        cx, cy = x0 + dx * w, y0 + dy * h + r * w
        d.ellipse([cx - r * w, cy - r * w, cx + r * w, cy + r * w], fill=(110, 108, 105))
    # small car silhouette, right
    cx = x1 - int(w * 0.22)
    d.rounded_rectangle([cx, horizon - int(h * 0.11), cx + int(w * 0.16), horizon - 4],
                        radius=8, fill=(30, 30, 34))
    d.ellipse([cx + 8, horizon - 14, cx + 28, horizon + 4], fill=INK)
    d.ellipse([cx + int(w * 0.09), horizon - 14, cx + int(w * 0.09) + 20, horizon + 4], fill=INK)


def tariff_pic(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(214, 231, 240))
    base = y0 + int(h * 0.82)
    d.rectangle([x0, base, x1, y1], fill=(120, 118, 110))
    # stacked shipping containers, sized to the box
    cols = [(200, 90, 40), (70, 140, 30), (30, 110, 60)]
    cw, ch = int(w * 0.20), int(h * 0.15)
    for row, (r, g, b) in enumerate(cols):
        for i in range(3):
            bx = x0 + int(w * 0.07) + i * (cw + 6)
            by = base - ch - row * (ch + 4)
            d.rectangle([bx, by, bx + cw, by + ch], fill=(r, g, b), outline=INK, width=2)
            for k in range(1, 5):
                d.line([(bx + k * cw // 5, by), (bx + k * cw // 5, by + ch)], fill=INK, width=1)
    # big % badge, inside the box
    bx, by, br = x1 - int(w * 0.20), y0 + int(h * 0.26), int(min(w, h) * 0.20)
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=RED, outline=(255, 255, 255), width=4)
    pct = "%"
    pf = font(SANS, int(br * 1.15))
    pw = d.textlength(pct, font=pf)
    d.text((bx - pw / 2, by - pf.size / 2 - 4), pct, font=pf, fill=(255, 255, 255))
    # short rising arrow, left of the badge
    d.line([(x0 + int(w * 0.08), base - int(h * 0.52)), (x0 + int(w * 0.26), base - int(h * 0.62)),
            (x0 + int(w * 0.40), base - int(h * 0.54))], fill=RED, width=6)


def refinery_pic(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(238, 226, 200))
    base = y0 + int(h * 0.86)
    d.rectangle([x0, base, x1, y1], fill=(96, 90, 82))
    # towers and chimneys, sized to the box
    for (fx, fw, fh) in [(0.08, 0.16, 0.38), (0.30, 0.12, 0.52), (0.78, 0.14, 0.34)]:
        tx = x0 + int(fx * w)
        d.rectangle([tx, base - int(fh * h), tx + int(fw * w), base],
                    fill=(150, 146, 138), outline=INK, width=2)
        d.rectangle([tx + 6, base - int(fh * h) - int(h * 0.07), tx + int(fw * w) - 6,
                     base - int(fh * h)], fill=(120, 116, 108), outline=INK, width=2)
    # flare stack with a small flame, right side
    sx = x1 - int(w * 0.16)
    d.rectangle([sx, base - int(h * 0.58), sx + int(w * 0.05), base],
                fill=(130, 126, 118), outline=INK, width=2)
    d.polygon([(sx - 6, base - int(h * 0.58)), (sx + int(w * 0.025), base - int(h * 0.72)),
               (sx + int(w * 0.05) + 6, base - int(h * 0.58))], fill=(245, 160, 30))
    # black smoke plume, capped inside the box
    for (fx, fy, fr) in [(0.44, 0.30, 0.09), (0.50, 0.20, 0.11), (0.57, 0.11, 0.13)]:
        cx, cy = x0 + fx * w, y0 + fy * h
        d.ellipse([cx - fr * w, cy - fr * w, cx + fr * w, cy + fr * w], fill=(40, 40, 42))
    # oil barrel
    bx = x0 + int(w * 0.60)
    d.rounded_rectangle([bx, base - int(h * 0.16), bx + int(w * 0.13), base],
                        radius=5, fill=(60, 90, 140), outline=INK, width=2)


def space_pic(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(16, 22, 48))
    for (fx, fy) in [(0.08, 0.10), (0.22, 0.24), (0.42, 0.08), (0.60, 0.20), (0.76, 0.10),
                     (0.92, 0.26), (0.14, 0.40), (0.88, 0.44)]:
        d.ellipse([x0 + fx * w - 3, y0 + fy * h - 3, x0 + fx * w + 3, y0 + fy * h + 3],
                  fill=(255, 255, 255))
    # Earth arc along the bottom, clipped by the panel render
    d.ellipse([x0 - int(w * 0.2), y0 + int(h * 0.62), x1 + int(w * 0.2), y0 + int(h * 1.7)],
              fill=(52, 110, 180), outline=(255, 255, 255), width=3)
    d.ellipse([x0 + int(w * 0.22), y0 + int(h * 0.66), x0 + int(w * 0.42), y0 + int(h * 0.82)],
              fill=(70, 150, 90))
    d.ellipse([x0 + int(w * 0.62), y0 + int(h * 0.70), x0 + int(w * 0.76), y0 + int(h * 0.82)],
              fill=(70, 150, 90))
    # station: hub, modules, solar panels, sized to the box
    cx, cy = x0 + w // 2, y0 + int(h * 0.36)
    pw, ph = int(w * 0.28), int(h * 0.16)
    d.rectangle([cx - pw - 8, cy - ph // 2, cx - int(w * 0.09), cy + ph // 2],
                fill=(52, 90, 160), outline=(255, 255, 255), width=2)
    d.rectangle([cx + int(w * 0.09), cy - ph // 2, cx + pw + 8, cy + ph // 2],
                fill=(52, 90, 160), outline=(255, 255, 255), width=2)
    for px in (cx - pw - 8, cx + int(w * 0.09)):
        for k in range(1, 4):
            xx = px + k * pw // 4
            d.line([(xx, cy - ph // 2), (xx, cy + ph // 2)], fill=(200, 220, 255), width=1)
    d.rounded_rectangle([cx - int(w * 0.09), cy - int(h * 0.10), cx + int(w * 0.09), cy + int(h * 0.10)],
                        radius=10, fill=(200, 200, 205), outline=INK, width=2)
    # capsule approaching from the upper right
    kx, ky = cx + int(w * 0.30), cy - int(h * 0.26)
    kw, kh = int(w * 0.13), int(h * 0.10)
    d.rounded_rectangle([kx, ky, kx + kw, ky + kh], radius=8, fill=(230, 230, 235),
                        outline=INK, width=2)
    d.polygon([(kx, ky + 4), (kx - int(w * 0.06), ky + kh // 2), (kx, ky + kh - 4)],
              fill=(180, 60, 40))
    d.line([(cx + int(w * 0.09), cy - 4), (kx, ky + kh // 2)], fill=(255, 255, 255), width=2)


def treaty_pic(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(206, 228, 238))
    # sun, inside the box
    d.ellipse([x1 - int(w * 0.26), y0 + int(h * 0.07), x1 - int(w * 0.10), y0 + int(h * 0.24)],
              fill=(250, 200, 60), outline=INK, width=2)
    # sea and island
    sea = y0 + int(h * 0.68)
    d.rectangle([x0, sea, x1, y1], fill=(70, 140, 180))
    d.ellipse([x0 + int(w * 0.08), sea - int(h * 0.10), x0 + int(w * 0.52), sea + int(h * 0.12)],
              fill=(110, 170, 90), outline=INK, width=2)
    # palm: trunk plus five straight fronds, all inside the box
    px, py = x0 + int(w * 0.28), sea - int(h * 0.06)
    top = (px + int(w * 0.04), py - int(h * 0.30))
    d.line([(px, py), top], fill=(110, 70, 40), width=7)
    for (ex, ey) in [(-0.16, -0.02), (-0.08, -0.10), (0.02, -0.13), (0.12, -0.10), (0.18, -0.02)]:
        d.line([top, (top[0] + int(ex * w), top[1] + int(ey * h))], fill=(50, 120, 60), width=6)
    # document with seal, right side, inside the box
    dw, dh = int(w * 0.40), int(h * 0.42)
    dx, dy = x1 - dw - int(w * 0.06), y0 + int(h * 0.30)
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(255, 253, 247), outline=INK, width=3)
    for k in range(3):
        d.line([(dx + 10, dy + int(dh * (0.22 + k * 0.18))), (dx + dw - 10, dy + int(dh * (0.22 + k * 0.18)))],
               fill=INK, width=3)
    d.ellipse([dx + dw // 2 - 14, dy + dh - 34, dx + dw // 2 + 14, dy + dh - 6],
              fill=RED, outline=(255, 255, 255), width=2)
    # two forearms meeting over the document
    d.rounded_rectangle([dx - int(w * 0.20), dy + int(dh * 0.42), dx + 6, dy + int(dh * 0.62)],
                        radius=9, fill=(222, 178, 140), outline=INK, width=2)
    d.rounded_rectangle([dx + dw - 6, dy + int(dh * 0.42), dx + dw + int(w * 0.20), dy + int(dh * 0.62)],
                        radius=9, fill=(190, 140, 105), outline=INK, width=2)


# ---------------------------------------------------------------- masthead

def masthead(d, top=28):
    d.rectangle([28, top, 996, top + 108], fill=PAPER)
    title = "THE WORLD IN ONE DAY"
    size = 58
    while size > 30 and d.textlength(title, font=font(SERIF, size)) > 968:
        size -= 2
    d.text((28, top), title, font=font(SERIF, size), fill=INK)
    d.line([(28, top + 74), (996, top + 74)], fill=RULE, width=4)
    d.text((28, top + 82), "THURSDAY, 26 NOVEMBER 2026", font=font(SANS, 30), fill=RED)
    right = "FIVE STORIES  ·  FIVE REGIONS"
    w = d.textlength(right, font=font(SANS, 22))
    d.text((996 - w, top + 86), right, font=font(SANS, 22), fill=INK)
    d.line([(28, top + 126), (996, top + 126)], fill=RULE, width=2)
    return top + 140


# ---------------------------------------------------------------- variants

def variant_a(d):
    y = masthead(d)
    gap = 20
    lead = (28, y, 620, 640)
    side = (640, y, 996, 640)
    panel(d, lead, "CAIRO TANKER FIRE: AT LEAST 31 KILLED",
          "Fuel tanker crash on the Ring Road; 21 hurt.", cairo_pic, head_size=32, sub_size=21)
    panel(d, side, "U.S. PROPOSES TARIFFS ON 14 PARTNERS",
          "Proposal only. China, the EU, Japan and India named.", tariff_pic)
    bw = (996 - 28 - 2 * gap) // 3
    row_y = 660
    boxes = [(28 + i * (bw + gap), row_y, 28 + (i + 1) * bw + i * gap, 996) for i in range(3)]
    panel(d, boxes[0], "HOUTHIS CLAIM REFINERY HIT",
          "Ras Tanura. Coalition: drones downed.", refinery_pic, head_size=26, sub_size=19)
    panel(d, boxes[1], "FIRST FOREIGN ASTRONAUT AT TIANGONG",
          "Pakistan's Zeeshan Ali, Shenzhou-24.", space_pic, head_size=26, sub_size=19)
    panel(d, boxes[2], "SOLOMON ISLANDS PACT",
          "With Australia: no foreign base.", treaty_pic, head_size=26, sub_size=19)


def variant_b(d):
    y = masthead(d)
    gap = 20
    top_y, bot_y = y, 996
    mid = (y + 996) // 2 - 10
    panel(d, (28, y, 488, mid), "CAIRO TANKER FIRE: AT LEAST 31 KILLED",
          "Fuel tanker crash on the Ring Road; 21 hurt.", cairo_pic)
    panel(d, (508, y, 996, mid), "U.S. PROPOSES TARIFFS ON 14 PARTNERS",
          "Proposal only. China, the EU, Japan and India named.", tariff_pic)
    bw = (996 - 28 - 2 * gap) // 3
    boxes = [(28 + i * (bw + gap), mid + gap, 28 + (i + 1) * bw + i * gap, 996) for i in range(3)]
    panel(d, boxes[0], "HOUTHIS CLAIM REFINERY HIT",
          "Ras Tanura. Coalition: drones downed.", refinery_pic, head_size=26, sub_size=19)
    panel(d, boxes[1], "FIRST FOREIGN ASTRONAUT AT TIANGONG",
          "Pakistan's Zeeshan Ali, Shenzhou-24.", space_pic, head_size=26, sub_size=19)
    panel(d, boxes[2], "SOLOMON ISLANDS PACT",
          "With Australia: no foreign base.", treaty_pic, head_size=26, sub_size=19)


def variant_c(d):
    y = masthead(d)
    rows = [
        ("1  CAIRO — TANKER FIRE KILLS AT LEAST 31",
         "Fuel tanker crash on the Ring Road; 21 people hurt.", cairo_pic),
        ("2  WASHINGTON — TARIFFS PROPOSED ON 14 PARTNERS",
         "Proposal only. China, the EU, Japan and India named.", tariff_pic),
        ("3  RAS TANURA — HOUTHIS CLAIM REFINERY HIT",
         "Coalition says drones were downed; smoke seen.", refinery_pic),
        ("4  TIANGONG — FIRST FOREIGN ASTRONAUT ABOARD",
         "Pakistan's Zeeshan Ali, on Shenzhou-24.", space_pic),
        ("5  CANBERRA — SOLOMON ISLANDS PACT SIGNED",
         "No foreign military base; Australia is primary partner.", treaty_pic),
    ]
    gap = 16
    rh = (996 - y - 4 * gap) // 5
    for i, (head, sub, pic) in enumerate(rows):
        ry = y + i * (rh + gap)
        box = (28, ry, 996, ry + rh)
        d.rectangle(box, fill=(255, 253, 247), outline=INK, width=3)
        pic_w = 300
        pic_img = render_pic(pic, (pic_w - 6, rh - 6))
        d._image.paste(pic_img, (31, ry + 3))
        d.line([(31 + pic_w, ry), (31 + pic_w, ry + rh)], fill=INK, width=3)
        tx = 31 + pic_w + 18
        max_w = 996 - 12 - tx
        hf, sf = font(SANS, 26), font(SANS_REG, 21)
        head_lines = wrap(d, head, hf, max_w)[:2]
        hy = ry + 16
        for line in head_lines:
            d.text((tx, hy), line, font=hf, fill=INK)
            hy += 32
        for line in wrap(d, sub, sf, max_w)[:2]:
            d.text((tx, hy + 4), line, font=sf, fill=MUTED)
            hy += 26


VARIANTS = {"A": variant_a, "B": variant_b, "C": variant_c}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="B", choices=list(VARIANTS))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    VARIANTS[args.variant](d)
    # Frame the whole page so the composition reads as one front page.
    d.rectangle([12, 12, W - 13, H - 13], outline=INK, width=4)
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print(out, img.size, os.path.getsize(out), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
