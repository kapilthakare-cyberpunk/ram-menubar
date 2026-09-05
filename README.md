# 🖥️ PNZ RAM Monitor for macOS

[![OS](https://img.shields.io/badge/macOS-Tahoe%2026%2B-blue?style=flat-square&logo=apple)](https://www.apple.com/macos)
[![SwiftBar](https://img.shields.io/badge/SwiftBar-Compatible-orange?style=flat-square)](https://github.com/swiftbar/SwiftBar)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)

A lightweight macOS menu bar utility that displays live RAM usage at a glance and lists memory-intensive processes. Designed specifically to support macOS 26+ (Tahoe) via **SwiftBar**.

```text
68%   ← Appears in your menu bar, updating dynamically every 5 seconds
```

---

## ✨ Features

- **Live Status bar:** Displays real-time RAM usage percentage, updating every 5 seconds.
- **Process List:** Lists the top memory-consuming processes inside a dropdown.
- **Interactive Termination:** Click-to-kill option on any process to terminate memory-hogging tasks instantly (with confirmation dialog).
- **Swap Usage:** Displays swap memory usage alongside RAM in the dropdown.

---

## 🛠️ Requirements

- **Operating System:** macOS 10.15 Catalina or later (Fully supports macOS 26 Tahoe)
- **SwiftBar:** Installed via Homebrew cask: `brew install --cask swiftbar`
- **Python:** Python 3.10+ installed via Homebrew or system installation

---

## 📥 Installation

### 1. Clone the Repository
```bash
git clone git@github.com:kapilthakare-cyberpunk/ram-menubar.git
cd ram-menubar
```

### 2. Run the Installer
```bash
chmod +x install.sh
./install.sh
```

> [!NOTE]  
> The installer automates the following actions:
> - Cleans up legacy LaunchAgent `.plist` and Application bundle configurations.
> - Verifies and installs SwiftBar via Homebrew Cask if missing.
> - Sets up a project-local virtual environment (`.venv/`) and installs `psutil`.
> - Marks the SwiftBar plugin script `plugins/ram.5s.py` as executable.

---

## ⚙️ Configuration

### 1. Launch SwiftBar
Start SwiftBar from your Applications folder, or execute:
```bash
open -a SwiftBar
```

### 2. Select Plugin Directory
When prompted by SwiftBar, choose the plugins directory inside this repository:
```text
/Users/kapilthakare/Projects/ram-menubar/plugins
```

Alternatively, if you already have a configured SwiftBar plugin directory, you can symlink the plugin:
```bash
ln -s "$(pwd)/plugins/ram.5s.py" "/YOUR/EXISTING/PLUGINS/DIR/ram.5s.py"
```

### 3. Customize Settings
To adjust the process list and update speed, edit the configuration constants at the top of [plugins/ram.5s.py](file:///Users/kapilthakare/Projects/ram-menubar/plugins/ram.5s.py):

```python
# Configuration
TOP_N = 5    # number of processes shown in the dropdown

# System processes to exclude from the process list and kill list
IGNORE_NAMES = {
    "kernel_task", "WindowServer", "launchd", "loginwindow",
    "Dock", "Finder", "SystemUIServer", "mediaremoted", "callservicesd",
}
```

> [!TIP]
> To change the refresh interval, simply rename the plugin file to reflect the new timing (e.g., rename to `ram.10s.py` for a 10-second refresh interval).

---

## 🗑️ Uninstallation

To clean up configurations and legacy files:
```bash
./uninstall.sh
```

To remove SwiftBar:
```bash
brew uninstall --cask swiftbar
```

---

## 📂 Project Structure

```text
ram-menubar/
├── plugins/
│   └── ram.5s.py        # SwiftBar plugin script (uses psutil from .venv)
├── install.sh           # One-shot shell installer
├── uninstall.sh         # Teardown script for legacy configurations
└── README.md            # This documentation
```
