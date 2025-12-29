import os
from typing import Optional
from pathlib import Path
from .decorators import validate_path
from .bash import run_bash_command
import shutil
import logging

logger = logging.getLogger(__name__)

def check_search_tools() -> Optional[str]:
    """
    Verify if 'ripgrep' is available.
    Returns error message if not found, else None.
    """
    # Check for rg (ripgrep)
    if shutil.which("rg"):
        return None
        
    return "Critical Error: 'ripgrep' (rg) is missing. Please contact administrator to install it."


@validate_path
async def search_code_tool(
    query: str,
    file_pattern: Optional[str] = None
) -> dict:
    """
    Search for code or content in the entire project using 'git grep'.
    
    Args:
        query: Content string to search for (e.g. "InitPlayer", "ERR_1001").
        file_pattern: Optional. Limit by filename glob (e.g. "*.cs", "*.json").
                      Example: "*.cs" will search only C# files.

    Returns:
        dict: Search results with file paths and matching lines.
    """
    if not query:
        return {"status": "error", "error": "Query is required."}

    # 1. Build Command (Strictly use rg)
    cmd_parts = ["rg", "-n", "-C", "2", "--no-heading", "--smart-case"]
    
    if file_pattern:
        # rg uses --glob for patterns
        # Handle OS-specific quoting
        if os.name == 'nt':
            # Windows (cmd.exe) requires double quotes
            cmd_parts.append(f'--glob "{file_pattern}"')
        else:
            # Linux/macOS (bash) prefers single quotes to prevent expansion
            cmd_parts.append(f"--glob '{file_pattern}'")
    
    # FIX: Use absolute 'cwd' (PROJECT_ROOT) as target.
    # We rely on 'cwd' parameter in run_bash_command to set the root.
    # rg searches current directory by default.
    cmd_parts += ["-e", f'"{query}"']

    cmd = " ".join(cmd_parts)

    # 3. Execution
    # Always run from PROJECT_ROOT to ensure relative paths in output are correct relative to root
    cwd = os.environ.get("PROJECT_ROOT", ".")
    
    # Increase timeout for large searches
    result = await run_bash_command(cmd, cwd=cwd)

    # --- REGEX FIX: Fallback to fixed string (-F) if regex parsing fails ---
    if result.get("exit_code") == 2:
        stderr = result.get("error", "").lower()
        if "regex parse error" in stderr:
            logger.warning(f"Regex parse error for query '{query}'. Falling back to literal search.")
            # Re-run with -F (Fixed string)
            cmd_fixed = cmd + " -F"
            result = await run_bash_command(cmd_fixed, cwd=cwd)
            # Mark that we fell back
            result["_fallback_used"] = True

    if result.get("status") == "error":
        # Check specific error conditions
        stderr = result.get("error", "").lower()
        exit_code = result.get("exit_code")

        # Case 1: "No matches found" often returns exit code 1 in rg
        # If exit code is 1 and NO critical error in stderr (like 'command not found'), it's just no results.
        if exit_code == 1:
             # Double check it wasn't a syntax error or path error
             if "no such file" in stderr or "fatal" in stderr:
                 return result # Return actual error
             
             # Assume empty match
             summary_msg = f"No matches for '{query}'."
             return {
                 "status": "success", 
                 "output": f"No matches found for '{query}'.",
                 "summary": summary_msg
             }
        return result

    output = result.get("output", "")
    if not output:
         summary_msg = f"No matches for '{query}' in All."
         return {
             "status": "success", 
             "output": f"No matches found for '{query}' in domain 'All'.",
             "summary": summary_msg
         }

    # --- PATH FIX: Convert to Absolute Paths ---
    # rg -n output format: relative_path:line_num:content
    # We want: absolute_path:line_num:content
    
    lines = output.splitlines()
    abs_lines = []
    root_path = Path(cwd).resolve()
    
    for line in lines:
        # Simple heuristic to identify match lines. 
        # CAUTION: Content might contain colons. Split only on first 2 colons.
        parts = line.split(':', 2)
        if len(parts) >= 3:
            rel_path_str = parts[0]
            line_num = parts[1]
            content = parts[2]
            
            # Check if it looks like a file path (not empty)
            if rel_path_str:
                try:
                    # Resolve relative path
                    abs_path = (root_path / rel_path_str).resolve()
                    # Reconstruct line
                    new_line = f"{abs_path}:{line_num}:{content}"
                    abs_lines.append(new_line)
                except Exception:
                    # If path logic fails, keep original line
                    abs_lines.append(line)
            else:
                 abs_lines.append(line)
        else:
            abs_lines.append(line)
            
    final_output = "\n".join(abs_lines)

    # 4. Formatting (Optional cleanup or truncation)
    match_count = len(abs_lines)
    if len(final_output) > 20000:
        final_output = final_output[:20000] + "\n... (Truncated) ..."
        
    fallback_note = " (Literal search fallback used)" if result.get("_fallback_used") else ""
        
    return {
        "status": "success", 
        "output": f"Search Results ('{file_pattern or 'All'}'){fallback_note}:\n{final_output}",
        "summary": f"Found ~{match_count} matches for '{query}' in All.{fallback_note}"
    }
