import os
import json
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from todo.models import Task
from todo import storage
from todo.utils import format_duration

# ---------- Configuration ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_PATH = os.path.join(BASE_DIR, "tasks.json")
LOG_PATH = os.path.join(BASE_DIR, "todo.log")

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

PRIORITY_COLORS = {
    "high": "#e53935",    # red
    "medium": "#1e88e5",  # blue
    "low": "#43a047",     # green
    "done": "#212121",    # black/near-black
}

# ---------- App ----------
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do Manager — Modern GUI")
        self.root.geometry("1000x650")
        self.root.minsize(800, 520)

        # style
        self.style = ttk.Style(root)
        self._setup_style()

        # data
        self.tasks = storage.load_tasks(TASKS_PATH)
        self.timers = {}  # task_id -> after_id
        self.timer_labels = {}  # task_id -> label widget to update

        # UI layout
        self._build_ui()
        self._render_tasks()

    def _setup_style(self):
        # Use a clean theme if available
        try:
            self.style.theme_use("clam")
        except:
            pass
        default_font = ("Segoe UI", 10)
        self.style.configure(".", font=default_font)
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Muted.TLabel", foreground="#666666")
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.root.configure(bg="#f4f6f8")

    def _build_ui(self):
        # top frame: title + search/filter
        top = ttk.Frame(self.root, padding=(12,10))
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.columnconfigure(1, weight=1)

        title = ttk.Label(top, text="To-Do Manager", style="Header.TLabel")
        title.grid(row=0, column=0, sticky="w")

        # search entry
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew", padx=8)
        self.search_var.trace_add("write", lambda *args: self._render_tasks())

        # filter controls
        self.status_filter = tk.StringVar(value="all")
        status_menu = ttk.OptionMenu(top, self.status_filter, "all", "all", "pending", "done", command=lambda _e: self._render_tasks())
        status_menu.grid(row=0, column=2, padx=6)

        self.priority_filter = tk.StringVar(value="all")
        priority_menu = ttk.OptionMenu(top, self.priority_filter, "all", "all", "high", "medium", "low", command=lambda _e: self._render_tasks())
        priority_menu.grid(row=0, column=3, padx=6)

        sort_btn = ttk.Button(top, text="Sort: Newest", command=lambda: self._toggle_sort(sort_btn))
        sort_btn.grid(row=0, column=4, padx=6)

        add_button = ttk.Button(top, text="Add Task", style="Accent.TButton", command=self._open_add_window)
        add_button.grid(row=0, column=5, padx=(12,0))

        # main frames
        left = ttk.Frame(self.root, padding=(12,6))
        left.grid(row=1, column=0, sticky="nswe")
        right = ttk.Frame(self.root, padding=(12,6))
        right.grid(row=1, column=1, sticky="nswe")

        # grid config to be responsive
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        # left: info / quick stats
        stats_card = ttk.Frame(left, style="Card.TFrame", padding=12)
        stats_card.grid(row=0, column=0, sticky="nwe")
        stats_title = ttk.Label(stats_card, text="Overview", font=("Segoe UI", 12, "bold"))
        stats_title.grid(row=0, column=0, sticky="w")
        self.stats_label = ttk.Label(stats_card, text="", style="Muted.TLabel")
        self.stats_label.grid(row=1, column=0, sticky="w", pady=(6,0))
        self._update_stats()

        # right: tasks list (scrollable)
        self.task_canvas = tk.Canvas(right, borderwidth=0, highlightthickness=0, bg="#f4f6f8")
        self.task_scroll = ttk.Scrollbar(right, orient="vertical", command=self.task_canvas.yview)
        self.task_frame = ttk.Frame(self.task_canvas)

        self.task_frame.bind(
            "<Configure>",
            lambda e: self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all"))
        )
        self.task_canvas.create_window((0,0), window=self.task_frame, anchor="nw")
        self.task_canvas.configure(yscrollcommand=self.task_scroll.set)

        self.task_canvas.grid(row=0, column=0, sticky="nswe")
        self.task_scroll.grid(row=0, column=1, sticky="ns")

        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        # internal state
        self.sort_newest = True

    def _toggle_sort(self, btn):
        self.sort_newest = not self.sort_newest
        btn.config(text=("Sort: Newest" if self.sort_newest else "Sort: Oldest"))
        self._render_tasks()

    def _update_stats(self):
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks if t.status != "done")
        done = total - pending
        high = sum(1 for t in self.tasks if t.priority == "high" and t.status != "done")
        txt = f"Total: {total}   Pending: {pending}   Done: {done}   High priority: {high}"
        self.stats_label.config(text=txt)

    def _render_tasks(self):
        # clear previous cards
        for child in self.task_frame.winfo_children():
            child.destroy()

        # prepare filtered+searched list
        q = self.search_var.get().strip().lower()
        status_f = self.status_filter.get()
        prio_f = self.priority_filter.get()

        tasks = list(self.tasks)
        if status_f != "all":
            tasks = [t for t in tasks if t.status == status_f]
        if prio_f != "all":
            tasks = [t for t in tasks if t.priority == prio_f]
        if q:
            tasks = [t for t in tasks if q in t.title.lower() or q in t.description.lower()]

        tasks.sort(key=lambda t: t.created_at, reverse=self.sort_newest)

        for i, task in enumerate(tasks):
            self._create_task_card(task, i)

        self._update_stats()

    def _create_task_card(self, task: Task, index: int):
        card = ttk.Frame(self.task_frame, style="Card.TFrame", padding=10, relief="flat")
        card.grid(row=index, column=0, sticky="ew", padx=(0,0), pady=(6,6))
        card.columnconfigure(1, weight=1)

        # priority badge
        color_key = "done" if task.status == "done" else task.priority
        badge_color = PRIORITY_COLORS.get(color_key, "#999999")
        badge = tk.Label(card, text=task.priority.upper() if task.status!="done" else "DONE", bg=badge_color, fg="white", padx=8, pady=4, font=("Segoe UI", 9, "bold"))
        badge.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0,10))

        # title
        title_txt = task.title
        if task.status == "done":
            title_txt = "✓ " + title_txt
        title_lbl = ttk.Label(card, text=title_txt, font=("Segoe UI", 11, "bold"))
        title_lbl.grid(row=0, column=1, sticky="w")

        # desc and meta
        desc_txt = task.description if task.description else "(no description)"
        desc_lbl = ttk.Label(card, text=desc_txt, style="Muted.TLabel")
        desc_lbl.grid(row=1, column=1, sticky="w")

        meta = f"Created: {task.created_at.split('T')[0]}"
        if task.due_date:
            meta += f"  •  Due: {task.due_date}"
        meta_lbl = ttk.Label(card, text=meta, style="Muted.TLabel")
        meta_lbl.grid(row=2, column=1, sticky="w", pady=(6,0))

        # right-side buttons
        btn_frame = ttk.Frame(card)
        btn_frame.grid(row=0, column=2, rowspan=3, sticky="e")

        edit_btn = ttk.Button(btn_frame, text="Edit", command=lambda t=task: self._open_edit_window(t))
        edit_btn.grid(row=0, column=0, padx=4, pady=2)

        if task.status != "done":
            done_btn = ttk.Button(btn_frame, text="Mark Done", command=lambda t=task: self._mark_done(t))
        else:
            done_btn = ttk.Button(btn_frame, text="Undo", command=lambda t=task: self._undo_done(t))
        done_btn.grid(row=0, column=1, padx=4, pady=2)

        del_btn = ttk.Button(btn_frame, text="Delete", command=lambda t=task: self._delete_task(t))
        del_btn.grid(row=0, column=2, padx=4, pady=2)

        # timer label only - no controls needed since timer starts automatically
        timer_frame = ttk.Frame(btn_frame)
        timer_frame.grid(row=1, column=0, columnspan=3, pady=(6,0))

        # elapsed time label
        elapsed = task.remaining_seconds if task.remaining_seconds is not None else 0
        elapsed_lbl = ttk.Label(timer_frame, text=f"Time: {format_duration(elapsed)}")
        elapsed_lbl.grid(row=0, column=0, padx=(0,6))
        self.timer_labels[task.id] = elapsed_lbl

        # Start timer automatically if not running and task is not done
        if task.id not in self.timers and task.status != "done":
            self._start_timer(task)

    # ---------- CRUD actions ----------
    def _open_add_window(self):
        self._open_task_window()

    def _open_edit_window(self, task: Task):
        self._open_task_window(task)

    def _open_task_window(self, task: Task = None):
        # modal window for add/edit task
        win = tk.Toplevel(self.root)
        win.transient(self.root)
        win.grab_set()
        win.title("Add Task" if task is None else "Edit Task")
        win.geometry("480x460")
        win.minsize(420,420)
        win.configure(bg="#f7f8fa")

        header = ttk.Frame(win, padding=12)
        header.pack(fill="x")
        title = ttk.Label(header, text=("Add a new task" if task is None else "Edit task"), font=("Segoe UI", 12, "bold"))
        title.pack(side="left")

        body = ttk.Frame(win, padding=12)
        body.pack(fill="both", expand=True)

        # Title
        ttk.Label(body, text="Title", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6,0))
        title_var = tk.StringVar(value=task.title if task else "")
        title_entry = ttk.Entry(body, textvariable=title_var)
        title_entry.pack(fill="x", pady=(0,6))

        # Description
        ttk.Label(body, text="Description", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6,0))
        desc_text = ScrolledText(body, height=6)
        desc_text.pack(fill="both", pady=(0,6))
        if task and task.description:
            desc_text.insert("1.0", task.description)

        # Priority & Due & Duration
        form_row = ttk.Frame(body)
        form_row.pack(fill="x", pady=(6,0))

        ttk.Label(form_row, text="Priority", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        prio_var = tk.StringVar(value=task.priority if task else "medium")
        prio_menu = ttk.OptionMenu(form_row, prio_var, prio_var.get(), "high", "medium", "low")
        prio_menu.grid(row=1, column=0, padx=(0,12), sticky="w")

        ttk.Label(form_row, text="Due (YYYY-MM-DD)", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w")
        due_var = tk.StringVar(value=task.due_date if task and task.due_date else "")
        due_entry = ttk.Entry(form_row, textvariable=due_var)
        due_entry.grid(row=1, column=1, padx=(6,12), sticky="w")

        # action buttons
        btn_frame = ttk.Frame(body)
        btn_frame.pack(fill="x", pady=(18,0))
        save_btn = ttk.Button(btn_frame, text="Save", style="Accent.TButton")
        save_btn.pack(side="right", padx=(6,0))
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=win.destroy)
        cancel_btn.pack(side="right")

        def on_save():
            title_text = title_var.get().strip()
            if not title_text:
                messagebox.showwarning("Validation error", "Title is required.")
                return
            description = desc_text.get("1.0", "end").strip()
            prio = prio_var.get()
            due = due_var.get().strip() or None

            if task is None:
                # add new
                new_id = storage.get_next_id(self.tasks)
                start_time = datetime.now()
                new_task = Task(
                    id=new_id,
                    title=title_text,
                    description=description,
                    status="pending",
                    priority=prio,
                    created_at=start_time.isoformat(),
                    due_date=due,
                    duration_seconds=0,  # Duration will be counted up automatically
                    remaining_seconds=0,  # Will be used to track elapsed time
                )
                self.tasks.append(new_task)
                logging.info(f"Added task {new_task.id}: {new_task.title}")
            else:
                # update existing
                task.title = title_text
                task.description = description
                task.priority = prio
                task.due_date = due
                # Keep the existing elapsed time (remaining_seconds) when editing
                logging.info(f"Updated task {task.id}")

            storage.save_tasks(TASKS_PATH, self.tasks)
            self._render_tasks()
            win.destroy()

        save_btn.config(command=on_save)

    def _mark_done(self, task: Task):
        task.status = "done"
        task.remaining_seconds = 0
        # stop timer if running
        if task.id in self.timers:
            self._stop_timer(task.id)
        storage.save_tasks(TASKS_PATH, self.tasks)
        self._render_tasks()

    def _undo_done(self, task: Task):
        task.status = "pending"
        # restore remaining to duration if zero
        if task.remaining_seconds == 0:
            task.remaining_seconds = task.duration_seconds
        storage.save_tasks(TASKS_PATH, self.tasks)
        self._render_tasks()

    def _delete_task(self, task: Task):
        if messagebox.askyesno("Delete", f"Delete task '{task.title}'?"):
            # stop timer if running
            if task.id in self.timers:
                self._stop_timer(task.id)
            self.tasks = [t for t in self.tasks if t.id != task.id]
            storage.save_tasks(TASKS_PATH, self.tasks)
            self._render_tasks()

    # ---------- Timer controls ----------
    def _toggle_timer(self, task: Task):
        if task.id in self.timers:
            # pause
            self._stop_timer(task.id)
            storage.save_tasks(TASKS_PATH, self.tasks)
            self._render_tasks()
        else:
            # start
            # if already done, do nothing
            if task.status == "done":
                messagebox.showinfo("Task is done", "This task is already marked done.")
                return
            if task.remaining_seconds <= 0:
                task.remaining_seconds = task.duration_seconds
            self._start_timer(task)

    def _start_timer(self, task: Task):
        def tick():
            # increment elapsed time
            for t in self.tasks:
                if t.id == task.id:
                    t.remaining_seconds = int(t.remaining_seconds + 1)
                    break
            # update label
            lbl = self.timer_labels.get(task.id)
            if lbl:
                lbl.config(text=f"Time: {format_duration(task.remaining_seconds)}")
            # schedule next tick if task is not done
            if task.status != "done":
                after_id = self.root.after(1000, tick)
                self.timers[task.id] = after_id

        # start first tick
        after_id = self.root.after(1000, tick)
        self.timers[task.id] = after_id
        logging.info(f"Started timer for task {task.id}")

    def _stop_timer(self, task_id: int):
        after_id = self.timers.get(task_id)
        if after_id:
            try:
                self.root.after_cancel(after_id)
            except Exception:
                pass
        if task_id in self.timers:
            del self.timers[task_id]
        logging.info(f"Stopped timer for task {task_id}")
        # persist current remaining seconds
        storage.save_tasks(TASKS_PATH, self.tasks)

    def _reset_timer(self, task: Task):
        # stop if running
        if task.id in self.timers:
            self._stop_timer(task.id)
        task.remaining_seconds = task.duration_seconds
        storage.save_tasks(TASKS_PATH, self.tasks)
        self._render_tasks()

# ---------- Run ----------
def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, app))
    root.mainloop()

def on_close(root, app: TodoApp):
    # stop timers and persist
    for tid in list(app.timers.keys()):
        app._stop_timer(tid)
    storage.save_tasks(TASKS_PATH, app.tasks)
    root.destroy()

if __name__ == "__main__":
    main()
