#!/bin/bash
# SessionStart hook: rebuild the CI-equivalent Python 3.11 dev environment in
# Claude Code cloud sessions. See docs/CI_CD_GUIDE.md for the CI contract.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# PyQt6 needs libegl1 (and friends) on Ubuntu before it can be imported.
QT_LIBS="libegl1 libxkbcommon0 libgl1 libfontconfig1 libdbus-1-3"
if ! dpkg -s $QT_LIBS >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get install -y -q $QT_LIBS >/dev/null 2>&1 \
    || { apt-get update -q >/dev/null && apt-get install -y -q $QT_LIBS >/dev/null; }
fi

PYTHON_BIN="$(command -v python3.11 || command -v python3)"
if [ ! -x .venv/bin/python ]; then
  "$PYTHON_BIN" -m venv .venv
fi

# setuptools>=83 must be in the active environment for pip-audit (see AGENTS.md).
.venv/bin/python -m pip install -q --upgrade pip "setuptools>=83"
.venv/bin/python -m pip install -q -e ".[dev,build]"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export VIRTUAL_ENV=\"$CLAUDE_PROJECT_DIR/.venv\""
    echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\""
    echo "export QT_QPA_PLATFORM=offscreen"
    echo "export OMNIX_MASTER_PASSWORD=ci-only-master-password"
    echo "export PYNPUT_BACKEND=dummy"
  } >> "$CLAUDE_ENV_FILE"
fi
