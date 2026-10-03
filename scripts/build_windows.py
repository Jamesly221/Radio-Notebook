"""Run on Windows after installing requirements-build.txt."""
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed', '--onedir', '--name', 'Radio-Notebook', str(root / 'main.py')], cwd=root, check=True)
out = root / 'dist/Radio-Notebook'
for folder in ('assets', 'data', 'examples', 'docs'):
    shutil.copytree(root / folder, out / folder, dirs_exist_ok=True)
shutil.copy(root / 'scripts/create_desktop_shortcut.ps1', out)
shutil.copy(root / 'README.md', out)
