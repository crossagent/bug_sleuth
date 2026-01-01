from bug_sleuth.entrypoints import create_app, before_agent_callback

# Default instantiation for ADK Web Debug & Tests
app = create_app()

# Expose root agent for backward compatibility
root_agent = app.root_agent