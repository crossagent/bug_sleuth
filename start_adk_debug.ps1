# start_adk_debug.ps1
# 启动 ADK Web 调试模式 (Visual Builder)

# Get the project root (where this script resides)
$ProjectRoot = $PSScriptRoot

# Define Data Directory
$DataDir = Join-Path $ProjectRoot "adk_data"



# Define Artifacts Path (Absolute)
$ArtifactsPath = Join-Path $DataDir "artifacts"
$SessionDbPath = Join-Path $DataDir "sessions.db"

# Create directories if not exists
if (-not (Test-Path $DataDir)) { New-Item -ItemType Directory -Path $DataDir -Force | Out-Null }
if (-not (Test-Path $ArtifactsPath)) { New-Item -ItemType Directory -Path $ArtifactsPath -Force | Out-Null }

# Convert to URI (Using uv run python for consistency and environment usage)
$ArtifactsUri = uv run python -c "from pathlib import Path; print(Path(r'$ArtifactsPath').resolve().as_uri())"
$SessionUri = uv run python -c "from pathlib import Path; print(f'sqlite+aiosqlite:///{Path(r'$SessionDbPath').resolve().as_posix()}')"

Write-Host "=============================================="
Write-Host "🚀 Starting ADK Debug UI (Visual Builder)"
Write-Host "📂 Project Root:  $ProjectRoot"
Write-Host "📦 Artifacts URI: $ArtifactsUri"
Write-Host "💾 Session URI:   $SessionUri"
Write-Host "=============================================="

# Call ADK Web CLI via uv
# Pointing to the 'agents' subdirectory
uv run adk web agents --artifact_service_uri "$ArtifactsUri" --session_service_uri "$SessionUri"
