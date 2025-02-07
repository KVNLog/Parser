# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['parser.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['undetected_chromedriver', 'undetected_chromedriver.cdp', 'undetected_chromedriver.devtool', 'undetected_chromedriver.dprocess', 'undetected_chromedriver.options', 'undetected_chromedriver.patcher', 'undetected_chromedriver.reactor', 'undetected_chromedriver.webelement'],
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
    a.binaries,
    a.datas,
    [],
    name='parser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
