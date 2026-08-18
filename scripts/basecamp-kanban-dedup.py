#!/usr/bin/env python3
"""Basecamp → Kanban dedup helper.

Given a Basecamp todo URL, extract the todo ID and search the company Kanban
board for an active task whose body references that todo.

Exit codes:
    0  — duplicate found, prints task ID to stdout
    1  — no duplicate found, safe to create
    2  — error
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
from pathlib import Path

TODO_URL_RE = re.compile(r"basecamp\.com/\d+/buckets/\d+/todos/(\d+)")


def board_db() -> Path:
    override = os.environ.get("HERMES_KANBOARD_DB")
    if override:
        return Path(override)
    slug = os.environ.get("HERMES_KANBAN_BOARD", "")
    if not slug:
        print("HERMES_KANBAN_BOARD or HERMES_KANBOARD_DB is required", file=sys.stderr)
        sys.exit(2)
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    return home / "kanban" / "boards" / slug / "kanban.db"


def extract_todo_id(url: str) -> str | None:
    if not url:
        return None
    match = TODO_URL_RE.search(url)
    return match.group(1) if match else None


def find_existing_task(todo_id: str) -> str | None:
    db = board_db()
    if not db.exists():
        return None
    conn = sqlite3.connect(db)
    try:
        cursor = conn.cursor()
        pattern = f"%todos/{todo_id}%"
        cursor.execute(
            "SELECT id FROM tasks WHERE body LIKE ? "
            "AND status IN ('running', 'ready', 'todo', 'blocked', 'review') "
            "ORDER BY created_at DESC LIMIT 1",
            (pattern,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: basecamp-kanban-dedup.py <basecamp_todo_url>", file=sys.stderr)
        sys.exit(2)

    todo_id = extract_todo_id(sys.argv[1])
    if not todo_id:
        print(f"Could not extract todo ID from URL: {sys.argv[1]}", file=sys.stderr)
        sys.exit(2)

    task_id = find_existing_task(todo_id)
    if task_id:
        print(task_id)
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
