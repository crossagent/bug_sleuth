# start_web.ps1

# Get the project root (where this script resides)
$ProjectRoot = $PSScriptRoot

# Define Data Directory
$DataDir = Join-Path $ProjectRoot "adk_data"

# [Config] Load .env for Local Development
# This ensures Python code doesn't need to depend on 'python-dotenv' or 'load_dotenv' logic
$EnvFile = Join-Path $ProjectRoot "agents\.env"
if (Test-Path $EnvFile) {
    Write-Host "🔧 Loading environment from $EnvFile..."
    Get-Content $EnvFile | ForEach-Object {
        # Match lines like KEY=VALUE, ignore comments (#)
        if ($_ -match "^\s*([^#=]+?)\s*=\s*(.*)$") {
            $Key = $matches[1]
            $Value = $matches[2]
            # Remove potential quotes
            $Value = $Value -replace '^"|"$', '' -replace "^'|'$", ""
            
            [System.Environment]::SetEnvironmentVariable($Key, $Value)
            # Write-Host "   Set $Key"
        }
    }
}
else {
    Write-Host "⚠️ Warning: No .env file found at $EnvFile"
}
# Define Artifacts Path (Absolute)
$ArtifactsPath = Join-Path $DataDir "artifacts"

# Define Sessions DB Path (Absolute)
$SessionDbPath = Join-Path $DataDir "sessions.db"

# Create directories if not exists
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
    Write-Host "Created data directory at: $DataDir"
}
if (-not (Test-Path $ArtifactsPath)) {
    New-Item -ItemType Directory -Path $ArtifactsPath -Force | Out-Null
    Write-Host "Created artifacts directory at: $ArtifactsPath"
}

# Convert to URI
# Use Python again for consistency
$ArtifactsUri = python -c "from pathlib import Path; print(Path(r'$ArtifactsPath').resolve().as_uri())"
$SessionUri = python -c "from pathlib import Path; print(f'sqlite+aiosqlite:///{Path(r'$SessionDbPath').resolve().as_posix()}')"

# Start ADK Web
Write-Host "=============================================="
Write-Host "🚀 Starting ADK Web Server (Unified Params)"
Write-Host "📂 Project Root:  $ProjectRoot"
Write-Host "📦 Artifacts URI: $ArtifactsUri"
Write-Host "💾 Session URI:   $SessionUri"
Write-Host "=============================================="
Write-Host ""

# Call ADK Web CLI
# Pointing to the 'agents' subdirectory
# adk web agents --artifact_service_uri "$ArtifactsUri" --session_service_uri "$SessionUri"

# Start Custom Server (Unified Web & API)
# This includes both the ADK Dev UI (via get_fast_api_app) and our custom /reporter & /upload endpoints
python deployment/server.py
