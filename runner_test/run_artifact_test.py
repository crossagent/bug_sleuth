"""
Artifact Read Test Agent (Modular Simulation)

This script provides a `AdkSimulationClient` to simulate multi-turn flows programmatically.
Each step (create session, upload, chat) is exposed as an async method ("API").

Run with: python runner_test/run_artifact_test.py
"""
import asyncio
import base64
import time
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Logging Setup
import logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(name)s - %(levelname)s - %(message)s'
)

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools import load_artifacts
from google.adk.events.event import Event, EventActions

# --- Plugins ---

class DebugPlugin(BasePlugin):
    """Debug Plugin to monitor LLM interactions"""
    def __init__(self):
        super().__init__(name="debug_plugin")
        self.call_count = 0
    
    async def before_model_callback(self, *, callback_context, llm_request):
        self.call_count += 1
        print(f"    [Plugin] >> LLM Request #{self.call_count} | Context Events: {len(llm_request.contents)}")
        return None

# --- Modular Client ---

class AdkSimulationClient:
    """
    A helper class to simulate interactions with the ADK backend.
    Think of this as a Python client for your Agent's API.
    """
    def __init__(self, app_name: str = "test_app", agent: LlmAgent = None):
        if not agent:
             raise ValueError("Agent must be provided")
        
        self.app_name = app_name
        self.agent = agent
        
        # Initialize Services (In-Memory for testing)
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        
        # Current Context
        self.user_id: str = "default_user"
        self.session_id: str = None
        self.session = None

    async def create_new_session(self, user_id: str, session_id: str, initial_state: Dict[str, Any] = None) -> str:
        """API: Create a new session"""
        print(f"\n[API] create_new_session(user={user_id}, session={session_id}, state_keys={list(initial_state.keys()) if initial_state else []})")
        self.user_id = user_id
        self.session_id = session_id
        
        self.session = await self.session_service.create_session(
            app_name=self.app_name, 
            user_id=user_id, 
            session_id=session_id,
            state=initial_state
        )
        print(f"  -> Session Created: {self.session.id}")
        return self.session.id

    async def upload_artifact(self, filename: str, data: bytes, mime_type: str = "application/octet-stream") -> str:
        """API: Upload a file as an artifact"""
        if not self.session: raise RuntimeError("No active session. Call create_new_session first.")
        
        print(f"\n[API] upload_artifact(filename={filename}, size={len(data)} bytes)")
        
        # Create Part
        part = types.Part(inline_data=types.Blob(mime_type=mime_type, data=data))
        
        # Save
        version = await self.artifact_service.save_artifact(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id,
            filename=filename,
            artifact=part
        )
        print(f"  -> Artifact Saved. Version: {version}")
        return filename

    async def patch_state(self, updates: Dict[str, Any]):
        """API: Update session state (Invisible System Event)"""
        if not self.session: raise RuntimeError("No active session.")
        
        print(f"\n[API] patch_state(keys={list(updates.keys())})")
        
        # Construct invisible event
        state_event = Event(
            author="user",
            timestamp=time.time(),
            actions=EventActions(state_delta=updates)
            # No content = Invisible to LLM
        )
        await self.session_service.append_event(self.session, state_event)
        print(f"  -> State Patched. New State: {self.session.state}")

    async def chat(self, user_text: str) -> List[str]:
        """API: Send a message to the agent and get responses (Multi-turn support)"""
        if not self.session: raise RuntimeError("No active session.")
        
        print(f"\n[API] chat(text='{user_text}')")
        
        responses = []
        
        async with Runner(
            app_name=self.app_name,
            agent=self.agent,
            session_service=self.session_service,
            artifact_service=self.artifact_service,
            plugins=[DebugPlugin()],
        ) as runner:
            
            message = types.Content(role="user", parts=[types.Part(text=user_text)])
            
            print("  -> Running Agent...")
            async for event in runner.run_async(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=message
            ):
                # We only care about what the model says (role='model') or tool calls
                if event.author == "model" and event.content:
                    for p in event.content.parts:
                        if p.text:
                            print(f"  <- [Agent Text] {p.text}")
                            responses.append(p.text)
                        if p.function_call:
                            print(f"  <- [Tool Call] {p.function_call.name}")
        
        return responses

# --- Helper to create dummy data ---
def create_dummy_png() -> bytes:
    return base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")

# --- Simulation Script ---

async def main():
    if "GOOGLE_API_KEY" not in os.environ and "PROJECT_ID" not in os.environ:
        print("[Error] GOOGLE_API_KEY or PROJECT_ID environment variable not set.")
        print("Please set it before running the test.")
        return

    print("Initializing Simulation Client...")
    
    # Define the agent logic (The "Brain")
    qa_agent = LlmAgent(
        name="bug_analyze_agent",
        model="gemini-2.5-flash",
        instruction="""
        You are a smart QA Assistant.
        If the user mentions a bug, check for screenshots ('clientScreenshotUrls') in state.
        If screenshots exist, verify them using `load_artifacts`.
        Keep your responses concise.
        """,
        tools=[load_artifacts],
    )
    
    client = AdkSimulationClient(agent=qa_agent)

    # --- Turn 1: Setup & Initial Context ---
    session_id = f"sim-{int(time.time())}"
    
    # 1. Create Session (Empty)
    await client.create_new_session(
        user_id="dev_user", 
        session_id=session_id
    )

    # 2. Upload Artifacts (The work)
    await client.upload_artifact("error.png", create_dummy_png(), "image/png")
    
    # 3. Patch State (Invisible Event - The context update)
    await client.patch_state({
        "bug_user_description": "Screen goes black",
        "clientScreenshotUrls": ["error.png"],
        "clientLogUrls": []
    })
    
    # --- Turn 2: Developer asks to analyze ---
    print("\n--- Turn 2 (Developer) ---")
    await client.chat("I see a new ticket. Can you analyze the screenshot?")

    # --- Turn 3: Follow up ---
    print("\n--- Turn 3 (Developer) ---")
    await client.chat("Is it a critical bug?")

if __name__ == "__main__":
    asyncio.run(main())
