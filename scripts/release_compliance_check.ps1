<#
.SYNOPSIS
    Pre-release compliance check for britecore_sdk.

.DESCRIPTION
    Verifies LICENSE, package metadata, legal docs, and dependency license
    compatibility before tagging a release.  Run from the repo root.

.PARAMETER SkipDependencyLicenses
    Skip the optional pip-licenses dependency audit (faster, offline-safe).

.EXAMPLE
    .\scripts\release_compliance_check.ps1
    .\scripts\release_compliance_check.ps1 -SkipDependencyLicenses
#>

[CmdletBinding()]
param(
    [switch]$SkipDependencyLicenses
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Failures = [System.Collections.Generic.List[string]]::new()
$Warnings = [System.Collections.Generic.List[string]]::new()

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host "  $Text"
    Write-Host ("=" * 60)
}

function Write-Pass {
    param([string]$Msg)
    Write-Host "  [PASS] $Msg" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Msg)
    Write-Host "  [WARN] $Msg" -ForegroundColor Yellow
    $script:Warnings.Add($Msg)
}

function Write-Fail {
    param([string]$Msg)
    Write-Host "  [FAIL] $Msg" -ForegroundColor Red
    $script:Failures.Add($Msg)
}

# ---------------------------------------------------------------------------
# 1. LICENSE file
# ---------------------------------------------------------------------------
Write-Header "1. LICENSE file"

$LicensePath = Join-Path $RepoRoot "LICENSE"
if (Test-Path $LicensePath) {
    Write-Pass "LICENSE file present."

    $licenseText = Get-Content $LicensePath -Raw
    if ($licenseText -match "Apache License") {
        Write-Pass "LICENSE contains Apache License header."
    }
    else {
        Write-Fail "LICENSE does not appear to contain Apache License text."
    }

    if ($licenseText -match "Copyright \d{4}") {
        Write-Pass "LICENSE contains a copyright notice."
    }
    else {
        Write-Warn "LICENSE has no recognizable copyright year. Verify manually."
    }
}
else {
    Write-Fail "LICENSE file is missing from repo root."
}

# ---------------------------------------------------------------------------
# 2. pyproject.toml metadata
# ---------------------------------------------------------------------------
Write-Header "2. Package metadata (pyproject.toml)"

$Pyproject = Join-Path $RepoRoot "pyproject.toml"
if (-not (Test-Path $Pyproject)) {
    Write-Fail "pyproject.toml not found."
}
else {
    $pyContent = Get-Content $Pyproject -Raw

    if ($pyContent -match 'license\s*=\s*"Apache-2.0"') {
        Write-Pass "license = Apache-2.0 is set."
    }
    else {
        Write-Fail "license field is missing or not Apache-2.0 in pyproject.toml."
    }

    if ($pyContent -match 'authors\s*=') {
        Write-Pass "authors field is set."
    }
    else {
        Write-Warn "authors field is missing - recommended for PyPI metadata."
    }

    $requiredUrls = @("Homepage", "Documentation", "Repository", "Issues", "Changelog")
    foreach ($url in $requiredUrls) {
        if ($pyContent -match "$url\s*=") {
            Write-Pass "[project.urls] $url is set."
        }
        else {
            Write-Warn "[project.urls] $url is missing - recommended for PyPI."
        }
    }
}

# ---------------------------------------------------------------------------
# 3. Legal / governance docs
# ---------------------------------------------------------------------------
Write-Header "3. Legal and governance docs"

$requiredDocNames = @(
    "LICENSING.md",
    "ATTRIBUTION.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md"
)
$requiredDocDescs = @(
    "License explanation and usage policy",
    "Third-party notice template and release checklist",
    "Vulnerability reporting policy",
    "Code of conduct",
    "Contributor guidelines"
)

for ($i = 0; $i -lt $requiredDocNames.Count; $i++) {
    $docPath = Join-Path $RepoRoot $requiredDocNames[$i]
    if (Test-Path $docPath) {
        Write-Pass "$($requiredDocNames[$i]) - $($requiredDocDescs[$i])"
    }
    else {
        Write-Warn "$($requiredDocNames[$i]) is missing ($($requiredDocDescs[$i]))."
    }
}

# ---------------------------------------------------------------------------
# 4. README badge / notice checks
# ---------------------------------------------------------------------------
Write-Header "4. README license references"

$ReadmePath = Join-Path $RepoRoot "README.md"
if (Test-Path $ReadmePath) {
    $readmeText = Get-Content $ReadmePath -Raw
    if ($readmeText -match "Apache") {
        Write-Pass "README references Apache license."
    }
    else {
        Write-Warn "README has no visible Apache license reference."
    }
    # Trademark notice is canonical in LICENSING.md; README is acceptable but not required.
    $licensingPath = Join-Path $RepoRoot "LICENSING.md"
    $trademarkInReadme = $readmeText -match "trademark|independent project|not endorsed|not affiliated"
    $trademarkInLicensing = (Test-Path $licensingPath) -and ((Get-Content $licensingPath -Raw) -match "trademark|Trademark")
    if ($trademarkInReadme -or $trademarkInLicensing) {
        Write-Pass "Trademark disclaimer present (README or LICENSING.md)."
    }
    else {
        Write-Warn "No trademark disclaimer found in README.md or LICENSING.md."
    }
}
else {
    Write-Warn "README.md not found."
}

# ---------------------------------------------------------------------------
# 5. ATTRIBUTION.md content review
# ---------------------------------------------------------------------------
Write-Header "5. ATTRIBUTION.md content review"

$AttributionPath = Join-Path $RepoRoot "ATTRIBUTION.md"
if (Test-Path $AttributionPath) {
    $attrText = Get-Content $AttributionPath -Raw
    if ($attrText -match "No additional third-party notices are currently recorded") {
        Write-Pass "ATTRIBUTION.md is present (no third-party notices currently recorded)."
    }
    else {
        Write-Pass "ATTRIBUTION.md has notice entries - review them before releasing."
    }
}
else {
    Write-Warn "ATTRIBUTION.md not found."
}

# ---------------------------------------------------------------------------
# 6. Dependency license audit (optional, requires pip-licenses)
# ---------------------------------------------------------------------------
Write-Header "6. Dependency license audit"

$incompatibleLicenses = @("GPL-2.0", "GPL-3.0", "AGPL", "LGPL-2.0", "CC-BY-NC", "EUPL")

if ($SkipDependencyLicenses) {
    Write-Host "  [SKIP] Dependency license audit skipped (-SkipDependencyLicenses)." -ForegroundColor Cyan
}
else {
    $pipLicensesAvailable = $false
    try {
        $null = & python -m piplicenses --version 2>&1
        $pipLicensesAvailable = $true
    }
    catch {
        Write-Host "  [INFO] pip-licenses not installed. Attempting install..." -ForegroundColor Cyan
        & python -m pip install --quiet pip-licenses
        $pipLicensesAvailable = $true
    }

    if ($pipLicensesAvailable) {
        try {
            $licenseOutput = & python -m piplicenses --format=plain-vertical 2>&1
            $foundIncompat = $false
            foreach ($bad in $incompatibleLicenses) {
                if ($licenseOutput -match [regex]::Escape($bad)) {
                    Write-Fail "Potentially incompatible license found in dependencies: $bad"
                    $foundIncompat = $true
                }
            }
            if (-not $foundIncompat) {
                Write-Pass "No obviously incompatible licenses detected in installed dependencies."
            }

            Write-Host ""
            Write-Host "  Dependency license summary (abbreviated):" -ForegroundColor Cyan
            $summaryLines = & python -m piplicenses --format=markdown --with-urls 2>&1
            $summaryLines | Select-Object -First 40 | ForEach-Object {
                Write-Host "  $_"
            }
        }
        catch {
            Write-Warn "pip-licenses audit failed: $($_.Exception.Message)"
        }
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Header "Compliance summary"

Write-Host ""
if ($Warnings.Count -gt 0) {
    Write-Host "  Warnings ($($Warnings.Count)):" -ForegroundColor Yellow
    foreach ($w in $Warnings) {
        Write-Host "    - $w" -ForegroundColor Yellow
    }
}

if ($Failures.Count -gt 0) {
    Write-Host ""
    Write-Host "  Failures ($($Failures.Count)):" -ForegroundColor Red
    foreach ($f in $Failures) {
        Write-Host "    - $f" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "  RESULT: NOT RELEASE-SAFE -- address failures above." -ForegroundColor Red
    exit 1
}
else {
    Write-Host ""
    Write-Host "  RESULT: RELEASE-SAFE (OK)" -ForegroundColor Green
    if ($Warnings.Count -gt 0) {
        Write-Host "  (Review warnings above before tagging.)" -ForegroundColor Yellow
    }
    exit 0
}
