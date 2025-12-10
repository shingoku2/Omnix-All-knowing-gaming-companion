# Agent Guidelines - Omnix Gaming Companion

## Build & Test Commands
**Setup:** `python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt` (dev: `requirements-dev.txt`)  
**Run app:** `python main.py`  
**Single test:** `pytest tests/unit/test_game_detector.py -v` or `pytest -k game_detector`  
**All tests:** `pytest` | **Coverage:** `pytest --cov=src --cov-report=html`  
**Lint/format:** `pre-commit run --all-files` (Black 100cols, isort, flake8, bandit)  
**Frontend:** `cd frontend && npm run dev` | **Windows build:** `python build_windows_exe.py`

## Code Style & Architecture
**Python 3.8+:** 4-space indent, type hints preferred, Black (100 chars), isort (profile=black), flake8 (127 chars, ignore E203)  
**Imports:** `from src.module import X` (never circular imports)  
**Architecture:** Strict layered design - GUI (PyQt6) → Business Logic → Data/Integration → Persistence  
**UI Components:** Use `src/ui/tokens.py` colors/spacing, reusable components in `src/ui/components/`  
**Testing:** `test_*.py` / `*_test.py`, classes `Test*`, functions `test_*`, use markers `@pytest.mark.unit` etc.

## Security & Configuration
**Secrets:** Store in keyring/`.env` (never commit), use `CredentialStore.get_key()`  
**Local data:** `~/.gaming_ai_assistant/`, never alter user dirs in tests  
**API Keys:** Via secure keyring, test with `CredentialStore.validate_key()`  
**Cross-platform:** Windows (pywin32), Linux/macOS (keyring), use `QT_QPA_PLATFORM=offscreen` for headless

## Key Patterns & Files
**AI Providers:** Implement `AIProvider` protocol in `providers.py`, use factory `create_provider()`  
**Game Detection:** Passive polling via `GameWatcher` (5s), match against `game_profiles.json`  
**Macros:** `MacroRunner.execute_macro()` in background, `pynput` for input simulation  
**Knowledge:** TF-IDF semantic search in `knowledge_index.py`, augment prompts via `KnowledgeIntegration`  
**Error Handling:** Log all failures, never silent fallbacks, use Qt signals for GUI updates

## Essential Testing
**Unit tests:** Mock everything external (providers, processes, files)  
**Integration tests:** Real file I/O, fake API responses  
**UI tests:** Set `QT_QPA_PLATFORM=offscreen` before importing PyQt6  
**Headless CI:** Set `OMNIX_MASTER_PASSWORD` env var for credential testing  
**Focus:** When changing UI/game code, explicitly run `test_gui_minimal.py`, `test_macro_runner_execution.py`