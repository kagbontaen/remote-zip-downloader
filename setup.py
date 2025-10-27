from setuptools import setup
import re
from pathlib import Path

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