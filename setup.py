from setuptools import setup
import re
from pathlib import Path

# Import py2exe. It's fine if this fails for users who aren't building the exe.
try:
    import py2exe
except ImportError:
    py2exe = None

# --- Helper functions ---
def get_version():
    """Extracts the version number from the main application file."""
    with open("remote_zip_viewer.py", "r") as f:
        match = re.search(r'__version__\s*=\s*"(.*?)"', f.read())
        if match:
            return match.group(1)
    raise RuntimeError("Version string not found.")

def get_long_description():
    """Reads the README.md file for the long description."""
    return Path("README.md").read_text(encoding="utf-8")

# --- Setup configuration ---
setup(
    name="remote-zip-viewer",
    version=get_version(),
    author="Kagbontaen",
    description="A web app to browse, preview, and download files from a remote ZIP archive without downloading the whole file.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/kagbontaen/remote-zip-downloader",
    license="MIT",
    py_modules=["remote_zip_viewer"],
    # --- py2exe configuration ---
    console=[{
        "script": "remote_zip_viewer.py",
        "icon_resources": [(1, "icon.ico")] # Assumes icon.ico is in the root
    }],
    options={
        'py2exe': {
            'bundle_files': 1, # Creates a single-file executable
            'compressed': True,
        }
    },
    zipfile="Library.zip", # Required for single-file bundle
    # --- Standard packaging configuration ---
    install_requires=[
        "Flask",
        "remotezip",
        "cachetools",
        "waitress",
    ],
    entry_points={
        "console_scripts": [
            "remote-zip-viewer=remote_zip_viewer:main",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)