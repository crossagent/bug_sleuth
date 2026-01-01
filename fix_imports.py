import os

ROOT_DIR = "d:/MyProject/bug_sleuth/bug_sleuth"

REPLACEMENTS = [
    ("from shared_libraries", "from bug_sleuth.shared_libraries"),
    ("import shared_libraries", "import bug_sleuth.shared_libraries"),
    ("from bug_analyze_agent ", "from bug_sleuth.bug_analyze_agent "),
    ("from bug_report_agent ", "from bug_sleuth.bug_report_agent "),
    ("from bug_reproduce_steps_agent ", "from bug_sleuth.bug_reproduce_steps_agent "),
    ("from bug_base_info_collect_agent", "from bug_sleuth.bug_base_info_collect_agent"),
    # Fix root prompt import in agent.py
    ("from prompt import ROOT_AGENT_PROMPT", "from bug_sleuth.prompt import ROOT_AGENT_PROMPT"),
    ("from agents.", "from bug_sleuth."),
    ("import agents.", "import bug_sleuth."),
]

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for old, new in REPLACEMENTS:
            new_content = new_content.replace(old, new)
            
        if new_content != content:
            print(f"Patching {filepath}...")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
    except Exception as e:
        print(f"Failed to process {filepath}: {e}")

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".py"):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
