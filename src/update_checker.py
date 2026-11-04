"""Check GitHub releases on demand without downloading or installing updates."""
import re

from packaging.version import InvalidVersion, Version


APP_VERSION = "0.1.0-beta.3"
# Public repository for release checks and the project's first beta.
GITHUB_REPOSITORY = "Mateuus-Goveia/buff-tracker"
REQUEST_TIMEOUT_MS = 5000
_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class UpdateCheckError(Exception):
    """Raised when the GitHub release check cannot be completed."""


def validate_repository(repository):
    if not isinstance(repository, str) or not _REPOSITORY_PATTERN.fullmatch(repository):
        raise UpdateCheckError("The GitHub repository is not configured correctly.")
    return repository


def releases_api_url(repository):
    repository = validate_repository(repository)
    return f"https://api.github.com/repos/{repository}/releases?per_page=100"


def select_latest_release(releases):
    """Select the highest valid semantic version, including prereleases."""
    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get("draft"):
            continue
        tag = release.get("tag_name", "")
        try:
            version = Version(tag.removeprefix("v"))
        except (InvalidVersion, AttributeError):
            continue
        candidates.append((version, release))

    if not candidates:
        raise UpdateCheckError("No published version was found for this project.")
    return max(candidates, key=lambda item: item[0])[1]


def evaluate_releases(releases, current_version):
    try:
        current = Version(current_version.removeprefix("v"))
    except (InvalidVersion, AttributeError) as exc:
        raise UpdateCheckError("The app version is not configured correctly.") from exc

    release = select_latest_release(releases)
    latest_tag = release["tag_name"]
    latest_version = Version(latest_tag.removeprefix("v"))
    return {
        "current_version": str(current),
        "latest_version": str(latest_version),
        "update_available": latest_version > current,
        "release_tag": latest_tag,
        "release_name": release.get("name") or latest_tag,
    }


