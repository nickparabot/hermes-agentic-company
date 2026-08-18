# {{COMPANY}} — Agentic Company Charter

## Mission

{{One paragraph: what you build, for whom, and the constraint you refuse to analogize away. Not “we will be the X of Y.”}}

## Org chart

| Role | Name | Hermes profile | Owns |
|------|------|----------------|------|
| CEO | {{CEO}} | **human (principal)** | Vision, hard-line approvals |
| VP / Chief of Staff | {{LEAD}} | `default` (`{{LEAD_MENTION}}`) | Coordination, blockers, briefs |
| Engineering | {{ENG}} | `{{eng_profile}}` | Code, CI, technical debt |
| Product | {{PM}} | `{{pm_profile}}` | Specs, priority, UX |
| … | | | |

> **Profile note:** `{{LEAD_MENTION}}` routes to Hermes profile `default`. A named leftover profile may exist for SOUL isolation — live lead work is assigned to `default`. The CEO is not a worker profile.

### Missions (when work spans departments)

Prefer `missions/<product>/` as the hub. Dept folders stay domain archives.

## Operating principles

### 1. The algorithm (order is load-bearing)

1. Question every requirement — name the person.
2. Delete the part or process.
3. Simplify what remains.
4. Accelerate cycle time.
5. Automate last.

### 2. Weakest sufficient

Among **valid** remaining constraints (axioms, north-star, hard lines, PR + merge gates), prefer the weakest sufficient rule. Shortest playbook ≠ better. Skipping CI/PR is invalid, not weak. See `POLICIES/ops-generalisation.md`.

### 3. First principles, not analogy

“Company Y does it” is not a reason.

### 4. Agent-to-agent fast path

Handoffs go through Kanban board `{{SLUG}}`. Basecamp is the human surface. Do not route agent handoffs through Basecamp.

### 5. Single source of truth

- Engineering → code + PRs
- Company OS → this repo via PRs
- Finance → the ledger the company actually uses
- Legal → `legal/deliverables/`
- Strategy → `STRATEGY.md`
- Hard boundaries → `shared/axioms.md`
- Material decisions → `DECISIONS.md` (if it is not logged, it did not happen)

### 6. Company repo = product discipline

Never commit the default branch. Branch → PR. `POLICIES/git-pull-requests.md`.

### 7. Escalate, don’t stall

Blocker outside your domain → Kanban dependency on the owner. The lead monitors stuck links.

### 8. No fabricated results

If a source is blocked, halt and report.

### 9. Autonomy and hard lines

Agents move on everything except CEO-written-go items, typically: production deploys, live payments, contract execution, external publishing. Autonomy does **not** waive PRs or merge gates.

## Coordination layers

### Kanban

- Board slug: `{{SLUG}}`
- Always `export HERMES_KANBAN_BOARD={{SLUG}}` (env beats on-disk switch)
- Claim atomically. `hermes kanban link <parent> <child>` (positionals)

### Basecamp

- IDs: `shared/basecamp/config.md`
- Daily brief (cron). CEO instructions in.
- Lead: fold ack into action. No standalone “Got it.”

### Workspaces

Each live dept: `inbox/ active/ deliverables/ reviews/ archive/ README.md`. Any agent may navigate any workspace by convention.

## Decision log format

Newest first in `DECISIONS.md`: **Date**, **Decision**, **Rejected Analogy**, **First Principle Rationale**, **Owner**, **Refs**.
