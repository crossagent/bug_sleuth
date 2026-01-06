from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from ..shared_libraries import constants
from . import prompt

from ..shared_libraries.constants import MODEL

import logging

logger = logging.getLogger(__name__)

from typing import Optional, List
from google.adk.tools import BaseTool
from ..skill_library.extensions import report_skill_registry

bug_report_agent = Agent(
    name="bug_report_agent",
    model=MODEL,
    description=(
        "Agent to confirm if user want to deliver result to platform."
    ),
    instruction=prompt.USER_INTENT_PROMPT,
    output_key="report_bug_info",
    tools=[report_skill_registry]
)


