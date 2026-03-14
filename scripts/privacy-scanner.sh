#!/usr/bin/env bash
set -euo pipefail

# Layer 2: Content Safety — scan for banned words/patterns
# These terms could leak internal project names, real identities, or client info

BANNED_PATTERNS=(
  "Matchpoint"
  "MatchPoint"
  "matchpoint"
  "TradeStream"
  "tradestream"
  "VeinRoute"
  "veinroute"
  "Velix"
  "velix"
  "project-beta"
  "project-beta"
  "matchpointai\.com"
  "tradestreamhq"
  "loam-dev"
  "pselamy@gmail"
)

FAILED=0

for pattern in "${BANNED_PATTERNS[@]}"; do
  if grep -rn "$pattern" content/posts/ 2>/dev/null; then
    echo "::error::Banned pattern found: $pattern"
    FAILED=1
  fi
done

if [ "$FAILED" -eq 1 ]; then
  echo "Privacy scan FAILED — remove banned terms before merging."
  exit 1
fi

echo "Privacy scan passed."
