#!/usr/bin/env python3
# <swiftbar.title>RAM Monitor</swiftbar.title>
# <swiftbar.version>v2.0</swiftbar.version>
# <swiftbar.author>Kapil Thakare</swiftbar.author>
# <swiftbar.author.github>kapilthakare-cyberpunk</swiftbar.author.github>
# <swiftbar.desc>Live RAM usage, swap, memory pressure, and top consumer processes with click-to-kill.</swiftbar.desc>
# <swiftbar.dependencies>python3, psutil</swiftbar.dependencies>
# <swiftbar.abouturl>https://github.com/kapilthakare-cyberpunk/ram-menubar</swiftbar.abouturl>
# <swiftbar.runInBash>false</swiftbar.runInBash>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>false</swiftbar.hideLastUpdated>

import os
import sys
import importlib.util
import logging
import subprocess
from typing import Any, Dict, List, Optional, Tuple

# ── Bootstrap: run under the project .venv so psutil is available ───────────
_SCRIPT = os.path.realpath(__file__)
_VENV_DIR = os.path.normpath(os.path.join(os.path.dirname(_SCRIPT), "..", ".venv"))
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
    psutil = None

# ── Configuration ─────────────────────────────────────────────────────────────
HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, ".local_staging_trash", "logs")
TOP_N = 5
CACHE_TTL = 2  # seconds
RCLONE_TIMEOUT = 6

IGNORE_NAMES = {
    "kernel_task", "WindowServer", "launchd", "loginwindow",
    "Dock", "Finder", "SystemUIServer", "mediaremoted", "callservicesd",
}

GB = 1024 ** 3
MB = 1024 ** 2

# ── UI Constants ─────────────────────────────────────────────────────────────
COLOR_BLUE = "#007AFF"
COLOR_GREEN = "#34C759"
COLOR_GRAY = "#8E8E93"
COLOR_ORANGE = "#FF9500"
COLOR_RED = "#FF3B30"
COLOR_PURPLE = "#AF52DE"
COLOR_TEAL = "#5AC8FA"

# ── Logging ──────────────────────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "ram_monitor.log"),
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
log = logging.getLogger("ram_monitor")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _clean(text: str) -> str:
    """Strip chars that would break SwiftBar line-attribute parsing."""
    return text.replace("|", "-").replace("\n", " ").strip()


def _cache_read(path: str, ttl: int) -> Optional[Any]:
    """Read a JSON cache file if it exists and is fresh."""
    now = time.time()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if now - data.get("timestamp", 0) < ttl:
            return data.get("payload")
    except Exception as exc:
        log.warning("Failed to read cache (%s): %s", path, exc)
    return None


def _cache_write(path: str, payload: Any) -> None:
    """Write a JSON cache file with a timestamp."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"timestamp": time.time(), "payload": payload}, f)
    except Exception as exc:
        log.warning("Failed to write cache (%s): %s", path, exc)


def run_cmd(cmd: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """Run a subprocess with default stdout/stderr capture and UTF-8 text."""
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)
    kwargs.setdefault("text", True)
    return subprocess.run(cmd, **kwargs)


def _pressure_color() -> Tuple[str, str]:
    """Return color and label for memory pressure based on system state."""
    try:
        res = run_cmd(["memory_pressure"], timeout=3)
        if res.returncode == 0 and "Memory pressure: normal" in (res.stdout or ""):
            return COLOR_GREEN, "Normal"
    except Exception:
        pass
    return COLOR_ORANGE, "Elevated"


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


def _fmt_gb(value: float) -> str:
    """Format bytes to GB with 1 decimal."""
    return f"{value / GB:.1f} GB"


def _fmt_mb(value: float) -> str:
    """Format bytes to MB with 0 decimals."""
    return f"{value / MB:.0f} MB"


# ── Data Fetchers ─────────────────────────────────────────────────────────────
def get_memory_stats() -> Dict[str, Any]:
    """Return memory and swap statistics."""
    try:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": vm.total,
            "used": vm.used,
            "free": vm.free,
            "active": vm.active,
            "inactive": vm.inactive,
            "wired": getattr(vm, "wired", 0),
            "compressed": getattr(vm, "compressed", 0),
            "percent": vm.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_free": swap.free,
            "swap_percent": swap.percent,
        }
    except Exception as exc:
        log.error("Failed to get memory stats: %s", exc, exc_info=True)
        return {}


def get_top_processes() -> List[Dict[str, Any]]:
    """Return top memory-consuming processes, excluding system processes."""
    procs = []
    try:
        for p in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                mi = p.info["memory_info"]
                nm = p.info["name"] or "?"
                if mi and nm not in IGNORE_NAMES:
                    procs.append({
                        "pid": p.info["pid"],
                        "name": nm,
                        "rss": mi.rss,
                        "vms": getattr(mi, "vms", 0),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as exc:
        log.warning("Failed to enumerate processes: %s", exc)

    procs.sort(key=lambda x: x["rss"], reverse=True)
    return procs[:TOP_N]


# ── Menu Sections ─────────────────────────────────────────────────────────────
def render_header(stats: Dict[str, Any]) -> None:
    """Render the menu bar title with usage percentage."""
    pct = int(round(stats.get("percent", 0)))
    print(f"{pct}% | font=.AppleSystemUIFont size=13")


def render_overview(stats: Dict[str, Any]) -> None:
    """Render memory overview section."""
    print("---")
    print("Memory Overview")

    used = stats.get("used", 0)
    total = stats.get("total", 0)
    free = stats.get("free", 0)
    pct = stats.get("percent", 0)

    print(f"RAM: {_fmt_gb(used)} / {_fmt_gb(total)}  ({pct:.1f}%) | color={COLOR_BLUE}")
    print(f"Free: {_fmt_gb(free)} | color={COLOR_GREEN}")

    # Memory pressure
    pressure_color, pressure_label = _pressure_color()
    print(f"Pressure: {pressure_label} | color={pressure_color}")

    # Swap
    swap_total = stats.get("swap_total", 0)
    swap_used = stats.get("swap_used", 0)
    if swap_total:
        print(f"Swap: {_fmt_gb(swap_used)} / {_fmt_gb(swap_total)} | color={COLOR_ORANGE}")
    else:
        print("Swap: none | color={COLOR_GRAY}")


def render_top_processes(procs: List[Dict[str, Any]]) -> None:
    """Render top memory-consuming processes with kill actions."""
    print("---")
    print(f"Top {TOP_N} Processes by RAM")

    if not procs:
        print("-- (no processes) | color={COLOR_GRAY}")
        return

    for p in procs:
        pid = p["pid"]
        name = p["name"]
        rss = p["rss"]
        label = f"{name[:32]:<32}  {_fmt_mb(rss):>7}"
        print(f"-- {_clean(label)} | {_kill_action(pid, name)}")


def render_actions() -> None:
    """Render utility actions."""
    print("---")
    print("Actions")
    print("-- Refresh | refresh=true")
    print("-- Open Activity Monitor | bash=open param1=/System/Applications/Utilities/Activity Monitor.app terminal=false")


# ── Renderer ──────────────────────────────────────────────────────────────────
def main() -> None:
    if psutil is None:
        print("err")
        print("---")
        print("psutil not installed")
        print("-- Install psutil: pip install psutil")
        return

    stats = get_memory_stats()
    if not stats:
        print("err")
        print("---")
        print("Failed to read memory stats")
        print("-- Refresh | refresh=true")
        return

    procs = get_top_processes()

    render_header(stats)
    render_overview(stats)
    render_top_processes(procs)
    render_actions()


if __name__ == "__main__":
    main()
