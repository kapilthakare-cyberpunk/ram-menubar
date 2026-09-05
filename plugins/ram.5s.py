#!/usr/bin/env python3
# <xbar.title>PNZ RAM Monitor</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>Kapil Thakare</xbar.author>
# <xbar.author.github>kapilthakare-cyberpunk</xbar.author.github>
# <xbar.desc>Live RAM usage percentage in the menu bar with top process list and click-to-kill.</xbar.desc>
# <xbar.dependencies>python3, psutil</xbar.dependencies>
# <xbar.abouturl>https://github.com/kapilthakare-cyberpunk/ram-menubar</xbar.abouturl>
# <swiftbar.runInBash>false</swiftbar.runInBash>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>false</swiftbar.hideLastUpdated>
"""
PNZ RAM Monitor — SwiftBar plugin
Reports live RAM usage in the macOS menu bar and lists the top memory consumers.

SwiftBar derives the refresh interval from the filename: `ram.5s.py` -> every 5s.
Click any process to confirm-then-force-quit it. Click "Refresh" to force an update.
"""

import os
import sys
import importlib.util

# ── Bootstrap: run under the project .venv so psutil is available ───────────
# The venv python is the same base interpreter (just a symlink), so we can't
# tell them apart by executable path. Re-exec only when psutil isn't importable
# from the current interpreter AND we're not already inside the venv.
_SCRIPT = os.path.realpath(__file__)  # resolve symlinks so ../.venv stays correct
_VENV_DIR = os.path.normpath(
    os.path.join(os.path.dirname(_SCRIPT), "..", ".venv")
)
_VENV_PY = os.path.join(_VENV_DIR, "bin", "python3")

if (
    importlib.util.find_spec("psutil") is None
    and os.path.exists(_VENV_PY)
    and os.path.realpath(sys.prefix) != os.path.realpath(_VENV_DIR)
):
    os.execv(_VENV_PY, [_VENV_PY, _SCRIPT])

try:
    import psutil
except ImportError:
    psutil = None  # main() reports this gracefully

# ── Config ────────────────────────────────────────────────────────────────────
TOP_N = 5
IGNORE_NAMES = {
    "kernel_task", "WindowServer", "launchd", "loginwindow",
    "Dock", "Finder", "SystemUIServer", "mediaremoted", "callservicesd",
}

GB = 1024 ** 3
MB = 1024 ** 2


def _clean(text: str) -> str:
    """Strip chars that would break SwiftBar line-attribute parsing (`|`)."""
    return text.replace("|", "-").replace("\n", " ").strip()


def _kill_action(pid: int, name: str) -> str:
    """SwiftBar click attributes that confirm, then force-quit a PID."""
    safe_name = name.replace("|", "-").replace('"', "'")
    dialog = (
        f'tell application "System Events" to display dialog '
        f'"Terminate {safe_name} (PID {pid})?" '
        f'buttons {{"Cancel", "Kill"}} default button "Cancel" '
        f'cancel button "Cancel" with icon caution'
    )
    return (
        f"bash=/usr/bin/osascript param1=-e param2={dialog} "
        f'param3=-e param4=do shell script "kill -9 {pid}" '
        f"terminal=false refresh=true"
    )


def main() -> None:
    if psutil is None:
        print("err")
        print("---")
        print("psutil not installed")
        print("-- Install psutil: pip install psutil")
        return
    try:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
    except Exception as e:  # never crash the menu bar; surface the error instead
        print("err")
        print("---")
        print(f"psutil failed: {_clean(str(e))}")
        print("-- Install psutil: pip install psutil")
        return

    pct = vm.percent
    pct_int = int(round(pct))
    used = vm.used / GB
    total = vm.total / GB

    # ── Menu bar title: percentage in the system font (color follows the menu bar) ──
    print(f"{pct_int}% | font=.AppleSystemUIFont size=13")

    # ── Dropdown ──
    print("---")
    print(f"RAM: {used:.1f} GB / {total:.0f} GB  ({pct_int}%)")
    if swap.total:
        print(f"Swap: {swap.used / GB:.1f} GB / {swap.total / GB:.0f} GB")
    else:
        print("Swap: none")

    print("-- Top Processes by RAM")
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            mi = p.info["memory_info"]
            nm = p.info["name"] or "?"
            if mi and nm not in IGNORE_NAMES:
                procs.append((p.info["pid"], nm, mi.rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    top = sorted(procs, key=lambda x: x[2], reverse=True)[:TOP_N]
    if not top:
        print("-- (no processes)")
    for pid, name, rss in top:
        label = f"{name[:32]:<32}  {rss / MB:>7.0f} MB"
        print(f"-- {_clean(label)} | {_kill_action(pid, name)}")

    print("--")
    print("-- ↻ Refresh | refresh=true")


if __name__ == "__main__":
    main()
