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

Run tests locally the way CI does: set `QT_QPA_PLATFORM=offscreen`,
`OMNIX_MASTER_PASSWORD=<any>`, and `PYNPUT_BACKEND=dummy`, and install `libegl1`
on Linux. `pytest.ini` pins `asyncio_default_fixture_loop_scope`; without it,
`-W error::DeprecationWarning` turns pytest-asyncio's warning into an
INTERNALERROR before collection.

Data-durability conventions (see `tests/unit/test_review_fixes.py`):
- Write user files atomically (temp file + `os.replace`); `config.py` has
  `_atomic_write_text`/`_atomic_write_json`.
- `Config.save_to_env` must keep `.env` keys it does not manage.
- `Config.save()` writes `<config_dir>/config.json`, which loads after `.env`
  and so wins. Any code that calls `save_to_env` with in-memory `Config` values
  must also call `config.save()`, or a stale JSON value overrides the change on
  restart. Only `_PERSISTED_FIELDS` load (type-checked; `_POSITIVE_FIELDS` must
  be > 0; `ai_provider` must be supported), and only from files stamped with
  exactly `int` `settings_version`; `save()` keeps unmanaged keys such as
  `schema_version`. UI save handlers must check `save()`'s result and must not
  report success when it returns False.
- Never write `AI_API_KEY` to JSON or back to `.env` once it is in the vault.
- `CredentialStore` quarantines the vault only on `InvalidToken`, never when the
  key is merely unavailable this run.
- `MainWindow` loads saved keybinds/macros into its managers at startup; the
  Settings tabs fall back to defaults when a manager is empty.
