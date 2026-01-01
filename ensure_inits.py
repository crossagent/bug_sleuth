import os

ROOT = "d:/MyProject/bug_sleuth/bug_sleuth"

def ensure_init(dir_path):
    init_file = os.path.join(dir_path, "__init__.py")
    if not os.path.exists(init_file):
        print(f"Creating {init_file}")
        with open(init_file, 'w') as f:
            f.write("")

for root, dirs, files in os.walk(ROOT):
    # Don't create in pycache
    if "__pycache__" in root:
        continue
    ensure_init(root)
