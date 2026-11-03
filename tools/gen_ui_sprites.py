"""Generate fallback theme sprites in assets/ui/theme/.

Each sprite is a 9-slice pixel-art frame (each art pixel = SCALE actual pixels).
To use custom sprites, replace the PNGs with the SAME NAME and border width
(see the SLICES table in assets/ui/theme/theme.qss).

Usage: python tools/gen_ui_sprites.py
"""
import os
import sys
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "ui", "theme")
S = 2  # Size of each art pixel.

# Palette
INK = "#0e0d0a"
GOLD = "#d9a93a"
GOLD_DK = "#7a5a1e"
GOLD_LT = "#f0cf7a"
PANEL = "#23262f"
INSET = "#1a1c23"
GREY = "#5b6275"
BLUE = "#2f5ea8"
BLUE_HI = "#4a7fd0"
BLUE_LO = "#1e3d73"
RED = "#9b2c2c"
RED_HI = "#c04545"
RED_LO = "#6e1f1f"
TAB_ON = "#26324d"
COPPER = "#b8793f"
COPPER_DK = "#7a4c2a"
BODY = "#2b2e38"


def hex_rgba(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def frame(name, fill, rings, size=24, light=None, dark=None, notch=True):
    """Draw a frame with concentric rings (outer to inner) and clipped corners."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    n = len(rings)
    for y in range(size):
        for x in range(size):
            bx, by = x // S, y // S
            bxr, byr = (size - 1 - x) // S, (size - 1 - y) // S
            if notch and min(bx, bxr) == 0 and min(by, byr) == 0:
                continue  # Clipped corner.
            d = min(bx, by, bxr, byr)
            if d < n:
                px[x, y] = hex_rgba(rings[d])
            else:
                c = fill
                if light and by == n and bx >= n and bxr >= n:
                    c = light  # Top highlight.
                elif dark and byr == n and bx >= n and bxr >= n:
                    c = dark   # Bottom shadow.
                px[x, y] = hex_rgba(c)
    img.save(os.path.join(OUT, name))
    return img


def ornament(img, pattern, colors):
    """Draw a mirrored corner ornament (pattern in art pixels) in all four corners."""
    px = img.load()
    n = img.size[0] // S
    for r, row in enumerate(pattern):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            for bx, by in {(c, r), (n - 1 - c, r), (c, n - 1 - r), (n - 1 - c, n - 1 - r)}:
                for dy in range(S):
                    for dx in range(S):
                        px[bx * S + dx, by * S + dy] = hex_rgba(colors[ch])
    return img


def procedural(name, grid, scale, painter):
    """Create a small sprite using painter(x, y) -> hex color or None."""
    img = Image.new("RGBA", (grid * scale, grid * scale), (0, 0, 0, 0))
    px = img.load()
    for y in range(grid):
        for x in range(grid):
            c = painter(x, y)
            if c:
                for dy in range(scale):
                    for dx in range(scale):
                        px[x * scale + dx, y * scale + dy] = hex_rgba(c)
    img.save(os.path.join(OUT, name))
    return img


def blocks(name, size, color, cells, base=None):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0)) if base is None else base.copy()
    px = img.load()
    for cx, cy in cells:
        for dy in range(S):
            for dx in range(S):
                px[cx * S + dx, cy * S + dy] = hex_rgba(color)
    img.save(os.path.join(OUT, name))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)

    # --- Panels (6 px border) ---
    frame("panel.png", PANEL, [INK, GOLD, GOLD_DK])
    # Buff card: copper frame with gold corner plates (8 px border).
    card = frame("card.png", "#262830", [INK, COPPER, COPPER_DK, INK], size=32)
    ornament(card, [".111", "1321", "12..", "1..."], {"1": GOLD, "2": GOLD_DK, "3": INK})
    card.save(os.path.join(OUT, "card.png"))
    # Tab content panel: thin gold line with corner ornaments (8 px border).
    content = frame("content.png", BODY, [INK, GOLD_DK, "#1c1d23", "#4a3b1e"], size=32)
    ornament(content, [".11.", "1.2.", "12..", "1..."], {"1": "#b88a2e", "2": "#4a3b1e"})
    content.save(os.path.join(OUT, "content.png"))
    # Icon frame (6 px border).
    frame("icon_frame.png", "#15161b", [INK, GOLD, GOLD_DK])
    # --- Inset areas (4 px border) ---
    frame("inset.png", INSET, [INK, "#343846"], size=16)

    # --- Blue buttons (6 px border) ---
    frame("button.png", BLUE, [INK, GOLD, GOLD_DK], light=BLUE_HI, dark=BLUE_LO)
    frame("button_hover.png", BLUE_HI, [INK, GOLD_LT, GOLD], light="#6b9be0", dark=BLUE)
    frame("button_pressed.png", BLUE_LO, [INK, GOLD_DK, "#4d3a10"], light="#183462", dark=BLUE_LO)
    frame("button_disabled.png", "#3a3d48", [INK, GREY, "#3a3d48"])
    # --- Danger button (6 px border) ---
    frame("danger.png", RED, [INK, GOLD_DK, "#4d3a10"], light=RED_HI, dark=RED_LO)
    frame("danger_hover.png", RED_HI, [INK, GOLD, GOLD_DK], light="#d86a6a", dark=RED)
    frame("danger_pressed.png", RED_LO, [INK, GOLD_DK, "#4d3a10"], dark=RED_LO)

    # --- Blue combo boxes (4 px border) ---
    frame("combo.png", BLUE, [INK, GOLD], size=16, light=BLUE_HI, dark=BLUE_LO)
    frame("combo_hover.png", BLUE_HI, [INK, GOLD_LT], size=16, light="#6b9be0", dark=BLUE)

    # --- Tabs (6 px border) ---
    frame("tab.png", INSET, [INK, GREY, "#2b2e38"])
    frame("tab_hover.png", "#232733", [INK, "#7b8499", "#2b2e38"])
    frame("tab_active.png", TAB_ON, [INK, GOLD, GOLD_DK])

    # --- Scrollbar (4 px border) ---
    frame("scroll_handle.png", GOLD_DK, [INK, GOLD], size=16)

    # --- 20x20 checkbox ---
    box = frame("check_off.png", "#15171d", [INK, GOLD], size=20, notch=False)
    check = [(2, 4), (3, 5), (4, 6), (5, 5), (6, 4), (7, 3),
             (2, 5), (3, 6), (4, 7), (5, 6), (6, 5), (7, 4)]
    blocks("check_on.png", 20, "#f4efe0", check, base=box)

    # --- Combo-box arrow (14x8) ---
    arrow = Image.new("RGBA", (14, 8), (0, 0, 0, 0))
    px = arrow.load()
    for row, width in enumerate([7, 5, 3, 1]):
        x0 = (7 - width) // 2
        for cx in range(x0, x0 + width):
            for dy in range(S):
                for dx in range(S):
                    px[cx * S + dx, row * S + dy] = hex_rgba("#f4efe0")
    arrow.save(os.path.join(OUT, "arrow_down.png"))
    # --- Logo (32x32 gold leaf), clock and gear icons (24x24) ---
    import math

    def leaf(x, y):
        dx, dy = x - 7.5, 7.5 - y
        u, v = (dx + dy) / math.sqrt(2), (dx - dy) / math.sqrt(2)
        def inside(u, v):
            return abs(u) <= 6.6 and abs(v) <= 3.6 * (1 - (u / 6.6) ** 2) ** 0.8
        def pt(xx, yy):
            dx2, dy2 = xx - 7.5, 7.5 - yy
            return inside((dx2 + dy2) / math.sqrt(2), (dx2 - dy2) / math.sqrt(2))
        stem = abs(v) < 0.6 and -9.2 <= u < -6.6
        if not (inside(u, v) or stem):
            return None
        edge = stem or any(not pt(x + ox, y + oy) for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            return "#6b4410"
        if abs(v) < 0.6:
            return "#b07a1c"
        return "#fbe08a" if v > 0 else "#e8b93a"
    leaf_img = procedural("logo.png", 16, 2, leaf)

    # --- App icon (window/taskbar/.exe): leaf on a gold frame, 256x256 + .ico ---
    base = frame("app_icon.png", "#15161b", [INK, GOLD, GOLD_DK], size=64)
    base.alpha_composite(leaf_img, (16, 16))
    big = base.resize((256, 256), Image.NEAREST)
    big.save(os.path.join(OUT, "app_icon.png"))
    big.save(os.path.join(OUT, "app_icon.ico"),
             sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    # --- Coffee cup for the donate button (16x16 art pixels, 32x32 px) ---
    mug = [
        "................",
        "....s...s.......",
        ".....s...s......",
        "................",
        "..oooooooooo....",
        "..ohhggggggoooo.",
        "..ohhggggggo..o.",
        "..ohhggggggo..o.",
        "..ohhggggggoooo.",
        "..ohgggggddo....",
        "...ogggggddo....",
        "....oddddddo....",
        ".....oooooo.....",
        "..oooooooooooo..",
        "................",
        "................",
    ]
    mug_colors = {"o": "#4a2f0c", "h": "#f6d46b", "g": "#e9b53a", "d": "#b57d1c", "s": "#f4efe0"}
    assert all(len(r) == 16 for r in mug) and len(mug) == 16
    procedural("coffee.png", 16, 2, lambda x, y: mug_colors.get(mug[y][x]))

    def clock(x, y):
        dx, dy = x - 5.5, y - 5.5
        r = math.hypot(dx, dy)
        if r > 5.6:
            return None
        if r > 4.5:
            return "#f0e6c8"
        if (x == 5 or x == 6) and 2 <= y <= 5:
            return "#ffffff"
        if y in (5, 6) and 5 <= x <= 8:
            return "#ffffff"
        return "#5a79b8"
    procedural("tab_timer.png", 12, 2, clock)

    def gear(x, y):
        dx, dy = x - 5.5, y - 5.5
        r, ang = math.hypot(dx, dy), math.atan2(dy, dx)
        outer = 5.7 if math.cos(8 * ang) > 0 else 4.5
        if r > outer or r < 1.9:
            return None
        return "#aab2c5"
    procedural("tab_config.png", 12, 2, gear)

    print(f"Sprites generated in {OUT}")


if __name__ == "__main__":
    sys.exit(main())
