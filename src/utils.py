import os
import sys
import json

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_asset_path(subfolder):
    base_dir = get_base_dir()
    possible_paths = []
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        possible_paths.append(os.path.join(sys._MEIPASS, "assets", subfolder))
    possible_paths.append(os.path.join(base_dir, "assets", subfolder))

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return os.path.join(base_dir, "assets", subfolder)

def get_data_dir():
    """Return bundled read-only app data, or the source-tree data directory."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundled_path = os.path.join(sys._MEIPASS, "data")
        if os.path.isdir(bundled_path):
            return bundled_path
    return os.path.join(get_base_dir(), "data")

BASE_DIR = get_base_dir()
DATA_DIR = get_data_dir()
ICONS_DIR = get_asset_path("icons")
DPAD_DIR = get_asset_path("d-pad")
SOUNDS_DIR = get_asset_path("sounds")
KEYBOARD_DIR = get_asset_path("keyboard")
FONTS_DIR = get_asset_path("fonts")
UI_DIR = get_asset_path("ui")
USER_BUFFS_PATH = os.path.join(BASE_DIR, "buffs.json")

def load_json_data(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def shortcut_asset_name(input_key, modifier):
    """Return the PNG name for a controller shortcut in assets/d-pad, or None."""
    if not input_key or input_key == "none":
        return None
    if modifier and modifier != "none":
        return f"combo_{modifier}_{input_key}_v2_square.png"
    if input_key in ("a", "b", "x", "y"):
        return f"{input_key}_button.png"
    return f"dpad_{input_key}_square.png"


def keyboard_asset_name(key_id):
    if not key_id or key_id == "none":
        return None
    return f"key_{key_id}.png"
