# Remote ZIP Viewer

[![Live Demo](https://img.shields.io/badge/Live_Demo-Visit-brightgreen)](https://remote-zip-downloader.onrender.com/)
[![CI/CD](https://github.com/kagbontaen/remote-zip-downloader/actions/workflows/python-app.yml/badge.svg)](https://github.com/kagbontaen/remote-zip-downloader/actions/workflows/python-app.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

A web app and command-line tool to browse, preview, and download files from a remote ZIP archive without downloading the whole file. This is particularly useful for inspecting large ZIP files stored on a web server.

This project was initially created as a modern, cross-platform replacement for the `pzb` command-line tool, providing both a rich web UI and a compatible CLI for scripting purposes.

!Screenshot of Remote ZIP Viewer

### [➡️ View the Live Demo Here](https://remote-zip-downloader.onrender.com/)

## Features

### Web Interface
- **Remote Browsing**: Navigate the directory structure of a remote ZIP file in your browser.
- **No Full Download Required**: Uses HTTP range requests to fetch only the necessary parts of the ZIP file.
- **File Preview**: Preview text and image files directly in the browser.
- **Download Individual Files**: Download specific files from the archive.
- **Secure Credential Handling**: Uses server-side sessions to manage HTTP and ZIP passwords, keeping them out of URL history.
- **Password Support**:
    - Supports HTTP Basic Authentication for accessing the remote file.
    - Supports password-protected (encrypted) ZIP archives.
- **User-Friendly UI**:
    - Collapsible folder tree to easily navigate the archive.
    - Search functionality to filter files and folders.
    - Remembers which folders were expanded for a given URL.
- **Local File Support**: Can also be used to browse ZIP files from your local disk via a native file dialog.

### Command-Line Interface (CLI)
- **List Files**: List the contents of a remote archive, with options to filter by path.
- **Download Files**: Download individual files from the command line.
- **Download Folders**: Recursively download all contents of a folder within the archive.
- **Stream to Console**: Stream a file's content directly to `stdout`.
- **Authentication**: Supports HTTP auth and SSL verification options.

### Core Engine
- **Portable**: Automatically installs missing dependencies on first run.
- **Performance Caching**: In-memory cache for file lists reduces redundant requests.
- **Robust Connectivity**: Automatically retries with SSL verification disabled on certificate errors.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/kagbontaen/remote-zip-downloader.git
    cd remote-zip-downloader
    ```

2.  (Optional but recommended) Create and activate a virtual environment:
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python -m venv venv
    source venv/bin/activate
    ```

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Starting the Web UI
Run the script without any arguments to start the web server. It will automatically install any missing packages.
```bash
python remote_zip_viewer.py
```
The application will automatically open in your default web browser.

### Using the Command-Line Interface
The CLI is powerful for scripting and quick actions.

**Syntax:**
`python remote_zip_viewer.py <url> [options]`

- **List all files in an archive:**
  ```bash
  python remote_zip_viewer.py http://example.com/archive.zip -l
  ```

- **Download a single file:**
  ```bash
  python remote_zip_viewer.py http://example.com/archive.zip -g path/to/file.txt -o ./downloads
  ```

- **Download an entire directory:**
  ```bash
  python remote_zip_viewer.py http://example.com/archive.zip -g path/to/folder/ --directory -o ./downloads
  ```

## Building the Executable

You can build a single-file executable for Windows using the provided `build.py` script, which utilizes PyInstaller.

```bash
python build.py
```
The executable will be located in the `dist` folder.

## Development & Testing

This project uses `pytest` for testing. To run the test suite, execute the following command from the project root directory:

```bash
pytest
```

## Roadmap

See the TODO.md file for a list of planned features and enhancements.

## License

This project is licensed under the MIT License.