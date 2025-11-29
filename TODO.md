# Project TODO List

## Completed

- [x] Create core web interface with Flask.
- [x] Implement remote ZIP file browsing using `remotezip`.
- [x] Add file preview for text and image files.
- [x] Add individual file download functionality.
- [x] Implement a command-line interface (CLI) for listing and downloading.
- [x] Add support for password-protected ZIP archives.
- [x] Implement robust error handling for missing/incorrect ZIP passwords.
- [x] Improve security by removing credentials from URL parameters.
- [x] Use secure server-side sessions for handling HTTP and ZIP passwords.
- [x] Add a file browser for local files.

## Future Ideas & Enhancements

- [ ] Add a "Download Folder" button to the web UI.
- [ ] Add a "Download All" button to get the entire original ZIP file.
- [ ] Write comprehensive tests for new features (session handling, password errors).
- [ ] Improve UI/UX, possibly with a more modern frontend framework or library.
- [ ] Add support for other archive formats (e.g., `.tar.gz`, `.7z`).
- [ ] Create a Dockerfile for easy containerized deployment.