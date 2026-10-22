# Omnix contributor context

Follow [AGENTS.md](AGENTS.md). This repository's canonical 3.0 application is
the Python 3.11+ PyQt6 package in `src/omnix`. Keep Tauri code in the separate
[Omnix Tauri](https://github.com/shingoku2/Omnix-Tauri) repository and do not
recreate it here. Do not add flat `src.<module>` imports.

Architecture and data-migration contracts live in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/UPGRADING.md](docs/UPGRADING.md).

CI uses GitHub-hosted Python 3.11 runners on Ubuntu, Windows, and macOS. Read
[docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md) before changing runner packages,
headless Qt setup, path-sensitive tests, or dependency auditing.

Claude Code cloud sessions run `.claude/hooks/session-start.sh` (registered in
`.claude/settings.json`). It installs the Qt system libraries, builds `.venv`
with `.[dev,build]`, and exports the CI test variables (`QT_QPA_PLATFORM`,
`OMNIX_MASTER_PASSWORD`, `PYNPUT_BACKEND`). Keep it in sync with the CI
install steps. The CI lint job runs `black --check src tests` directly; never
wrap it in `find -exec ... \;`, which swallows failures.
