# RAM Monitor

A lightweight macOS menu bar utility that displays live RAM usage at a glance and lists memory-intensive processes. Built for SwiftBar.

```text
77%   -- appears in your menu bar, updating dynamically every 5 seconds
```

## Features

- **Live status bar:** Real-time RAM usage percentage, updating every 5 seconds.
- **Memory overview:** Used/free RAM, memory pressure, and swap usage in the dropdown.
- **Top processes:** Lists the top memory-consuming processes with click-to-kill.
- **Action shortcuts:** Open Activity Monitor or refresh data instantly.

## Requirements

- macOS 14+
- SwiftBar installed via Homebrew Cask: `brew install --cask swiftbar`
- Python 3.10+ with `psutil`

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:kapilthakare-cyberpunk/ram-menubar.git
   cd ram-menubar
   ```

2. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. Open SwiftBar and select the plugin directory:
   ```text
   /Users/kapilthakare/Projects/ram-menubar/plugins
   ```

## Configuration

Edit `plugins/ram.5s.py` to adjust:

```python
TOP_N = 5
IGNORE_NAMES = {
    "kernel_task", "WindowServer", "launchd", "loginwindow",
    "Dock", "Finder", "SystemUIServer", "mediaremoted", "callservicesd",
}
```

Change the refresh interval by renaming the plugin file, for example `ram.10s.py` for 10-second updates.

## Uninstallation

```bash
./uninstall.sh
brew uninstall --cask swiftbar
```
