import sys
import os

sys.path.insert(0, os.getcwd())

print("STEP 1: Import bug_sleuth package")
try:
    import bug_sleuth
    print(f"SUCCESS: bug_sleuth imported from {bug_sleuth.__file__}")
except Exception as e:
    print(f"FAIL STEP 1: {e}")
    sys.exit(1)

print("STEP 2: Import bug_sleuth.shared_libraries")
try:
    import bug_sleuth.shared_libraries
    print("SUCCESS: shared_libraries imported")
except Exception as e:
    print(f"FAIL STEP 2: {e}")
    sys.exit(1)

print("STEP 3: Import bug_sleuth.bug_analyze_agent.agent")
try:
    from bug_sleuth.bug_analyze_agent import agent
    print("SUCCESS: bug_analyze_agent imported")
except Exception as e:
    print(f"FAIL STEP 3: {e}")
    sys.exit(1)

print("STEP 4: Import bug_sleuth.agent (Main Entrypoint)")
try:
    from bug_sleuth.agent import app
    print("SUCCESS: App imported")
except Exception as e:
    print(f"FAIL STEP 4: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
