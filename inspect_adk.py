import google.adk
import logging
try:
    import google.adk.agents
    print("M: google.adk.agents OK")
    print(dir(google.adk.agents))
except ImportError as e:
    print(f"M: google.adk.agents FAIL: {e}")

try:
    from google.adk import ContextCacheConfig
    print("Found ContextCacheConfig in google.adk")
except ImportError:
    print("Not in google.adk")

try:
    from google.adk.agents import ContextCacheConfig
    print("Found ContextCacheConfig in google.adk.agents")
except ImportError:
    print("Not in google.adk.agents")
