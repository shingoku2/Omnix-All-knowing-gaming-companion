# Specification: Settings Implementation & Dynamic HUD

## Overview
This track focuses on transforming the currently static Settings module into a fully functional control center and updating the HUD to display real-time, accurate information about the active game. It bridges the new React frontend with the existing Python backend logic for configuration and game monitoring.

## Functional Requirements
- **Functional Settings Module:**
    - **Appearance:** Implement controls for Theme selection, UI Opacity, and Scaling.
    - **AI/LLM:** Implement Model selection (Ollama/OpenAI), API Key management, and System Prompt editing.
    - **Keybinds/Macros:** UI and logic for viewing, recording, and editing global macros and profile-specific keybinds.
- **Persistence Logic:**
    - Implement a "Manual Save" workflow where changes are cached in the UI and committed to the `config.yaml` only when the user clicks "Save Changes".
    - Provide a "Discard" or "Reset" option to revert unsaved changes.
- **Dynamic Game Info HUD:**
    - **Game Detection:** Update the HUD to show the actual title of the detected game process.
    - **Session Tracking:** Implement a session timer that starts when a game is detected and stops when it closes.
    - **System Stats:** Display real-time CPU and RAM usage specific to the game process (if possible) or general system stats.
    - **Process Info:** Display the game's executable path and basic version information derived from file metadata.

## Non-Functional Requirements
- **Responsiveness:** Settings changes should reflect in the UI immediately (preview) even before saving.
- **Performance:** System stat polling should be efficient (e.g., once per second) to avoid CPU spikes.

## Acceptance Criteria
- [ ] Users can change the AI model in the Settings menu and have it persist after clicking "Save" and restarting the app.
- [ ] Macro recording triggered from the UI correctly saves to the backend.
- [ ] The HUD session timer accurately reflects the duration of the current gaming session.
- [ ] The HUD correctly identifies "No Game Detected" vs the actual name of a running game (e.g., "Elden Ring").
- [ ] Discarding changes in the Settings menu reverts all UI toggles/inputs to their last saved state.

## Out of Scope
- Integration with external platform APIs (Steam, Epic Games Store).
- Automatic game-specific knowledge base downloads (handled in a separate track).
