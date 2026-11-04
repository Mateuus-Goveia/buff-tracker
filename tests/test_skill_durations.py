import json
from pathlib import Path


CLASSES_PATH = Path(__file__).parents[1] / "data" / "classes.json"


def load_skills():
    data = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))
    skills = {}
    for jobs in data.values():
        for job_skills in jobs.values():
            for name, skill in job_skills.items():
                skills.setdefault(name, []).append(skill)
    return skills


def test_every_timed_skill_has_a_duration_for_each_level():
    for name, entries in load_skills().items():
        for entry in entries:
            durations = entry["durations"]
            expected_levels = {str(level) for level in range(1, entry["max_level"] + 1)}
            assert set(durations) == expected_levels, name
            assert all(isinstance(seconds, int) and seconds > 0 for seconds in durations.values()), name


def test_corrected_skill_duration_tables():
    skills = load_skills()
    expected_tables = {
        "Focus": [70, 80, 90, 100, 110, 130, 140, 150, 160, 170, 195, 205, 215, 225, 235, 260, 270, 280, 290, 300],
        "Iron Body": [300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 600],
        "Sword Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Axe Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Blunt Weapon Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Spear Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Polearm Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Bow Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Crossbow Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Claw Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Dagger Booster": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Rage": [150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 300],
        "Iron Will": [150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 300],
        "Magic Armor": [300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 600],
        "Meditation": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Invincible": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Bless": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
        "Soul Arrow": [60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228, 240, 252, 264, 276, 300],
        "Soul Arrow: Crossbow": [60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228, 240, 252, 264, 276, 300],
        "Haste": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 300],
    }
    for name, expected in expected_tables.items():
        for entry in skills[name]:
            actual = [entry["durations"][str(level)] for level in range(1, entry["max_level"] + 1)]
            assert actual == expected, name


def test_untimed_skills_are_not_in_timed_buff_catalog():
    names = load_skills()
    assert "Magic Guard" not in names
    assert "Dark Sight" not in names
