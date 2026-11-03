from types import SimpleNamespace

from src.keyboard_listener import key_id
from src.options import normalize_id
from src.utils import keyboard_asset_name, shortcut_asset_name


def test_legacy_portuguese_ids_are_normalized():
    assert normalize_id("Botão A") == "a"
    assert normalize_id("Cima") == "up"
    assert normalize_id("L2") == "l2"


def test_unknown_ids_are_preserved():
    assert normalize_id("custom") == "custom"


def test_controller_shortcut_asset_names():
    assert shortcut_asset_name("a", "none") == "a_button.png"
    assert shortcut_asset_name("left", "none") == "dpad_left_square.png"
    assert shortcut_asset_name("a", "l2") == "combo_l2_a_v2_square.png"
    assert shortcut_asset_name("none", "none") is None


def test_keyboard_asset_name():
    assert keyboard_asset_name("f1") == "key_f1.png"
    assert keyboard_asset_name("none") is None


def test_special_keyboard_keys_map_to_asset_ids():
    assert key_id(SimpleNamespace(name="ctrl_l", char=None)) == "ctrl"
    assert key_id(SimpleNamespace(name="page_up", char=None)) == "pup"
    assert key_id(SimpleNamespace(name="up", char=None)) == "arrow_up"
    assert key_id(SimpleNamespace(name="f12", char=None)) == "f12"


def test_character_keys_are_case_insensitive_and_punctuation_is_mapped():
    assert key_id(SimpleNamespace(name=None, char="H")) == "h"
    assert key_id(SimpleNamespace(name=None, char="?")) == "slash"
    assert key_id(SimpleNamespace(name=None, char="+")) == "equals"


def test_unsupported_keyboard_keys_return_none():
    assert key_id(SimpleNamespace(name=None, char=None)) is None
    assert key_id(SimpleNamespace(name=None, char="€")) is None
