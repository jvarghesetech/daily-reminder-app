#!/usr/bin/env python3
"""Daily Reminder App — add, list, delete, snooze, and receive macOS notifications."""

import json
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".daily_reminders.json"
SNOOZE_FILE = Path.home() / ".daily_reminders_snooze.json"


def load_reminders():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return []


def save_reminders(reminders):
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=2)


def load_snoozed():
    if SNOOZE_FILE.exists():
        with open(SNOOZE_FILE) as f:
            return json.load(f)
    return []


def save_snoozed(snoozed):
    with open(SNOOZE_FILE, "w") as f:
        json.dump(snoozed, f, indent=2)


def notify(title, message):
    script = f'display notification "{message}" with title "{title}" sound name "Glass"'
    subprocess.run(["osascript", "-e", script])


def cmd_snooze(index, minutes=10):
    reminders = load_reminders()
    if index < 1 or index > len(reminders):
        print(f"  No reminder with index {index}.")
        sys.exit(1)
    reminder = reminders[index - 1]
    snooze_until = (datetime.now() + timedelta(minutes=minutes)).strftime("%H:%M")
    snoozed = load_snoozed()
    snoozed.append({"name": reminder["name"], "time": snooze_until})
    save_snoozed(snoozed)
    print(f"  Snoozed '{reminder['name']}' — will remind again at {snooze_until}")


def cmd_add(name, time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        print(f"  Invalid time format '{time_str}'. Use HH:MM (e.g. 08:00)")
        sys.exit(1)

    reminders = load_reminders()
    reminders.append({"name": name, "time": time_str})
    save_reminders(reminders)
    print(f"  Added: '{name}' at {time_str}")


def cmd_list():
    reminders = load_reminders()
    if not reminders:
        print("  No reminders set. Add one with: python reminders.py add \"name\" HH:MM")
        return
    print(f"\n  {'#':<4} {'Time':<8} Reminder")
    print("  " + "-" * 36)
    for i, r in enumerate(reminders, 1):
        print(f"  {i:<4} {r['time']:<8} {r['name']}")
    print()


def cmd_delete(index):
    reminders = load_reminders()
    if index < 1 or index > len(reminders):
        print(f"  No reminder with index {index}.")
        sys.exit(1)
    removed = reminders.pop(index - 1)
    save_reminders(reminders)
    print(f"  Deleted: '{removed['name']}' at {removed['time']}")


def cmd_run():
    print("  Reminder daemon running. Press Ctrl+C to stop.\n")
    fired_today = set()

    while True:
        now = datetime.now().strftime("%H:%M")
        date_key = datetime.now().strftime("%Y-%m-%d")

        # Check regular reminders
        reminders = load_reminders()
        for r in reminders:
            key = f"{date_key}-{r['name']}-{r['time']}"
            if r["time"] == now and key not in fired_today:
                print(f"  REMINDER: {r['name']} ({r['time']})")
                notify("Daily Reminder", r["name"])
                fired_today.add(key)

        # Check snoozed reminders
        snoozed = load_snoozed()
        remaining = []
        for s in snoozed:
            key = f"snooze-{date_key}-{s['name']}-{s['time']}"
            if s["time"] == now and key not in fired_today:
                print(f"  SNOOZE REMINDER: {s['name']} ({s['time']})")
                notify("Snoozed Reminder", s["name"])
                fired_today.add(key)
            else:
                remaining.append(s)
        if len(remaining) != len(snoozed):
            save_snoozed(remaining)

        # Clean up old keys at midnight
        if now == "00:00":
            fired_today = {k for k in fired_today if k.startswith(date_key)}
            save_snoozed([])

        time.sleep(30)


def print_help():
    print("""
  Daily Reminder App
  ------------------
  python reminders.py add "Reminder name" HH:MM   Add a reminder
  python reminders.py list                         List all reminders
  python reminders.py delete <number>              Delete a reminder by number
  python reminders.py snooze <number> [minutes]   Snooze a reminder (default: 10 mins)
  python reminders.py run                          Start the notification daemon
""")


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return

    command = args[0]

    if command == "add":
        if len(args) < 3:
            print("  Usage: python reminders.py add \"Reminder name\" HH:MM")
            sys.exit(1)
        cmd_add(args[1], args[2])

    elif command == "list":
        cmd_list()

    elif command == "delete":
        if len(args) < 2 or not args[1].isdigit():
            print("  Usage: python reminders.py delete <number>")
            sys.exit(1)
        cmd_delete(int(args[1]))

    elif command == "snooze":
        if len(args) < 2 or not args[1].isdigit():
            print("  Usage: python reminders.py snooze <number> [minutes]")
            sys.exit(1)
        minutes = int(args[2]) if len(args) > 2 and args[2].isdigit() else 10
        cmd_snooze(int(args[1]), minutes)

    elif command == "run":
        try:
            cmd_run()
        except KeyboardInterrupt:
            print("\n  Daemon stopped.")

    else:
        print(f"  Unknown command: '{command}'")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
