#!/usr/bin/env bash
# Scaffold the company folder skeleton. Does not write SOULs or touch ~/.hermes.
# Usage: COMPANY_ROOT=~/work/acme SLUG=acme DEPTS="vp engineering product" ./scripts/scaffold.sh

set -euo pipefail

COMPANY_ROOT="${COMPANY_ROOT:-}"
DEPTS="${DEPTS:-vp engineering}"

if [[ -z "$COMPANY_ROOT" ]]; then
  echo "COMPANY_ROOT is required" >&2
  exit 1
fi

mkdir -p "$COMPANY_ROOT"/{POLICIES,shared/basecamp,shared/meetings,missions}

kit_root="$(cd "$(dirname "$0")/.." && pwd)"

cp -n "$kit_root/templates/company-gitignore" "$COMPANY_ROOT/.gitignore" || true
cp -n "$kit_root/templates/axioms.md" "$COMPANY_ROOT/shared/axioms.md" || true
cp -n "$kit_root/POLICIES/"*.md "$COMPANY_ROOT/POLICIES/" || true
cp -n "$kit_root/scripts/webhook-proxy.py" "$COMPANY_ROOT/shared/basecamp/" || true
cp -n "$kit_root/scripts/basecamp-kanban-dedup.py" "$COMPANY_ROOT/shared/basecamp/" || true
cp -n "$kit_root/scripts/kanban-completion-bridge.py" "$COMPANY_ROOT/shared/basecamp/" || true
cp -n "$kit_root/templates/webhook-handler-prompt.md" "$COMPANY_ROOT/shared/basecamp/" || true
cp -n "$kit_root/templates/agent-routing.json" "$COMPANY_ROOT/shared/basecamp/" || true
cp -n "$kit_root/templates/basecamp-config.md" "$COMPANY_ROOT/shared/basecamp/config.md" || true

for dept in $DEPTS; do
  mkdir -p "$COMPANY_ROOT/$dept"/{inbox,active,deliverables,reviews,archive}
  if [[ ! -f "$COMPANY_ROOT/$dept/README.md" ]]; then
    sed "s/{{DEPT}}/$dept/g; s/{{NAME}}/TBD/g" "$kit_root/templates/dept-readme.md" \
      > "$COMPANY_ROOT/$dept/README.md"
  fi
done

find "$COMPANY_ROOT" -type d -empty -not -path '*/.git/*' -exec touch {}/.gitkeep \;

echo "Scaffolded $COMPANY_ROOT"
echo "Next: fill COMPANY.md / STRATEGY.md / DECISIONS.md from templates, then branch + PR."
