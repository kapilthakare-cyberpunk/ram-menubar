#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
PLUGIN_SRC="$SCRIPT_DIR/plugins/ram.5s.py"

echo "============================================="
echo "RAM Monitor - SwiftBar Plugin Installer"
echo "============================================="

# 1. Clean up legacy elements
echo "-> Cleaning up legacy elements..."
"$SCRIPT_DIR/uninstall.sh"

# 2. Check system python
SYSTEM_PYTHON=$(command -v python3 2>/dev/null || true)
if [[ -z "$SYSTEM_PYTHON" ]]; then
    echo "[ERROR] python3 not found. Install via: brew install python"
    exit 1
fi

# 3. Create virtual environment if needed
if [[ ! -d "$VENV_DIR" ]]; then
    echo "-> Creating virtual environment at $VENV_DIR..."
    $SYSTEM_PYTHON -m venv "$VENV_DIR"
fi

# 4. Install/upgrade dependencies
echo "-> Installing/upgrading dependencies (psutil)..."
"$VENV_PYTHON" -m pip install --quiet --upgrade pip
"$VENV_PYTHON" -m pip install --quiet --upgrade psutil

# 5. Ensure plugin is executable
echo "-> Making SwiftBar plugin executable..."
chmod +x "$PLUGIN_SRC"

# 6. Verify SwiftBar is installed
if ! [ -d "/Applications/SwiftBar.app" ] && ! [ -d "$HOME/Applications/SwiftBar.app" ]; then
    echo "-> SwiftBar not found. Installing via Homebrew Cask..."
    brew install --cask swiftbar
fi

echo ""
echo "[OK] RAM Monitor SwiftBar plugin is set up!"
echo ""
echo "How to configure SwiftBar:"
echo "    1. Launch SwiftBar from your Applications or run: open -a SwiftBar"
echo "    2. When prompted, select your SwiftBar plugins folder. We recommend setting it to:"
echo "       $SCRIPT_DIR/plugins"
echo "    3. If you already use SwiftBar with a different folder, create a symlink to our plugin:"
echo "       ln -s \"$PLUGIN_SRC\" \"/YOUR/EXISTING/PLUGINS/DIR/ram.5s.py\""
echo "============================================="
