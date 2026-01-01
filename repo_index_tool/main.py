
import os
import argparse
import yaml
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from db import DatabaseManager
from parser import CodeParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("CodeIndexer")

IGNORE_DIRS = {'.git', '.svn', '.vs', '.bug_sleuth_agent', 'Library', 'Temp', 'Obj', 'Build', 'Logs'}

def load_config_repos(config_path):
    """Extracts repository paths from config.yaml."""
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return []
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            repos = []
            if 'repositories' in config:
                repos_list = config['repositories']
                if isinstance(repos_list, list):
                    for repo_data in repos_list:
                        if isinstance(repo_data, dict) and 'path' in repo_data:
                            repos.append(repo_data['path'])
                elif isinstance(repos_list, dict):
                    # Fallback for old dict format just in case
                    for _, repo_data in repos_list.items():
                         if isinstance(repo_data, dict) and 'path' in repo_data:
                            repos.append(repo_data['path'])
            return repos
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return []

def scan_files(root_dir):
    """Yields all .cs files in the directory, respecting ignore list."""
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith('.cs'):
                yield os.path.join(root, file)

def index_repo(repo_path, rebuild=False):
    """Indexes a single repository."""
    logger.info(f"--- Indexing Repository: {repo_path} ---")
    
    if not os.path.exists(repo_path):
        logger.warning(f"Repo path does not exist: {repo_path}")
        return

    # Setup DB
    db_path = os.path.join(repo_path, ".bug_sleuth_agent", "code_index.db")
    if rebuild and os.path.exists(db_path):
        try:
            os.remove(db_path)
            logger.info("Deleted existing DB for rebuild.")
        except Exception as e:
            logger.error(f"Failed to delete DB: {e}")

    try:
        db = DatabaseManager(db_path)
        db.connect()
    except Exception as e:
        logger.error(f"Skipping repo due to DB error: {e}")
        return

    parser = CodeParser()
    file_count = 0
    symbol_count = 0
    start_time = time.time()

    # We could parallelize this, but SQLite write lock is single-threaded.
    # Parsing can be parallel, DB writes sequential.
    # For simplicity in V1, let's keep it single threaded or simple batch.
    
    files = list(scan_files(repo_path))
    total_files = len(files)
    logger.info(f"Found {total_files} .cs files to process.")

    for i, file_path in enumerate(files):
        # relative path for DB
        rel_path = os.path.relpath(file_path, repo_path).replace("\\", "/")
        
        # Parse
        symbols = list(parser.parse_file(file_path))
        
        if symbols:
            # Clear old symbols for this file (if not full rebuild, handling update logic - strict rebuild assumes empty DB)
            # db.clear_file_symbols(rel_path) 
            
            for sym in symbols:
                db.insert_symbol(
                    name=sym['name'],
                    symbol_type=sym['type'],
                    file_path=rel_path,
                    start_line=sym['start_line'],
                    end_line=sym['end_line']
                )
                symbol_count += 1
        
        file_count += 1
        if i % 100 == 0 and i > 0:
            logger.info(f"Processed {i}/{total_files} files...")

    db.commit()
    db.close()
    
    elapsed = time.time() - start_time
    logger.info(f"Indexed {file_count} files, {symbol_count} symbols in {elapsed:.2f}s.")
    logger.info(f"DB Location: {db_path}")

def main():
    parser = argparse.ArgumentParser(description="Bug Sleuth Code Indexer")
    parser.add_argument("--repo_path", help="Specific repository path to index")
    parser.add_argument("--config", help="Path to config.yaml", default="bug_sleuth/config.yaml")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of database")
    
    args = parser.parse_args()
    
    repos_to_index = []
    
    if args.repo_path:
        repos_to_index.append(args.repo_path)
    else:
        # Load from config
        logger.info(f"Loading repos from {args.config}")
        repos_to_index = load_config_repos(args.config)
        
    if not repos_to_index:
        logger.warning("No repositories found to index.")
        return

    for repo in repos_to_index:
        index_repo(repo, rebuild=args.rebuild)

if __name__ == "__main__":
    main()
