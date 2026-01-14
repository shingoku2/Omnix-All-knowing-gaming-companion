# Product Guidelines: Omnix

## Tone and Voice
- **The "Professional Sidekick":** Omnix balances tactical precision with encouraging support. It should speak like an experienced co-op partner—concise and data-driven when strategy is needed, but friendly and supportive to keep the session enjoyable.
- **Actionable & Direct:** Avoid fluff. Responses should prioritize utility and speed, helping the user make better decisions in real-time.

## Visual Identity & UX
- **Modern Gaming HUD:** The UI should feel like a premium, integrated part of a high-end game's HUD. This includes high-contrast dark themes, neon accents (cyberpunk/sci-fi), and sharp, technical typography.
- **Smart Information Density:** Layouts should be compact and information-dense, maximizing the visibility of stats, logs, and tips without overwhelming the screen.
- **Immersive Non-Distraction:** While the design is bold, the overlay must never block critical game information. Use transparency and minimize transitions to stay out of the user's way.

## Development Principles
- **Extreme Modularity:** Core services (detection, automation, AI) must remain decoupled from game-specific logic and from each other. Circular dependencies are strictly prohibited. Adding support for a new game should ideally require only a new configuration or knowledge pack, not core code changes.
- **Privacy by Design:** Local-first is the law. All AI operations, gameplay logs, and session data default to local storage. Any remote connection must be explicitly configured and approved by the user.
- **Fail-Safe Robustness:** The application must remain responsive regardless of AI inference speed or background task load. If a subsystem fails (e.g., a specific knowledge base is unreachable), the rest of the companion must degrade gracefully.

## User Engagement
- **Transparency:** Clearly communicate when the AI is processing or when a macro is active.
- **Customization:** Empower the user to tailor the overlay's density and the AI's "chatty-ness" to their preference.
