import os
import uvicorn

# 1. 模拟设置公司特有的环境变量 (在真实生产环境中，这应该在 .env 或 CI/CD 流水线中设置)
os.environ["PRODUCT"] = "My Company's Secret Game"
os.environ["PROJECT_ROOT"] = "/data/projects/my_game" # 公司服务器上的真实路径

# 2. [关键] 配置插件映射
# 告诉 Core Agent: "请加载 examples.company_tools 里的 real_deploy_tool 给 bug_analyze_agent 用"
os.environ["ADK_TOOLS_BUG_ANALYZE_AGENT"] = "examples.company_tools.real_deploy_tool"

# 3. 导入开源的核心 App
# 注意：这里我们 import 的是开源库的 app 对象，完全没有修改它的代码
# 由于我们在第2步设置了环境变量，Import 时 plugin_loader 就会自动工作
try:
    from agents.bug_analyze_agent.agent import app
    print("✅ Successfully imported Open Source Agent Core.")
except ImportError as e:
    import traceback
    traceback.print_exc()
    print(f"❌ Failed to import agent: {e}")
    exit(1)

if __name__ == "__main__":
    print("🚀 Launching Company Internal Agent Service...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
