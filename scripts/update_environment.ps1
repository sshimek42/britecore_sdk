[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter()]
    [switch]$Advanced,

    [Parameter()]
    [switch]$SkipTests,

    [Parameter()]
    [switch]$SecurityAudit,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [string]$PythonVersion = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Align SupportsShouldProcess with this script's DryRun path so -WhatIf is non-mutating.
if ($WhatIfPreference -and -not $DryRun) {
    $DryRun = $true
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$startTime = Get-Date

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Subheader {
    param([string]$Message)
    Write-Host "`n[*] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  [!] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  [X] $Message" -ForegroundColor Red
}

function Invoke-Command-Safe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DisplayName,

        [Parameter(Mandatory = $true)]
        [scriptblock]$ScriptBlock,

        [switch]$ContinueOnError
    )

    Write-Subheader $DisplayName

    if ($DryRun) {
        Write-Host "  [DRY RUN] Would execute: $DisplayName" -ForegroundColor Gray
        return $true
    }

    try {
        & $ScriptBlock
        Write-Success "$DisplayName completed"
        return $true
    }
    catch {
        if ($ContinueOnError) {
            Write-Warning "$DisplayName failed: $_"
            return $false
        }
        else {
            throw
        }
    }
}

function Get-VersionInfo {
    param([string]$Command)

    try {
        $version = & $Command --version 2>&1 | Select-Object -First 1
        return $version
    }
    catch {
        return "Not installed or not available"
    }
}

function Compare-Versions {
    param(
        [string]$Current,
        [string]$Latest
    )

    $currentVersionObj = [version]($Current -replace '[^0-9.]')
    $latestVersionObj = [version]($Latest -replace '[^0-9.]')

    if ($latestVersionObj -gt $currentVersionObj) {
        return "outdated"
    }
    elseif ($latestVersionObj -eq $currentVersionObj) {
        return "current"
    }
    else {
        return "ahead"
    }
}

# ============================================================================
# Initialization & Checks
# ============================================================================

Write-Header "ENVIRONMENT UPDATE SCRIPT"

Write-Subheader "Verifying prerequisites..."

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not installed or not on PATH. Install uv first: https://docs.astral.sh/uv/"
}
Write-Success "uv is installed: $(Get-VersionInfo uv)"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "python is not installed or not on PATH"
}
Write-Success "python is installed: $(Get-VersionInfo python)"

$currentUvVersion = Get-VersionInfo uv
$currentPythonVersion = Get-VersionInfo python

# ============================================================================
# Step 1: Update uv (Optional in advanced mode)
# ============================================================================

if ($Advanced) {
    Write-Subheader "Checking for uv updates..."

    if ($DryRun) {
        Write-Host "  [DRY RUN] Would check: uv self update" -ForegroundColor Gray
    }
    else {
        try {
            $before = $currentUvVersion
            & uv self update 2>&1 | ForEach-Object { Write-Host "  $_" }
            $after = Get-VersionInfo uv

            if ($before -ne $after) {
                Write-Success "uv updated: $before → $after"
            }
            else {
                Write-Success "uv is already up to date: $after"
            }
        }
        catch {
            Write-Warning "Could not update uv: $_"
        }
    }
}

# ============================================================================
# Step 2: Check Python Version
# ============================================================================

Write-Subheader "Checking Python compatibility..."

$pythonVersionFull = & python --version
$pythonVersionMatch = [regex]::Match($pythonVersionFull, '(\d+\.\d+)')
$pythonVersionShort = $pythonVersionMatch.Groups[1].Value

if ([version]$pythonVersionShort -lt [version]"3.11") {
    Write-Error-Custom "Python 3.11+ is required, but you have $pythonVersionShort"
    throw "Unsupported Python version"
}
Write-Success "Python version compatible: $pythonVersionFull"

$supportedPythonVersions = @("3.11", "3.12", "3.13", "3.14")
if ($pythonVersionShort -notin $supportedPythonVersions) {
    Write-Warning "Python $pythonVersionShort is not in the documented supported versions: $($supportedPythonVersions -join ', ')"
}

# ============================================================================
# Step 3: Update Dependencies
# ============================================================================

Write-Header "UPDATING DEPENDENCIES"

$syncArgs = @("sync")
if ($Advanced) {
    $syncArgs += "--upgrade"
}

Push-Location $repoRoot
try {
    Invoke-Command-Safe -DisplayName "Syncing dependencies (uv sync)" -ScriptBlock {
        & uv @syncArgs
        if ($LASTEXITCODE -ne 0) {
            throw "uv sync failed with exit code $LASTEXITCODE"
        }
    }

    # ============================================================================
    # Step 4: Security Audit (Optional in advanced mode)
    # ============================================================================

    if ($Advanced -or $SecurityAudit) {
        Invoke-Command-Safe -DisplayName "Running security audit (pip-audit)" -ScriptBlock {
            & uv run pip-audit
            if ($LASTEXITCODE -eq 0) {
                Write-Success "No security vulnerabilities found"
            }
            elseif ($LASTEXITCODE -eq 1) {
                Write-Warning "Vulnerabilities detected but audit completed"
            }
        } -ContinueOnError
    }

    # ============================================================================
    # Step 5: Run Tests
    # ============================================================================

    if (-not $SkipTests) {
        Invoke-Command-Safe -DisplayName "Running test suite (pytest)" -ScriptBlock {
            & uv run pytest --tb=short
            if ($LASTEXITCODE -ne 0) {
                throw "Tests failed with exit code $LASTEXITCODE"
            }
        }
    }
    else {
        Write-Subheader "Skipping test suite (--SkipTests flag set)"
    }
}
finally {
    Pop-Location
}

# ============================================================================
# Summary Report
# ============================================================================

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Header "UPDATE COMPLETE"

Write-Subheader "Environment Summary:"
Write-Host "  uv version:            $(Get-VersionInfo uv)"
Write-Host "  python version:        $pythonVersionFull"
Write-Host "  project root:          $repoRoot"
Write-Host "  duration:              $([int]$duration.TotalSeconds)s"
Write-Host ""

Write-Subheader "Available Extras:"
Write-Host "  dev, docs, interactive, async-http, typed-config, all"
Write-Host ""

if ($Advanced) {
    Write-Subheader "Next Steps (Advanced Mode):"
    Write-Host "  • Review pip-audit results if vulnerabilities found"
    Write-Host "  • Check CHANGELOG.md for breaking changes"
    Write-Host "  • Run: britecore-quick-check (to verify SDK functionality)"
    Write-Host ""
}

Write-Subheader "Useful Commands:"
Write-Host "  uv update              Update dependencies to latest compatible versions"
Write-Host "  uv run pytest          Run tests"
Write-Host "  uv run ruff check .    Lint the code"
Write-Host "  uv run black .         Format the code"
Write-Host ""

if ($DryRun) {
    Write-Warning "This was a DRY RUN - no changes were made"
    Write-Host ""
}

Write-Success "Environment is ready for development!"
Write-Host ""
