# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('data', 'data'), ('LICENSE', '.'), ('ASSET_CREDITS.md', '.')],
    hiddenimports=['pynput.keyboard._win32', 'pynput._util.win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Controle de Buffs',
    icon='assets/ui/theme/app_icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Controle de Buffs',
)
