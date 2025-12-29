from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from agents.shared_libraries import constants
from . import prompt
from . import tools
from agents.shared_libraries.constants import MODEL

import logging

logger = logging.getLogger(__name__)

bug_report_agent = Agent(
    name="bug_report_agent",
    model=MODEL,
    description=(
        "Agent to confirm if user want to deliver result to platform."
    ),
    instruction=prompt.USER_INTENT_PROMPT,
    output_key="report_bug_info",
    tools=[tools.submit_bug_report]
)
