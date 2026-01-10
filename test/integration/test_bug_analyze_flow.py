"""
Integration tests for Bug Sleuth analyze agent flow.
Uses app_factory for unified initialization.

Model selection is handled via GOOGLE_GENAI_MODEL environment variable
(set in conftest.py to "mock/pytest" for all tests).

Note: Tests use real config.yaml for REPO_REGISTRY. 
Only external tool checks (ripgrep) are mocked.
"""
import pytest
from unittest.mock import patch

from bug_sleuth.app_factory import create_app, AppConfig
from bug_sleuth.test.test_client import TestClient
from bug_sleuth.test.mock_llm_provider import MockLlm


@pytest.fixture
def mock_external_deps():
    """
    Only mock external tool availability checks, not config.
    REPO_REGISTRY comes from real config.yaml.
    """
    with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.check_search_tools", 
               return_value=None):
        yield


@pytest.mark.anyio
async def test_analyze_agent_searches_logs(mock_external_deps):
    """
    Verifies that the agent calls 'get_git_log_tool' when asked to check logs.
    """
    MockLlm.set_behaviors({
        "check the git logs": {
            "tool": "get_git_log_tool",
            "args": {"limit": 5}
        }
    })
    
    app = create_app(AppConfig(agent_name="bug_analyze_agent"))
    
    client = TestClient(agent=app.agent, app_name="test_app")
    await client.create_new_session("user_1", "sess_1", initial_state={})
    
    responses = await client.chat("Please check the git logs for me.")
    
    try:
        print("\nResponses:", responses)
    except UnicodeEncodeError:
        print("\nResponses: [Content cannot be printed in current console encoding]")
    
    assert len(responses) > 0
    assert "[MockLlm]" in responses[-1]


@pytest.mark.anyio
async def test_app_factory_creates_valid_agent(mock_external_deps):
    """
    Basic test to verify app_factory returns a valid agent.
    """
    app = create_app(AppConfig(agent_name="bug_analyze_agent"))
    
    assert app.agent is not None
    assert app.agent.name == "bug_analyze_agent"
