
import os
import sys
import logging
import click
import uvicorn
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bug_sleuth.cli")

@click.group()
def main():
    """Bug Sleuth CLI Tool"""
    pass

@main.command()
@click.option("--port", default=8000, help="Port to run the server on.")
@click.option("--host", default="127.0.0.1", help="Host to run the server on.")
@click.option("--skills-dir", envvar="SKILL_PATH", help="Path to the skills directory.")
@click.option("--config", envvar="CONFIG_FILE", help="Path to the configuration file.")
@click.option("--env-file", default=".env", help="Path to .env file.")
def serve(port, host, skills_dir, config, env_file):
    """
    Start the Bug Sleuth Agent Server.
    """
    # 1. Load Environment Variables
    if os.path.exists(env_file):
        logger.info(f"Loading environment from {env_file}")
        load_dotenv(env_file)
    
    # 2. Set Environment Variables for Agent
    if skills_dir:
        os.environ["SKILL_PATH"] = os.path.abspath(skills_dir)
        logger.info(f"Set SKILL_PATH to {os.environ['SKILL_PATH']}")
    
    if config:
        os.environ["CONFIG_FILE"] = os.path.abspath(config)
        logger.info(f"Set CONFIG_FILE to {os.environ['CONFIG_FILE']}")
        
    # 3. Start Uvicorn Server
    # We import the app factory strings to avoid loading logic before env vars are set
    logger.info(f"Starting Bug Sleuth Server on {host}:{port}")
    
    # Check if we should use the existing app instance or a factory
    # The existing code in bug_sleuth.agents.agent instantiates 'app' globally on import.
    # This implies that importing it WILL trigger initialization.
    # So we must ensure env vars are set BEFORE this import happens in the Uvicorn worker process?
    # Uvicorn loads the app. If we pass "bug_sleuth.agents.agent:app", it imports it.
    # Since we are setting os.environ HERE in the main process, Uvicorn (if run programmatically) 
    # should inherit them if run in the same process or forked.
    
    # However, uvicorn.run can take the app object directly if we import it first. 
    # But checking 'agent.py', it loads extensions at top level.
    # So we MUST set env vars *before* importing 'bug_sleuth.agents.agent'.
    
    try:
        from bug_sleuth.agents.agent import app
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
