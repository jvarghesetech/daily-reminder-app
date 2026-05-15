#!/usr/bin/env python3
"""Set up or remove the Daily Reminder App as a macOS Launch Agent (auto-starts on login)."""

import sys
import subprocess
from pathlib import Path

PLIST_NAME = "com.dailyreminder.app.plist"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_PATH = LAUNCH_AGENTS_DIR / PLIST_NAME


def get_script_path():
    return (Path(__file__).parent / "reminders.py").resolve()


def get_python_path():
    result = subprocess.run(["which", "python3"], capture_output=True, text=True)
    return result.stdout.strip()


def cmd_install():
    python = get_python_path()
    script = get_script_path()

    if not script.exists():
        print(f"  Could not find reminders.py at {script}")
        sys.exit(1)

    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dailyreminder.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>{script}</string>
        <string>run</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{Path.home()}/.daily_reminders.log</string>
    <key>StandardErrorPath</key>
    <string>{Path.home()}/.daily_reminders_error.log</string>
</dict>
</plist>
"""

    PLIST_PATH.write_text(plist_content)
    subprocess.run(["launchctl", "load", str(PLIST_PATH)])
    print(f"  Auto-start installed! The reminder daemon will now run automatically on login.")
    print(f"  Logs: ~/.daily_reminders.log")


def cmd_uninstall():
    if not PLIST_PATH.exists():
        print("  Auto-start is not installed.")
        return
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)])
    PLIST_PATH.unlink()
    print("  Auto-start removed. The daemon will no longer run on login.")


def cmd_status():
    result = subprocess.run(
        ["launchctl", "list", "com.dailyreminder.app"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  Auto-start is ACTIVE — daemon is running in the background.")
    else:
        print("  Auto-start is NOT active. Run: python setup_autostart.py install")


def print_help():
    print("""
  Daily Reminder — Auto-start Setup
  -----------------------------------
  python setup_autostart.py install     Install as a macOS Login Item (runs on startup)
  python setup_autostart.py uninstall   Remove auto-start
  python setup_autostart.py status      Check if auto-start is active
""")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print_help()
        return

    command = args[0]
    if command == "install":
        cmd_install()
    elif command == "uninstall":
        cmd_uninstall()
    elif command == "status":
        cmd_status()
    else:
        print(f"  Unknown command: '{command}'")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
