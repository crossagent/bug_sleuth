import os
import uvicorn
from pathlib import Path
from google.adk.cli.fast_api import get_fast_api_app
from fastapi.responses import HTMLResponse

# Define Project Paths
# server.py is in <project_root>/deployment/
DEPLOYMENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Define Roots
# APP_ROOT: Where the agent code/server code lives (e.g. /app)
APP_ROOT = os.path.dirname(DEPLOYMENT_DIR)

# PROJECT_ROOT: Where the Target Game Code lives (e.g. /project_root)
# If not set, default to APP_ROOT
PROJECT_ROOT = os.getenv("PROJECT_ROOT", APP_ROOT)



# 2. ADK_DATA_DIR: Where runtime data lives (e.g. /app/adk_data)
# We anchor this to APP_ROOT by default, unless absolute path provided
ADK_DATA_DIR = os.getenv("ADK_DATA_DIR", "adk_data")
if not os.path.isabs(ADK_DATA_DIR):
    ADK_DATA_DIR = os.path.join(APP_ROOT, ADK_DATA_DIR)

# 3. Agents & Artifacts
# Agents are part of the APP, not the Target Code
AGENTS_DIR = os.path.join(APP_ROOT, "agents")
ARTIFACTS_DIR = os.path.join(ADK_DATA_DIR, "artifacts")

# Ensure directories exist
os.makedirs(ADK_DATA_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# Configuration for Local Persistence
# 1. Artifacts: file:// URI (Resolve to absolute path for safety)
artifact_service_uri = Path(ARTIFACTS_DIR).resolve().as_uri()

# 2. Sessions: SQLite URI
session_db_path = os.path.abspath(os.path.join(ADK_DATA_DIR, "sessions.db"))
session_service_uri = f"sqlite+aiosqlite:///{session_db_path}"

print(f"Server Configuration:")
print(f"  Agents Dir:   {AGENTS_DIR}")
print(f"  Artifacts:    {artifact_service_uri}")
print(f"  Sessions:     {session_service_uri}")
print(f"  Web UI:       Enabled")
print(f"  A2A RPC:      Enabled")

# Create the FastAPI app using ADK's helper
port = int(os.getenv("PORT", 8000))
app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=session_service_uri,
    artifact_service_uri=artifact_service_uri,
    web=True,
    a2a=False,
    host="0.0.0.0",
    port=port
)

# --- Custom Extensions for Bug Report UI ---
# We keep this endpoint to serve the UI HTML file.
# The UI's logic is now refactored to use ADK's native APIs directly.

@app.get("/reporter", response_class=HTMLResponse)
async def get_reporter_ui():
    """Serve the standalone bug reporter UI."""
    # In a real app, use StaticFiles. Here we read the single HTML file for simplicity.
    # UI is part of the App, so use APP_ROOT
    ui_path = os.path.join(APP_ROOT, "bug_report_ui", "index.html")
    if os.path.exists(ui_path):
        with open(ui_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>UI Not Found</h1>"

if __name__ == "__main__":
    # Run from Project Root: `python deployment/server.py`
    uvicorn.run(app, host="0.0.0.0", port=port)
