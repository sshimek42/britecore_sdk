[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter()]
    [ValidatePattern('^\d+\.\d+$')]
    [string]$PythonVersion = "3.11",

    [Parameter()]
    [string[]]$Extras = @("dev", "docs"),

    [Parameter()]
    [switch]$SkipLegacyVenv311Cleanup
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-UvCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $display = "uv " + ($Arguments -join " ")
    if ($WhatIfPreference) {
        Write-Host "[WhatIf] $display"
        return
    }

    Write-Host "> $display"
    & uv @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $display"
    }
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not installed or not on PATH. Install uv first: https://docs.astral.sh/uv/"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $repoRoot ".venv"
$legacyVenvPath = Join-Path $repoRoot ".venv311"

Push-Location $repoRoot
try {
    if (Test-Path $venvPath) {
        if ($PSCmdlet.ShouldProcess($venvPath, "Remove broken/stale virtual environment")) {
            if ($WhatIfPreference) {
                Write-Host "[WhatIf] Remove-Item -Recurse -Force $venvPath"
            }
            else {
                Remove-Item -Recurse -Force $venvPath
            }
        }
    }

    if ((-not $SkipLegacyVenv311Cleanup) -and (Test-Path $legacyVenvPath)) {
        if ($PSCmdlet.ShouldProcess($legacyVenvPath, "Remove legacy .venv311 environment")) {
            if ($WhatIfPreference) {
                Write-Host "[WhatIf] Remove-Item -Recurse -Force $legacyVenvPath"
            }
            else {
                Remove-Item -Recurse -Force $legacyVenvPath
            }
        }
    }

    Invoke-UvCommand -Arguments @("venv", "--python", $PythonVersion)

    $syncArgs = @("sync", "--python", $PythonVersion)
    foreach ($extra in $Extras) {
        if (-not [string]::IsNullOrWhiteSpace($extra)) {
            $syncArgs += @("--extra", $extra)
        }
    }
    Invoke-UvCommand -Arguments $syncArgs

    Write-Host ""
    Write-Host "Environment rebuild complete."
    Write-Host ""
    Invoke-UvCommand -Arguments @(
        "run",
        "python",
        "-c",
        "import sys, britecore_sdk; print(sys.executable); print(britecore_sdk.__version__)"
    )
}
finally {
    Pop-Location
}

