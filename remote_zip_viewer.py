def _ensure_dependencies():
    """
    Checks for required packages and prompts for installation if they are missing.
    This makes the script more portable by handling its own dependencies.
    """
    import sys
    import subprocess
    
    # List of required packages and their corresponding import names
    required_packages = {
        'Flask': 'flask',
        'remotezip': 'remotezip',
        'cachetools': 'cachetools',
        'waitress': 'waitress'
    }
    
    missing_packages = []
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
            
    if missing_packages:
        print(f"The following required packages are missing: {', '.join(missing_packages)}")
        print("Attempting to install them now...")
        python_executable = sys.executable
        subprocess.check_call([python_executable, "-m", "pip", "install", *missing_packages])
        sys.exit("\nDependencies installed successfully. Please run the script again.")

_ensure_dependencies()

from flask import Flask, request, render_template_string, Response, redirect, url_for, abort
from remotezip import RemoteZip
from pathlib import Path
import mimetypes
from functools import wraps
from cachetools import cached, TTLCache

app = Flask(__name__)
__version__ = "0.7.1"
app.jinja_env.globals['version'] = __version__

INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Remote ZIP Viewer</title>
<link rel="icon" href="http://kagbontaen.ucoz.lv/Project1.ico">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
<style>
  :root { --pico-font-size: 100%; }
  main { padding-top: 2rem; }
  .error { color: var(--pico-color-red-500); }
  .tree ul { list-style-type: none; padding-left: 1.5rem; }
  .tree li { padding: 0.2rem 0; }
  .tree-item { display: flex; align-items: center; gap: 0.5rem; }
  .tree-item-label { flex-grow: 1; }
  .tree-item-size { color: var(--pico-secondary); font-size: 0.9em; min-width: 100px; text-align: right; }
  .tree-item-actions { display: flex; justify-content: flex-end; gap: 0.5rem; min-width: 380px; }
  .tree-item-actions a[role="button"] { width: 120px; margin: 0; padding: 0.5rem 0; text-align: center; white-space: nowrap; }
  .folder > .tree-item { cursor: pointer; font-weight: bold; }
  .folder > ul { display: none; }
  .folder.expanded > ul { display: block; }
  .folder > .tree-item .icon-open, .folder.expanded > .tree-item .icon-closed { display: none; }
  .folder.expanded > .tree-item .icon-open { display: inline-block; }
  .icon { width: 1em; height: 1em; vertical-align: -0.125em; }
  .hidden { display: none; }
  mark { background-color: var(--pico-color-yellow-200); padding: 0; }
</style>
</head>
<body>
<main class="container">
  <h2 style="margin-bottom: 1.5rem;">Remote ZIP Viewer</h2>
  <form action="{{ url_for('view') }}" method="get">
    <label for="url">Remote ZIP URL</label>
    <input type="search" id="url" name="url" value="{{ url or '' }}" placeholder="https://example.com/archive.zip" required>
    <div id="auth-fields" class="{% if not user %}hidden{% endif %}">
      <div class="grid">
        <div>
          <label for="user">Username (optional)</label>
          <input type="text" id="user" name="user" value="{{ user or '' }}" placeholder=" ">
        </div>
        <div>
          <label for="password">Password</label>
          <input type="password" id="password" name="password" value="{{ password or '' }}" placeholder=" ">
        </div>
      </div>
    </div>
    <div class="grid" style="align-items: end; margin-top: 1.5rem;">
      <div class="grid" style="gap: 0.5rem;">
      <fieldset class="grid" style="margin: 0; gap: 2rem;">
          <label for="auth_switch">
            <input type="checkbox" id="auth_switch" name="auth_switch" role="switch" {% if user %}checked{% endif %}>
            Authentication
          </label>
          <label for="no_verify">
            <input type="checkbox" id="no_verify" name="no_verify" role="switch" {% if no_verify %}checked{% endif %}>
            Disable SSL verification
          </label>
      </fieldset>
        <button id="open-btn" type="submit">Open</button>
        <button id="clear-btn" type="button" class="secondary">Clear</button>
      </div>
    </div>
  </form>

  {% if error %}
    <p class="error"><strong>Error:</strong> {{ error }}</p>
  {% endif %}

  {% if tree is defined %}
  <article style="margin-top: 2rem;">
    <header>Contents of <a href="{{url}}" target="_blank">{{ url }}</a></header>
    <div style="padding: 1rem 0;">
      <input type="search" id="search-box" placeholder="Search files and folders...">
    </div>
    <div class="tree">
  {% macro render_tree(subtree, prefix='') %}
    <ul>
    {% for name, node in subtree|dictsort %}
      {% if node.type == 'dir' %}
        <li id="folder-{{ (prefix + name)|replace('/', '-') }}" class="folder" onclick="toggle(event, this)">
          <div class="tree-item">
            <svg class="icon icon-closed" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>
            <svg class="icon icon-open" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-2.06 11L15 15.28 12.06 17l-1.06-1.06L14.44 12 11 8.56 12.06 7.5 15 10.44 17.94 7.5 19 8.56 15.56 12l3.44 3.44L17.94 17z"/></svg>
            <span class="tree-item-label">{{ name }}</span>
          </div>
          {{ render_tree(node.children, prefix + name + '/') }}
        </li>
      {% else %}
        <li class="file">
          <div class="tree-item">
            <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z"/></svg>
            <span class="tree-item-label" title="{{ name }}">{{ name }}</span>
            <span class="tree-item-size">{{ node.info.file_size|format_bytes }}</span>
            <div class="tree-item-actions">
              {% if node.info.is_text %}
                <a href="{{ url_for('preview_file') }}?url={{ url|urlencode }}&name={{ node.info.filename|urlencode }}{% if no_verify %}&no_verify=on{% endif %}{% if user %}&user={{ user|urlencode }}{% endif %}{% if password %}&password={{ password|urlencode }}{% endif %}" role="button" class="outline secondary btn-sm">Preview</a>
              {% endif %}
              {% if node.info.is_image %}
                <a href="{{ url_for('preview_image') }}?url={{ url|urlencode }}&name={{ node.info.filename|urlencode }}{% if no_verify %}&no_verify=on{% endif %}{% if user %}&user={{ user|urlencode }}{% endif %}{% if password %}&password={{ password|urlencode }}{% endif %}" role="button" class="outline secondary btn-sm">Image</a>
              {% endif %}
              <a href="{{ url_for('download_file') }}?url={{ url|urlencode }}&name={{ node.info.filename|urlencode }}{% if no_verify %}&no_verify=on{% endif %}{% if user %}&user={{ user|urlencode }}{% endif %}{% if password %}&password={{ password|urlencode }}{% endif %}" role="button" class="outline secondary btn-sm download-btn" data-filename="{{ node.info.filename }}">Get File</a>

            </div>
          </div>
        </li>
      {% endif %}
    {% endfor %}
    </ul>
  {% endmacro %}
  {{ render_tree(tree) }} {# Initial call to the macro #}
    </div>
  </article>
  {% endif %}
<script>
  const currentUrl = "{{ url or '' }}";
  const folderStateKey = `folderState-${currentUrl}`;
  const downloadStateKey = `downloadState-${currentUrl}`;

  // --- Event Listeners ---
  document.addEventListener('DOMContentLoaded', () => {
    // Restore folder state on page load
    // Restore download state on page load
    if (currentUrl && typeof storageKey !== 'undefined') {
      try {
        const state = JSON.parse(localStorage.getItem(storageKey) || '{}');
        Object.keys(state).forEach(folderId => {
          if (state[folderId]) {
            const element = document.getElementById(folderId);
            if (element) element.classList.add('expanded');
          }
        });
      } catch (e) { console.error('Could not parse folder state:', e); }
    }
    if (currentUrl && typeof downloadStateKey !== 'undefined') {
      try {
        const downloadedFiles = JSON.parse(localStorage.getItem(downloadStateKey) || '[]');
        downloadedFiles.forEach(filename => {
          const btn = document.querySelector(`.download-btn[data-filename="${filename}"]`);
          if (btn) updateDownloadButton(btn);
        });
      } catch (e) { console.error('Could not parse download state:', e); }
    }


    // Loading indicator for the "Open" button
    document.querySelector('form').addEventListener('submit', () => {
      document.getElementById('open-btn').setAttribute('aria-busy', 'true');
    });

    // Clear button functionality
    document.getElementById('clear-btn').addEventListener('click', () => {
      window.location.href = "{{ url_for('index') }}";
    });

    // Add click listeners for all download buttons
    document.querySelectorAll('.download-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const filename = btn.dataset.filename;
        let downloadedFiles = JSON.parse(localStorage.getItem(downloadStateKey) || '[]');
        if (!downloadedFiles.includes(filename)) {
          downloadedFiles.push(filename);
          localStorage.setItem(downloadStateKey, JSON.stringify(downloadedFiles));
        }
      });
    });

    // Toggle auth fields visibility
    const authSwitch = document.getElementById('auth_switch');
    const authFields = document.getElementById('auth-fields');
    if (authSwitch && authFields) {
        authSwitch.addEventListener('change', () => {
            authFields.classList.toggle('hidden', !authSwitch.checked);
            // Clear fields when hiding
            if (!authSwitch.checked) {
                document.getElementById('user').value = '';
                document.getElementById('password').value = '';
            }
        });
    }
  });
  
  // Search functionality
  const searchBox = document.getElementById('search-box');
  if (searchBox) {
    searchBox.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const allItems = document.querySelectorAll('.tree li');

        // If search is cleared, unhide everything and let localStorage state take over.
        if (!searchTerm) {
            allItems.forEach(item => item.classList.remove('hidden'));
            return;
        }

        // First, hide all items.
        allItems.forEach(item => item.classList.add('hidden'));

        // Find matches and reveal them and their parents.
        allItems.forEach(item => {
            const label = item.querySelector('.tree-item-label');
            if (label && label.textContent.toLowerCase().includes(searchTerm)) {
                // Show the matched item itself.
                item.classList.remove('hidden');
                // Show and expand all of its parent folders.
                let parent = item.parentElement.closest('li.folder');
                while (parent) {
                    parent.classList.remove('hidden');
                    parent.classList.add('expanded');
                    parent = parent.parentElement.closest('li.folder');
                }
            }
        });
    });
  }

  // --- Functions ---
  function toggle(event, element) {
    event.stopPropagation();
    element.classList.toggle('expanded');
    // Save folder state to localStorage
    const state = JSON.parse(localStorage.getItem(folderStateKey) || '{}');
    state[element.id] = element.classList.contains('expanded');
    localStorage.setItem(folderStateKey, JSON.stringify(state));
  }

  function updateDownloadButton(btn) {
    btn.textContent = 'Downloaded';
    btn.setAttribute('disabled', '');
    btn.classList.remove('secondary');
  }
</script>
<footer class="container" style="text-align: center; margin-top: 2rem; color: var(--pico-secondary);">
  <small>
    Remote ZIP Viewer v{{ version }} | © 2025 <a href="https://kagbontaen.ucoz.lv" target="_blank">Kagbontaen</a> |
    <a href="https://github.com/kagbontaen/remote-zip-downloader" target="_blank">Source Code</a>
  </small>
</footer>
</main>
</body>
</html>
"""

TEXT_EXTS = (".txt",".md",".py",".csv",".log",".json",".xml",".html",".htm",".cfg",".ini",".plist",".yaml",".yml")
IMAGE_EXTS = (".png",".jpg",".jpeg",".gif",".webp")

@app.template_filter('format_bytes')
def format_bytes(size):
    """Formats a file size in bytes into a human-readable string."""
    if size is None:
        return "0 bytes"
    power = 1024
    n = 0
    power_labels = {0: 'bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < len(power_labels) - 1:
        size /= power
        n += 1
    if n == 0:
        return f"{int(size)} {power_labels[n]}"
    return f"{size:.2f} {power_labels[n]}"

# Cache for storing the directory structure of remote ZIP files.
# It holds up to 100 different URLs and each entry expires after 300 seconds (5 minutes).
file_list_cache = TTLCache(maxsize=100, ttl=300)

def _get_session_kwargs(insecure=False, auth=None):
    """Returns the kwargs for the RemoteZip session."""
    kwargs = {'verify': not insecure}
    if auth:
        kwargs['auth'] = auth
    return kwargs

@cached(file_list_cache)
def list_entries(url, insecure=False, auth=None):
    """Parses a remote ZIP file and returns its directory structure as a nested dict."""
    tree = {}
    kwargs = _get_session_kwargs(insecure, auth)
    app.logger.info(f"Cache miss. Fetching and processing directory for {url}")
    with RemoteZip(url, **kwargs) as rz:
        for info in rz.infolist():
            # Skip directory entries, we build the structure from file paths
            if info.is_dir():
                continue

            parts = info.filename.split('/')
            current_level = tree
            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {"type": "dir", "children": {}}
                current_level = current_level[part]["children"]
            
            filename = parts[-1]
            if filename:
                current_level[filename] = {
                    "type": "file",
                    "info": {
                        "filename": info.filename,
                        "file_size": info.file_size,
                        "compress_size": info.compress_size,
                        "is_text": info.filename.lower().endswith(TEXT_EXTS),
                        "is_image": info.filename.lower().endswith(IMAGE_EXTS),
                    }
                }
    return tree

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/view")
def view():
    url = request.args.get("url")
    insecure = request.args.get("no_verify") == "on"
    user = request.args.get("user")
    password = request.args.get("password")

    if not url: return redirect(url_for("index"))

    auth = None
    if user:
        auth = (user, password or '')

    try:
        tree = list_entries(url, insecure=insecure, auth=auth)
        return render_template_string(INDEX_HTML, tree=tree, url=url, no_verify=insecure, user=user, password=password)
    except Exception as e:
        return render_template_string(INDEX_HTML, error=str(e), url=url, no_verify=insecure, user=user, password=password)

def with_remote_zip(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        url = request.args.get("url")
        name = request.args.get("name")
        insecure = request.args.get("no_verify") == "on"
        user = request.args.get("user")
        password = request.args.get("password")

        if not url or not name:
            abort(400, "Missing 'url' or 'name' parameter.")
        
        auth = None
        if user:
            auth = (user, password or '')

        # Pass the parsed arguments to the decorated function
        return f(url, name, insecure, auth, *args, **kwargs)
    return decorated_function

def _stream_zip_file(url, name, insecure, auth=None):
    """
    A generator that creates a RemoteZip instance and streams a file from it.
    This ensures the RemoteZip object remains open during the entire stream.
    """
    try:
        with RemoteZip(url, **_get_session_kwargs(insecure, auth)) as rz:
            with rz.open(name) as f:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
    except FileNotFoundError:
        # This error won't be caught by Flask's regular error handlers
        # because it happens inside a generator. We can't easily abort(404).
        # The stream will just be empty, resulting in a 0-byte response.
        app.logger.error(f"File '{name}' not found in zip at url {url}")
    except Exception as e:
        app.logger.error(f"Error streaming zip file from url {url}: {e}")

@app.route("/preview")
@with_remote_zip
def preview_file(url, name, insecure, auth):
    with RemoteZip(url, **_get_session_kwargs(insecure, auth)) as rz:
        with rz.open(name) as f:
            data = f.read(100*1024)  # limit preview size
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1", errors="replace")
    return f"<h3>Preview of {name}</h3><pre>{text}</pre>" # Preview is not streamed, so original logic is fine

@app.route("/image")
@with_remote_zip
def preview_image(url, name, insecure, auth):
    mime, _ = mimetypes.guess_type(name)
    return Response(_stream_zip_file(url, name, insecure, auth), mimetype=mime or "application/octet-stream")

@app.route("/file")
@with_remote_zip
def download_file(url, name, insecure, auth):
    headers = {"Content-Disposition": f'attachment; filename="{Path(name).name}"'}
    return Response(_stream_zip_file(url, name, insecure, auth), headers=headers, mimetype="application/octet-stream")

def _cli_download(file_in_zip, url, output_path, insecure, auth, create_dirs):
    """Handles the command-line download operation with progress display."""
    import time
    
    print(f"Connecting to {url}...")
    output = Path(output_path)

    if output.is_dir():
        output = output / Path(file_in_zip).name

    # If create_dirs is specified, create the full path
    if create_dirs:
        output = Path(output_path) / file_in_zip

    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with RemoteZip(url, **_get_session_kwargs(insecure, auth)) as rz:
            try:
                print(f"Searching for '{file_in_zip}' in archive...")
                info = rz.getinfo(file_in_zip)
                total_size = info.file_size
            except KeyError:
                print(f"Error: File '{file_in_zip}' not found in the remote archive.")
                return

            print(f"Downloading '{file_in_zip}' ({total_size} bytes) to '{output}'...")

            downloaded_bytes = 0
            start_time = time.time()

            with rz.open(file_in_zip) as source, open(output, "wb") as target:
                while True:
                    chunk = source.read(8192)
                    if not chunk:
                        break
                    target.write(chunk)
                    downloaded_bytes += len(chunk)

                    elapsed_time = time.time() - start_time
                    speed = downloaded_bytes / elapsed_time if elapsed_time > 0 else 0
                    speed_mbps = (speed * 8) / (1024 * 1024)
                    
                    percent = (downloaded_bytes / total_size) * 100 if total_size > 0 else 100
                    
                    progress_bar = f"[{'=' * int(percent / 2):<50}]"
                    
                    # Use \r to return to the beginning of the line
                    print(f"\r{progress_bar} {percent:.1f}% - {downloaded_bytes/1024/1024:.2f}MB - {speed_mbps:.2f} Mbps", end="")

            # Print a newline at the end
            print("\nDownload complete.")

    except Exception as e:
        print(f"An error occurred: {e}")

def _cli_download_folder(folder_path, url, output_path, insecure, auth):
    """Handles downloading all files within a specified folder in the ZIP."""
    import time

    print(f"Connecting to {url} to download folder '{folder_path}'...")
    output_base = Path(output_path)

    # Ensure the base output path exists
    output_base.mkdir(parents=True, exist_ok=True)

    try:
        with RemoteZip(url, **_get_session_kwargs(insecure, auth)) as rz:
            # Normalize folder path to end with a slash
            if not folder_path.endswith('/'):
                folder_path += '/'

            # Find all files that are inside the specified folder_path
            files_to_download = [
                info for info in rz.infolist()
                if info.filename.startswith(folder_path) and not info.is_dir()
            ]

            if not files_to_download:
                print(f"Error: No files found in folder '{folder_path}' or folder does not exist.")
                return

            print(f"Found {len(files_to_download)} file(s) to download.")

            for i, info in enumerate(files_to_download):
                # Determine the output path for the file
                # This preserves the subdirectory structure relative to the output path
                relative_path = info.filename
                file_output_path = output_base / relative_path

                # Create parent directories for the file
                file_output_path.parent.mkdir(parents=True, exist_ok=True)

                print(f"\n[{i+1}/{len(files_to_download)}] Downloading '{info.filename}' to '{file_output_path}'...")

                with rz.open(info.filename) as source, open(file_output_path, "wb") as target:
                    while True:
                        chunk = source.read(8192)
                        if not chunk:
                            break
                        target.write(chunk)
            print("\nFolder download complete.")

    except Exception as e:
        print(f"An error occurred: {e}")

def _cli_stream_to_console(file_in_zip, url, insecure, auth):
    """Handles streaming a file's content directly to standard output."""
    import sys
    try:
        # Write directly to the stdout buffer to handle binary data
        for chunk in _stream_zip_file(url, file_in_zip, insecure, auth):
            sys.stdout.buffer.write(chunk)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

def _cli_list_files(url, list_path, no_subdirs, insecure, auth):
    """Lists files and directories from the remote ZIP."""
    from fnmatch import fnmatch

    print(f"Fetching file list from {url}...")
    try:
        with RemoteZip(url, **_get_session_kwargs(insecure, auth)) as rz:
            all_files = [info.filename for info in rz.infolist() if not info.is_dir()]

        if list_path:
            # Normalize list_path to ensure it's treated as a directory
            if not list_path.endswith('/'):
                list_path += '/'
            
            # Filter files that are directly within the list_path
            if no_subdirs:
                # Show only files directly in list_path, no deeper
                files_to_show = [f for f in all_files if f.startswith(list_path) and '/' not in f[len(list_path):]]
            else:
                # Show all files and subdirs under list_path
                files_to_show = [f for f in all_files if f.startswith(list_path)]
        else:
            # Listing from the root
            if no_subdirs:
                # Show only files in the root
                files_to_show = [f for f in all_files if '/' not in f]
            else:
                # Show all files
                files_to_show = all_files

        print("\nContents:")
        for filename in sorted(files_to_show):
            print(filename)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    """Main function to run the web server or handle CLI commands."""
    import socket
    import webbrowser
    import atexit
    from threading import Timer
    from waitress import serve
    import sys
    import argparse
    
    PORT_FILE = ".port"
    port = None
    
    # Try to read the port from a file to maintain it across reloads
    try:
        with open(PORT_FILE, "r") as f:
            port = int(f.read())
    except (FileNotFoundError, ValueError):
        # If the file doesn't exist or is invalid, find a new port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", 80))
            port = 80
            sock.close()
        except (socket.error, OSError):
            import random
            port = random.randint(5000, 6000)
            print(f"Port 80 not available. do you have IIS running on port 80?")
            print(f"Using a random port between 5000 and 6000 instead.")
            print(f" Using random port: {port}")
        
        # Save the chosen port for next time
        with open(PORT_FILE, "w") as f:
            f.write(str(port))
        # Register a function to clean up the file on exit
        atexit.register(lambda: Path(PORT_FILE).unlink(missing_ok=True))
    
    parser = argparse.ArgumentParser(
        description="Remote ZIP Viewer and Downloader. Run without arguments to start the web UI.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # --- CLI Mode Arguments ---
    cli_group = parser.add_argument_group('CLI Mode Options')
    cli_group.add_argument('url', nargs='?', help='The URL of the remote ZIP archive.')

    # Listing files
    cli_group.add_argument('-l', '--list', nargs='?', const='', default=None, dest='list_path',
                           help="Shows contents of the zip. Optionally specify a path to list its contents.")
    cli_group.add_argument('--nosubdirs', action='store_true',
                           help="Don't show subdirectories. Used with -l or --list.")

    # Downloading files/directories
    cli_group.add_argument('-g', '--get', dest='get_path',
                           help='Path to a remote file or directory to download.')
    cli_group.add_argument('-d', '--directory', action='store_true',
                           help='Treat the path from -g/--get as a directory and download recursively.')
    cli_group.add_argument('-o', '--output', dest='output_path', default='.',
                           help='Specify destination path for downloads. Defaults to the current directory.')
    cli_group.add_argument('-c', '--create-directories', action='store_true',
                           help="Create the full directory structure for a downloaded file.")

    # Authentication and Security
    cli_group.add_argument('-u', '--user', dest='auth_user',
                           help='Authenticate to the web server. Format: user[:password]')
    cli_group.add_argument('-k', '--insecure', action='store_true',
                           help='Disable SSL certificate verification.')

    args = parser.parse_args()

    # Determine if we are in CLI mode
    is_cli_mode = args.url or args.list_path is not None or args.get_path

    if is_cli_mode:
        if not args.url:
            parser.error("The 'url' argument is required for CLI mode.")

        # --- Authentication ---
        auth = None
        if args.auth_user:
            if ':' in args.auth_user:
                user, pw = args.auth_user.split(':', 1)
                auth = (user, pw)
            else:
                auth = (args.auth_user, '')

        # --- Action: List Files ---
        if args.list_path is not None:
            _cli_list_files(args.url, args.list_path, args.nosubdirs, args.insecure, auth)

        # --- Action: Get File/Directory ---
        elif args.get_path:
            if args.directory:
                # Download a directory
                _cli_download_folder(args.get_path, args.url, args.output_path, args.insecure, auth)
            else:
                # Download a single file
                _cli_download(args.get_path, args.url, args.output_path, args.insecure, auth, args.create_directories)
        else:
            print("No action specified. Use -l/--list to list files or -g/--get to download.", file=sys.stderr)

    else:
        # Otherwise, start the web server
        url = f"http://127.0.0.1{f':{port}' if port != 80 else ''}"
        print(f"Server starting at {url}")
        Timer(1, lambda: webbrowser.open(url)).start()
        serve(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    # This block is for local development and for running the compiled executable.
    main()
