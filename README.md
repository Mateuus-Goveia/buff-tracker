# Buff Tracker

An independent desktop utility for tracking game buff timers. It supports controller and keyboard input modes, English and Portuguese interface languages, and reminder sounds. The keyboard listener runs while the app is open and does not suppress key events.

## Run from source

```powershell
python -m pip install -r requirements.txt
python main_desktop.py
```

Choose the input mode and interface language in the Settings tab. In keyboard mode, assign keys with the on-screen keyboard. Each key can be assigned to one buff at a time. Ctrl, Alt, and Shift are treated as individual keys, not as modifiers.

## Privacy

The app does not send usage data or keyboard input over the network. In keyboard mode, it uses a global keyboard listener while the app is running to detect assigned keys; it does not block key presses or save the user's general keystrokes. The listener stops when the app closes. The app opens donation sites only when the user chooses a donation method. After the public GitHub repository is configured, update checks will contact GitHub only when the user clicks **Check for updates**; GitHub can see the request's IP address and the app version from its User-Agent, but the app sends no device ID or personal profile. Buff presets and preferences are stored locally in `buffs.json` and `settings.json`; do not share those files if they contain personal configuration.

## Version and update checks

The app version and public GitHub repository are configured in `src/update_checker.py`. Before publishing a release, update `APP_VERSION` to match its semantic version tag (for example, `0.1.0-beta.1`) and set `GITHUB_REPOSITORY` to `owner/repository`. The app checks published releases, including prereleases, when the user clicks the update button. It only opens the GitHub releases page; users download and replace the app themselves.

## Run the tests

Install the development dependencies, including `pytest`:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Contributing

Contributions are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening an issue or pull request. The project uses Conventional Commits, topic branches, pull requests, and automated tests on Windows.

Please read the [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md). Report security issues privately rather than in a public issue.

## Beta status

This is an early beta. The first release targets Windows and is distributed as a portable folder; automatic updates are not installed by the app. Review the release notes and back up `buffs.json` and `settings.json` before replacing an older copy.

## Build for Windows

On Windows, create a virtual environment, install the development and build dependencies, then run the build script. The script uses a clean DLL search path to avoid picking up unrelated Qt libraries from other applications on the computer.

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\tools\build_windows.ps1
```

The build script creates `dist/Controle de Buffs/` and `dist/Controle-de-Buffs-Windows.zip`. The folder includes a shortcut; distribute the ZIP so users can extract the complete portable app and open it from that shortcut.

## License and assets

The application code and project data are released under the MIT License in `LICENSE`. Asset origins and their separate terms are listed in [`ASSET_CREDITS.md`](ASSET_CREDITS.md). The bundled Press Start 2P font is distributed under the SIL Open Font License 1.1; its license is included alongside the font.

This project is not affiliated with, endorsed by, or associated with Nexon.
