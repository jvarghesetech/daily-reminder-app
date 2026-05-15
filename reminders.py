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


REPEAT_OPTIONS = ["daily", "weekdays", "weekends", "mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_MAP = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def reminder_active_today(r):
    repeat = r.get("repeat", "daily")
    weekday = datetime.now().weekday()  # 0=Mon, 6=Sun
    if repeat == "daily":
        return True
    if repeat == "weekdays":
        return weekday < 5
    if repeat == "weekends":
        return weekday >= 5
    if repeat in DAY_MAP:
        return weekday == DAY_MAP[repeat]
    return True


def cmd_add(name, time_str, repeat="daily", category="general"):
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        print(f"  Invalid time format '{time_str}'. Use HH:MM (e.g. 08:00)")
        sys.exit(1)

    if repeat not in REPEAT_OPTIONS:
        print(f"  Invalid repeat '{repeat}'. Choose from: {', '.join(REPEAT_OPTIONS)}")
        sys.exit(1)

    reminders = load_reminders()
    reminders.append({"name": name, "time": time_str, "repeat": repeat, "category": category})
    save_reminders(reminders)
    print(f"  Added: '{name}' at {time_str} ({repeat}) [{category}]")


def cmd_list(filter_category=None):
    reminders = load_reminders()
    if not reminders:
        print("  No reminders set. Add one with: python reminders.py add \"name\" HH:MM")
        return
    if filter_category:
        reminders_filtered = [(i+1, r) for i, r in enumerate(reminders) if r.get("category", "general") == filter_category]
    else:
        reminders_filtered = [(i+1, r) for i, r in enumerate(reminders)]

    if not reminders_filtered:
        print(f"  No reminders in category '{filter_category}'.")
        return

    print(f"\n  {'#':<4} {'Time':<8} {'Repeat':<10} {'Category':<12} Reminder")
    print("  " + "-" * 56)
    for idx, r in reminders_filtered:
        repeat = r.get("repeat", "daily")
        category = r.get("category", "general")
        print(f"  {idx:<4} {r['time']:<8} {repeat:<10} {category:<12} {r['name']}")
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
            if r["time"] == now and key not in fired_today and reminder_active_today(r):
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
  python reminders.py add "name" HH:MM [repeat] [category]   Add a reminder
                                                  repeat: daily (default), weekdays, weekends,
                                                          mon, tue, wed, thu, fri, sat, sun
                                                  category: health, work, personal, general (default)
  python reminders.py list [category]              List all reminders (or filter by category)
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
            print("  Usage: python reminders.py add \"Reminder name\" HH:MM [repeat]")
            sys.exit(1)
        repeat = args[3] if len(args) > 3 else "daily"
        category = args[4] if len(args) > 4 else "general"
        cmd_add(args[1], args[2], repeat, category)

    elif command == "list":
        category = args[1] if len(args) > 1 else None
        cmd_list(category)

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
