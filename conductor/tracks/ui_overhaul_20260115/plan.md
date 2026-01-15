# Plan: UI Overhaul - "Omnix Evolution"

## Phase 1: Foundation & Design Tokens
- [x] Task: Define Design Tokens - Extract colors, gradients, and glow effects from `assets/UI_Elements/*.png` into Tailwind config. [6b31b70]
- [ ] Task: Global CSS Setup - Create base utility classes for the "Cyberpunk" aesthetic (e.g., `.omni-frame`, `.omni-glow`).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Design Tokens' (Protocol in workflow.md)

## Phase 2: React Component Recreation (Frontend)
- [ ] Task: Main Container Frame - Recreate the primary container using CSS Grid/Flexbox and Tailwind.
- [ ] Task: Right-Side Menu - Implement the navigation sidebar with hover states and active indicators.
- [ ] Task: Chat Module - Rebuild the chat interface using the new design assets.
- [ ] Task: Central HUD & Footer - Implement the overlay-specific HUD elements.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: React Component Recreation' (Protocol in workflow.md)

## Phase 3: Navigation & Transitions
- [ ] Task: Animation System - Implement Framer Motion (or equivalent) for menu transitions.
- [ ] Task: Sub-menu Routing - Ensure Settings, Macros, and Knowledge Base load correctly within the new frames.
- [ ] Task: Re-style Sub-menus - Apply the new design tokens to all existing internal menu components.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Navigation & Transitions' (Protocol in workflow.md)

## Phase 4: PyQt6 Shell & Integration
- [ ] Task: PyQt6 Window Styling - Update the main window shell to host the new React-based UI seamlessly.
- [ ] Task: Overlay Container Update - Sync the PyQt6 overlay window with the new HUD dimensions.
- [ ] Task: Integration Testing - Verify that Python-to-JS communication still works for all modules.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: PyQt6 Shell & Integration' (Protocol in workflow.md)

## Phase 5: Final Polish & Verification
- [ ] Task: Performance Audit - Profile CPU/GPU usage during gameplay with the new UI.
- [ ] Task: Visual QA - Cross-reference every screen against the original PNG assets.
- [ ] Task: Bug Scrub - Fix any layout or interaction regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Final Polish & Verification' (Protocol in workflow.md)
