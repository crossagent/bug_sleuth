import logging
from typing import Optional
from google.adk.tools import ToolContext
from bug_sleuth.shared_libraries.state_keys import StateKeys

logger = logging.getLogger(__name__)

def refine_bug_state(
    tool_context: ToolContext,
    bug_description: Optional[str] = None,
    occurrence_time: Optional[str] = None,
    product_branch: Optional[str] = None,
    device_info: Optional[str] = None,
    device_name: Optional[str] = None,
    fps: Optional[str] = None,
    ping: Optional[str] = None,
    nick_name: Optional[str] = None,
    client_version: Optional[str] = None
) -> str:
    """
    Refine and update the bug state with new or corrected information.
    
    Args:
        bug_description: Detailed description of the bug.
        occurrence_time: Time when the bug occurred.
        product_branch: The code branch where the bug is found.
        device_info: Platform information (e.g., Android 12, iOS 15).
        device_name: Specific device model (e.g., Pixel 6, iPhone 13).
        fps: Frame per second at the time of the bug.
        ping: Network latency (ms).
        nick_name: User's nickname.
        client_version: The version of the client software.
    """
    state = tool_context.state
    updated_fields = []

    if bug_description:
        state[StateKeys.BUG_DESCRIPTION] = bug_description
        updated_fields.append(StateKeys.BUG_DESCRIPTION)
    
    if occurrence_time:
        state[StateKeys.BUG_OCCURRENCE_TIME] = occurrence_time
        updated_fields.append(StateKeys.BUG_OCCURRENCE_TIME)
        
    if product_branch:
        state[StateKeys.PRODUCT_BRANCH] = product_branch
        updated_fields.append(StateKeys.PRODUCT_BRANCH)
        
    if device_info:
        state[StateKeys.DEVICE_INFO] = device_info
        updated_fields.append(StateKeys.DEVICE_INFO)
        
    if device_name:
        state[StateKeys.DEVICE_NAME] = device_name
        updated_fields.append(StateKeys.DEVICE_NAME)

    if fps:
        state[StateKeys.FPS] = fps
        updated_fields.append(StateKeys.FPS)

    if ping:
        state[StateKeys.PING] = ping
        updated_fields.append(StateKeys.PING)

    if nick_name:
        state[StateKeys.NICK_NAME] = nick_name
        updated_fields.append(StateKeys.NICK_NAME)

    if client_version:
        state[StateKeys.CLIENT_VERSION] = client_version
        updated_fields.append(StateKeys.CLIENT_VERSION)
        
    if not updated_fields:
        return "No information provided to update."

    return f"Successfully updated fields: {', '.join(updated_fields)}"
