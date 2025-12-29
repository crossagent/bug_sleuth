# start_server_deploy.ps1
# 启动 Server 长期部署模式 (Port 50086)

# Get the project root (where this script resides)
$ProjectRoot = $PSScriptRoot

# Define Data Directory
$DataDir = Join-Path $ProjectRoot "adk_data"

# [Config] Load .env for Local Development
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
        }
    }
}
else {
    Write-Host "⚠️ Warning: No .env file found at $EnvFile"
}

# Define Artifacts Path (Absolute)
$ArtifactsPath = Join-Path $DataDir "artifacts"

# Create directories if not exists
if (-not (Test-Path $DataDir)) { New-Item -ItemType Directory -Path $DataDir -Force | Out-Null }
if (-not (Test-Path $ArtifactsPath)) { New-Item -ItemType Directory -Path $ArtifactsPath -Force | Out-Null }

# Set Deployment Port
$env:PORT = 50086

Write-Host "=============================================="
Write-Host "🚀 Starting Production Server"
Write-Host "📂 Project Root:  $ProjectRoot"
Write-Host "🔌 Port:          $env:PORT"
Write-Host "=============================================="

# Start Custom Server (Unified Web & API) using uv
uv run python deployment/server.py
