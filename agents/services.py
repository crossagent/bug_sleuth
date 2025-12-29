import platform
import urllib.parse
from google.adk.cli.service_registry import get_service_registry
from google.adk.artifacts import file_artifact_service

def create_artifact_service_windows(uri: str, **kwargs):
    """
    Custom factory for file:// URIs on Windows to handle absolute paths correctly.
    Fixes the issue where 'file:///E:/...' becomes '/E:/...' (invalid) instead of 'E:/...'
    """
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != "file":
        return None
    
    # On Windows, parsed.path for 'file:///E:/foo' is '/E:/foo'.
    # We need to strip the leading slash to make it a valid path 'E:/foo'.
    path_str = parsed.path
    if path_str.startswith("/") and ":" in path_str:
        path_str = path_str[1:]
        
    print(f"[Services] Windows Path Patch: Resolved '{uri}' to '{path_str}'")
    return file_artifact_service.FileArtifactService(root_dir=path_str)

# Register the patch if we are on Windows
if platform.system() == "Windows":
    print("[Services] Loading Windows compatibility patch for Artifact Service...")
    registry = get_service_registry()
    # Overwrite the default 'file' handler with our patched version
    registry.register_artifact_service("file", create_artifact_service_windows)
