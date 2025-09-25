import json
import os
import shutil
from typing import List
from .models import Task

def load_tasks(path: str) -> List[Task]:
    if not os.path.exists(path):
        # create an empty tasks file
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # backup corrupt file and return empty list
        bak = path + ".bak"
        shutil.copy(path, bak)
        return []
    tasks = [Task.from_dict(item) for item in data]
    return tasks

def save_tasks(path: str, tasks: List[Task]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=2)
    # atomic replace on most OSes
    os.replace(tmp, path)

def get_next_id(tasks: List[Task]) -> int:
    if not tasks:
        return 1
    return max(int(t.id) for t in tasks) + 1
