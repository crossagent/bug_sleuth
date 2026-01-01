import os

ROOT = "d:/MyProject/bug_sleuth/bug_sleuth"

print(f"Scanning {ROOT} for '.PRODUCT'...")
for root, dirs, files in os.walk(ROOT):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if ".PRODUCT" in content:
                        print(f"FOUND in {path}")
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if ".PRODUCT" in line:
                                print(f"  Line {i+1}: {line.strip()}")
            except Exception as e:
                print(f"Error reading {path}: {e}")
