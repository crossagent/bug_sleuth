import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from agents.bug_analyze_agent.agent import bug_analyze_agent
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder

async def main():
    print("Generating agent.json for bug_analyze_agent...")
    # URL is a placeholder, will be overwritten by server at runtime usually, 
    # but the card content (metadata) is what matters for discovery.
    builder = AgentCardBuilder(
        agent=bug_analyze_agent, 
        rpc_url="http://localhost:8000/a2a/bug_analyze_agent"
    )
    card = await builder.build()
    
    output_path = "agents/bug_analyze_agent/agent.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(card.model_dump_json(indent=2, by_alias=True))
    print(f"Successfully wrote {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
