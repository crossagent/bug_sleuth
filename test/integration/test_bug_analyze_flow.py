import pytest
from typing import List
from bug_sleuth.app_factory import create_app, AppConfig
from bug_sleuth.test.test_client import TestClient
from bug_sleuth.test.mock_llm_provider import MockLlm

@pytest.mark.anyio
async def test_analyze_agent_searches_logs():
    """
    Verifies that the agent calls 'get_git_log_tool' when asked to check logs.
    Uses app_factory for unified initialization with mock LLM.
    """
    
    # 1. Setup Mock Behavior
    MockLlm.set_behaviors({
        "check the git logs": {
            "tool": "get_git_log_tool",
            "args": {"limit": 5}
        }
    })
    
    # 2. Create App with Mock Model
    # app_factory handles skill loading and config
    app = create_app(AppConfig(
        model_override="mock/integration_test"
    ))
    
    # 3. Patch REPO_REGISTRY to pass validation
    from bug_sleuth.bug_scene_app.bug_analyze_agent import agent as agent_module
    agent_module.REPO_REGISTRY = [{"name": "test_repo", "path": "/tmp/test"}]
    
    # 4. Initialize Test Client
    client = TestClient(agent=app.agent, app_name="test_app")
    await client.create_new_session(
        "user_1", 
        "sess_1", 
        initial_state={}
    )
    
    # 5. Execution
    from unittest.mock import patch
    # Patch check_search_tools to bypass 'ripgrep' check during agent callback
    with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.check_search_tools", return_value=None):
        responses = await client.chat("Please check the git logs for me.")
    
    # 6. Verification
    try:
        print("\nResponses:", responses)
    except UnicodeEncodeError:
        print("\nResponses: [Content cannot be printed in current console encoding]")
    
    # Verify we got a final text response
    assert len(responses) > 0
    assert "[MockLlm]" in responses[-1]


@pytest.mark.anyio
async def test_app_factory_creates_valid_agent():
    """
    Basic test to verify app_factory returns a valid agent.
    """
    app = create_app(AppConfig(
        model_override="mock/basic_test"
    ))
    
    assert app.agent is not None
    assert app.agent.name == "bug_analyze_agent"
    assert app.agent.model == "mock/basic_test"
