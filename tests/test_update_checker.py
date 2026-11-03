import pytest

from src.update_checker import (
    UpdateCheckError,
    evaluate_releases,
    releases_api_url,
    select_latest_release,
    validate_repository,
)


def test_repository_must_be_owner_and_repository():
    assert validate_repository("sample/project") == "sample/project"
    assert releases_api_url("sample/project") == "https://api.github.com/repos/sample/project/releases?per_page=100"
    with pytest.raises(UpdateCheckError):
        validate_repository("https://github.com/sample/project")


def test_select_latest_release_includes_prereleases_and_skips_drafts():
    releases = [
        {"tag_name": "v1.0.0", "draft": False},
        {"tag_name": "v1.1.0-beta.2", "draft": False},
        {"tag_name": "v9.0.0", "draft": True},
        {"tag_name": "not-a-version", "draft": False},
    ]

    assert select_latest_release(releases)["tag_name"] == "v1.1.0-beta.2"


def test_newer_release_is_detected():
    releases = [{"tag_name": "v0.2.0", "name": "Beta 2", "draft": False}]
    result = evaluate_releases(releases, "0.1.0b1")

    assert result["update_available"] is True
    assert result["latest_version"] == "0.2.0"


def test_matching_release_is_not_reported_as_an_update():
    releases = [{"tag_name": "v0.1.0-beta.1", "draft": False}]
    result = evaluate_releases(releases, "0.1.0b1")

    assert result["update_available"] is False
