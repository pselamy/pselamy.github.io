#!/usr/bin/env bash
set -euo pipefail

# Layer 1: Validate required frontmatter fields in blog posts

REQUIRED_FIELDS=("title" "date" "slug" "description" "tags")
FAILED=0

for f in content/posts/**/*.md; do
  [ -f "$f" ] || continue

  # Extract frontmatter (between --- markers)
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$f")

  for field in "${REQUIRED_FIELDS[@]}"; do
    if ! echo "$frontmatter" | grep -q "^${field}:"; then
      echo "::error file=$f::Missing required frontmatter field: $field"
      FAILED=1
    fi
  done
done

if [ "$FAILED" -eq 1 ]; then
  echo "Frontmatter validation FAILED."
  exit 1
fi

echo "Frontmatter validation passed."
