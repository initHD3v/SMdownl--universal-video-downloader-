"""
PyInstaller spec file for SMdown
Build command: pyinstaller SMdown.spec

NOTE: Using ONEDIR mode for faster startup on macOS
"""

# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.datastruct import Tree
from PyInstaller.building.api import PYZ, EXE, COLLECT, PKG
from PyInstaller.building.osx import BUNDLE

block_cipher = None

# Get absolute path to project root (spec file directory)
spec_dir = os.getcwd()
assets_dir = os.path.join(spec_dir, 'assets')

a = Analysis(
    ['app/main.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[(assets_dir, 'assets')],
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'yt_dlp.extractor.extractors',
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtNetwork',
        'ffmpeg',
        'certifi',
        'requests',
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

# ONEDIR MODE BUNDLE
app = BUNDLE(
    exe,
    name='SMdown.app',
    icon=os.path.join(assets_dir, 'logo.png'),
    bundle_identifier='com.smdown.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '12.0',
        'LSBackgroundOnly': 'False',  # Show in dock
        'NSSupportsAutomaticGraphicsSwitching': 'True',
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True,
        },
    },
    entitlements_file='entitlements.plist',
)
