#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Environment Update Script for macOS/Linux
# ============================================================================
# A comprehensive bash script for keeping your development environment,
# Python, uv, and project dependencies up to date.
#
# Usage:
#   ./scripts/update_environment.sh [OPTIONS]
#
# OPTIONS:
#   -a, --advanced          Enable advanced mode (update uv, upgrade deps, security audit)
#   -s, --skip-tests        Skip running pytest suite
#   --security-audit        Force security audit even in simple mode
#   -d, --dry-run          Show what would happen without making changes
#   -h, --help             Show this help message
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
ADVANCED=false
SKIP_TESTS=false
SECURITY_AUDIT=false
DRY_RUN=false
START_TIME=$(date +%s)

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    local msg="$1"
    echo ""
    echo "============================================================"
    echo " $msg"
    echo "============================================================"
    echo ""
}

print_subheader() {
    local msg="$1"
    echo ""
    echo "[*] $msg"
}

print_success() {
    local msg="$1"
    echo "  [OK] $msg"
}

print_warning() {
    local msg="$1"
    echo "  [!] $msg"
}

print_error() {
    local msg="$1"
    echo "  [X] $msg" >&2
}

run_command() {
    local display_name="$1"
    local continue_on_error="${3:-false}"
    shift 2

    print_subheader "$display_name"

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would execute: $display_name"
        return 0
    fi

    if ! "$@"; then
        if [ "$continue_on_error" = true ]; then
            print_warning "$display_name failed"
            return 0
        else
            print_error "$display_name failed"
            exit 1
        fi
    fi

    print_success "$display_name completed"
    return 0
}

get_version() {
    local cmd="$1"
    if command -v "$cmd" &> /dev/null; then
        "$cmd" --version 2>&1 | head -n 1
    else
        echo "Not installed or not available"
    fi
}

show_help() {
    sed -n '3,18p' "$0"
    exit 0
}

# ============================================================================
# Parse Arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--advanced)
            ADVANCED=true
            shift
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --security-audit)
            SECURITY_AUDIT=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# ============================================================================
# Initialization & Checks
# ============================================================================

print_header "ENVIRONMENT UPDATE SCRIPT"

print_subheader "Verifying prerequisites..."

if ! command -v uv &> /dev/null; then
    print_error "uv is not installed or not on PATH"
    echo "Install uv: https://docs.astral.sh/uv/"
    exit 1
fi
print_success "uv is installed: $(get_version uv)"

if ! command -v python &> /dev/null; then
    print_error "python is not installed or not on PATH"
    exit 1
fi
print_success "python is installed: $(get_version python)"

# ============================================================================
# Step 1: Update uv (Optional in advanced mode)
# ============================================================================

if [ "$ADVANCED" = true ]; then
    print_subheader "Checking for uv updates..."

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would check: uv self update"
    else
        before=$(get_version uv)
        if uv self update 2>&1 | grep -q "already up to date\|Updated"; then
            after=$(get_version uv)
            if [ "$before" != "$after" ]; then
                print_success "uv updated: $before → $after"
            else
                print_success "uv is already up to date: $after"
            fi
        fi
    fi
fi

# ============================================================================
# Step 2: Check Python Version
# ============================================================================

print_subheader "Checking Python compatibility..."

PYTHON_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+')

if ! python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    print_error "Python 3.11+ is required, but you have $PYTHON_VERSION"
    exit 1
fi
print_success "Python version compatible: $(python --version)"

# ============================================================================
# Step 3: Update Dependencies
# ============================================================================

print_header "UPDATING DEPENDENCIES"

cd "$REPO_ROOT"

SYNC_ARGS=("sync")
if [ "$ADVANCED" = true ]; then
    SYNC_ARGS+=("--upgrade")
fi

run_command "Syncing dependencies (uv sync)" uv "${SYNC_ARGS[@]}"

# ============================================================================
# Step 4: Security Audit (Optional in advanced mode)
# ============================================================================

if [ "$ADVANCED" = true ] || [ "$SECURITY_AUDIT" = true ]; then
    run_command "Running security audit (pip-audit)" \
        uv run pip-audit true
fi

# ============================================================================
# Step 5: Run Tests
# ============================================================================

if [ "$SKIP_TESTS" = false ]; then
    run_command "Running test suite (pytest)" uv run pytest --tb=short
else
    print_subheader "Skipping test suite (--skip-tests flag set)"
fi

# ============================================================================
# Summary Report
# ============================================================================

print_header "UPDATE COMPLETE"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

print_subheader "Environment Summary:"
echo "  uv version:            $(get_version uv)"
echo "  python version:        $(python --version)"
echo "  project root:          $REPO_ROOT"
echo "  duration:              ${DURATION}s"
echo ""

print_subheader "Available Extras:"
echo "  dev, docs, interactive, async-http, typed-config, all"
echo ""

if [ "$ADVANCED" = true ]; then
    print_subheader "Next Steps (Advanced Mode):"
    echo "  • Review pip-audit results if vulnerabilities found"
    echo "  • Check CHANGELOG.md for breaking changes"
    echo "  • Run: britecore-quick-check (to verify SDK functionality)"
    echo ""
fi

print_subheader "Useful Commands:"
echo "  uv update              Update dependencies to latest compatible versions"
echo "  uv run pytest          Run tests"
echo "  uv run ruff check .    Lint the code"
echo "  uv run black .         Format the code"
echo ""

if [ "$DRY_RUN" = true ]; then
    print_warning "This was a DRY RUN - no changes were made"
    echo ""
fi

print_success "Environment is ready for development!"
echo ""
