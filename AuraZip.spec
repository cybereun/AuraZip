# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import json

project_root = os.path.abspath(SPECPATH)
sys.path.insert(0, project_root)
from license_bundle import create_license_bundle
from packaging_support import filter_qt_virtual_keyboard

channel = os.environ.get('AURAZIP_BUILD_CHANNEL', 'github')
if channel not in ('github', 'store'):
    raise ValueError('AURAZIP_BUILD_CHANNEL must be github or store')
metadata_dir = os.path.abspath(os.path.join('build', 'channel-metadata', channel))
os.makedirs(metadata_dir, exist_ok=True)
metadata_file = os.path.join(metadata_dir, 'distribution.json')
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump({'channel': channel}, f)

license_notice = create_license_bundle(
    os.path.join(project_root, 'build', 'generated_licenses', 'THIRD_PARTY_NOTICES.txt'),
    project_root=project_root,
)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (metadata_file, 'build_metadata'),
        (license_notice, 'licenses'),
    ],
    hiddenimports=[
        'py7zr',
        'pyzipper',
        'updater',
        'version',
        'dialogs',
        'extra_tools',
        'help_dialog',
        'start_view',
        'archive_view',
        'archive_engine',
        'ribbon',
        'theme',
        'workers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'torch'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Qt Virtual Keyboard is GPL-only in Qt's community edition and AuraZip does
# not use it. Remove its DLL/plugin from all PyInstaller collections.
a.binaries = filter_qt_virtual_keyboard(a.binaries)
a.datas = filter_qt_virtual_keyboard(a.datas)
a.zipfiles = filter_qt_virtual_keyboard(a.zipfiles)
a.pure = filter_qt_virtual_keyboard(a.pure)

# Qt uses the Windows system ICU API. PyInstaller can accidentally pick up
# an incompatible third-party icuuc.dll (for example, from Poppler) from
# the build machine; its versioned exports cannot satisfy Qt6Core.dll.
a.binaries = [entry for entry in a.binaries if entry[0].lower() != 'icuuc.dll']

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AuraZip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AuraZip',
)
