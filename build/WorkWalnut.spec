# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path


PROJECT_ROOT = Path(SPECPATH).resolve().parent
APP_DIR = PROJECT_ROOT / "app"
IS_MACOS = sys.platform == "darwin"

a = Analysis(
    [str(APP_DIR / "wallnut_pet.py")],
    pathex=[str(APP_DIR)],
    binaries=[],
    datas=[
        (str(APP_DIR / "assets"), "assets"),
        (str(APP_DIR / "config.json"), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["numpy", "matplotlib", "pandas", "scipy"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="工作坚果" if IS_MACOS else "启动工作坚果",
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
)

collection = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="工作坚果",
)

if IS_MACOS:
    app = BUNDLE(
        collection,
        name="工作坚果.app",
        bundle_identifier="io.github.dazhanglang.work-walnut",
        info_plist={
            "CFBundleDisplayName": "工作坚果",
            "CFBundleName": "工作坚果",
            "NSHighResolutionCapable": True,
            "LSUIElement": True,
        },
    )
