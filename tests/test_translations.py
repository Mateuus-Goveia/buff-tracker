import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = PROJECT_ROOT / "assets" / "lang"


def test_supported_language_files_are_valid_and_have_matching_keys():
    translations = {}
    for language in ("pt", "en"):
        path = LANG_DIR / f"{language}.json"
        with path.open(encoding="utf-8") as file:
            translations[language] = json.load(file)

        assert isinstance(translations[language], dict)
        assert all(isinstance(value, str) for value in translations[language].values())

    assert set(translations["pt"]) == set(translations["en"])
