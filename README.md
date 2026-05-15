# Daily Reminder App

A simple command-line app to manage daily reminders with macOS notifications.

## Features

- Add reminders with a name and time
- List all your reminders
- Delete reminders
- Background daemon that sends macOS notifications at the right time

## Usage

### Add a reminder
```bash
python reminders.py add "Drink water" 08:00
python reminders.py add "Go for a walk" 18:30
python reminders.py add "Read a book" 21:00
```

### List all reminders
```bash
python reminders.py list
```

### Delete a reminder
```bash
python reminders.py delete 1
```

### Start the notification daemon
```bash
python reminders.py run
```

Keep the daemon running in a terminal tab — it checks every 30 seconds and fires a macOS notification when a reminder time matches.

## Requirements

- Python 3.6+
- macOS (for notifications via `osascript`)

No external dependencies needed.

## Data

Reminders are stored in `~/.daily_reminders.json`.
