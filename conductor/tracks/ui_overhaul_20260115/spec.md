# Specification: UI Overhaul - "Omnix Evolution"

## Overview
This track involves a comprehensive recreation of the entire Omnix UI (Main Window, Overlay, and all sub-menus) based on the "sci-fi/cyberpunk" design language established in the `assets/UI_Elements` directory. The goal is to move from the current functional design to a highly polished, immersive aesthetic using a hybrid approach of PyQt6 and React/Tailwind.

## Functional Requirements
- **Global Theme Application:** Implement the new visual style across all existing modules (Chat, Settings, Knowledge Base, Macro Manager, Session Coaching).
- **Hybrid UI Integration:**
    - **PyQt6:** Update the main application shell and native window borders to match the "Main Container Frame."
    - **React/Vite:** Recreate the Overlay HUD, Chat Module, and all internal sub-menus using React and Tailwind CSS.
- **Visual Fidelity:** Recreate the gradients, glows, and geometric shapes from the PNG assets using pure CSS/Tailwind (CSS-first approach).
- **Navigation & Layout:**
    - Use the "Right-Side Menu" logic for primary navigation between app modules.
    - Implement the "Central HUD" and "Chat Module" as modular, draggable components within the overlay.
- **Animated Transitions:** Implement smooth slide-in or fade transitions when switching between sub-menus or opening panels.

## Non-Functional Requirements
- **Performance:** Ensure the new CSS-heavy UI does not negatively impact game frame rates (target <1% CPU overhead).
- **Responsiveness:** UI elements must scale appropriately for different screen resolutions (1080p, 1440p, 4K).
- **Maintainability:** Use CSS variables/Tailwind tokens to ensure the theme can be easily tweaked in one place.

## Acceptance Criteria
- [ ] The Main Container Frame matches the visual reference in `assets/UI_Elements/Main Container Frame.png`.
- [ ] All sub-menus (Settings, Macro, etc.) are accessible and functional within the new design.
- [ ] Transitions between menus are smooth and animated.
- [ ] The Overlay remains interactive and movable over a running game.
- [ ] No regression in existing functionality (AI chat still works, game detection still works).

## Out of Scope
- Changing the underlying AI logic or Ollama integration.
- Adding new functional features not present in the current version (this is a visual/UX recreation).
