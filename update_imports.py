#!/usr/bin/env python3
"""
Script to update all imports from bug_sleuth.bug_scene_app to bug_sleuth.bug_scene_app
"""
import os
from pathlib import Path

def update_file(file_path):
    """Update imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the import
        new_content = content.replace('bug_sleuth.bug_scene_app', 'bug_sleuth.bug_scene_app')
        
        # Only write if changed
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    root = Path('.')
    updated_count = 0
    
    # Update Python files
    for py_file in root.rglob('*.py'):
        # Skip venv and cache directories
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        if update_file(py_file):
            updated_count += 1
    
    # Update markdown files
    for md_file in root.rglob('*.md'):
        if '.venv' in str(md_file):
            continue
        if update_file(md_file):
            updated_count += 1
    
    # Update specific config files
    for config_file in ['pyproject.toml', 'docker-compose.yml']:
        if Path(config_file).exists():
            if update_file(Path(config_file)):
                updated_count += 1
    
    print(f"\nTotal files updated: {updated_count}")

if __name__ == '__main__':
    main()
