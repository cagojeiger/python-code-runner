#!/usr/bin/env bash
#
# Shell script to find and display files while pruning (skipping) certain directories
# and excluding specific file name patterns.
#
# Usage:
#   ./script.sh
#
# This script demonstrates:
#   - How to exclude entire directories from the search using '-prune'.
#   - How to exclude specific file name patterns (e.g., '*.pyc', 'poetry.lock').
#   - How to output each file with a header and its content.

set -euo pipefail
# set -x  # Uncomment for debug (shows each command executed)

###############################################################################
# 1) DIRECTORIES TO PRUNE
#    We skip searching these directories entirely (no recursion).
###############################################################################
PRUNE_DIRS=(
  ".git"
  "__pycache__"
  ".mypy_cache"
  ".pytest_cache"
  "helm"
)

###############################################################################
# 2) FILE NAME PATTERNS TO EXCLUDE
#    These are patterns for individual files, not directories.
###############################################################################
EXCLUDE_FILENAME_PATTERNS=(
  "*.pyc"
  "poetry.lock"
  "Pipfile.lock"
  "*requirements*.txt"
  "export_project.sh"
)

###############################################################################
# (A) CONSTRUCT THE PRUNE EXPRESSION
#     - For each directory in PRUNE_DIRS, add a clause like:
#       -path "./.git" -prune -o
#     - This means "if path is .git -> prune (skip recursion), else -> proceed"
###############################################################################
PRUNE_EXPRESSION=()
for dir in "${PRUNE_DIRS[@]}"; do
  PRUNE_EXPRESSION+=( -path "./$dir" -prune -o )
done

###############################################################################
# (B) CONSTRUCT THE EXCLUDE EXPRESSION
#     - We want to exclude certain file names.
#     - The logic is: -not ( -name "pattern1" -o -name "pattern2" ... )
###############################################################################
EXCLUDE_EXPRESSION=()
if ((${#EXCLUDE_FILENAME_PATTERNS[@]} > 0)); then
  EXCLUDE_EXPRESSION+=( -not \( -false )
  for pattern in "${EXCLUDE_FILENAME_PATTERNS[@]}"; do
    EXCLUDE_EXPRESSION+=( -o -name "$pattern" )
  done
  EXCLUDE_EXPRESSION+=( \) )
fi

###############################################################################
# (C) RUN THE FIND COMMAND
#     1) Prune the specified directories.
#     2) Only consider regular files (-type f).
#     3) Exclude file name patterns from EXCLUDE_EXPRESSION.
#     4) Use -print0 for safe handling of filenames with special chars/spaces.
###############################################################################
find . \
  "${PRUNE_EXPRESSION[@]}" \
  \( -type f \
     "${EXCLUDE_EXPRESSION[@]}" \
  \) \
  -print0 |
while IFS= read -r -d '' file; do
  echo "===== $file ====="
  cat "$file"
  echo
done
