import os
import json
import tempfile
from todo.storage import load_tasks, save_tasks, get_next_id
from todo.models import Task

def test_save_and_load(tmp_path):
    p = tmp_path / "tasks.json"
    tasks = [
        Task(id=1, title="One"),
        Task(id=2, title="Two", priority="high"),
    ]
    save_tasks(str(p), tasks)
    loaded = load_tasks(str(p))
    assert len(loaded) == 2
    assert loaded[0].title == "One"
    assert loaded[1].priority == "high"

def test_get_next_id(tmp_path):
    p = tmp_path / "tasks.json"
    tasks = []
    save_tasks(str(p), tasks)
    assert get_next_id([]) == 1
    tlist = [Task(id=5, title="x")]
    assert get_next_id(tlist) == 6
