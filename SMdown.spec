"""
PyInstaller spec file for SMdown
Build command: pyinstaller SMdown.spec
"""

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'ffmpeg',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SMdown',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',  # Apple Silicon
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns',
)

app = BUNDLE(
    exe,
    name='SMdown.app',
    icon='assets/icon.icns',
    bundle_identifier='com.smdown.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '12.0',
    },
)
