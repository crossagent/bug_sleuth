
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Setup Environment & Path
# Ensure we can import 'agents' module
PROJECT_ROOT = Path(__file__).parent.parent
# sys.path.insert(0, str(PROJECT_ROOT / "agents")) # Removed: bug_sleuth is now a package
sys.path.insert(0, str(PROJECT_ROOT)) # For runner_test modules

# Load Env (for API Keys)
load_dotenv(PROJECT_ROOT / "bug_sleuth" / "agents" / ".env")

from runner_test.client import AdkSimulationClient
try:
    from bug_sleuth.agents.bug_analyze_agent.agent import bug_analyze_agent
except ImportError as e:
    print(f"Error importing agent: {e}")
    sys.exit(1)

async def main():
    print(">>> Initializing Test for BugAnalyzeAgent <<<")
    
    # 2. Instantiate Client with REAL Agent
    client = AdkSimulationClient(agent=bug_analyze_agent)
    
    # 3. Setup Session
    session_id = "test-session-001"
    await client.create_new_session(user_id="tester", session_id=session_id)
    
    # 4. Patch State (Simulate context from Client)
    # We provide a dummy bug description
    await client.patch_state({
        "bug_user_description": "I want to verify the server code search functionality.",
        "clientLogUrls": [],
        "clientScreenshotUrls": []
    })
    
    # 5. Send Prompt
    query = "Search for the code 'MULTI_REPO_PROOF_123' to verify multi-repo access."
    print(f"\n[User] {query}")
    
    responses = await client.chat(query)
    
    print("\n>>> Test Finished <<<")
    print("Agent Responses:", responses)

if __name__ == "__main__":
    asyncio.run(main())
