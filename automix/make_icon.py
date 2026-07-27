"""Generates the AutoMix app icon (.ico multi-size + .png)."""
from PIL import Image, ImageDraw
import os

BG = (23, 24, 27, 255)
PANEL_RING = (51, 53, 58, 255)
AMBER = (232, 163, 61, 255)
TEAL = (61, 214, 192, 255)
RED = (229, 72, 77, 255)


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = size * 0.04
    d.ellipse([pad, pad, size - pad, size - pad], fill=BG, outline=PANEL_RING,
              width=max(1, int(size * 0.012)))

    bar_count = 5
    bar_colors = [AMBER, AMBER, TEAL, AMBER, RED]
    heights = [0.30, 0.50, 0.72, 0.44, 0.22]
    usable_w = size * 0.62
    usable_h = size * 0.5
    gap = usable_w / bar_count * 0.28
    bar_w = (usable_w - gap * (bar_count - 1)) / bar_count
    start_x = (size - usable_w) / 2
    baseline_y = size * 0.72

    for i in range(bar_count):
        h = usable_h * heights[i]
        x0 = start_x + i * (bar_w + gap)
        x1 = x0 + bar_w
        y1 = baseline_y
        y0 = baseline_y - h
        radius = bar_w * 0.35
        d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=bar_colors[i])

    return img


def main():
    sizes = [16, 32, 48, 64, 128, 256]
    images = [draw_icon(s) for s in sizes]
    images[-1].save("assets/icon.png")
    images[-1].save("assets/automix.ico", sizes=[(s, s) for s in sizes])
    print("Wrote assets/icon.png and assets/automix.ico")


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    main()
