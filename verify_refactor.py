import sys
import os

# Add CWD to python path
sys.path.insert(0, os.getcwd())

try:
    print("Attempting to import app from bug_sleuth.agent...")
    from bug_sleuth.agent import app
    print(f"SUCCESS: App initialized. Root agent: {app.root_agent.name}")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"RUNTIME ERROR: {e}")
    import traceback
    traceback.print_exc()
