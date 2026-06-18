#!/bin/bash
# Run this script after creating MaclearDataSolutions/pm-plugin on GitHub.com
# Usage: bash push_to_github.sh

set -e

REPO_URL="https://github.com/MaclearDataSolutions/pm-plugin.git"

# Add remote (skip if already set)
if ! git remote get-url origin &>/dev/null 2>&1; then
  git remote add origin "$REPO_URL"
  echo "Remote added: $REPO_URL"
else
  echo "Remote already exists: $(git remote get-url origin)"
fi

git push -u origin main
echo "Done. Pushed to $REPO_URL"
