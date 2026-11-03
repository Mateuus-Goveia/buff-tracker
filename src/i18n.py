"""Portuguese and English translations live in assets/lang/<code>.json; use tr("key")."""
import json
import os

from PySide6.QtCore import QLocale

from src.utils import BASE_DIR, get_asset_path

SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
LANGUAGES = ("pt", "en")

_strings = {}
_fallback = {}
_lang = "en"


def _read_lang_file(code):
    path = os.path.join(get_asset_path("lang"), f"{code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def get_setting(key, default=None):
    return _load_settings().get(key, default)


def set_setting(key, value):
    data = _load_settings()
    data[key] = value
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass  # Without write access, the setting is not remembered.


def detect_language():
    saved = get_setting("language")
    if saved in LANGUAGES:
        return saved
    return "pt" if QLocale.system().name().lower().startswith("pt") else "en"


def init():
    set_language(detect_language(), save=False)


def set_language(code, save=True):
    global _strings, _fallback, _lang
    if code not in LANGUAGES:
        code = "en"
    _strings = _read_lang_file(code)
    _fallback = _read_lang_file("en")
    _lang = code
    if save:
        set_setting("language", code)


def current_language():
    return _lang


def tr(key, **kwargs):
    text = _strings.get(key) or _fallback.get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
