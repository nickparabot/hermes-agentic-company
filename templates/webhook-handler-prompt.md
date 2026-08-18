Basecamp webhook event received.

Event kind: {{kind}}
Recording ID: {{recording.id}}
Recording type: {{recording.type}}
Recording content: {{recording.content}}
Recording URL: {{recording.app_url}}
Bucket ID: {{recording.bucket.id}}
Creator: {{recording.creator.name}}

## IDENTITY GUARDS (always run first)

1. **Bot-originated comments — IGNORE entirely (no Basecamp reply, no Kanban).**
   - Creator name is the lead agent, or email matches the lead bot email, OR
   - Content matches completion-bridge: "<Name> completed this task." / "Default completed this task."
   These are posts FROM the completion bridge or the lead agent. Replying creates infinite comment_created loops.
2. **Bare numeric content** (recording.content is only digits): IGNORE.
3. Parent todo ID for comments: extract from URL `/todos/{PARENT_ID}` — NEVER comment on the comment recording ID itself.

## DEDUP CHECK (before creating any Kanban task)

    python3 $COMPANY_ROOT/shared/basecamp/basecamp-kanban-dedup.py "{{todo_url}}"

- Exit 0 + task ID: ACTIVE task exists. Do NOT create a new task. Comment on that Kanban task only when the event is a NEW human instruction.
- Exit 1: no active task — safe to create (if routing rules say so).
- Exit 2: error — log and proceed carefully.

## If kind is todo_created

- Check recording.content for an @mention mapped in $COMPANY_ROOT/shared/basecamp/agent-routing.json
- NO @mention: IGNORE entirely. CEO personal one-offs. No Kanban, no comment.
- @mention AND no existing task:
  - export HERMES_KANBAN_BOARD=$SLUG
  - hermes kanban create "<todo content minus @mention>" --assignee <profile> --body "Basecamp todo: <url>" --idempotency-key "basecamp-<todo_id>"
  - If assignee is the current profile AND this session will execute: claim in the SAME shell as create.
  - basecamp comment on the TODO id: "Routed to <Agent> via Kanban. Work starting. - <Lead>"
- @mention AND existing task: Kanban comment with new context; Basecamp: "Additional context routed to existing Kanban task. - <Lead>"

## If kind is comment_created

- Identity guards first — bot/completion-bridge → stop.
- Do NOT post standalone "Got it." acks.
- Only act if the comment is from a human AND contains an @mention, OR is a clear new instruction on an open todo:
  - Dedup on parent todo URL
  - Existing task → hermes kanban comment
  - No task → create like todo_created
- Comments without @mention and without clear new work: IGNORE.

## If kind is todo_completed or todo_updated

- No action.

## Basecamp comment rules

- Always target the **todo** recording ID (from /todos/N), never a Comment recording ID.
- Sign off: - <Lead>
- Intake + one meaningful update per work item; no empty acks.

## Dual-session

Creating a card assigned to the current profile spawns a dispatcher worker within one tick. Claim-first if this session will ship; otherwise monitor-only. Never start a second full CI/deploy on a card that is already running with a spawned worker.
