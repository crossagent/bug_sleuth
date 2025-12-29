import os
import functools
from pathlib import Path

PROJECT_ROOT = os.getenv("PROJECT_ROOT")



def validate_path(func):
    """
    Decorator to validate and resolve 'path' argument against PROJECT_ROOT.
    
    1. Intercepts 'path' argument.
    2. Resolves relative path to absolute path based on PROJECT_ROOT.
    3. Checks if the path is within PROJECT_ROOT (security).
    4. Injects the absolute path back into args/kwargs.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not PROJECT_ROOT:
            return {"status": "error", "error": "PROJECT_ROOT not set in environment."}
            
        # Inspect arguments to find 'path'
        # Note: We rely on the convention that the argument is named 'path'
        # If it's passed as kwarg:
        if 'path' in kwargs:
            original_path = kwargs['path']
            if original_path:
                resolved_path = _resolve_and_check(original_path)
                if isinstance(resolved_path, dict): # Error dict
                     return resolved_path
                kwargs['path'] = str(resolved_path)
        
        # If it's passed as arg, we need to mapping based on function signature.
        # But for simpler ADK tools, kwargs is the standard way parameters are passed from the LLM call decoder.
        # However, if we call it manually or if ADK passes args positionally (less common for tool calling), we might miss it.
        # For this implementation, we focused on kwargs as ADK invokes tools with named arguments.
        
        return await func(*args, **kwargs)

    return wrapper

def _resolve_and_check(path_str: str) -> Path | dict:
    try:
        # Handle absolute path
        p = Path(path_str)
        root = Path(PROJECT_ROOT).resolve()
        
        if not p.is_absolute():
            p = (root / p).resolve()
        else:
            p = p.resolve()
            
        # Security Check: Ensure path is within root
        # commonpath will throw ValueError if paths are on different drives on Windows
        try:
             if root not in p.parents and root != p:
                 return {"status": "error", "error": f"Access Denied: Path '{path_str}' is outside project root '{PROJECT_ROOT}'."}
        except ValueError:
             return {"status": "error", "error": f"Access Denied: Path '{path_str}' is on a different drive than project root."}
             
        return p
    except Exception as e:
        return {"status": "error", "error": f"Path validation error: {str(e)}"}
