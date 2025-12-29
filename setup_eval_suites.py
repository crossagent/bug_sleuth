import subprocess
import os
import json

def run_adk_cmd(cmd_list):
    print(f"Running: {' '.join(cmd_list)}")
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        print("Success.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (Exit Code {e.returncode}):")
        print(e.stderr)
        return False

def setup_suites():
    agent_path = "agents/bug_analyze_agent"
    base_eval_path = "eval_cases/bug_analyze_agent"

    suites = [
        {
            "id": "bug_analyze_agent_tool_usage_cli",
            "path": f"{base_eval_path}/tool_usage",
            "cases": "cases.json"
        },
        {
            "id": "bug_analyze_agent_integrated_cli",
            "path": f"{base_eval_path}/integrated",
            "cases": "scenario.json"
        }
    ]

    for suite in suites:
        print(f"\n--- Setting up Suite: {suite['id']} ---")
        
        # 1. Force Cleanup (Delete existing to avoid 'Exists' error)
        evalset_file = f"{agent_path}/{suite['id']}.evalset.json"
        if os.path.exists(evalset_file):
            print(f"Removing existing set: {evalset_file}")
            os.remove(evalset_file)
        
        # 2. Create Eval Set
        if not run_adk_cmd(["adk", "eval_set", "create", agent_path, suite['id']]):
            continue
            
        # 3. Add Test Case
        try:
            dummy_session_path = f"{suite['path']}/temp_session_input.json"
            with open(dummy_session_path, 'w') as f:
                log_path = r"e:\soc_team_copilot\soc_bug_scene\eval_cases\test_data\2025-12-19_16-47-18.log"
                json.dump({
                    "app_name": "bug_analyze_agent", 
                    "user_id": "test_user",
                    "state": {
                        "bug_user_description": "Evaluation Test Run",
                        "clientLogUrl": log_path,
                        "bug_occurrence_time": "2025-12-19 16:47:18"
                    }
                }, f)
                
            cmd = [
                "adk", "eval_set", "add_eval_case", 
                agent_path, 
                suite['id'],
                "--scenarios_file", f"{suite['path']}/{suite['cases']}",
                "--session_input_file", dummy_session_path
            ]
            run_adk_cmd(cmd)
            os.remove(dummy_session_path)

            # 4. Post-process to Assign Readable IDs
            if os.path.exists(evalset_file):
                with open(evalset_file, 'r') as f:
                    data = json.load(f)
                
                id_maps = {
                    "bug_analyze_agent_tool_usage_cli": [
                        "case_1_plan", 
                        "case_2_logs", 
                        "case_3_code", 
                        "case_4_git",
                        "case_5_search"
                    ],
                    "bug_analyze_agent_integrated_cli": [
                        "integrated_scenario_1"
                    ]
                }
                
                if suite['id'] in id_maps:
                    print(f"Humanizing IDs for {suite['id']}...")
                    readable_ids = id_maps[suite['id']]
                    cases = data.get("eval_cases", [])
                    for i, case in enumerate(cases):
                        if i < len(readable_ids):
                            old_id = case['eval_id']
                            new_id = readable_ids[i]
                            case['eval_id'] = new_id
                            print(f"  - {old_id} -> {new_id}")
                    
                    with open(evalset_file, 'w') as f:
                        json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Failed to prepare suite {suite['id']}: {e}")

if __name__ == "__main__":
    if not os.path.exists("adk_config.json"):
        print("Warning: adk_config.json not found in CWD.")
    setup_suites()

