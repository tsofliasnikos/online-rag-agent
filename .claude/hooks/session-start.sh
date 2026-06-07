#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Install Python dependencies
uv pip install -r requirements.txt --system -q

# Install markitdown skill (microsoft/markitdown)
uv tool install 'markitdown[all]' --quiet 2>/dev/null || uv tool upgrade markitdown --quiet 2>/dev/null || true
