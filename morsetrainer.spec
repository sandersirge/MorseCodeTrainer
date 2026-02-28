# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Morse Code Trainer."""
import sys
from pathlib import Path

block_cipher = None

# Paths
PROJECT_ROOT = Path(SPECPATH)
SRC_PATH = PROJECT_ROOT / 'src'
RESOURCES_PATH = SRC_PATH / 'main' / 'resources'
ICONS_PATH = PROJECT_ROOT / 'resources' / 'icons'

# Determine icon based on platform
if sys.platform == 'win32':
    icon_file = str(ICONS_PATH / 'morsetrainer.ico')
elif sys.platform == 'darwin':
    icon_file = str(ICONS_PATH / 'morsetrainer.icns')
else:
    icon_file = None

# Collect data files (resources) — skip directories that are empty or missing
_resource_dirs = ['letters', 'numbers', 'symbols', 'testing', 'translation']
datas = []
for _name in _resource_dirs:
    _dir = RESOURCES_PATH / _name
    if _dir.is_dir() and any(_dir.iterdir()):
        datas.append((str(_dir), f'src/main/resources/{_name}'))

a = Analysis(
    ['run.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'customtkinter',
        'ttkbootstrap',
        'pygame',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MorseCodeTrainer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MorseCodeTrainer',
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Morse Code Trainer.app',
        icon=icon_file,
        bundle_identifier='com.sandersirge.morsetrainer',
        info_plist={
            'CFBundleName': 'Morse Code Trainer',
            'CFBundleDisplayName': 'Morse Code Trainer',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
