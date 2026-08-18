# Policy: Pull requests for the company repo

**Status:** Active
**Owner:** Lead agent (VP)
**Applies to:** Every Hermes profile and human contributor
**Scope:** The company repo (charter, strategy, dept workspaces, policies, shared tooling)

## Principle

Treat the company the same way you treat product code. Changes are reviewable units, not silent edits on a shared mainline.

## Rules

1. **Never commit directly to the default branch** (`main` / `master`). Branch first.
2. **Open a pull request for every change set** that touches this repo — docs, policies, deliverables, scripts.
3. **One concern per PR** when practical.
4. **Link the PR** on the Kanban task before claiming done.
5. **Do not merge your own PR** unless the CEO (or the lead relaying the CEO) waives review, or the change is a trivial typo the lead pre-cleared.
6. **Branch names:** `feat/…`, `fix/…`, `docs/…`, `policy/…`, `chore/…`.
7. **Secrets stay out.** Never commit `.env`, credentials, tokens, or PII.

## Workflow (minimum)

```bash
cd "$COMPANY_ROOT"
git fetch origin
git checkout -b docs/short-description origin/master   # or origin/main
# …edit…
git add -p && git status
git commit -m "docs: clear value-communicating subject"
# Assert branch is not the default branch before push
git push -u origin HEAD
gh pr create --base master --title "…" --body "Why / what / how to verify"
```

## Exceptions (narrow)

| Case | Allowed? |
|------|----------|
| Local WIP on a private branch | Yes — still open a PR before claiming done |
| Emergency hotfix with CEO verbal go | Branch + PR still required; merge may be expedited |
| Profile SOUL/skills under `~/.hermes/` | Outside this repo; still review multi-agent SOUL edits |
| Kanban DB under `~/.hermes/kanban/` | Out of scope |

There is **no** “too small for a PR” exception inside this repo.

## Why

- Agents work in parallel. PRs are the cheap merge-conflict and quality gate.
- Company decisions need a bisectable history.
- If we will not open a PR for our own operating system, we will not hold product repos to that bar either.

## Enforcement

- Lead flags direct-to-default-branch commits in the daily brief and opens cleanup PRs.
- Completions that only leave files on disk with no PR are **not** done.
