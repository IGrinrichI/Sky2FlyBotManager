# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
import os


# Собираем все скомпилированные .pyd файлы из папки проекта
def collect_pyd(dir_name):
    pyds = []
    for root, dirs, files in os.walk(dir_name):
        for f in files:
            if f.endswith(".pyd"):
                # Сохраняем структуру папок (файл, путь_внутри_exe)
                rel_path = os.path.relpath(root, ".")
                pyds.append((os.path.join(root, f), rel_path))
    return pyds


binaries = [(f, '.') for f in os.listdir(".") if f.endswith(".pyd")] + collect_pyd('../Clicker')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('images', 'images'),
        ('private_key.pem', '.'),
        ('*.kv', '.'),
        ('Sky2FlyBotManagerAutoUpdater.bat', '.'),
        ('gui_logger_script.js', '.'),
    ],
    hiddenimports=['win32api', 'win32con', 'win32gui', 'win32ui',
                   'kivy', 'kivy.core.window', 'kivy.graphics.shader', 'requests', 'winsound', 'win32process', 'frida'],
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
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='Sky2FlyBotManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/icon.png'
)
