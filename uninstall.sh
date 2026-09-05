#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  uninstall.sh  -  RAM Monitor uninstaller (Legacy cleanup)
# ---------------------------------------------------------------------------
set -euo pipefail

PLIST_LABEL="com.ram-menubar"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
APP_PATH="$HOME/Applications/RAMMonitor.app"
LOG_OUT="$HOME/Library/Logs/ram-menubar.log"
LOG_ERR="$HOME/Library/Logs/ram-menubar-err.log"

echo ""
echo "-> Unloading legacy LaunchAgent..."
launchctl bootout gui/$(id -u) "$PLIST_PATH" 2>/dev/null || true

echo "-> Removing legacy plist and files..."
rm -f "$PLIST_PATH"
rm -rf "$APP_PATH"
rm -f "$LOG_OUT" "$LOG_ERR"

echo ""
echo "[OK] Legacy elements uninstalled."
echo "   (To completely remove SwiftBar, run: brew uninstall --cask swiftbar)"
echo ""
