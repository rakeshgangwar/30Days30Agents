#!/usr/bin/env python3

from setuptools import setup

APP = ['app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',  # We'll create this icon file
    'plist': {
        'CFBundleName': 'Gradient Screenshot',
        'CFBundleDisplayName': 'Gradient Screenshot',
        'CFBundleIdentifier': 'com.gradientscreenshot',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
    'packages': ['PIL', 'PyQt5', 'cv2', 'numpy'],
    'includes': ['sip'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
