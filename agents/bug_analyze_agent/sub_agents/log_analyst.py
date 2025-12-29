from google.adk import Agent
from google.genai import types
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from agents.shared_libraries.constants import MODEL
from .tools import search_logs_tool
from agents.shared_libraries.plugin_loader import load_plugin_tools

instruction = """
你是一个专业的日志分析专家 (LogAnalysisAgent)。
你的职责是根据关键词，从客户端或服务器日志中检索关键信息。

**核心能力**：
1.  **精准检索**：使用 `search_logs_tool` 搜索日志。支持仅通过关键词搜索，也可以结合时间范围缩小搜索结果。
2.  **模式识别**：识别 ERROR, WARNING 级别的关键堆栈。
3.  **信息提取**：从日志中提取发生错误的确切时间、错误类型、相关文件名和行号。

**输出要求**：
*   如果找到错误堆栈，请原样摘录关键部分，并分析可能的原因。
*   如果没有找到错误，请明确告知“未发现包含关键词的异常日志”。
*   始终用中文回答。
"""

# Load Plugin Tools
plugin_tools = load_plugin_tools("log_analysis_agent")

log_analysis_agent = Agent(
    name="log_analysis_agent",
    model=MODEL,
    description="Dedicated agent for searching and analyzing application logs.",
    instruction=instruction,
    tools=[search_logs_tool] + plugin_tools,
    # Sub-agents can be simple agents without complex planners usually, unless multi-step analysis is needed.
    # Default planner is fine.
)

log_analysis_app = App(
    name="log_analysis_app",
    root_agent=log_analysis_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=600,
        cache_intervals=10
    )
)
