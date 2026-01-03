# ADK Testing Framework

This directory contains the automated testing infrastructure for the ADK components of this project.

## Structure
*   `unit/`: Tests for individual tools (e.g., Parsers) that do not require an Agent/LLM context.
*   `integration/`: Tests for Agent workflows. These use a **Mock LLM** to simulate model responses without network calls or costs.
*   `utils/`: Shared utilities, including the `MockLlm` provider and `TestClient`.

## Running Tests
Run all tests:
```bash
python -m pytest tests/
```

Run only integration tests:
```bash
python -m pytest tests/integration/
```

## Writing Integration Tests
1.  **Define Mock Behavior**: Use `MockLlm.set_behaviors` to map expected user input keywords to `FunctionCall` responses or text.
2.  **Patch Environment**: If testing agents with strict dependency checks (like `RepoRegistry` or `ripgrep`), use `unittest.mock` to patch them.
3.  **Inject State**: Ensure `initial_state` contains all variables required by the Agent's prompt (e.g., `project_root`).
