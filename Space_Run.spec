# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],  # Use your launcher script
    pathex=[],
    binaries=[],
    datas=[
        ('high_score.json', '.'),
        ('constants.py', '.'),
        ('main.py', '.'),
        ('obstacles.py', '.'),
        ('player.py', '.'),
        ('utils.py', '.'),
        ('visuals.py', '.')
    ],
    hiddenimports=['pygame'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Space Run',
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
    name='Space Run',
)

app = BUNDLE(
    coll,
    name='Space Run.app',
    icon=None,
    bundle_identifier='com.yourname.spacerun',
    info_plist={
        'NSHighResolutionCapable': True,
        'NSQuitAlwaysKeepsWindows': False,
    }
) 