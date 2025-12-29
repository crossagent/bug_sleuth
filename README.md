# BugSleuth: Automated Bug Analysis Agent

**BugSleuth** is an intelligent agent framework designed to automate the process of analyzing, reproducing, and reporting software bugs. It leverages LLMs to investigate issues, parsing logs, and identifying root causes.

## Features

*   **Automated Log Analysis**: Parses application logs to identify error patterns.
*   **Reproduction Steps**: attempts to deduce the steps required to reproduce a reported bug.
*   **Integrated Reporting**: Generates detailed bug reports with findings.
*   **Extensible Framework**: Designed to be integrated into custom toolchains.

## The BugSleuth Pipeline

The core value of BugSleuth is its ability to autonomously **deduce reproduction steps** from complex, noisy production environments. It transforms raw chaos into actionable reports via a structured 4-stage pipeline:

```mermaid
graph TD
    subgraph "Phase 1: Collection"
        A[Start: Bug Occurs] -->|Log & Context| B(Base Info)
    end
    
    subgraph "Phase 2: Analysis (Concurrent)"
        B --> C{Orchestrator}
        C -->|Dispatch| D[Log Analyst Agent]
        C -->|Search & Diff| E[Code Analyst Agent]
        D -->|Error Pattern| F[Hypothesis]
        E -->|Git History| F
    end
    
    subgraph "Phase 3: Reproduction"
        F --> G[Reproduction Agent]
        G -->|Simulate User Actions| H{Verify?}
        H -->|Success| I[Generate Steps]
        H -->|Fail| C
    end
    
    subgraph "Phase 4: Reporting"
        I --> J[Bug Report Agent]
        J --> K[Final PDF / Notification]
    end
    
    style G fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
```

1.  **Collection**: Captures logs, screenshots, and device state.
2.  **Analysis**: Concurrently analyzes logs for error patterns and code for recent changes (Git history/Diffs) to form a hypothesis.
3.  **Reproduction (Core)**: The system attempts to simulate user actions based on the hypothesis to verify the bug. **Finding the exact reproduction steps is the key deliverable.**
4.  **Reporting**: Synthesizes all findings into a clear, actionable report for developers.

## Installation

```bash
pip install -e .
```

## Getting Started

1.  **Environment Setup**:
    Ensure you have your target project's root directory accessible.

2.  **Run the Server**:
    ```bash
    bug-sleuth-server
    ```

## Contributing

This project is open source. Contributions are welcome!
