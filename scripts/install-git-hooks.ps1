param(
    [switch]$ShowOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $repoRoot
try {
    git rev-parse --is-inside-work-tree | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "This script must be run from a git working tree."
    }

    $hooksPath = ".githooks"
    if (-not (Test-Path $hooksPath)) {
        throw "Expected hooks directory '$hooksPath' was not found."
    }

    if ($ShowOnly) {
        Write-Host "Run this command to enable tracked hooks:" -ForegroundColor Cyan
        Write-Host "git config core.hooksPath $hooksPath"
        return
    }

    git config core.hooksPath $hooksPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set core.hooksPath."
    }

    $activeHooksPath = git config --get core.hooksPath
    Write-Host "Configured core.hooksPath = $activeHooksPath" -ForegroundColor Green
}
finally {
    Pop-Location
}

