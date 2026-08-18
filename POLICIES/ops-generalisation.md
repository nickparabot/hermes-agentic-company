# Policy: Ops generalisation (weakest sufficient process)

**Status:** Active
**Owner:** Lead agent (VP)
**Applies to:** All Hermes profiles + CEO instruction shape
**Theory source:** Bennett 2023, arXiv:2301.12987 — optimal hypothesis is weakest valid, not shortest

## Intent

Maximise the chance that operating rules **generalise** to novel tasks. Prefer the **weakest sufficient** constraints among those that remain valid under axioms, the north-star metric, and hard lines. Do not equate shorter docs with better ops. Do not add ceremony to look rigorous.

Composes with the charter algorithm: question → delete → simplify → accelerate → automate last. Weakness is the selection rule **after** delete.

## Rules

### R1 — Weakest sufficient brief

| Who | Duty |
|-----|------|
| **CEO** | Prefer outcome + constraint + DoD over implementation recipes |
| **Agents** | If a brief overfits, question and propose weaker acceptance criteria before build |
| **Product** | One weak spec > same-day multi-rev thrash; flip via `DECISIONS.md` |

### R2 — One owner per ship unit

- Webhook creates a card for the **current** profile:
  - CEO said ship/close/into production → **claim-first** this session; no parallel dispatcher CI.
  - Otherwise → **monitor-only** (route + comment; do not dual heavy work).
- Product merge: local CI + `gh signoff` (`merge-gates.md`) — never waived by “weak process.”
- Deploy: **one** owner.
- Status-only human comments → Basecamp answer; **no** new Kanban epic unless build is ordered.

### R3 — WIP soft caps

- ≤2 heavy `running` engineering tasks per profile when work contends on a shared test DB or deploy host.
- Lead: many coordination cards OK; **at most one** full CI or deploy at a time on shared envs.

### R4 — Weekly generalisation check (lead brief)

1. Novel CEO asks that landed **without** new policy/ceremony
2. Friction that forced a **more brittle** process — delete candidate
3. Hard-line blockers older than 7 days (keys, CEO go, contracts)

### R5 — Spec and decision strength

- Prefer physics-level constraints over procedural laundry lists.
- Material product flips get **one** decision-log entry; engineering rework is named, not silent.

## What this policy does **not** weaken

- `shared/axioms.md` hard lines
- `POLICIES/merge-gates.md`
- `POLICIES/git-pull-requests.md`
- Kanban-for-agents / Basecamp-for-humans split
- No fabricated results

Invalid “weak” shortcuts (skip CI, skip PR, agent handoff via Basecamp) are out of scope.

## Enforcement

- Lead flags dual-owner and overfit-brief defects on the card and in the brief.
- Completions that dual-ran CI/deploy against an active claim are process defects — note them; do not normalize.
