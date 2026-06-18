#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_FILE="$SKILL_DIR/assets/empty_questionnaire.md"
TARGET_FILE="$TARGET_DIR/empty_questionnaire.md"

mkdir -p "$TARGET_DIR"

if [ -e "$TARGET_FILE" ]; then
  echo "empty_questionnaire.md already exists at $TARGET_FILE. not overwriting."
  exit 0
fi

cp "$SOURCE_FILE" "$TARGET_FILE"
echo "created $TARGET_FILE"
