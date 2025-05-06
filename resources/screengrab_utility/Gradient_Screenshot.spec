# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder', 'cv2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
plist = {
    'CFBundleName': 'Gradient Screenshot',
    'CFBundleDisplayName': 'Gradient Screenshot',
    'CFBundleIdentifier': 'com.gradientscreenshot',
    'CFBundleVersion': '1.0.0',
    'CFBundleShortVersionString': '1.0.0',
    'NSHumanReadableCopyright': 'Copyright 2025',
    'NSHighResolutionCapable': True,
    'NSRequiresAquaSystemAppearance': False,  # Support dark mode
}

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Gradient Screenshot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Gradient Screenshot',
)
app = BUNDLE(
    coll,
    name='Gradient Screenshot.app',
    icon='icon.icns',  
    bundle_identifier='com.gradientscreenshot',
    info_plist=plist,
)
