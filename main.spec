# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main.py'],
<<<<<<< HEAD
             pathex=['C:\\Users\\SteveHerbert\\Documents\\YouTubeToCSV'],
=======
             pathex=['/Users/steve/github/YouTubeToCSV'],
>>>>>>> 57d619a5eccbc604675dda378f351f2407c7fe82
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
<<<<<<< HEAD
          [],
          exclude_binaries=True,
=======
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
>>>>>>> 57d619a5eccbc604675dda378f351f2407c7fe82
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
<<<<<<< HEAD
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
=======
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
>>>>>>> 57d619a5eccbc604675dda378f351f2407c7fe82
