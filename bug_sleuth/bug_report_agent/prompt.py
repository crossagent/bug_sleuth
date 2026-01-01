from pydantic import BaseModel, Field
from typing import Optional

USER_INTENT_PROMPT = """
不需要询问任何问题，直接使用工具submit_bug_report将bug的信息提交到平台，工具会自行组织信息，唤起即可。
    """