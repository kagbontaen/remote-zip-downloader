# Project TODO List & Roadmap

This file tracks planned features and improvements for the Remote ZIP Viewer.

## High Priority

- [x] **Implement Caching for File Lists:** Introduce a time-based in-memory cache (e.g., using `cachetools`) for the `list_entries` function. This will prevent re-fetching and re-processing the ZIP directory on every page load for the same URL, providing a major performance boost.

## Medium Priority

- [x] **Enhance Frontend User Experience (UX):**
    - [x] **Preserve Folder State:** Use browser `localStorage` to remember which folders a user has expanded, restoring the view on subsequent visits.
    - [x] **Add Loading Indicator:** Show a spinner or "Processing..." message after the "Open" button is clicked to provide immediate feedback.
    - [x] **Add Reset Button:** Implement a "Clear" button to easily reset the URL input and file tree.

- [ ] **Add Unit and Integration Tests:**
    - [ ] **Unit Tests:** Create tests for `list_entries` using `pytest` and a mock `RemoteZip` object to validate tree generation logic.
    - [ ] **Integration Tests:** Use Flask's test client to simulate requests to all routes (`/`, `/view`, `/file`, `/preview`, `/image`) to ensure they function correctly.

## Low Priority / Future Ideas

- [ ] **Expand Functionality:**
    - [ ] **File Search/Filter:** Add a client-side search box to filter the file tree in real-time.
    - [ ] **Support for Authenticated URLs:** Allow passing authentication headers (e.g., Bearer tokens) for accessing private ZIP archives.
    - [ ] **Download Selected as ZIP:** Add checkboxes to files/folders and a "Download Selected" button to stream a new ZIP containing only the chosen items.