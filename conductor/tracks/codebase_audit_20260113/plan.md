# Plan: Comprehensive Codebase Audit & Roadmap

## Phase 1: Automated Analysis & Discovery
- [ ] Task: Run static analysis tools on the Python backend.
    - [ ] Sub-task: Execute `flake8 src/` and capturing output.
    - [ ] Sub-task: Execute `mypy src/` (type checking) and capture output.
    - [ ] Sub-task: Analyze tool output to identify hotspots of complexity or error.
- [ ] Task: Run static analysis on the React frontend.
    - [ ] Sub-task: Run `npm run lint` in `frontend/`.
    - [ ] Sub-task: Analyze `frontend/` dependency usage for outdated packages.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Automated Analysis & Discovery' (Protocol in workflow.md)

## Phase 2: Manual Code Review & Bug Hunting
- [ ] Task: Review Core Logic Modules.
    - [ ] Sub-task: Audit `src/game_detector.py` for potential race conditions or polling inefficiencies.
    - [ ] Sub-task: Audit `src/ai_assistant.py` for error handling gaps in provider switching.
    - [ ] Sub-task: Audit `src/macro_manager.py` for safety checks and edge cases.
- [ ] Task: Review UI/Overlay Architecture.
    - [ ] Sub-task: Check `src/gui.py` and `src/overlay.py` for threading issues (blocking main thread).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Manual Code Review & Bug Hunting' (Protocol in workflow.md)

## Phase 3: Performance & Architecture Assessment
- [ ] Task: Analyze resource usage patterns.
    - [ ] Sub-task: Identify potentially expensive operations (e.g., frequent IO, large loops).
    - [ ] Sub-task: Review memory management in long-running sessions.
- [ ] Task: Review Architecture against `tech-stack.md`.
    - [ ] Sub-task: Check for deviations from the intended modular architecture.
    - [ ] Sub-task: Identify circular dependencies or tight coupling.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Performance & Architecture Assessment' (Protocol in workflow.md)

## Phase 4: Roadmap & Deliverables Synthesis
- [ ] Task: Compile findings into actionable items.
    - [ ] Sub-task: Create a list of "Bug Fix" tasks.
    - [ ] Sub-task: Create a list of "Refactoring" tasks.
- [ ] Task: Propose Next Feature.
    - [ ] Sub-task: Analyze `product.md` and current capabilities.
    - [ ] Sub-task: Propose 1-2 candidates for the next major feature implementation.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Roadmap & Deliverables Synthesis' (Protocol in workflow.md)
