# Basecamp configuration

- **Account ID:** {{ACCOUNT_ID}}
- **Account Name:** {{ACCOUNT_NAME}}
- **Project ID:** {{PROJECT_ID}}
- **Project Name:** {{PROJECT_NAME}}
- **Project URL:** https://app.basecamp.com/{{ACCOUNT_ID}}/projects/{{PROJECT_ID}}
- **Message Board ID:** {{MESSAGE_BOARD_ID}}
- **Default Todoset ID:** {{TODOSET_ID}}
- **Agent Tasks todolist ID:** {{TODOLIST_ID}}

## Usage rules

- Agents post daily briefs to the message board.
- The CEO posts direct instructions here; agents read and act.
- Do **not** route inter-agent handoffs through Basecamp. Use Kanban.
- `basecamp todo <id>` **creates** a todo. Fetch with `basecamp show todo <id>`.
- Comments go on the **todo** ID (`/todos/{id}`), never a Comment recording ID.

## Webhook architecture

- **Stable domain:** `{{WEBHOOK_DOMAIN}}`
- **Signature proxy:** `shared/basecamp/webhook-proxy.py` (`BASECAMP_EXPECTED_BUCKET` = **project** ID)
- **Dedup helper:** `shared/basecamp/basecamp-kanban-dedup.py`
- **Secret env:** `~/.config/basecamp/webhook-secret.env` (`BASECAMP_WEBHOOK_SECRET`)
- **Flow:** Basecamp → HTTPS reverse proxy → :9876 (UA + bucket + HMAC V2 + X-Request-ID) → Hermes :8644

## Routing rules

- `todo_created` + @mention → dedup, then Kanban assign from `agent-routing.json`
- `todo_created` without @mention → IGNORE
- `comment_created` → identity guard first (ignore lead-bot + completion-bridge). Human + @mention → dedup + route. No standalone “Got it.”
- `todo_completed` / `todo_updated` → no action
- CEO is **not** in `agent-routing.json`. Lead mention → `default`.
