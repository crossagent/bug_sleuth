# BugSleuth

### 设计初衷：如何提一个“好”的 Bug？ (Design Philosophy)

**"修 bug 最重要的是提一个好的 bug 描述。"**

在一个理想的世界里，每一个 Bug 报告都包含完整的 **现场信息 (Context)** 和 **确定的重现步骤 (Reproduction Steps)**。

但现实是残酷的。要准确地总结出这两点，往往需要对系统的实现方案有 **非常全局的把握**。
*   在涉及多个部门（客户端、服务端、引擎、美术）的大型工程中，没有任何一个单点 QA 或普通开发者能轻易做到这点。
*   结果就是：**被迫由最熟悉实现的程序专家承担了大量的初步分析工作**。他们不得不花费宝贵的时间去“猜”现场，去“试”重现，只是为了补全那个本该在 Bug 单里的信息。

**这就是大规模协作的痛点：信息的非对称与理解成本的错位。**

### BugSleuth 的解法

**利用 AI 极强的理解与阅读能力，让 AI 来承担这个“理解”的重任。**

BugSleuth 不仅仅是一个调试器，它试图借助 AI 形成一种 **良好的沟通范式**。
*   它阅读代码，理解全局逻辑。
*   它分析日志，还原现场。
*   它代替人类专家完成“从现象到逻辑”的映射。

最终，由 AI 替你提出那个包含 **精确现场与重现步骤的“好 Bug”**。

## 实现思路 (Implementation Approach)

为了达成上述目标，BugSleuth 采用了一套 **"Artifact-Driven Agent" (制品驱动代理)** 的架构：

1.  **以“排查计划”为核心 (Plan-Driven)**：
    *   Agent 不是漫无目的地乱撞。它必须维护一个持续更新的 `investigation_plan.md`。
    *   Thinking -> Updating Plan -> Executing Tools。每一步行动都必须基于当前的计划。

2.  **混合专家架构 (Hybrid Architecture)**：
    *   **Orchestrator (主脑)**：负责宏观逻辑推理和规划。
    *   **Specialist Tools (专家工具)**：
        *   `LogAnalyst`: 专门处理海量日志的 RAG 检索引擎。
        *   `CodeSearch`: 基于语义级的代码索引。
        *   `GitTracer`: 关联代码变更与 Bug 的时序关系。

3.  **Token 经济学 (Token Economics)**：
    *   为了在有限的上下文窗口（Context Window）不仅能“读”代码，还能“思考”，我们引入了精细的 **Token 预算管理**。
    *   非代码文件只读片段，代码文件读关键上下文，确保 AI 的“脑容量”始终用于核心逻辑分析。

4.  **无损的信息流 (Lossless Visualization)**：
    *   通过自定义的 `VisualLlmAgent`，我们将从工具调用到思维链的每一个环节都可视化呈现。用户不仅看到结果，更看到 AI "如何像一个专家一样思考"。

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

### 3.2 Bridge Agent Implementation (Private Project Integration)

Create a file named `bridge_agent.py` in your project's `agents/` directory:

```python
import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# 1. Configure the environment
# Point this to your local directory containing SKILL.md and tool.py files
os.environ["SKILL_PATH"] = os.path.abspath("../skills")

# 2. Import the agent
# Note: Importing bug_sleuth will automatically load skills from SKILL_PATH
from bug_sleuth import agent

if __name__ == "__main__":
    # 3. Create ADK App
    # The 'agent' variable imported above is a valid LlmAgent instance
    app = get_fast_api_app(
        agents_dir=".", # Scan current directory for 'agent' or 'root_agent'
        host="0.0.0.0",
        port=9000
    )
    uvicorn.run(app)
```

**Key Concepts:**
*   **Direct Exposure**: The `bug_sleuth` package directly exposes the `agent` instance.
*   **Environment Configuration**: `SKILL_PATH` must be set *before* importing `bug_sleuth` (or set globally in the OS/Dockerfile) to ensure plugins are loaded during initialization.

### 3.3 Run with ADK CLI

If your `bridge_agent.py` is in `./agents`:

```bash
adk web ./agents
```

Ensure `SKILL_PATH` is set in your environment variables if running via CLI.

