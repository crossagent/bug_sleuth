"""
Application Factory - Unified App Initialization

Usage:
    # Server (root agent)
    app = create_app(AppConfig(skill_path="skills", config_file="config.yaml"))
    root_agent = app.agent
    
    # Testing with Mock LLM (set via environment variable)
    # GOOGLE_GENAI_MODEL=mock/test python -m pytest
    app = create_app(AppConfig(agent_name="bug_analyze_agent"))
    client = AgentTestClient(agent=app.agent)

Model selection is now handled via GOOGLE_GENAI_MODEL environment variable:
- "gemini-2.0-flash" (default) -> Native Gemini
- "mock/xxx" -> MockLlm for testing
- "openai/gpt-4o" -> LiteLLM for OpenAI
- "anthropic/claude-3" -> LiteLLM for Anthropic
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Literal, Any

logger = logging.getLogger(__name__)

# Supported agent names
AgentName = Literal["bug_scene_agent", "bug_analyze_agent", "bug_report_agent"]


@dataclass
class AppConfig:
    """Configuration for application initialization."""
    
    # Agent selection
    agent_name: AgentName = "bug_analyze_agent"  # Default for backward compatibility
    
    # Paths
    skill_path: Optional[str] = None
    config_file: Optional[str] = None
    
    # Environment overrides (alternative to env vars)
    env_overrides: dict = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create config from environment variables."""
        return cls(
            skill_path=os.getenv("SKILL_PATH"),
            config_file=os.getenv("CONFIG_FILE"),
        )


class BugSleuthApp:
    """
    Lightweight application container.
    Holds the configured agent and related components.
    """
    
    def __init__(self, agent: Any, skill_registry_stats: dict = None, all_agents: dict = None):
        self.agent = agent
        self.root_agent = agent  # ADK convention
        self.skill_registry_stats = skill_registry_stats or {}
        self._all_agents = all_agents or {}
    
    def get_agent(self, name: str = None) -> Any:
        """Returns the specified agent instance (or main agent if name is None)."""
        if name is None:
            return self.agent
        return self._all_agents.get(name, self.agent)


def create_app(config: AppConfig = None) -> BugSleuthApp:
    """
    Factory function to create a fully configured application.
    
    This function:
    1. Applies environment overrides
    2. Loads skills into global registries
    3. Loads configuration file
    4. Imports and returns the selected agent
    
    Note: Model selection is now handled via GOOGLE_GENAI_MODEL environment variable
    in constants.py, not via app_factory parameters.
    
    Args:
        config: Application configuration. If None, uses environment defaults.
    
    Returns:
        BugSleuthApp instance with configured agent.
    """
    config = config or AppConfig.from_env()
    
    # 1. Apply environment overrides
    for key, value in config.env_overrides.items():
        os.environ[key] = str(value)
    
    # 2. Set config file path (before agent import)
    if config.config_file:
        os.environ["CONFIG_FILE"] = os.path.abspath(config.config_file)
        logger.info(f"Set CONFIG_FILE to {os.environ['CONFIG_FILE']}")
    
    # 3. Load Skills (before agent import so registries are populated)
    skill_stats = _load_skills(config.skill_path)
    
    # 4. Import agents based on selection
    # Note: Model is determined by GOOGLE_GENAI_MODEL env var at constants.py import time
    agents_dict = {}
    selected_agent = None
    
    if config.agent_name == "bug_scene_agent":
        from bug_sleuth.bug_scene_app.agent import bug_scene_agent
        from bug_sleuth.bug_scene_app.bug_analyze_agent.agent import bug_analyze_agent
        from bug_sleuth.bug_scene_app.bug_report_agent.agent import bug_report_agent
        
        selected_agent = bug_scene_agent
        agents_dict = {
            "bug_scene_agent": bug_scene_agent,
            "bug_analyze_agent": bug_analyze_agent,
            "bug_report_agent": bug_report_agent,
        }
            
    elif config.agent_name == "bug_analyze_agent":
        from bug_sleuth.bug_scene_app.bug_analyze_agent.agent import bug_analyze_agent
        selected_agent = bug_analyze_agent
        agents_dict = {"bug_analyze_agent": bug_analyze_agent}
            
    elif config.agent_name == "bug_report_agent":
        from bug_sleuth.bug_scene_app.bug_report_agent.agent import bug_report_agent
        selected_agent = bug_report_agent
        agents_dict = {"bug_report_agent": bug_report_agent}
    
    logger.info(f"App created with agent: {config.agent_name}")
    
    return BugSleuthApp(
        agent=selected_agent,
        skill_registry_stats=skill_stats,
        all_agents=agents_dict
    )


def _load_skills(skill_path: Optional[str]) -> dict:
    """Load skills and return registry stats."""
    from bug_sleuth.skill_library.skill_loader import SkillLoader
    from bug_sleuth.skill_library.extensions import (
        root_skill_registry, 
        report_skill_registry, 
        analyze_skill_registry
    )
    
    path = skill_path
    if not path:
        # Auto-discover from CWD
        if os.path.exists("skills") and os.path.isdir("skills"):
            path = "skills"
    
    if path and os.path.exists(path):
        abs_path = os.path.abspath(path)
        logger.info(f"Loading skills from: {abs_path}")
        SkillLoader(abs_path).load_skills()
    else:
        logger.info("No skill path provided or found. Skipping skill loading.")
    
    # Return stats for debugging/logging
    return {
        "root": len(root_skill_registry._tools),
        "report": len(report_skill_registry._tools),
        "analyze": len(analyze_skill_registry._tools),
    }
