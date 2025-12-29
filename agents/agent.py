from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.genai import types
from google.adk.sessions import State
from agents.shared_libraries.state_keys import StateKeys
import uuid
import logging
import os
from typing import Optional

# Sub-agents
from bug_analyze_agent import bug_analyze_agent
from bug_reproduce_steps_agent import bug_reproduce_steps_agent
from bug_report_agent import bug_report_agent
from bug_base_info_collect_agent.agent import bug_base_info_collect_agent

# Prompt
from prompt import ROOT_AGENT_PROMPT

logger = logging.getLogger(__name__)

# Environment check
_IS_TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

async def file_content_check(ctx: InvocationContext) -> Optional[types.Content]:
    """Check if there are any inline data parts in user_content and save them as artifacts."""

    if not ctx.user_content or not ctx.user_content.parts:
        return None
    
    # Check for inline_data
    has_inline_data = False
    for part in ctx.user_content.parts:
        if hasattr(part, 'inline_data') and part.inline_data is not None:
            has_inline_data = True
            break
    
    if not has_inline_data:
        return None
    
    nick_name = ctx.session.state.get('nickName', 'user')
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    parts_to_remove = []
    saved_files = []
    large_files = []
    
    MAX_FILE_SIZE = 10 * 1024 * 1024

    for i, part in enumerate(ctx.user_content.parts):
        if hasattr(part, 'inline_data') and part.inline_data is not None:
            parts_to_remove.append(i)
            
            file_data = part.inline_data.data
            file_size = len(file_data) if file_data else 0
            
            mime_type = part.inline_data.mime_type
            extension = ""
            if mime_type:
                if "image/jpeg" in mime_type:
                    extension = "jpg"
                elif "text/plain" in mime_type:
                    extension = "txt"
                else:
                    extension = mime_type.split('/')[-1] if '/' in mime_type else "dat"
            
            filename = f"{nick_name}_{timestamp}_{uuid.uuid4()}.{extension}"
            
            if file_size > MAX_FILE_SIZE:
                file_size_mb = file_size / (1024 * 1024)
                large_files.append(f"{filename} ({file_size_mb:.1f}MB)")
                logger.info(f"File {filename} is too large ({file_size_mb:.1f}MB), skipping save.")
            else:
                try:
                    version = await ctx.artifact_service.save_artifact(  #type: ignore
                        session_id=ctx.session.id,
                        user_id=ctx.user_id,           
                        app_name=ctx.app_name,
                        filename=filename, 
                        artifact=part
                    )  
                    print(f"Successfully saved artifact '{filename}' as version {version}.")
                    saved_files.append(filename)
                    ctx.session.state["filename"] = version 

                except ValueError as e:
                    print(f"Error saving artifact: {e}. Is ArtifactService configured in Runner?")
                except Exception as e:
                    print(f"An unexpected error occurred during artifact save: {e}")
    
    for i in reversed(parts_to_remove):
        ctx.user_content.parts.pop(i)

    messages = []
    if saved_files:
        files_list = "、".join(saved_files)
        messages.append(f"已成功保存文件：{files_list}")
    
    if large_files:
        large_files_list = "、".join(large_files)
        messages.append(f"以下文件超过10MB限制，未能保存：{large_files_list}")
    
    if messages:
        final_message = "。".join(messages)
        if large_files and not saved_files:
            final_message += "。过大的文件目前还不支持上传。"
        elif saved_files:
            final_message += "。因为分析非文本信息较为昂贵，目前仅仅支持上传。"
        
        return types.Content(parts=[types.Part(text=final_message)])
    else:
        return types.Content(parts=[types.Part(text="检测到文件上传，但处理过程中出现问题。请重新上传文件或直接描述您的问题。")])


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

# Instantiate the root agent directly
root_agent = LlmAgent(
    name="bug_scene_agent",
    prompt=ROOT_AGENT_PROMPT,
    sub_agents=[
        bug_base_info_collect_agent,
        bug_analyze_agent,
        bug_report_agent,
        bug_reproduce_steps_agent,
    ],
    before_agent_callback=before_agent_callback
)

# Wrap with App for context caching support
app = App(
    name="bug_scene_app",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,    # Minimum tokens to trigger caching
        ttl_seconds=600,    # Store for up to 10 minutes
        cache_intervals=10, # Refresh after 10 uses
    )
)