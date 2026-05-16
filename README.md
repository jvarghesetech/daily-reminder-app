# Daily Reminder App

A command-line app for macOS to create, manage, and receive notifications for daily reminders.

## Features

- Add reminders with a name, time, repeat pattern, category, sound, and priority
- List all reminders or filter by category
- Edit reminder properties (name, time, repeat, category, sound)
- Delete reminders by index
- Search reminders by keyword
- Pause and resume individual reminders
- **Snooze** — postpone a reminder by any number of minutes (default: 10 min)
- Priority levels (low, medium, high) — shown in sorted order
- Repeat options — daily, weekdays, weekends, or specific days
- Sound options — Glass, Ping, Basso, and more
- Activity log with date filtering
- Import/export reminders for backup and sharing
- "Next" command — shows upcoming reminders for today
- Background daemon that checks every 30 seconds and fires macOS notifications

## Usage

### Add a reminder
```bash
python reminders.py add "Drink water" 08:00
python reminders.py add "Go for a walk" 18:30 --repeat weekdays --priority high
```

### List all reminders
```bash
python reminders.py list
```

### Edit a reminder
```bash
python reminders.py edit 1
```

### Delete a reminder
```bash
python reminders.py delete 1
```

### Snooze a reminder
```bash
python reminders.py snooze 1          # snooze for 10 minutes (default)
python reminders.py snooze 1 20       # snooze for 20 minutes
```

### Search reminders
```bash
python reminders.py search "water"
```

### See what's coming up today
```bash
python reminders.py next
```

### Start the notification daemon
```bash
python reminders.py run
```

Keep the daemon running in a terminal tab — it checks every 30 seconds and fires a macOS notification when a reminder time matches.

### Auto-start on login
```bash
python setup_autostart.py
```

## Requirements

- Python 3.6+
- macOS (notifications via `osascript`)

No external dependencies needed.

## Data

Reminders are stored in `~/.daily_reminders.json`.
