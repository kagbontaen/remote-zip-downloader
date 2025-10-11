# Remote ZIP Viewer

[![Live Demo](https://img.shields.io/badge/Live_Demo-Visit-brightgreen)](https://remote-zip-downloader.onrender.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)

A single-file Flask web application to browse, preview, and download the contents of a remote ZIP archive without needing to download the entire file first.

### [➡️ View the Live Demo Here](https://remote-zip-downloader.onrender.com/)

---

## Features

-   **Efficient Remote Access**: Uses HTTP range requests to fetch only the ZIP file's central directory, saving bandwidth and time.
-   **Interactive Web UI**: Clean and responsive interface built with Pico.css.
-   **File Tree Navigation**: Displays the archive's contents in a collapsible folder structure.
-   **File Previews**:
    -   In-browser preview for text files.
    -   In-browser rendering for common image formats.
-   **Direct Downloads**: Download individual files directly from the archive.
-   **Performance Caching**: Caches the file directory for recently accessed URLs to provide near-instant subsequent loads.
-   **Real-time Search**: Instantly filter the file tree to find specific files or folders.
-   **Persistent State**: Remembers which folders you've expanded for a given URL.

## Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/kagbontaen/remote-zip-downloader.git
    cd remote-zip-downloader
    ```

2.  (Optional but recommended) Create and activate a virtual environment:
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install the required dependencies from the `requirements.txt` file:
    ```sh
    pip install -r requirements.txt
    ```

## Usage (Local Development)

Run the Flask development server:
```sh
python remote_zip_viewer.py
```

Open your web browser and navigate to `http://127.0.0.1:5000`.

## Development & Testing

This project uses `pytest` for unit and integration testing. To run the test suite, execute the following command from the project root directory:

```sh
pytest
```

## Roadmap

See the TODO.md file for a list of planned features and enhancements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.