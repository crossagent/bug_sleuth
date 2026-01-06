import os
import sys
import uuid
import importlib.util
import importlib.machinery
import logging
from typing import List, Optional, Type, Dict, Any
from google.adk.tools import FunctionTool, BaseTool
from google.adk.tools.base_toolset import BaseToolset
import yaml

logger = logging.getLogger(__name__)

class SkillLoader:
    def __init__(self, skill_path: str):
        self.skill_path = skill_path

    def load_skills(self) -> None:
        """
        Scans and imports .py modules from the skill directory.
        Importing the module triggers the self-registration logic in the skill code.
        """
        if not os.path.exists(self.skill_path):
            logger.warning(f"Skill path does not exist: {self.skill_path}")
            return

        logger.info(f"Loading skills from: {self.skill_path}")
        
        # Recursively search for .py files
        for root, dirs, files in os.walk(self.skill_path):
             for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    module_path = os.path.join(root, file)
                    self._load_module(module_path)

    def _load_module(self, module_path: str):
        module_name = f"skill_module_{uuid.uuid4().hex}"
        try:
            # Load Module to trigger side-effects (registrations)
            loader = importlib.machinery.SourceFileLoader(module_name, module_path)
            spec = importlib.util.spec_from_loader(loader.name, loader)
            if not spec or not spec.loader:
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            logger.info(f"Loaded skill module: {module_path}")
                        
        except Exception as e:
            logger.error(f"Failed to load module {module_path}: {e}")



