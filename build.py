import PyInstaller.__main__
import os
import shutil
from pathlib import Path

# --- Configuration ---
APP_NAME = "RemoteZipViewer"
ENTRY_POINT = "remote_zip_viewer.py"
ICON_PATH = "icon.ico" # Optional: path to an icon file

def build():
    """Runs PyInstaller to build the executable."""
    build_folder = Path("build")
    dist_folder = Path("dist")

    # Clean up previous builds
    if build_folder.exists():
        print("Cleaning up 'build' folder...")
        shutil.rmtree(build_folder)
    if dist_folder.exists():
        print("Cleaning up 'dist' folder...")
        shutil.rmtree(dist_folder)

    pyinstaller_args = [
        '--name=%s' % APP_NAME,
        '--onefile',
        '--console', # Use '--console' for a visible command window
        ENTRY_POINT,
    ]

    if os.path.exists(ICON_PATH):
        print(f"Using icon: {ICON_PATH}")
        pyinstaller_args.append('--icon=%s' % ICON_PATH)

    print(f"Running PyInstaller with args: {pyinstaller_args}")
    PyInstaller.__main__.run(pyinstaller_args)
    print("\nBuild complete. Executable is in the 'dist' folder.")

if __name__ == "__main__":
    build()
