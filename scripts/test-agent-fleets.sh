#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m coverage erase
python3 -m coverage run scripts/test-stage-operating-agent-fleets.py
python3 -m coverage run --append scripts/test-check-rendered-agent-fleets.py
python3 -m coverage report
