from src.models import BuffItem


def test_duration_is_stored_as_integer():
    buff = BuffItem("buff-1", "Haste", "120", "haste.png", "bell1")

    assert buff.duration == 120


def test_to_dict_preserves_buff_configuration():
    buff = BuffItem(
        "buff-2", "Haste (Lv. 10)", 180, "haste.png", "bell2",
        input_key="a", modifier="l2", raw_skill_name="Haste", keyboard_key="h",
    )

    assert buff.to_dict() == {
        "id": "buff-2",
        "name": "Haste (Lv. 10)",
        "duration": 180,
        "icon_file": "haste.png",
        "sound_file": "bell2",
        "input_key": "a",
        "modifier": "l2",
        "is_consumable": False,
        "raw_skill_name": "Haste",
        "keyboard_key": "h",
    }


def test_new_buff_starts_inactive():
    buff = BuffItem("buff-3", "Bless", 60, None, "bell1")

    assert not buff.is_active
    assert buff.remaining == 0
    assert not buff.sound_played_warning
