# Plan: Comprehensive Codebase Audit & Roadmap

## Phase 1: Automated Analysis & Discovery [checkpoint: 690aafe]
- [ ] Task: Run static analysis tools on the Python backend.
    - [ ] Sub-task: Execute `flake8 src/` and capturing output.
    - [ ] Sub-task: Execute `mypy src/` (type checking) and capture output.
    - [ ] Sub-task: Analyze tool output to identify hotspots of complexity or error.
- [ ] Task: Run static analysis on the React frontend.
    - [ ] Sub-task: Run `npm run lint` in `frontend/`.
    - [ ] Sub-task: Analyze `frontend/` dependency usage for outdated packages.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Automated Analysis & Discovery' (Protocol in workflow.md)

## Phase 2: Manual Code Review & Bug Hunting [checkpoint: e3b1d8a]
- [x] Task: Review Core Logic Modules.
    - [x] Sub-task: Audit `src/game_detector.py` for potential race conditions or polling inefficiencies.
    - [x] Sub-task: Audit `src/ai_assistant.py` for error handling gaps in provider switching.
    - [x] Sub-task: Audit `src/macro_manager.py` for safety checks and edge cases.
- [x] Task: Review UI/Overlay Architecture.
    - [x] Sub-task: Check `src/gui.py` and `src/overlay.py` for threading issues (blocking main thread).
- [x] Task: Conductor - User Manual Verification 'Phase 2: Manual Code Review & Bug Hunting' (Protocol in workflow.md)

## Phase 3: Performance & Architecture Assessment [checkpoint: 01765c1]
- [x] Task: Analyze resource usage patterns.
    - [x] Sub-task: Identify potentially expensive operations (e.g., frequent IO, large loops).
    - [x] Sub-task: Review memory management in long-running sessions.
- [x] Task: Review Architecture against `tech-stack.md`.
    - [x] Sub-task: Check for deviations from the intended modular architecture.
    - [x] Sub-task: Identify circular dependencies or tight coupling.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Performance & Architecture Assessment' (Protocol in workflow.md)

## Phase 4: Roadmap & Deliverables Synthesis [checkpoint: f2484ac]
- [x] Task: Compile findings into actionable items.
    - [x] Sub-task: Create a list of "Bug Fix" tasks.
    - [x] Sub-task: Create a list of "Refactoring" tasks.
- [x] Task: Propose Next Feature.
    - [x] Sub-task: Analyze `product.md` and current capabilities.
    - [x] Sub-task: Propose 1-2 candidates for the next major feature implementation.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Roadmap & Deliverables Synthesis' (Protocol in workflow.md)
