from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.agents.context_cache_config import ContextCacheConfig

from bug_sleuth.bug_scene_app.bug_analyze_agent.agent import bug_analyze_agent
from bug_sleuth.bug_scene_app.agent import bug_scene_agent

# --- Instantiate App (Global) ---
app = App(
    name="bug_scene_app",
    root_agent=bug_analyze_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=600,
        cache_intervals=1,
    ),
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,
        overlap_size=1
    )
)
