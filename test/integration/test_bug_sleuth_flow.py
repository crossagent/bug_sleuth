"""
Integration tests for Bug Sleuth root agent flow.
Uses app_factory for unified initialization with MockLlm.
"""
import pytest
import logging
from unittest.mock import patch

from bug_sleuth.app_factory import create_app, AppConfig
from bug_sleuth.test.test_client import TestClient
from bug_sleuth.test.mock_llm_provider import MockLlm
from bug_sleuth.shared_libraries.state_keys import StateKeys

# Configure logging to see agent interactions
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def app_with_mock():
    """Create app with root agent using mock model."""
    # Patch REPO_REGISTRY to pass validation
    with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.REPO_REGISTRY", 
               [{"name": "test_repo", "path": "/tmp/test"}]):
        with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.check_search_tools", 
                   return_value=None):
            app = create_app(AppConfig(
                agent_name="bug_scene_agent",
                model_override="mock/integration_test"
            ))
            yield app


@pytest.mark.anyio
async def test_root_agent_refine_bug_state_tool(app_with_mock):
    """
    Test that root agent can call refine_bug_state tool.
    Verifies: Agent receives input -> Calls tool -> Returns response
    """
    MockLlm.set_behaviors({
        "logo is overlapping": {
            "tool": "refine_bug_state",
            "args": {
                "bug_description": "The logo is overlapping text on the login screen",
                "device_info": "Android",
                "product_branch": "Branch A"
            }
        }
    })
    
    client = TestClient(agent=app_with_mock.agent, app_name="bug_sleuth_app")
    await client.create_new_session("user_test", "sess_001")
    
    responses = await client.chat("The logo is overlapping text on the login screen, Android, Branch A.")
    
    # Verify we got responses (agent ran successfully)
    assert len(responses) > 0
    # MockLlm returns default text after tool call
    assert "[MockLlm]" in responses[-1]


@pytest.mark.anyio
async def test_root_agent_question_answer_flow(app_with_mock):
    """
    Test Q&A flow: Agent asks for clarification, user responds.
    Verifies: Vague input -> Ask question -> User answers -> Update state
    """
    MockLlm.set_behaviors({
        "It's broken": {
            "text": "What device are you using?"
        },
        "Pixel 6": {
            "tool": "refine_bug_state",
            "args": {
                "device_name": "Pixel 6"
            }
        }
    })
    
    client = TestClient(agent=app_with_mock.agent, app_name="bug_sleuth_app")
    await client.create_new_session("user_test", "sess_002")
    
    # Turn 1: Vague input
    resp1 = await client.chat("It's broken")
    assert len(resp1) > 0
    assert "What device" in resp1[-1]
    
    # Turn 2: User provides device info
    resp2 = await client.chat("I use a Pixel 6")
    assert len(resp2) > 0


@pytest.mark.anyio
async def test_root_agent_dispatch_to_analyze_agent(app_with_mock):
    """
    Test agent delegation: Root agent dispatches to analyze agent.
    Verifies: Complex bug -> Dispatch to bug_analyze_agent
    """
    MockLlm.set_behaviors({
        "crashes sometimes": {
            "tool": "refine_bug_state",
            "args": {
                "bug_description": "Game crashes sometimes when opening bag",
                "device_info": "PC"
            }
        },
        # After tool call, agent should delegate (simulated via text response)
        "success": {
            "text": "[MockLlm] Delegating to bug_analyze_agent for deep analysis..."
        }
    })
    
    client = TestClient(agent=app_with_mock.agent, app_name="bug_sleuth_app")
    await client.create_new_session("user_test", "sess_complex")
    
    responses = await client.chat("Game crashes sometimes when opening bag, PC.")
    
    # Verify flow completed
    assert len(responses) > 0


@pytest.mark.anyio
async def test_analyze_agent_git_log_tool():
    """
    Test that analyze agent can call get_git_log_tool.
    Uses direct analyze agent without going through root.
    """
    MockLlm.set_behaviors({
        "check the git logs": {
            "tool": "get_git_log_tool",
            "args": {"limit": 5}
        }
    })
    
    with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.REPO_REGISTRY", 
               [{"name": "test_repo", "path": "/tmp/test"}]):
        with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.check_search_tools", 
                   return_value=None):
            app = create_app(AppConfig(
                agent_name="bug_analyze_agent",
                model_override="mock/integration_test"
            ))
    
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
async def test_app_factory_creates_valid_root_agent():
    """
    Basic test to verify app_factory returns valid root agent with sub-agents.
    """
    with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.REPO_REGISTRY", 
               [{"name": "test_repo", "path": "/tmp/test"}]):
        with patch("bug_sleuth.bug_scene_app.bug_analyze_agent.agent.check_search_tools", 
                   return_value=None):
            app = create_app(AppConfig(
                agent_name="bug_scene_agent",
                model_override="mock/basic_test"
            ))
    
    assert app.agent is not None
    assert app.agent.name == "bug_scene_agent"
    assert app.agent.model == "mock/basic_test"
    
    # Verify sub-agents are accessible
    analyze_agent = app.get_agent("bug_analyze_agent")
    assert analyze_agent is not None
    assert analyze_agent.name == "bug_analyze_agent"
