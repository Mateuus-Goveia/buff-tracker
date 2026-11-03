# Buff Tracker

An independent desktop companion for tracking game buff timers. It supports controller and keyboard input modes, English and Portuguese interface languages, and selectable reminder sounds. The keyboard listener detects assigned keys while the app is open and does not suppress key events.

## Download and run on Windows

Download the latest **Windows portable ZIP** from the [Releases page](https://github.com/Mateuus-Goveia/buff-tracker/releases). Extract the complete ZIP and open **Controle de Buffs.lnk** from the extracted folder. Keep the shortcut, executable, and bundled files together. **Python does not need to be installed.**

This is an early beta. Back up `buffs.json` and `settings.json` before replacing an older copy.

## Features

- Track MapleStory Classic buff and consumable timers.
- Choose joystick/controller or keyboard shortcuts. In keyboard mode, assign each key to at most one buff. Ctrl, Alt, and Shift are treated as individual keys, not as modifiers.
- Use the interface in English or Portuguese.
- Choose from 22 reminder sounds.
- Support the project through PayPal or Pix from inside the app.

## Privacy

The app does not send usage data or keyboard input over the network. In keyboard mode, it uses a global keyboard listener while open to detect assigned keys; it does not block key presses or save general keystrokes. The listener stops when the app closes. The app opens donation sites only when the user chooses a donation method. Update checks contact GitHub only when the user clicks **Check for updates**; GitHub can see the request's IP address and app version from its User-Agent. The app sends no device ID or personal profile. Buff presets and preferences are stored locally in `buffs.json` and `settings.json`; do not share those files if they contain personal configuration.

## Updates

Click **Check for updates** in the app to check for published GitHub releases, including betas. The app opens the Releases page for manual download; it does not download or install updates automatically. If no release has been published yet, the check will report that no published version is available.

## Run from source

For development, install the dependencies and start the app:

```powershell
python -m pip install -r requirements.txt
python main_desktop.py
```

## Tests

Install the development dependencies, including `pytest`, and run the unit tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Contributing

Contributions are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening an issue or pull request. The project uses Conventional Commits, topic branches, pull requests, and automated tests on Windows. Please also read the [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md). Report security issues privately rather than in a public issue.

## Build for Windows

Use Python 3.12, 3.13, or 3.14 on Windows to build the portable app. Create a virtual environment, install the development and build dependencies, then run the build script. It uses a clean DLL search path to avoid picking up unrelated Qt libraries from other applications.

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\tools\build_windows.ps1
```

The script creates `dist/Controle de Buffs/` and `dist/Controle-de-Buffs-Windows.zip`. Distribute the complete ZIP; it contains the shortcut and all files needed to run the app.

## License and assets

The application code and project data are released under the MIT License in `LICENSE`. Asset origins and their separate terms are listed in [`ASSET_CREDITS.md`](ASSET_CREDITS.md). The bundled Press Start 2P font is distributed under the SIL Open Font License 1.1; its license is included alongside the font.

This project is not affiliated with, endorsed by, or associated with Nexon.
