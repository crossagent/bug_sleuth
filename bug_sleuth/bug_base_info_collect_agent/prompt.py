from bug_sleuth.shared_libraries.state_keys import StateKeys

BASE_BUG_INFO_COLLECT_PROMPT = """
目前已知bug的必须包含的信息有：
1. bug的描述信息
2. bug发生的时间
3. bug发生的分支
4. bug发生的设备

目前已知
bug的描述信息为：{bug_description}
bug发生的时间为：{bug_occurrence_time}
bug发生的分支为：{productBranch}
bug发生的设备类型为：{device_info}
bug发生的设备名称为：{device_name}

当前的时间是：{cur_date_time}，如果用户提及是相对于现在的时间，可以用这个时间换算。

如果bug信息中还缺少必要的信息，就主动询问用户。
    """

def get_prompt()-> str:
    return BASE_BUG_INFO_COLLECT_PROMPT.format(
        bug_description=f"{{{StateKeys.BUG_DESCRIPTION}}}",
        bug_occurrence_time=f"{{{StateKeys.BUG_OCCURRENCE_TIME}}}",
        productBranch=f"{{{StateKeys.PRODUCT_BRANCH}}}",
        device_info=f"{{{StateKeys.DEVICE_INFO}}}",
        device_name=f"{{{StateKeys.DEVICE_NAME}}}",
        cur_date_time=f"{{{StateKeys.CUR_DATE_TIME}}}"
    )