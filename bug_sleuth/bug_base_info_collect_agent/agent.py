from google.adk.agents import Agent
from . import prompt
from bug_sleuth.shared_libraries import constants
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
import json
import logging
from pydantic import BaseModel, Field
from typing import Optional
from bug_reproduce_steps_agent.agent import bug_reproduce_steps_agent
from pydantic import BaseModel, Field
from google.genai import types
from bug_sleuth.shared_libraries.state_keys import StateKeys
from datetime import datetime

# 获取当前模块的 logger。它会自动继承 "bug_sleuth" logger 的配置
logger = logging.getLogger(__name__)

class BugEssentialInfo(BaseModel):
    bug_description: str = Field(description="Bug的描述信息")
    occurrence_time: str = Field(description="Bug发生的时间,类似于'2023年10月01日 12:00:00'")
    branch: str = Field(description="Bug发生的分支")
    device: str = Field(description="Bug发生的设备")
    is_complete: bool = Field(default=False, description="bug基础信息是否完整")
    additional_questions: Optional[str] = Field(default=None, description="如果bug信息不完整，询问用户需要补充哪些信息")

def determine_bug_info_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    try:
        text_content = callback_context.state.get("bug_essential_info", "{}")
        if text_content:
            bug_info = BugEssentialInfo.model_validate(text_content)

            if bug_info.is_complete:
                callback_context.state[StateKeys.BUG_INFO_COMPLETED] = True
                callback_context.state[StateKeys.BUG_OCCURRENCE_TIME] = bug_info.occurrence_time

                content=types.Content(role="model", parts=[types.Part.from_text(
                    text=f"确认bug发生时间为{bug_info.occurrence_time}")
                ])
            else:
                callback_context.state[StateKeys.BUG_INFO_COMPLETED] = False

                content=types.Content(role="model", parts=[types.Part.from_text(
                    text=bug_info.additional_questions or "bug信息不完整，请提供更多细节。")
                ])

            return content
    except Exception as e:
        logger.error(f"Error determining bug info: {e}")
        return None

def init_before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    if not callback_context.state.get(StateKeys.BUG_OCCURRENCE_TIME):
        callback_context.state[StateKeys.BUG_OCCURRENCE_TIME] = "未知"

    if not callback_context.state.get(StateKeys.BUG_DESCRIPTION):
        callback_context.state[StateKeys.BUG_DESCRIPTION] = "未知"
    
    # 获取当前时间（带时区）
    current_time = datetime.now(constants.USER_TIMEZONE)
    
    # 添加当前时间信息，格式化为年月日
    cur_date_time = current_time.strftime("%Y年%m月%d日 %H:%M:%S")
    callback_context.state[StateKeys.CUR_DATE_TIME] = cur_date_time  

bug_base_info_collect_agent = Agent(
    model=constants.MODEL,
    name="bug_base_info_collect_agent",
    description="A helpful agent to ensure that the bug report contains all necessary information.",
    instruction=prompt.get_prompt(),
    output_key="bug_essential_info",
    output_schema=BugEssentialInfo,
    before_agent_callback=init_before_agent_callback,
    after_agent_callback=determine_bug_info_callback,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)