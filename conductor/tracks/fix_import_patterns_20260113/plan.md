# Plan: Fix Import Patterns

## Phase 1: Identification & Setup [checkpoint: 2991d70]
- [x] Task: Create `test_imports.py` to verify module importability.
    - [x] Sub-task: Implement the script logic to crawl `src/` and attempt dynamic imports.
    - [x] Sub-task: Run the script and document current failures.
- [x] Task: Identify inconsistent import patterns using shell commands.
    - [x] Sub-task: Run `grep -r "^from [a-z_]* import" src/ --include="*.py"` to find bad imports.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Identification & Setup' (Protocol in workflow.md)

## Phase 2: Core Module Refactoring
- [ ] Task: Standardize imports in `src/game_profile.py`.
- [ ] Task: Standardize imports in `src/macro_manager.py`.
- [ ] Task: Standardize imports in `src/knowledge_integration.py`.
- [ ] Task: Verify Phase 2 changes using `test_imports.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Module Refactoring' (Protocol in workflow.md)

## Phase 3: Global Cleanup & Final Validation
- [ ] Task: Standardize remaining imports in all files under `src/`.
- [ ] Task: Update test files in `tests/` to use standardized import paths if necessary.
- [ ] Task: Run full test suite (`pytest tests/`) and `test_imports.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Global Cleanup & Final Validation' (Protocol in workflow.md)
