from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.genai import types
from google.adk.sessions import State
from shared_libraries.state_keys import StateKeys
import uuid
import logging
import os
from typing import Optional

# Sub-agents
from bug_analyze_agent import bug_analyze_agent
from bug_reproduce_steps_agent import bug_reproduce_steps_agent
from bug_report_agent import bug_report_agent
from bug_base_info_collect_agent.agent import bug_base_info_collect_agent

# Prompt
from prompt import ROOT_AGENT_PROMPT

logger = logging.getLogger(__name__)

# Environment check
_IS_TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

async def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback function to be executed before each agent runs.
    """
    if _IS_TEST_MODE:
        return None

    state = callback_context.state
    if not state.get("session_initialized"):
        # First interaction
        if state.get("deviceInfo") is None:
             pass
        else:
             state["session_initialized"] = True
             
    return None

# Instantiate the root agent directly
root_agent = LlmAgent(
    name="bug_scene_agent",
    prompt=ROOT_AGENT_PROMPT,
    sub_agents=[
        bug_base_info_collect_agent,
        bug_analyze_agent,
        bug_report_agent,
        bug_reproduce_steps_agent,
    ],
    before_agent_callback=before_agent_callback
)

# Wrap with App for context caching support
app = App(
    name="bug_scene_app",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,    # Minimum tokens to trigger caching
        ttl_seconds=600,    # Store for up to 10 minutes
        cache_intervals=10, # Refresh after 10 uses
    )
)