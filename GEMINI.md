# Omnix - All-knowing Gaming Companion

## Project Overview

**Omnix** is a sophisticated desktop AI gaming companion designed to enhance the gaming experience through automated game detection, AI-powered assistance, macro automation, and session coaching. It leverages local LLMs (via Ollama) to ensure privacy and offline capability.

### Key Features
*   **Automatic Game Detection:** Monitors running processes to identify games.
*   **Local AI Integration:** Uses Ollama for privacy-first, cost-free AI inference.
*   **Knowledge System:** Ingests game-specific docs (wikis, PDFs) for context-aware answers.
*   **Macro Automation:** Records and replays keyboard/mouse actions.
*   **Overlay UI:** Movable, resizable in-game overlay.
*   **Session Coaching:** AI analysis of gameplay patterns.
*   **HRM Integration:** Hierarchical Reasoning Model for enhanced strategic analysis.

### Technology Stack
*   **Language:** Python 3.8+
*   **GUI Framework:** PyQt6
*   **Frontend (Overlay/Dashboard):** React, TypeScript, Vite, Tailwind CSS (located in `frontend/`)
*   **AI Engine:** Ollama (Local LLMs)
*   **Key Libraries:** `psutil` (monitoring), `pynput` (input control), `beautifulsoup4` (scraping), `cryptography` (security).

## Project Structure

```
G:\GitHub\Edward-s-Stuff\
├── src/                        # Core Python source code
│   ├── gui.py                  # Main PyQt6 application window
│   ├── ai_assistant.py         # AI interaction logic
│   ├── game_detector.py        # Process monitoring
│   ├── macro_manager.py        # Automation logic
│   ├── knowledge_*.py          # Knowledge base & search (TF-IDF)
│   └── ui/                     # UI Components & Design System
├── frontend/                   # React/Vite frontend (likely for web views/overlay)
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── tests/                      # Pytest suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── ui/                     # UI tests
├── scripts/                    # Utility and CI scripts
├── assets/                     # Static assets (images, icons)
├── .github/workflows/          # CI/CD configurations
├── requirements.txt            # Python dependencies
├── BUILD.bat                   # Unified build script
└── main.py                     # Application entry point
```

## Development Workflow

### Prerequisites
*   Python 3.8+
*   Node.js (for frontend)
*   Ollama (installed and running)

### Installation
1.  **Python Setup:**
    ```bash
    python -m venv .venv
    # Activate venv (Windows: .venv\Scripts\activate, Unix: source .venv/bin/activate)
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```
2.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    ```

### Running the Application
*   **Core App:** `python main.py`
*   **Frontend Dev Server:** `cd frontend && npm run dev`

### Testing
*   **Run All Tests:** `pytest`
*   **Run Specific Suite:** `pytest tests/unit/`
*   **UI Smoke Test:** `python scripts/ui_test_tool.py`
*   **Coverage:** `pytest --cov=src --cov-report=html`

### Building
*   **Windows Executable:** `BUILD.bat` (uses PyInstaller)
*   **Debug Build:** `BUILD.bat debug`
*   **Frontend Build:** `cd frontend && npm run build`

## Code Conventions
*   **Style:** Adheres to PEP 8. enforced via `black` and `isort`.
*   **Linting:** `flake8` and `pre-commit` hooks are used.
*   **Testing:** `pytest` is the standard framework. Tests should be placed in `tests/` and mirror the source structure where possible.
*   **Architecture:** Modular design. New features should be isolated in specific modules within `src/` to avoid circular dependencies.

## Key Documentation
*   `README.md`: General overview and user guide.
*   `CLAUDE.md`: Developer-focused architecture and troubleshooting guide.
*   `TESTING.md`: Detailed testing instructions.
*   `AGENTS.md`: Context for AI agents.

## Recent Updates

### HRM Integration (2025-12-10)
*   Added Hierarchical Reasoning Model (HRM) integration for enhanced reasoning capabilities
*   Intelligent routing to HRM for complex reasoning questions in gaming contexts
*   New settings tab for HRM configuration and dependency management
*   Conditional loading with graceful degradation when HRM is unavailable
*   Added PyTorch and HRM dependencies as optional requirements with clear installation instructions
