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
from google.adk.events.event import Event, EventActions
from google.adk.tools import load_artifacts

# Import shared client logic
from runner_test.client import AdkSimulationClient

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
