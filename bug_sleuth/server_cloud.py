
import os
import sys
import logging
from pathlib import Path
from typing import Optional

from google.adk.cli.fast_api import get_fast_api_app
from fastapi.responses import HTMLResponse
from fastapi import FastAPI

# Configure Logging
logger = logging.getLogger("bug_sleuth.server")

# 1. Path Configuration
# PACKAGE_ROOT is the directory containing this file (package root 'bug_sleuth')
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

# Read configuration from Environment Variables
# These should be set by the CLI or environment before importing/running this module if non-default.

app_dir_env = os.getenv("ADK_APP_DIR")
if app_dir_env:
    AGENTS_DIR = os.path.abspath(app_dir_env)
else:
    AGENTS_DIR = PACKAGE_ROOT  # ADK scans subdirs (e.g., bug_scene_app)

data_dir_env = os.getenv("ADK_DATA_DIR")
if not data_dir_env:
    data_dir_env = "adk_data" # Default

if not os.path.isabs(data_dir_env):
    DATA_DIR = os.path.abspath(data_dir_env)
else:
    DATA_DIR = data_dir_env

ARTIFACTS_DIR = os.path.join(DATA_DIR, "artifacts")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# Services Configuration
# Local Artifacts: file:// URI
artifact_service_uri = Path(ARTIFACTS_DIR).resolve().as_uri()

# Local Sessions: SQLite URI
session_db_path = os.path.join(DATA_DIR, "sessions.db")
session_service_uri = f"sqlite+aiosqlite:///{session_db_path}"

logger.info(f"Server Configuration:")
logger.info(f"  Package Root: {PACKAGE_ROOT}")
logger.info(f"  Agents Dir:   {AGENTS_DIR}")
logger.info(f"  Artifacts:    {artifact_service_uri}")
logger.info(f"  Sessions:     {session_service_uri}")

# --- 1.5. Load Extensions (Services & Skills) ---
from bug_sleuth.skill_library.skill_loader import SkillLoader

skill_path = os.getenv("SKILL_PATH")
if skill_path and os.path.exists(skill_path):
    logger.info(f"Initializing Skill System from: {skill_path}")
    skill_loader = SkillLoader(skill_path)
    # Just run the skills; they will self-register into the global registries
    skill_loader.load_skills()
else:
    logger.info("No SKILL_PATH set or path does not exist. Skipping skill loading.")

try:
    # 2. Create FastAPI App using ADK Wrapper (Global Instance)
    # This wrapper handles the logic of loading agents from AGENTS_DIR 
    # and checking 'bug_analyze_agent' compatibility.
    # We read host/port from env or defaults, though uvicorn usually overrides execution binding.
    # The app creation mainly care about the services.
    
    app = get_fast_api_app(
        agents_dir=AGENTS_DIR,
        session_service_uri=session_service_uri,
        artifact_service_uri=artifact_service_uri,
        web=True,
        a2a=False
    )
    
    # 3. Register UI Endpoint
    # Mounts the 'reporter' UI which is a simple HTML file.
    @app.get("/reporter", response_class=HTMLResponse)
    async def get_reporter_ui():
        """Serve the embedded bug reporter UI."""
        ui_path = os.getenv("BUG_SLEUTH_UI_PATH")
        
        if ui_path and os.path.exists(ui_path):
             with open(ui_path, "r", encoding="utf-8") as f:
                return f.read()
        
        return f"<h1>Bug Sleuth UI Not Found</h1><p>Please configure BUG_SLEUTH_UI_PATH environment variable or use --ui-path CLI option.</p>"

except Exception as e:
    logger.error(f"Failed to create app: {e}")
    raise e
