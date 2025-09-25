# To-Do Manager — Modern GUI (Python + JSON)

A single-user, local To-Do Manager implemented in Python with a modern Tkinter GUI.
Features:
- Create / Read / Update / Delete tasks (CRUD)
- Local JSON persistence (`tasks.json`) with atomic saves
- Priority badges (High=red, Medium=blue, Low=green). Done tasks show black badge.
- Timer per-task (start/pause/reset). When timer finishes the task is marked done.
- Search, filter by status and priority, sort by newest/oldest
- Simple, modern UI designed to be clean and responsive on desktop

## Requirements
- Python 3.8+ (Tkinter included). No external packages required.
- Recommended screen size: 1024×600 or larger for best layout.

## How to run
1. Unzip the project folder.
2. In a terminal, run:
```bash
python app.py
```
This will open the GUI.

## Project layout
```
todo_manager_gui/
├─ app.py
├─ tasks.json
├─ todo/
│  ├─ __init__.py
│  ├─ models.py
│  ├─ storage.py
│  └─ utils.py
├─ todo.log
└─ tests/
   └─ test_storage.py
```

## Notes & future enhancements
- Concurrency: currently this is a single-process app. Atomic writes are used to reduce corruption risk.
- Backup: corrupt JSONs are backed up to `tasks.json.bak`.
- Future: export to CSV, web UI, login/multi-user, notifications.

Enjoy! — built as a polished, simple, single-user desktop app.
