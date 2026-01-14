# Specification: Fix Import Patterns

## 1. Overview
The project currently has inconsistent import patterns (e.g., `from module import X` vs `from src.module import X`). This causes circular import failures and makes modules difficult to test in isolation. This track standardizes all internal imports to the `from src.module import X` pattern.

## 2. Goals
-   Identify all inconsistent imports in the `src/` directory.
-   Standardize all internal imports to use the `src.` prefix.
-   Ensure all modules can be imported without circular dependency errors.
-   Verify that the application still runs and all tests pass.

## 3. Implementation Strategy
1.  **Identify:** Use `grep` or similar tools to find imports that do not use the `src.` prefix for internal modules.
2.  **Verify Script:** Create a standalone test script (`test_imports.py`) that attempts to import every module in `src/` to catch circular dependencies.
3.  **Refactor:** Iteratively update files, focusing on core modules first (`ai_assistant.py`, `game_profile.py`, `knowledge_integration.py`).
4.  **Validate:** Run `test_imports.py` and the existing test suite after each set of changes.

## 4. Verification Plan
-   **Automated Import Test:** `python test_imports.py` must pass for all modules.
-   **Existing Test Suite:** `pytest tests/` must pass.
-   **Linting (Optional):** Ensure no new shadowing issues are introduced.
