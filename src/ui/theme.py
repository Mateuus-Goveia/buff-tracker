"""Load the pixel font and build the stylesheet (QSS) from assets/ui/theme sprites."""
import os
from pathlib import Path

from PySide6.QtGui import QFontDatabase

from src.utils import FONTS_DIR, UI_DIR

THEME_DIR = Path(UI_DIR) / "theme"
FALLBACK_FONT = "Segoe UI"

# Sizes in pixels. Adjust these for the selected pixel font.
FONT_SIZES = {"@FS_SM@": 11, "@FS@": 13, "@FS_LG@": 15, "@FS_XL@": 20}


def load_pixel_font():
    """Register fonts from assets/fonts and return the family name to use."""
    if not os.path.isdir(FONTS_DIR):
        return FALLBACK_FONT
    files = sorted(f for f in os.listdir(FONTS_DIR) if f.lower().endswith((".ttf", ".otf")))
    # Prefer pixel_font.ttf.
    files.sort(key=lambda f: f.lower() != "pixel_font.ttf")
    for name in files:
        font_id = QFontDatabase.addApplicationFont(os.path.join(FONTS_DIR, name))
        families = QFontDatabase.applicationFontFamilies(font_id) if font_id != -1 else []
        if families:
            return families[0]
    return FALLBACK_FONT


def build_stylesheet(font_family):
    qss_path = THEME_DIR / "theme.qss"
    if not qss_path.exists():
        print(f"WARNING: theme not found at {qss_path}")
        return ""
    qss = qss_path.read_text(encoding="utf-8")
    qss = qss.replace("@UI@", THEME_DIR.as_posix()).replace("@FONT@", font_family)
    for token, size in FONT_SIZES.items():
        qss = qss.replace(token, str(size))
    return qss


def theme_asset(name):
    """Return a sprite path, preferring assets/ui/<name> over the fallback in assets/ui/theme/."""
    own = Path(UI_DIR) / name
    return str(own if own.exists() else THEME_DIR / name)
