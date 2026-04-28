param(
    [string]$BranchName = "fileshare-settings",
    [string]$RemoteName = "fileshare",
    [string]$CommitMessage = "chore(fileshare): sync settings toml",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$settingsFile = "src/britecore_sdk/settings/settings.toml"
$secretsFile = "src/britecore_sdk/settings/.secrets.toml"
$tempWorktree = Join-Path ([System.IO.Path]::GetTempPath()) ("britecore-fileshare-sync-" + [guid]::NewGuid().ToString("N"))
$startPoint = "master"

function Invoke-Git {
    param([string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed"
    }
}

Push-Location $repoRoot
try {
    Invoke-Git -GitArgs @("rev-parse", "--is-inside-work-tree") | Out-Null

    if (-not (Test-Path $settingsFile) -or -not (Test-Path $secretsFile)) {
        throw "Both settings TOML files must exist before syncing."
    }

    & git fetch --quiet $RemoteName $BranchName *> $null
    if ($LASTEXITCODE -eq 0) {
        $startPoint = "$RemoteName/$BranchName"
    }

    Invoke-Git -GitArgs @("worktree", "add", "--detach", $tempWorktree, $startPoint)

    Push-Location $tempWorktree
    try {
        Invoke-Git -GitArgs @("checkout", "-B", $BranchName)

        New-Item -ItemType Directory -Force -Path "src/britecore_sdk/settings" | Out-Null
        Copy-Item (Join-Path $repoRoot $settingsFile) $settingsFile -Force
        Copy-Item (Join-Path $repoRoot $secretsFile) $secretsFile -Force

        Invoke-Git -GitArgs @("add", "-f", $settingsFile, $secretsFile)

        & git diff --cached --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "No changes detected in settings TOML files." -ForegroundColor Yellow
            return
        }

        if ($DryRun) {
            Write-Host "Dry run: staged changes in temporary worktree:" -ForegroundColor Cyan
            Invoke-Git -GitArgs @("status", "--short")
            return
        }

        Invoke-Git -GitArgs @("commit", "-m", $CommitMessage)
        Invoke-Git -GitArgs @("push", "--force-with-lease", $RemoteName, "${BranchName}:$BranchName")
        Write-Host "Synced settings TOML files to $RemoteName/$BranchName" -ForegroundColor Green
    }
    finally {
        Pop-Location
        & git worktree remove --force $tempWorktree 2>$null
    }
}
finally {
    Pop-Location
}
