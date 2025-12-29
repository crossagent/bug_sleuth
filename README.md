# BugSleuth: Automated Bug Analysis Agent

**BugSleuth** is an intelligent agent framework designed to automate the process of analyzing, reproducing, and reporting software bugs. It leverages LLMs to investigate issues, parsing logs, and identifying root causes.

## Features

*   **Automated Log Analysis**: Parses application logs to identify error patterns.
*   **Reproduction Steps**: attempts to deduce the steps required to reproduce a reported bug.
*   **Integrated Reporting**: Generates detailed bug reports with findings.
*   **Extensible Framework**: Designed to be integrated into custom toolchains.

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
