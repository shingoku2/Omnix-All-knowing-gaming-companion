# Repository Guidelines

## Project Structure & Modules
- `src/`: Core application (AI routing, credential storage, game detection, PyQt6 UI, design system). `src/ui/components/` hosts reusable widgets; `src/knowledge_*` manages TF-IDF search; `src/macro_*` handles automation.
- `frontend/`: Web assets for the dashboard/overlay integrations.
- `tests/`: Pytest suite plus utility scripts; note `pytest.ini` ignores some heavier test files unless called explicitly.
- `scripts/` and root `*.bat` helpers: local builds, coverage, GUI smoke tests. Build outputs land in `build/` and `dist/`.
- `docs/` and root markdown files (e.g., `CLAUDE.md`, `TESTING.md`): deeper architecture and QA notes.

## Build, Test, and Development Commands
- Create env: `python -m venv .venv; .\.venv\Scripts\activate`
- Install runtime deps: `pip install -r requirements.txt`; dev extras: `pip install -r requirements-dev.txt`.
- Run app from source: `python main.py` (reads `.env` and keyring config).
- Tests: `pytest` (respects ignores in `pytest.ini`); full coverage: `pytest --cov=src --cov-report=html`.
- Lint/format/security sweep: `pre-commit run --all-files` (Black 100 cols, isort, Flake8, Bandit, markdownlint).
- Windows build: `python build_windows_exe.py` or `pyinstaller GamingAIAssistant.spec` (artifacts in `dist/`).

## Coding Style & Naming
- Python 3.8+ with 4-space indentation; prefer type hints where practical.
- Formatting via Black (line length 100) and isort (profile=black). Flake8 (`--max-line-length=127`, ignore E203) governs linting; fix warnings before commit.
- Tests follow `test_*.py` / `*_test.py`, classes `Test*`, functions `test_*`. Keep module/file names descriptive (e.g., `game_detector.py`, `knowledge_store.py`).

## Testing Guidelines
- Run `pytest` locally before PRs; add `-n auto` for speed if needed. For focused runs: `pytest tests/game` or `pytest -k game_detector`.
- Generate coverage when touching core logic or security-sensitive areas and review `htmlcov/index.html`.
- UI/games tests that are ignored by default (`test_gui_minimal.py`, `test_macro_runner_execution.py`, etc.) should be invoked directly when you change related code.

## Commit & Pull Request Guidelines
- Commit style is short, imperative summaries (e.g., "Fix application functionality", "Move AI thread to assistant"). Group related changes per commit.
- Before pushing: `pre-commit run --all-files` and relevant `pytest` scope; attach coverage/screenshot evidence for UI or gameplay-detection changes.
- PRs should include: brief problem/solution statement, impacted modules, test commands/output, and note any config/env prerequisites (`.env`, keyring). Link issues when available.

## Security & Configuration
- Secrets live in keyring/`.env`; never commit keys (hooks include `detect-private-key`). `.env.example` documents required vars; prefer Anthropic/OpenAI/Gemini keys set via Setup Wizard or manual edit.
- Keep local data in `~/.gaming_ai_assistant/` (profiles, macros, themes). Avoid altering user directories in tests; use temp paths/fixtures from `conftest.py`.
