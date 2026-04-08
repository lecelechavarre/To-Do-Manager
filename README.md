# Task Manager                    
Python • Tkinter • JSON       
      
A single-user, desktop-based task management application built with Python and Tkinter.  
Designed with clear separation of concerns, atomic persistence guarantees, and a minimal dependency footprint.
 
--- 

## 1. Purpose 
 
This project provides a lightweight, local task management system intended for: 

- Personal productivity
- Offline-first environments
- Educational demonstration of layered Python architecture
- Simple desktop task tracking without external dependencies

The application prioritizes: 

- Data integrity
- Maintainable architecture
- Zero external packages
- Predictable behavior
- Clean, modern UI

---

## 2. Architecture Overview

The application follows a layered design to maintain separation of concerns:

```
GUI Layer (app.py)
        │
Domain Layer (todo/models.py)
        │
Persistence Layer (todo/storage.py)
        │
JSON File (tasks.json)
```

### Component Responsibilities

| File | Responsibility |
|------|---------------|
| `app.py` | GUI rendering, user interaction, event handling |
| `models.py` | Task domain model, validation, business rules |
| `storage.py` | Atomic read/write logic, corruption handling |
| `utils.py` | Shared helpers (formatting, time utilities, etc.) |
| `tasks.json` | Persistent task storage |
| `todo.log` | Application logging |
| `tests/` | Unit tests (primarily storage layer) |

This structure allows:

- Independent testing of storage logic
- Clear boundary between UI and data
- Easier future migration (e.g., JSON → SQLite)

---

## 3. Feature Set

### Core CRUD
- Create tasks
- Read/View tasks
- Update tasks
- Delete tasks

### Task Attributes
- Title
- Description
- Priority (High / Medium / Low)
- Status (Pending / Done)
- Creation timestamp
- Per-task countdown timer

### Timer System
- Start / Pause / Reset timer
- Automatic completion when timer reaches zero
- UI updates reflect task state in real-time

### Filtering & Sorting
- Search by title
- Filter by:
  - Status
  - Priority
- Sort by:
  - Newest
  - Oldest

### Visual Indicators
- Priority badges:
  - High → Red
  - Medium → Blue
  - Low → Green
- Completed tasks → Black badge

---

## 4. Data Model

Tasks are stored in `tasks.json`.

### Example Structure

```json
{
  "id": "uuid-string",
  "title": "Write documentation",
  "description": "Complete enterprise-grade README",
  "priority": "high",
  "status": "pending",
  "created_at": "2026-02-12T08:30:00Z",
  "timer_total_seconds": 1500,
  "timer_remaining_seconds": 1200
}
```

### Constraints

- `priority` ∈ {high, medium, low}
- `status` ∈ {pending, done}
- `timer_remaining_seconds >= 0`
- `id` is unique (UUID recommended)

---

## 5. Persistence Strategy

### Atomic Writes

To prevent corruption:

1. Data is written to a temporary file.
2. The temp file replaces `tasks.json`.
3. If replacement fails, original file remains intact.

This prevents partial writes in cases such as:

- Power interruption
- Process termination
- Disk write failure

### Corruption Handling

If `tasks.json` fails to load:

- It is backed up as `tasks.json.bak`
- A new file is created
- Error is logged in `todo.log`

---

## 6. Logging

Application-level logging is written to:

```
todo.log
```

Typical events logged:

- Load failures
- Write errors
- Backup operations
- Unexpected exceptions

This allows easier debugging in production environments.

---

## 7. Requirements

- Python 3.8+
- Tkinter (included with standard Python)
- No external dependencies

Recommended screen resolution:

```
1024 × 600 or larger
```

---

## 8. Running the Application

```bash
python app.py
```

This launches the desktop GUI.

---

## 9. Testing

Unit tests are located in:

```
tests/
```

To run tests (if pytest is installed):

```bash
pytest tests/
```

### Covered Areas

- JSON read/write logic
- Atomic save behavior
- Corrupt file fallback handling

GUI testing is intentionally not automated in this version.

---

## 10. Concurrency Model

This application is designed as:

> Single-process, single-user

It does not support:

- Concurrent file access
- Multi-instance synchronization
- Multi-user state consistency

If multiple instances are launched simultaneously, race conditions may occur.

Future improvement would include:

- File locking
- Database-backed persistence

---

## 11. Design Decisions

### JSON Instead of SQLite

Chosen for:

- Simplicity
- Human-readable storage
- No external dependencies
- Suitable for single-user environment

Trade-off:
- Not optimized for large datasets
- No built-in concurrency control

---

### Tkinter Instead of PyQt / Kivy

Chosen for:

- Native availability
- Zero installation friction
- Lightweight footprint

Trade-off:
- Limited advanced UI components
- Less modern widget ecosystem

---

### No External Libraries

Intentional design choice to:

- Ensure portability
- Avoid dependency management
- Keep environment requirements minimal

---

## 12. Limitations

- Single-user only
- File-based storage (not scalable)
- No authentication system
- No background notifications
- GUI-only (no CLI interface)

---

## 13. Performance Characteristics

Expected behavior:

- Instant load for small to medium task sets
- Linear scaling with task count
- Suitable for personal task volumes (< 10,000 tasks)

For large-scale usage, database migration is recommended.

---

## 14. Future Roadmap

Planned enhancements:

- CSV export
- SQLite backend option
- Multi-user support
- Authentication layer
- Desktop notifications
- Web-based interface
- Packaging as executable (PyInstaller)

---

## 15. Project Structure

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

---

## 16. License

For personal and educational use.  
Modify and extend as needed.

---
