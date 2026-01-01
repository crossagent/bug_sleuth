import os
import logging
from typing import Optional
from google.adk.agents.llm_agent import LlmAgent
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from bug_sleuth.skill_loader import SkillLoader
from bug_sleuth.prompt import ROOT_AGENT_PROMPT
from bug_sleuth.bug_analyze_agent.agent import create_bug_analyze_agent
from bug_sleuth.bug_reproduce_steps_agent import bug_reproduce_steps_agent
from bug_sleuth.bug_report_agent import bug_report_agent
from bug_sleuth.bug_base_info_collect_agent.agent import bug_base_info_collect_agent

logger = logging.getLogger(__name__)

# Re-implementing callback here to avoid circular dependency
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

def create_app(config_path: Optional[str] = None, skill_path: Optional[str] = None) -> App:
    """
    Factory function to create the Bug Sleuth App instance.
    
    Args:
        config_path (str, optional): Path to config.yaml. 
        skill_path (str, optional): Path to external skills directory. Defaults to SKILL_PATH env var.
    """
    
    # 1. Determine Skill Path
    final_skill_path = skill_path or os.getenv("SKILL_PATH")
    
    analyze_agent_tools = []
    analyze_agent_instructions = ""
    
    # 2. Dynamic Skill Loading
    if final_skill_path:
        if os.path.exists(final_skill_path):
            logger.info(f"Loading skills from: {final_skill_path}")
            loader = SkillLoader(final_skill_path)
            loader.load_skills()
            
            # Specifically retrieve for bug_analyze_agent
            analyze_agent_tools = loader.get_tools_for_agent("bug_analyze_agent")
            analyze_agent_instructions = loader.get_instruction_suffix_for_agent("bug_analyze_agent")
            
            logger.info(f"Injected {len(analyze_agent_tools)} tools into bug_analyze_agent.")
        else:
            logger.warning(f"SKILL_PATH defined but not found: {final_skill_path}")

    # 3. Create Sub-Agents
    # Note: Only bug_analyze_agent supports injection currently. 
    # To support others, their agent.py needs similar refactoring.
    
    analyze_agent_instance = create_bug_analyze_agent(
        extra_tools=analyze_agent_tools,
        instruction_suffix=analyze_agent_instructions
    )

    # 4. Create Root Agent
    root_agent = LlmAgent(
        name="bug_scene_agent",
        prompt=ROOT_AGENT_PROMPT,
        sub_agents=[
            bug_base_info_collect_agent,
            analyze_agent_instance,
            bug_report_agent,
            bug_reproduce_steps_agent,
        ],
        before_agent_callback=before_agent_callback
    )

    # 5. Create App
    app = App(
        name="bug_scene_app",
        root_agent=root_agent,
        context_cache_config=ContextCacheConfig(
            min_tokens=2048,
            ttl_seconds=600,
            cache_intervals=10,
        )
        # context_cache_config=None,
    )
    
    return app
