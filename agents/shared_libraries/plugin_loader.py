import os
import importlib
import logging
from typing import List, Any
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

def load_plugin_tools(agent_name: str) -> List[Any]:
    """
    Dynamically loads external tools configured specifically for the given agent.
    
    Configuration Source:
        Environment Variable: ADK_TOOLS_{AGENT_NAME_UPPER}
        Format: "module.path.tool_function_name, another.module.tool_name"
    
    Args:
        agent_name (str): The name of the agent (e.g., "bug_analyze_agent").
    
    Returns:
        List[FunctionTool]: A list of loaded FunctionTool objects.
    """
    env_key = f"ADK_TOOLS_{agent_name.upper()}"
    plugin_config = os.getenv(env_key, "")
    
    if not plugin_config:
        logger.debug(f"No external tools configured for {agent_name} (Env: {env_key})")
        return []

    loaded_tools = []
    logger.info(f"Loading external tools for {agent_name} from {env_key}='{plugin_config}'")

    for path in plugin_config.split(","):
        path = path.strip()
        if not path:
            continue
            
        try:
            # Expected format: "package.module.function_name"
            if "." not in path:
                logger.error(f"Invalid tool path format '{path}'. Expected 'module.function'.")
                continue
                
            module_path, func_name = path.rsplit(".", 1)
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the function
            tool_func = getattr(module, func_name)
            
            # Wrap in FunctionTool
            # Assuming external tools are compliant FunctionTools or raw functions
            if isinstance(tool_func, FunctionTool):
                tool_instance = tool_func
            else:
                tool_instance = FunctionTool(tool_func)
                
            loaded_tools.append(tool_instance)
            logger.info(f"✅ Successfully loaded external tool: {func_name} from {module_path}")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import module for tool '{path}': {e}")
        except AttributeError as e:
            logger.error(f"❌ Module '{module_path}' has no attribute '{func_name}': {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error loading tool '{path}': {e}")
            
    return loaded_tools
