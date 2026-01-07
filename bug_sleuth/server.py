
import os
import sys
import logging
import shutil
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import HTMLResponse

# ADK Imports
from google.adk.cli.adk_web_server import AdkWebServer
from google.adk.cli.utils.agent_loader import AgentLoader
from google.adk.cli.service_registry import get_service_registry, load_services_module
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager
from google.adk.evaluation.local_eval_set_results_manager import LocalEvalSetResultsManager
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.genai import types

# Configure Logging
logger = logging.getLogger("bug_sleuth.server")

# 1. Path Configuration
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

AGENTS_DIR = PACKAGE_ROOT

data_dir_env = os.getenv("ADK_DATA_DIR")
if not data_dir_env:
    data_dir_env = "adk_data"

if not os.path.isabs(data_dir_env):
    DATA_DIR = os.path.abspath(data_dir_env)
else:
    DATA_DIR = data_dir_env

ARTIFACTS_DIR = os.path.join(DATA_DIR, "artifacts")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# Services Configuration
artifact_service_uri = Path(ARTIFACTS_DIR).resolve().as_uri()
session_db_path = os.path.join(DATA_DIR, "sessions.db")
session_service_uri = f"sqlite+aiosqlite:///{session_db_path}"

logger.info(f"Server Configuration:")
logger.info(f"  Package Root: {PACKAGE_ROOT}")
logger.info(f"  Agents Dir:   {AGENTS_DIR}")
logger.info(f"  Artifacts:    {artifact_service_uri}")
logger.info(f"  Sessions:     {session_service_uri}")

try:
    # 2. Manual Bootstrapping of ADK Services
    # This logic replicates google.adk.cli.fast_api.get_fast_api_app

    # Initialize Eval Managers
    eval_sets_manager = LocalEvalSetsManager(agents_dir=AGENTS_DIR)
    eval_set_results_manager = LocalEvalSetResultsManager(agents_dir=AGENTS_DIR)

    # Initialize Agent Loader
    agent_loader = AgentLoader(AGENTS_DIR)

    # Load Custom Services
    load_services_module(AGENTS_DIR)
    service_registry = get_service_registry()

    # Build Memory Service
    memory_service = InMemoryMemoryService() # Defaulting to InMemory for now as in get_fast_api_app default

    # Build Session Service
    if session_service_uri:
        session_service = service_registry.create_session_service(
             session_service_uri, agents_dir=AGENTS_DIR
        )
        if not session_service:
            session_service = DatabaseSessionService(db_url=session_service_uri)
    else:
        session_service = InMemorySessionService()

    # Build Artifact Service
    if artifact_service_uri:
        artifact_service = service_registry.create_artifact_service(
            artifact_service_uri, agents_dir=AGENTS_DIR
        )
        if not artifact_service:
             # Fallback manual creation if registry fails (though registry should handle file://)
             from google.adk.artifacts.file_artifact_service import FileArtifactService
             artifact_service = FileArtifactService(root_dir=Path(ARTIFACTS_DIR))
    else:
        artifact_service = InMemoryArtifactService()

    # Build Credential Service
    credential_service = InMemoryCredentialService()

    # Create AdkWebServer
    adk_web_server = AdkWebServer(
        agent_loader=agent_loader,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
        credential_service=credential_service,
        eval_sets_manager=eval_sets_manager,
        eval_set_results_manager=eval_set_results_manager,
        agents_dir=AGENTS_DIR,
    )

    # Create FastAPI App
    # We pass web_assets_dir to get_fast_api_app if we want the standard ADK UI, 
    # but here we are using a custom reporter UI, so we might ommit it or pass it if we want both.
    # Assuming we want standard dev-ui capabilities potentially.
    
    # Locate ADK web assets for dev-ui
    import google.adk.cli.fast_api
    adk_fast_api_dir = Path(google.adk.cli.fast_api.__file__).parent
    adk_web_assets = adk_fast_api_dir / "browser"

    app = adk_web_server.get_fast_api_app(
        web_assets_dir=adk_web_assets,
        otel_to_cloud=False
    )

    # 3. Register Custom Endpoints

    @app.post("/init")
    async def init_session(
        app_name: str = Body(..., embed=True),
        user_id: str = Body(..., embed=True),
        message: Optional[str] = Body(None, embed=True)
    ):
        """Initializes a session, optionally invoking the agent with a message."""
        logger.info(f"Initializing session for app: {app_name}, user: {user_id}")
        
        # Check if session exists or create new
        # We don't have a simple 'get_or_create' so we try to get recent sessions or create one.
        # For simplicity, if we are 'initializing', we might want a clean session or use a specific one.
        # Let's create a NEW session ID to ensure fresh start if called.
        
        # Actually, best practice for 'init' is typically to start fresh.
        # But if the UI refreshes, we might want to keep history.
        # Let's assume we create a new one for now.
        session = await session_service.create_session(app_name=app_name, user_id=user_id)
        
        if message:
            # Create a user event
            event = Event(
                id=str(uuid.uuid4()),
                author="user",
                content=types.Content(
                    role="user",
                    parts=[types.Part(text=message)]
                ),
                timestamp=time.time(),
                turn_complete=True 
            )
            
            # Append event
            await session_service.append_event(session, event)
            
            # Note: We are just appending the event. The ADK Runner needs to pick this up.
            # get_fast_api_app binds the event processing usually via /run_agent endpoints.
            # If we want to TRIGGER the agent, we might need to use the Runner.
            # However, standard ADK UI logic is: Append Event -> UI detects change -> UI calls /run?
            # Or usually: POST /run_agent which takes the message.
            
            # If we just want to seed the history, append_event is enough. 
            # If we want to RUN it, we should probably call the run logic or let the client call run.
            
            # For this request, "Input as an event" implies seeding the input.
            
        return {"session_id": session.id}

    @app.post("/upload")
    async def upload_file(
        file: UploadFile = File(...),
        app_name: str = Form(...),
        user_id: str = Form(...),
        session_id: str = Form(...)
    ):
        """Uploads a file and logs it as an event in the session."""
        logger.info(f"Uploading file {file.filename} for session {session_id}")
        
        # 1. Save artifact
        # ArtifactService usually expects 'Part' or similar, or we can use specific internal methods.
        # Looking at ArtifactService overrides (e.g. FileArtifactService), they usually have 'create_artifact'.
        # Let's look at BaseArtifactService signature if possible.
        # But wait, exposed artifact_service is abstract base type in variables, but concrete at runtime.
        # FileArtifactService specifically handles file://. 
        
        # Actually, let's just use the helper provided in fast_api.py or similar?
        # fast_api.py doesn't expose upload/download easily for agents.
        # Let's just save it using standard python for now if ArtifactService is complex, 
        # BUT the goal is to use ArtifactService.
        
        # Let's assume FileArtifactService.save_artifact takes a filename and bytes/stream.
        # Checking adk code would be ideal, but let's assume standard file writing for 'file://' service.
        
        # The 'FileArtifactService' (from inspection) maps 'file://root' -> 'root/filename'.
        # It's safer to rely on the service abstraction if we can, but 'create_artifact' might need 'types.Part'.
        
        # Simplest approach for 'file' service:
        # Just write to the artifacts dir directly since we know the path.
        # AND register it in the session?
        
        # Actually, sticking to the path:
        file_path = Path(ARTIFACTS_DIR) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Append Event
        # We need to tell the agent a file was uploaded.
        # We can create a user event saying "Uploaded file: <filename>"
        # Or a system event.
        
        session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        event = Event(
            id=str(uuid.uuid4()),
            author="user", 
            content=types.Content(
                role="user",
                parts=[types.Part(text=f"Uploaded file: {file.filename}")]
            ),
            timestamp=time.time(),
            turn_complete=True
        )
        await session_service.append_event(session, event)
        
        return {"filename": file.filename, "path": str(file_path)}


    # 4. Register UI Endpoint (Restoring original UI)
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
