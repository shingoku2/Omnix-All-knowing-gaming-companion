# Omnix Gaming Companion - AI Assistant Context

## Project Overview

Omnix is a sophisticated desktop AI gaming companion that automatically detects what game you're playing and provides AI-powered assistance, knowledge integration, macro automation, and session coaching to enhance your gaming experience. The project was developed as a passion project using AI assistance for the entire codebase, demonstrating the viability of AI-assisted development.

### Key Features
- **🎯 Automatic Game Detection** - Monitors 15 pre-configured games with custom profile support
- **🤖 Ollama AI Integration** - Local/remote LLM inference without API keys (privacy-focused)
- **📚 Knowledge System** - Per-game knowledge packs with semantic search (TF-IDF algorithm)
- **⌨️ Macro & Automation** - Record and execute keyboard/mouse macros with hotkey support
- **📊 Session Coaching** - AI-powered gameplay insights and improvement tips
- **🔒 Privacy First** - All AI inference runs locally by default
- **🎨 Modern Design System** - Consistent UI with design tokens and reusable components
- **🪟 Advanced Overlay** - Movable, resizable, minimizable with auto-save

### Technology Stack
- **Language**: Python 3.8+ (~14,700 LOC)
- **GUI Framework**: PyQt6 6.6.0+
- **AI Integration**: Ollama (local/remote LLM inference)
- **Process Monitoring**: psutil for game detection
- **Automation**: pynput for keyboard/mouse simulation
- **Security**: cryptography (AES-256) + keyring (system keyring) for credential storage
- **Build Tool**: PyInstaller for executable creation

## Project Architecture

### Core Components
- **main.py** - Application entry point with comprehensive error handling
- **config.py** - Configuration management (environment variables + JSON files)
- **game_detector.py** - Process monitoring for game detection using psutil
- **ai_assistant.py** - High-level AI interface with Ollama provider
- **knowledge_*.py** - Complete knowledge management system (ingestion, indexing, integration)
- **macro_*.py** - Macro recording, execution, and keybinding management
- **gui.py** - Main GUI application (~1,800 LOC) with PyQt6
- **ui/design_system.py** - Token-based design system with reusable components

### Layered Architecture
```
Presentation (PyQt6 GUI) → Business Logic → Data/Integration → Persistence
```

### Data Flow
```
User Input → Game Detection → Profile Lookup → Knowledge Integration
→ AI Assistant → Ollama Provider → Session Logger → GUI Response
```

## Building and Running

### Prerequisites
- Python 3.8+ (3.10+ recommended)
- Ollama installed (download from https://ollama.ai)

### Installation and Setup
```bash
# Clone the repository
git clone https://github.com/shingoku2/Omnix-All-knowing-gaming-companion.git
cd Omnix-All-knowing-gaming-companion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Install and configure Ollama
curl https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3  # or another model of your choice
```

### Running the Application
```bash
# Run from source
python main.py
```

### Building Executables
```bash
# Windows build (automated)
BUILD.bat                    # Release build
BUILD.bat debug             # Debug build (shows console)

# Manual PyInstaller build
pyinstaller GamingAIAssistant.spec
# Output: dist/GamingAIAssistant/GamingAIAssistant.exe
```

### Configuration
The application supports configuration via:
- **Environment variables** (.env file)
- **JSON files** in `~/.gaming_ai_assistant/`
- **Runtime settings** saved through the GUI

Example `.env` configuration:
```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Application Settings
OVERLAY_HOTKEY=ctrl+shift+g
CHECK_INTERVAL=5

# Overlay Window Settings (auto-saved when you move/resize)
OVERLAY_X=100
OVERLAY_Y=100
OVERLAY_WIDTH=900
OVERLAY_HEIGHT=700
OVERLAY_MINIMIZED=false
OVERLAY_OPACITY=0.95
```

## Usage Instructions

### Basic Usage
1. Launch the Gaming AI Assistant
2. Ensure Ollama is running in the background with a model loaded
3. Open any supported game (e.g., League of Legends, Elden Ring, etc.)
4. The assistant will automatically detect it and provide an overview
5. Ask questions in the chat interface
6. Use `Ctrl+Shift+G` to toggle the window visibility

### Example Questions
- "What's the best build for a tank character?"
- "How do I defeat the boss in the Fire Temple?"
- "What are some beginner tips?"
- "Explain the crafting system"
- "What's the current meta?"

### Advanced Features
- **Knowledge Packs**: Import PDFs, DOCX, TXT, Markdown files, or web URLs as game-specific knowledge bases
- **Macro System**: Create and execute keyboard/mouse macros with safety limits
- **Session Coaching**: Track your gaming sessions and get AI-powered insights
- **Game Profiles**: Customize AI behavior per game with custom system prompts

### Keyboard Shortcuts
- **Ctrl+Shift+G** - Toggle assistant window
- **Enter** - Send message
- **Escape** - Clear input field

## Development Conventions

### Python Style
- PEP 8 compliance
- Type hints for functions
- Google-style docstrings
- 4-space indentation

### Naming Conventions
- Classes: `PascalCase` (e.g., `GameDetector`)
- Functions: `snake_case` (e.g., `detect_running_game()`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Private: `_leading_underscore` (e.g., `_normalize_name()`)

### Qt Patterns
Always use worker threads for long operations to prevent GUI freezing:
```python
# GOOD: Non-blocking
worker = AIWorkerThread(ai_assistant, question)
worker.response_ready.connect(display_response)
worker.start()
```

### UI Components
Use the design system components:
```python
# GOOD
from ui.components.buttons import OmnixButton
button = OmnixButton("Click Me", variant="primary")

# AVOID hardcoded styles
button = QPushButton("Click Me")
button.setStyleSheet("background: blue;")
```

## Testing

### Test Organization
```
tests/
├── unit/                 # Logic tests (no GUI)
│   ├── test_game_detector.py
│   ├── test_knowledge_system.py
│   └── ...
├── ui/                   # GUI tests
│   ├── test_gui_minimal.py
│   └── ...
└── integration/          # Integration tests
    ├── test_ollama_integration.py
    └── ...
```

### Running Tests
```bash
python -m pytest              # Run all tests
python test_before_build.py   # Pre-build validation
```

For headless testing:
```bash
# Offscreen platform (recommended for CI)
export QT_QPA_PLATFORM=offscreen
python -m pytest
```

## Security and Privacy

### Data Protection
- Local processing: All data processing happens on your machine
- Direct API calls: Communicates directly with AI providers (no intermediaries)
- Encrypted storage: API keys encrypted with AES-256 and stored in system keyring
- No telemetry: No usage tracking, analytics, or data collection
- Session privacy: Gaming sessions stored locally only

### What Gets Sent to AI Providers
- Your questions and conversation history
- Game context (game name, current profile)
- Relevant knowledge pack excerpts (if enabled)
- No screenshots, no keystrokes, no personal data beyond what you type

### Platform Security
- Windows: Windows Credential Manager integration
- macOS: Keychain Services integration
- Linux: SecretService D-Bus API with encrypted fallback

## Project Files Location

### Core Application
```
Main:        main.py
Config:      src/config.py
Game:        src/game_detector.py
AI:          src/ai_assistant.py, src/providers.py
Knowledge:   src/knowledge_*.py
Macros:      src/macro_*.py
GUI:         src/gui.py
UI System:   src/ui/design_system.py
User Data:   ~/.gaming_ai_assistant/
```

### Documentation
- **README.md**: User documentation and quick start
- **CLAUDE.md**: Comprehensive developer guide (~500 lines)
- **QWEN.md**: Current AI assistant context file
- **SETUP.md**: Installation and configuration guide
- Various markdown files for testing, troubleshooting, and CI/CD

## Troubleshooting

### Common Issues

#### Ollama Connection Issues
- Verify the Ollama daemon is running (`ollama serve` or the installed service)
- Check `OLLAMA_HOST` matches your daemon address (default `http://localhost:11434`)
- Ensure the model is pulled locally: `ollama pull llama3`
- Use Settings → AI Providers → Test Connection to validate connectivity

#### Game Not Detected
- Verify the game is actually running
- Check Task Manager/Activity Monitor for the exact process name
- Add custom profile: Settings → Game Profiles → Add Custom Profile
- Check logs in `gaming_ai_assistant_*.log` for detection attempts

#### Knowledge Packs Not Working
- Ensure knowledge pack is enabled: Settings → Knowledge Packs
- Verify pack is associated with the correct game profile
- Rebuild index if needed (delete and re-add sources)
- Check that knowledge integration is enabled in game profile settings

#### Macros Not Executing
- Verify macro is enabled in Macro Manager
- Check hotkey bindings for conflicts
- Ensure game window has focus (if not set to system-wide)
- Review macro execution logs for errors

### Development Troubleshooting
- Circular import errors: Ensure consistent use of `src.` prefix in imports
- GUI freezing: Always use worker threads for long operations
- Build errors: Check PyInstaller spec file for missing hidden imports/data files
- Search index issues: Use index rebuild functionality if search results are inconsistent

## Recent Updates

### Major Version 2.0 - Ollama-Only Migration (2025-12-06)
- Simplified to Ollama exclusively - no API keys required by default
- Privacy-first, local-first architecture
- Model freedom - supports any Ollama model (llama3, mistral, codellama, etc.)
- Automatic model discovery showing available models from Ollama daemon
- Connection testing with validation of Ollama availability

### HRM Integration (2025-12-10)
- Added Hierarchical Reasoning Model (HRM) integration for enhanced reasoning capabilities
- Intelligent routing to HRM for complex reasoning questions in gaming contexts
- New settings tab for HRM configuration and dependency management
- Conditional loading with graceful degradation when HRM is unavailable
- Added PyTorch and HRM dependencies as optional requirements with clear installation instructions

### CI/CD Enhancement (2025-11-20)
- Self-hosted runner on Proxmox LXC
- Automated testing and deployment pipeline

### Search Index Persistence Fix (2025-11-19)
- Fixed TF-IDF model state not persisting to disk
- Search results now remain accurate after application restarts

### Theme System Unification (2025-11-17)
- Migrated from dual theme systems to unified token-based design
- Per-token customization with real-time UI updates via observer pattern
- Automatic theme.json v1 → v2 migration with backward compatibility
- Zero breaking changes via compatibility layer

## External Dependencies

### Core Dependencies
- psutil >= 5.9.0: Process monitoring for game detection
- requests >= 2.31.0: HTTP requests for knowledge ingestion
- PyQt6 >= 6.6.0: Desktop GUI framework
- python-dotenv >= 1.0.0: Environment variable loading
- cryptography >= 41.0.0: Secure credential encryption
- ollama >= 0.3.0: Ollama API client
- pynput >= 1.7.6: Keyboard/mouse automation
- keyring >= 24.2.0: Secure credential storage

### Optional Dependencies
- PyPDF2 >= 3.0.0: PDF processing for knowledge packs
- pdfplumber >= 0.9.0: Advanced PDF processing