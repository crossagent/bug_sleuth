# 定义所有状态键的常量
class StateKeys:
    DEVICE_INFO = "deviceInfo"
    DEVICE_NAME = "deviceName"

    BUG_INFO_COMPLETED = "bug_info_completed"
    BUG_DESCRIPTION = "bug_description"
    BUG_USER_DESCRIPTION = "bug_user_description"
    PRODUCT_BRANCH = "productBranch"
    PRODUCT = "product"
    CLIENT_LOG_URL = "clientLogUrl"
    CLIENT_LOG_URLS = "clientLogUrls"  # LIST
    CLIENT_SCREENSHOT_URLS = "clientScreenshotUrls"  # LIST
    CLIENT_VERSION = "clientVersion"
    SERVER_ID = "serverId"
    ROLE_ID = "roleId"
    NICK_NAME = "nickName"
    BUG_OCCURRENCE_TIME = "bug_occurrence_time"
    FPS = "fps"
    PING = "ping"

    CUR_DATE_TIME = "cur_date_time"
    CUR_TIMESTAMP = "cur_timestamp"
    CURRENT_OS = "current_os"

    USER_INTENT = "user_intent"

    BUG_DESCRIPTION = "bug_description"
    BUG_REPRODUCTION_STEPS = "bug_reproduction_steps"
    BUG_REPRODUCTION_CONFIDENCE = "bug_reproduction_confidence"
    BUG_REPRODUCTION_GUESS_CAUSE = "bug_reproduction_guess_cause"

    CURRENT_INVESTIGATION_PLAN = "current_investigation_plan"
    STEP_COUNT = "step_count"


class AgentKeys:
    BUG_REASON = "bug_reason_agent"
    USER_INTENT = "user_intent_agent"
    BUG_INFO = "bug_info_agent"
    BUG_REPORT = "bug_report_agent"