# Contributing

Thanks for helping improve Buff Tracker. This guide keeps changes easy to review and safe to release.

## Before you start

- Search existing issues and pull requests before opening a duplicate.
- For a significant feature or behavior change, open an issue first so the scope can be discussed.
- Keep each pull request focused on one problem or feature.
- Do not include `settings.json`, `buffs.json`, personal data, generated build folders, API keys, or other secrets.
- Do not add game files or assets copied from MapleStory or another third party. Follow `ASSET_CREDITS.md` for project asset terms.

## Development setup

Use Python 3.12, 3.13, or 3.14 on Windows for development and packaging.

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m pytest
```

To build the portable Windows app, run `tools/build_windows.ps1`. Distribute the complete generated folder or its ZIP; do not distribute only the `.exe`.

## Branch names

Create a short topic branch from `main`:

- `feat/<short-description>` — user-facing feature
- `fix/<short-description>` — bug fix
- `docs/<short-description>` — documentation
- `test/<short-description>` — tests
- `refactor/<short-description>` — internal restructuring
- `build/<short-description>` or `ci/<short-description>` — build and automation

Use lowercase words separated by hyphens. Do not commit directly to `main`.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```text
<type>(optional-scope): <short imperative summary>
```

Examples:

```text
feat(keyboard): add key rebinding dialog
fix(audio): keep selected alert when editing a buff
docs: explain the portable Windows build
test(updates): cover prerelease ordering
```

Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, and `revert`. Use lowercase, write the summary in English, keep it concise, and omit the trailing period. Add a body when the reason or trade-offs are not clear from the summary. Mark breaking changes with `!` and explain them in the body.

## Pull requests

- Open pull requests against `main` and use the same Conventional Commit format for the title.
- Explain the problem, the approach, and any user-visible behavior change.
- Link related issues with `Closes #123` when applicable.
- Add or update tests for behavior changes and run `python -m pytest` before submitting.
- Update translations, README, changelog, or asset credits when the change requires it.
- Include screenshots for visual changes and describe manual Windows checks.
- Keep unrelated formatting or refactoring out of the change.
- Do not merge while required checks are failing. The maintainer may ask for revisions before merging.

The project uses squash merging so the main branch keeps one Conventional Commit per pull request. Branches are deleted after merge.

## Code and tests

- Keep application code, identifiers, comments, and developer documentation in English. User-facing strings belong in both `assets/lang/en.json` and `assets/lang/pt.json`.
- Match the existing Python style and prefer small, testable functions.
- Tests must not depend on game files, network access, or a contributor's personal settings.
- Do not add dependencies without explaining why they are needed.

## Releases

The maintainer creates version tags in the form `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-beta.N`. Beta releases must be marked as prereleases on GitHub. Update `APP_VERSION`, `CHANGELOG.md`, and the packaged Windows build to match the tag.
