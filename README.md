# BugSleuth

**打破大工程团队的信息传递壁垒，让修复 Bug 回归逻辑本身。**

> "修 bug 最重要的是提一个好的 bug 描述。"

在数百人的大型工程团队中，修复 Bug 的瓶颈往往不在于“怎么改代码”，而在于**信息传递**：QA 发现问题，试图描述现场；开发尝试复现，却因环境不同而失败；相互拉扯中浪费了大量时间。

**BugSleuth** 致力于解决这一痛点。它不仅仅是一个调试工具，更是一个**智能化的信息传递与分析管道**。

## 核心理念 (Core Concept)

我们的工具旨在打通过去割裂的调试环节：

1.  **快速截取现场 (Snapshot)**：在一键之间，捕获完整的环境上下文、日志、截图与内存状态。
2.  **业务逻辑分析 (Logic Analysis)**：不只是 grep 错误码，而是基于对业务逻辑的理解（Agent）去分析异常。
3.  **明确重现步骤 (Stable Repro)**：这是最关键的一步。系统产出的不是模糊的猜测，而是**明确、稳定、可执行的重现步骤**。
4.  **精准修复 (Fix)**：基于确定的重现步骤，修复变的有的放矢。

## 工作流 (The Pipeline)

```mermaid
flowchart LR
    subgraph Context ["现场 (The Scene)"]
        direction TB
        Logs[日志/Logs]
        State[状态/State]
        Screen[截图/Screenshot]
    end

    subgraph Gap ["信息传递瓶颈 (The Gap)"]
        direction TB
        Transfer[❌ 口头描述/模糊文档]
        Miss[❌ 关键信息丢失]
    end

    subgraph Solution ["BugSleuth 管道"]
        direction TB
        Analyzer[🕵️‍♂️ ID-Bot (侦探回溯)]
        Repro[🔁 生成重现步骤 (Repro Steps)]
        Fix[🛠️ 辅助修复 (Fix)]
    end

    Context --> Analyzer
    Analyzer -- "基于逻辑分析" --> Repro
    Repro -- "明确稳定的步骤" --> Fix

    style Context fill:#f9f,stroke:#333,stroke-width:2px,color:black
    style Solution fill:#bbf,stroke:#333,stroke-width:2px,color:black
    style Repro fill:#f96,stroke:#333,stroke-width:4px,color:black
```

## 功能特性

*   **现场快照**：自动收集客户端/服务端全链路日志与状态。
*   **智能归因**：利用 LLM + RAG 分析日志与代码逻辑的关联。
*   **交互式排查**：Agent 如同经验丰富的同事，与你对话推进调查。
*   **标准化报告**：输出包含根因分析、重现步骤和修复建议的完整报告。

## 快速开始

（待补充具体启动命令）
