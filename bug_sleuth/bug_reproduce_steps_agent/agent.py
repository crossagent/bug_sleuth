from google.adk import Agent
from . import prompt
from bug_sleuth.shared_libraries import constants
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from typing import Optional
import json
import logging
from pydantic import BaseModel, Field
from typing import Optional
from google.genai import types
from bug_sleuth.shared_libraries import constants
from bug_sleuth.shared_libraries.state_keys import AgentKeys,StateKeys

# 获取当前模块的 logger。它会自动继承 "bug_sleuth" logger 的配置
logger = logging.getLogger(__name__)

class BugReproduceSteps(BaseModel):
    """Bug重现步骤信息结构体"""
    bug_description: str = Field(description="bug现象的描述")
    reproduce_steps: str = Field(description="如果没有进行深入分析，以用户的描述为准。如果分析出了真正的原因，就进一步完善重现步骤。但不要脱离用户的描述")
    guess_cause: Optional[str] = Field(default=None, description="用户对bug可能原因的推测或初步分析，不明确可以不填，明确的一定要带证据来源")
    reproduce_confidence: int = Field(default=1, description="重现信心，1-10分，1分表示不确定，10分表示非常确定")

def init_before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    pass

def determine_reproduce_steps_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    try:
        text_content = callback_context.state.get(AgentKeys.BUG_INFO, "{}")
        if text_content:
            bug_info = BugReproduceSteps.model_validate(text_content)

            callback_context.state[StateKeys.BUG_DESCRIPTION] = bug_info.bug_description
            callback_context.state[StateKeys.BUG_REPRODUCTION_STEPS] = bug_info.reproduce_steps
            callback_context.state[StateKeys.BUG_REPRODUCTION_CONFIDENCE] = bug_info.reproduce_confidence
            callback_context.state[StateKeys.BUG_REPRODUCTION_GUESS_CAUSE] = bug_info.guess_cause

            if bug_info.reproduce_confidence >= 8:
                content=types.Content(role="model", parts=[types.Part.from_text(
                    text=f"我很有信心能重现，重现步骤为{bug_info.reproduce_steps}")
                ])
            else:
                content=types.Content(role="model", parts=[types.Part.from_text(
                    text=f"当前重现信心为{bug_info.reproduce_confidence}，满分10分，是否选择让我尝试分析一下提升信心还是上报反馈BUG？有更多信息要补充吗？")
                ])

            return content
    except Exception as e:
        logger.error(f"Error determining bug info: {e}")
        return None

bug_reproduce_steps_agent = Agent(
    model=constants.MODEL,
    name="bug_reproduce_steps_agent",
    description="A helpful agent to extract bug information",
    instruction=prompt.EXTRACT_BUG_INFO_PROMPT,
    output_key=AgentKeys.BUG_INFO,
    output_schema=BugReproduceSteps,
    before_agent_callback=init_before_agent_callback,
    after_agent_callback=determine_reproduce_steps_callback,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
