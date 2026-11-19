#!/usr/bin/env bash
set -e
REPO_NAME="${1:-frontend-craft-and-prompt-knowledge}"
VISIBILITY="${2:-public}"

git init -b main
git add .
git commit -m "v5 (CI-Verified): Deep-research spec-verified optical UI, Three.js WebGPU/PBR, ML/Crypto & 2026 AI builder budget KB"

if command -v gh >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push
  echo "Published to GitHub: $REPO_NAME"
else
  echo "GitHub CLI (gh) not found. Create an empty repo named '$REPO_NAME' on github.com, then run:"
  echo "  git remote add origin https://github.com/<YOUR_USERNAME>/$REPO_NAME.git"
  echo "  git push -u origin main"
fi
