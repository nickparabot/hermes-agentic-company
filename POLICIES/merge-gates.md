# Policy: Merge gates (local CI + signoff)

**Status:** Active
**Owner:** Lead agent (VP)
**Applies to:** Every Hermes profile and human contributor
**Scope:** Product mainlines (deployable app repos). Company-repo PR rules live in `git-pull-requests.md`.

## Principle

Merging to main is a quality gate, not a convenience. Prod hot-patches and manual verification do not replace the formal gate.

## Rules

1. **Before any merge** to a product default branch (`main` / `master`):
   1. Run the repo’s **full local CI gate** on the PR HEAD (`bin/ci` or the command recorded in `config.yaml` / `STRATEGY.md`).
   2. Publish a **green commit status** via `gh signoff` (or the status the CI command emits on success). Empty GitHub check runs / `total_count: 0` are **not** green.
   3. Only then run `gh pr merge` (or equivalent).
2. **Never merge** because prod was hot-patched and “looks fixed.” Land the fix through the gate so the next image build is proven.
3. **Self-merge** still requires the gate. Urgency is not a waiver.
4. **Exception:** only the CEO’s **written** waiver (Basecamp/Kanban) may skip CI or signoff. Record the waiver URL on the PR body and Kanban task.
5. Completions that claim “merged” without CI + signoff proof are **not done**.

After merge, pull the default branch and sign off the **merge commit** too — merge OIDs often have empty statuses even when HEAD was signed.

## Why

Cloud CI minutes run out. Local CI + a real commit status is the standing gate. A past production-shaped org merged an outage fix without this gate; the outcome was correct and the process was not. Do not repeat it.

## Enforcement

- Lead flags ungated merges in the daily brief.
- Engineering SOUL restates this rule. Completions without proof are invalid.
