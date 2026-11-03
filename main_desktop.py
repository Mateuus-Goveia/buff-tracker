import sys

from src.app import AppBuffTracker

if __name__ == "__main__":
    if sys.platform == "win32":
        # Use a dedicated ID so Windows shows the app icon instead of the Python icon.
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("controle.buffs.app")
        except Exception:
            pass
    app = AppBuffTracker()
    sys.exit(app.run())
