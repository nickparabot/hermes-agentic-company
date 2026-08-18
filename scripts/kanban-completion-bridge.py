#!/usr/bin/env python3
"""Kanban → Basecamp completion bridge.

Polls recently-completed tasks on HERMES_KANBAN_BOARD. For a task that:
  1. status=done
  2. completed within LOOKBACK_SECONDS
  3. body contains a Basecamp todo URL
  4. has no reported_to_basecamp marker comment

posts a comment on that todo via the `basecamp` CLI and marks the task.

Silent on success (no stdout) so a no_agent cron stays quiet.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

BOARD = os.environ.get("HERMES_KANBAN_BOARD", "")
ACCOUNT = os.environ.get("BASECAMP_ACCOUNT_ID", "")
PROJECT = os.environ.get("BASECAMP_PROJECT_ID", "")
LOOKBACK_SECONDS = int(os.environ.get("BRIDGE_LOOKBACK_SECONDS", "600"))
REPORTED_MARKER = "reported_to_basecamp:"
TODO_RE = re.compile(r"basecamp\.com/(\d+)/buckets/(\d+)/todos/(\d+)")
SYSTEM_AUTHORS = {
    a.strip()
    for a in os.environ.get("BRIDGE_SYSTEM_AUTHORS", "default,dashboard").split(",")
    if a.strip()
}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


def kanban(*args: str) -> object | None:
    if not BOARD:
        print("HERMES_KANBAN_BOARD is required", file=sys.stderr)
        return None
    result = run(["hermes", "kanban", "--board", BOARD, *args])
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def extract_todo(body: str) -> tuple[str, str, str] | None:
    match = TODO_RE.search(body or "")
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def already_reported(comments: list[dict]) -> bool:
    for comment in comments:
        text = (comment.get("body") or comment.get("content") or "") + ""
        if REPORTED_MARKER in text:
            return True
    return False


def assemble_report(task: dict, show: dict) -> str:
    comments = show.get("comments") or []
    agent_bits = []
    for comment in comments:
        author = str(comment.get("author") or comment.get("created_by") or "")
        body = comment.get("body") or comment.get("content") or ""
        if author in SYSTEM_AUTHORS:
            continue
        if REPORTED_MARKER in body:
            continue
        if body.strip():
            agent_bits.append(body.strip())
    if agent_bits:
        summary = "\n\n".join(agent_bits[-3:])
    else:
        summary = (show.get("latest_summary") or task.get("result") or "").strip()
    if not summary:
        summary = "Task completed. No summary available."
    title = task.get("title") or task.get("id")
    assignee = task.get("assignee") or "agent"
    return (
        f"<p><strong>{assignee}</strong> completed <code>{task.get('id')}</code>: {title}</p>"
        f"<p>{summary}</p>"
    )


def mark_reported(task_id: str, todo_id: str) -> None:
    run(
        [
            "hermes",
            "kanban",
            "--board",
            BOARD,
            "comment",
            task_id,
            f"{REPORTED_MARKER} {todo_id}",
        ]
    )


def post_basecamp(account: str, project: str, todo_id: str, html: str) -> bool:
    result = run(
        [
            "basecamp",
            "comment",
            "--account",
            account,
            "--project",
            project,
            todo_id,
            html,
        ]
    )
    return result.returncode == 0


def main() -> int:
    if not BOARD or not ACCOUNT or not PROJECT:
        print(
            "HERMES_KANBAN_BOARD, BASECAMP_ACCOUNT_ID, BASECAMP_PROJECT_ID are required",
            file=sys.stderr,
        )
        return 1

    data = kanban("list", "--status", "done", "--json")
    if not isinstance(data, list):
        return 0

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=LOOKBACK_SECONDS)
    errors = 0

    for task in data:
        completed_at = task.get("completed_at")
        if not completed_at:
            continue
        try:
            ts = datetime.fromtimestamp(float(completed_at), tz=timezone.utc)
        except (ValueError, TypeError):
            continue
        if ts < cutoff:
            continue

        todo = extract_todo(task.get("body") or "")
        if not todo:
            continue
        account, project, todo_id = todo
        # Prefer the task body's account/project; fall back to env if parse odd.
        account = account or ACCOUNT
        project = project or PROJECT

        raw_show = kanban("show", task["id"], "--json")
        show: dict = raw_show if isinstance(raw_show, dict) else {}
        maybe_task = show.get("task")
        inner = maybe_task if isinstance(maybe_task, dict) else task
        comments = show.get("comments") or []
        if already_reported(comments):
            continue

        html = assemble_report(inner, show)
        if not post_basecamp(account, project, todo_id, html):
            print(f"basecamp comment failed for {task.get('id')} todo={todo_id}", file=sys.stderr)
            errors += 1
            continue
        mark_reported(task["id"], todo_id)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
