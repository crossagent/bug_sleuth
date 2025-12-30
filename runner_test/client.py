"""
ADK Simulation Client

A reusable client for testing ADK agents programmatically.
"""
import logging
import time
from typing import List, Dict, Any

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.plugins.base_plugin import BasePlugin
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

    def __init__(self, app_name: str = "test_app", agent: LlmAgent = None, plugins: List[BasePlugin] = None):
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
        
        self.plugins = plugins or []

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
            plugins=self.plugins,
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
