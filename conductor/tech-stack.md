# Technology Stack: Omnix

## Backend (Core Logic)
- **Primary Language:** Python 3.8+
- **Application Framework:** PyQt6 (Main application shell, system tray, and heavy-duty window management).
- **Process Monitoring:** `psutil` for zero-latency game detection.
- **Input & Automation:** `pynput` for recording and executing mouse/keyboard macros.
- **Environment Management:** `python-dotenv` and `PyYAML` for configuration and profile management.
- **Security:** `cryptography` and `keyring` for local credential and sensitive data protection.

## Frontend (Overlay & Dashboard)
- **Framework:** React (Vite-powered) hosted within PyQt6 `QWebEngineView`.
- **Language:** TypeScript for type-safe UI logic.
- **Styling:** Tailwind CSS with custom design tokens for the cyberpunk/sci-fi aesthetic.
- **Icons:** `lucide-react` for consistent, lightweight UI elements.
- **Animation:** `framer-motion` for complex UI transitions.
- **Integration:** `QWebChannel` for bidirectional Python-React communication.

## AI & Intelligence
- **Inference Engines:** Modular support for [Ollama](https://ollama.com/) and OpenAI-compatible APIs (LM Studio, AnythingLLM, etc.) for local LLM orchestration.
- **Data Ingestion:** `beautifulsoup4`, `lxml`, and `requests` for web scraping and wiki processing.
- **Document Analysis:** `PyPDF2` and `pdfplumber` for ingestion of PDFs and game manuals.
- **Search System:** Semantic search using TF-IDF for context-aware knowledge retrieval.

## Deployment & Build
- **Windows Packaging:** `PyInstaller` (managed via custom `BUILD.bat` and python scripts).
- **Testing:** `pytest` for unit and integration testing.
- **Linting & Analysis:** `flake8` for style adherence and `mypy` for static type checking.
