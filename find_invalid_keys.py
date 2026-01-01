import os

ROOT = "d:/MyProject/bug_sleuth/bug_sleuth"

print(f"Scanning {ROOT} for Invalid Keys...")
for root, dirs, files in os.walk(ROOT):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if "StateKeys.PRODUCT" in content:
                        print(f"FOUND StateKeys.PRODUCT in: {path}")
                    if "AgentKeys.PRODUCT" in content:
                        print(f"FOUND AgentKeys.PRODUCT in: {path}")
            except Exception as e:
                pass
