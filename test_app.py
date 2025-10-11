from unittest.mock import patch, MagicMock, mock_open
from remote_zip_viewer import list_entries

# --- Unit Tests ---

def test_list_entries_structure():
    """
    Unit test for the list_entries function to ensure it builds the correct
    directory tree structure from a flat list of file paths.
    """
    # 1. Setup: Create a mock ZipInfo object
    class MockZipInfo:
        def __init__(self, filename, is_dir=False, file_size=0, compress_size=0):
            self.filename = filename
            self.file_size = file_size
            self.compress_size = compress_size
            self._is_dir = is_dir

        def is_dir(self):
            return self._is_dir

    # 2. Mock the remotezip.RemoteZip class
    mock_infolist = [
        MockZipInfo("root.txt", file_size=100),
        MockZipInfo("folder1/", is_dir=True),
        MockZipInfo("folder1/file1.txt", file_size=200),
        MockZipInfo("folder1/subfolder/file2.py", file_size=300),
    ]

    # Use patch to replace RemoteZip for the duration of this test
    with patch('remote_zip_viewer.RemoteZip') as mock_remote_zip:
        # Configure the mock to return our fake file list
        mock_remote_zip.return_value.__enter__.return_value.infolist.return_value = mock_infolist

        # 3. Execution: Call the function we want to test
        tree = list_entries("http://fake.zip", no_verify=False)

    # 4. Assertions: Check if the output is correct
    assert "root.txt" in tree
    assert tree["root.txt"]["type"] == "file"
    assert tree["root.txt"]["info"]["file_size"] == 100

    assert "folder1" in tree
    assert tree["folder1"]["type"] == "dir"
    
    children = tree["folder1"]["children"]
    assert "file1.txt" in children
    assert children["file1.txt"]["info"]["is_text"] is True
    assert children["file1.txt"]["info"]["file_size"] == 200

    assert "subfolder" in children
    sub_children = children["subfolder"]["children"]
    assert "file2.py" in sub_children
    assert sub_children["file2.py"]["info"]["is_text"] is True
    assert sub_children["file2.py"]["info"]["file_size"] == 300


# --- Integration Tests ---

def test_index_route(client):
    """Test that the index route loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Remote ZIP Viewer" in response.data

def test_view_route_success(client, mocker):
    """Test the /view route with a valid URL, mocking the backend call."""
    # Mock the list_entries function to avoid network calls and return a fake tree
    mock_tree = {"file.txt": {"type": "file", "info": {"filename": "file.txt", "file_size": 123}}}
    mocker.patch('remote_zip_viewer.list_entries', return_value=mock_tree)

    response = client.get("/view?url=http://fake.zip")
    assert response.status_code == 200
    assert b"Contents of" in response.data
    assert b"file.txt" in response.data
    assert b"123 bytes" in response.data

def test_view_route_error(client, mocker):
    """Test the /view route when the backend call fails."""
    # Mock list_entries to raise an exception
    mocker.patch('remote_zip_viewer.list_entries', side_effect=Exception("Network Error"))

    response = client.get("/view?url=http://fake.zip")
    assert response.status_code == 200
    assert b"<strong>Error:</strong> Network Error" in response.data

def test_download_file_route(client, mocker):
    """Test the /file download route."""
    # Mock the streaming function to return predictable data
    mocker.patch('remote_zip_viewer._stream_zip_file', return_value=[b"chunk1", b"chunk2"])

    response = client.get("/file?url=http://fake.zip&name=file.txt")
    
    assert response.status_code == 200
    assert response.data == b"chunk1chunk2"
    assert response.headers["Content-Disposition"] == 'attachment; filename="file.txt"'

def test_preview_file_route(client, mocker):
    """Test the /preview text file route."""
    # We need to mock RemoteZip and its open() method here
    mock_file_content = b"This is a preview."
    mock_open_context = mock_open(read_data=mock_file_content)
    
    mock_rz_instance = MagicMock()
    mock_rz_instance.open.return_value = mock_open_context
    
    mocker.patch('remote_zip_viewer.RemoteZip', return_value=MagicMock(__enter__=MagicMock(return_value=mock_rz_instance)))
    
    response = client.get("/preview?url=http://fake.zip&name=doc.txt")
    assert response.status_code == 200
    assert b"<h3>Preview of doc.txt</h3>" in response.data
    assert b"<pre>This is a preview.</pre>" in response.data