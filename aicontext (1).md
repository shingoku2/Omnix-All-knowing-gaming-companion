# Omnix Development Context & Reference

**Project:** OMNIX - All-Knowing Gaming Companion  
**Version:** 1.3 (14,700 LOC Python)  
**Last Updated:** January 13, 2026  
**Status:** Stable with recommended cleanups

---

## QUICK FACTS

| Metric | Value |
|--------|-------|
| **Total Lines** | 14,700 |
| **Python Files** | 42 |
| **Test Functions** | 272 |
| **Core Modules** | 9 |
| **Supported Games** | 37+ |
| **AI Providers** | 3 (Anthropic, OpenAI, Google) |
| **Test Coverage** | ~25-30% |
| **Python Version** | 3.9+ |
| **GUI Framework** | PyQt6 |
| **Frontend** | React + TypeScript |
| **Database** | SQLite |
| **Build Type** | PyInstaller (Windows .exe) |

---

## ARCHITECTURE OVERVIEW

```
OMNIX Gaming Companion
├── Backend (Python)
│   ├── AI System
│   │   ├── ai_assistant.py - Main Q&A interface
│   │   ├── ai_router.py - Multi-provider routing
│   │   ├── providers/ - Anthropic, OpenAI, Gemini
│   │   └── api_keys/ - Key management
│   │
│   ├── Game System
│   │   ├── game_detector.py - Game detection
│   │   ├── game_watcher.py - Game process monitoring
│   │   ├── game_profiles.json - Game metadata
│   │   └── profiles/ - 37+ game configs
│   │
│   ├── Knowledge System
│   │   ├── knowledge_index.py - TF-IDF search
│   │   ├── knowledge_integration.py - Augmentation
│   │   ├── knowledge_packs/ - Knowledge databases
│   │   └── knowledge_store.py - Persistence
│   │
│   ├── Macro System
│   │   ├── macro_manager.py - Macro orchestration
│   │   ├── macro_runner.py - Macro execution
│   │   ├── macro_generator.py - AI-powered generation
│   │   └── macros.json - Recorded macros
│   │
│   ├── Storage Layer
│   │   ├── base_store.py - Abstract storage
│   │   ├── credential_store.py - Encrypted API keys
│   │   ├── file_store.py - JSON persistence
│   │   ├── session_logger.py - Activity logging
│   │   └── sqlite_store.py - Structured data
│   │
│   ├── GUI (Qt)
│   │   ├── gui.py - Main window (PyQt6)
│   │   ├── overlay.py - Floating overlay
│   │   ├── dialogs/ - Settings, about, etc.
│   │   └── widgets/ - Custom Qt components
│   │
│   └── Utilities
│       ├── config.py - Config management
│       ├── logger.py - Logging setup
│       ├── error_recovery.py - Crash recovery
│       └── validator.py - Input validation
│
├── Frontend (React)
│   ├── src/
│   │   ├── components/ - React components
│   │   ├── pages/ - Page components
│   │   ├── styles/ - Tailwind CSS
│   │   ├── hooks/ - Custom React hooks
│   │   └── App.tsx - Main app
│   │
│   └── public/ - Static assets
│
└── Testing
    ├── tests/ - Pytest test suite (272 tests)
    ├── conftest.py - Fixtures
    ├── test_imports.py - Circular import detection
    └── .coveragerc - Coverage configuration
```

---

## MAJOR COMPONENTS

### 1. AI System (5,000 LOC)
Handles multi-provider LLM integration with provider abstraction

**Files:**
- `src/ai_assistant.py` - High-level Q&A interface
- `src/ai_router.py` - Provider routing logic
- `src/providers/` - Provider implementations
- `src/providers/anthropic_provider.py` - Claude API
- `src/providers/openai_provider.py` - GPT-4 integration
- `src/providers/gemini_provider.py` - Google Gemini

**Key Functions:**
```python
ai_assistant.ask_question(question: str) -> str  # Main interface
ai_router.route_request(prompt: str) -> str  # Selects provider
provider.complete(prompt: str) -> str  # Provider-specific
```

**Critical Files for Code Changes:**
- Add new provider: Create `src/providers/new_provider.py` + register in `ai_router.py`
- Change AI logic: Modify `ai_assistant.py` methods
- Provider issues: Check `.env` credentials + provider rate limits

---

### 2. Game System (3,500 LOC)
Detects running games and provides game-specific context

**Files:**
- `src/game_detector.py` - Process detection logic
- `src/game_watcher.py` - Continuous monitoring
- `src/game_profile.py` - Game metadata class
- `src/game_profiles.json` - Profile database (37+ games)
- `profiles/` - Per-game JSON files

**Key Structures:**
```python
GameProfile:
  name: str              # "The Witcher 3"
  executable: str       # "witcher3.exe"
  process_names: List   # ["witcher3.exe", "GOG.exe"]
  wiki_url: str        # Knowledge base URL
  ai_context: str      # AI system prompt
  macros: List[str]    # Available macros
```

**How It Works:**
1. Detector polls process list every 5 seconds (currently)
2. Matches executable names against game profiles
3. Returns matched profile with game-specific context
4. Watcher tracks continuous play session
5. AI system augments responses with game knowledge

**Performance Issue:**
- Current: Scans all processes every 5s (CPU waste)
- Recommended: Use process event hooks on Windows

---

### 3. Knowledge System (2,000 LOC)
Augments AI responses with game-specific knowledge

**Files:**
- `src/knowledge_index.py` - TF-IDF search index
- `src/knowledge_integration.py` - Q&A augmentation
- `src/knowledge_store.py` - Knowledge pack storage
- `knowledge_packs/` - Knowledge database files

**How It Works:**
1. User asks question: "How do I beat the dragon?"
2. Knowledge index searches packs for relevant docs
3. Top 3 results added to AI prompt as context
4. AI provides answer informed by knowledge pack

**Knowledge Pack Format:**
```json
{
  "name": "Elden Ring - Boss Strategies",
  "version": "1.2",
  "documents": [
    {
      "title": "Malenia Boss Guide",
      "content": "Malenia is weak to fire attacks... ",
      "game": "Elden Ring",
      "category": "boss_strategy"
    }
  ]
}
```

**Search Implementation:**
- TF-IDF vectorizer from scikit-learn
- Cosine similarity for relevance ranking
- Top-K results (default K=3)

---

### 4. Macro System (2,500 LOC)
Records and plays back keyboard/mouse sequences

**Files:**
- `src/macro_manager.py` - Macro orchestration
- `src/macro_runner.py` - Execution engine
- `src/macro_generator.py` - AI-powered generation
- `macros.json` - Recorded macros database

**Macro Safety Features:**
- Max 100 actions per macro (prevents runaway)
- Timeout: 30 seconds max execution
- User must grant permission before playback
- Unsafe actions blocked (e.g., `taskkill`)
- Execution pause on any error

**Macro Structure:**
```python
Macro:
  name: str            # "Witcher: Dodge Right"
  game: str            # "The Witcher 3"
  actions: List[Action]
  
Action:
  type: str            # "key_press", "mouse_move", "wait"
  params: Dict
  delay: float         # Milliseconds
```

**Example Macro:**
```json
{
  "name": "Shield Bash Attack",
  "game": "Elden Ring",
  "actions": [
    {"type": "key_press", "key": "right", "duration": 0.1},
    {"type": "wait", "duration": 0.2},
    {"type": "key_press", "key": "l1", "duration": 0.05},
    {"type": "wait", "duration": 0.3}
  ]
}
```

---

### 5. Storage Layer (1,000 LOC)
Handles all data persistence with encryption

**Files:**
- `src/base_store.py` - Abstract base class
- `src/credential_store.py` - Encrypted API keys (Fernet)
- `src/file_store.py` - JSON file persistence
- `src/session_logger.py` - Activity logging
- `src/sqlite_store.py` - Structured data (future)

**Storage Hierarchy:**
```
BaseStore
├─ CredentialStore - API keys in Fernet encrypted form
├─ FileStore - JSON files for profiles, macros
├─ SessionLogger - CSV activity logs
└─ SQLiteStore - Game statistics, metrics
```

**Credential Storage:**
- Preferred: System keyring (Windows Credential Manager, macOS Keychain, Linux SecretService)
- Fallback: Fernet-encrypted file in `~/.gamingaiassistant/master.key`
- Optional: Password-derived encryption (set `OMNIX_KEY_PASSWORD`)

---

### 6. GUI System (2,000 LOC)
PyQt6-based desktop interface

**Files:**
- `src/gui.py` - Main application window
- `src/overlay.py` - Floating overlay widget
- `src/settings_dialog.py` - Settings interface
- `src/dialogs/` - Modal dialogs
- `src/widgets/` - Custom Qt components

**Main Features:**
- Game detection display + auto-update
- AI chat interface (question/answer)
- Settings tabbed dialog (AI, games, macros, etc.)
- Floating overlay (hotkey toggleable)
- Macro recorder and manager
- Knowledge pack browser

**GUI Threading:**
- Main thread: Qt event loop
- Worker thread: AI requests (non-blocking)
- Queue: Thread-safe communication between threads

---

## CRITICAL CONFIGURATION FILES

### `.env` - API Credentials
```bash
# Anthropic (Primary)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI (Alternative)
OPENAI_API_KEY=sk-...

# Google (Alternative)
GOOGLE_API_KEY=...

# Optional Features
OMNIX_CONFIG_DIR=~/.gamingaiassistant
OMNIX_LOG_LEVEL=INFO
OMNIX_KEY_PASSWORD=your-password-here  # For key encryption
```

### `~/.gamingaiassistant/` - User Data
```
~/.gamingaiassistant/
├── config.json - App settings
├── game_profiles.json - Installed game configs
├── macros.json - User-recorded macros
├── knowledge_packs/ - Custom knowledge databases
├── master.key - Encrypted API key (if no keyring)
├── logs/ - Activity logs
│   ├── session_YYYYMMDD.log
│   ├── errors.log
│   └── ai_interactions.csv
└── cache/ - Temporary files
    ├── game_detection.pkl
    └── knowledge_index.pkl
```

### `game_profiles.json` - Game Metadata
```json
[
  {
    "name": "The Witcher 3",
    "executable": "bin\\x64\\witcher3.exe",
    "process_names": ["witcher3.exe", "GOG.exe"],
    "wiki_url": "https://witcher-wiki.com",
    "ai_context": "RPG set in fantasy world...",
    "macros": ["dodge_roll", "sign_cast", "meditate"]
  }
]
```

---

## TESTING INFRASTRUCTURE

### Test Organization
```
tests/
├── conftest.py - Fixtures (272 test functions use these)
├── test_ai_system.py - AI provider tests
├── test_game_detection.py - Game detection tests
├── test_knowledge_integration.py - Knowledge augmentation
├── test_macro_system.py - Macro safety & execution
├── test_storage.py - Storage layer tests
├── test_gui.py - GUI widget tests
├── test_config.py - Configuration tests
└── ... (20 test files total)
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_ai_system.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Only fast tests (skip GUI)
pytest tests/ -v -m "not gui"

# Specific test
pytest tests/test_ai_system.py::test_anthropic_provider -v
```

### Key Fixtures (conftest.py)
```python
@pytest.fixture
def temp_config():
    """Temporary config directory for tests"""
    # Returns isolated test config dir
    
@pytest.fixture
def mock_ai_router():
    """Mock AI router (no actual API calls)"""
    
@pytest.fixture
def mock_game_detector():
    """Mock game detector (returns test game)"""
    
@pytest.fixture
def qapp():
    """Qt application for GUI tests"""
```

---

## DEVELOPMENT WORKFLOW

### 1. Making Code Changes
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
vim src/your_module.py

# Test locally
pytest tests/test_your_module.py -v

# Format code
black src/ --line-length=127

# Lint check
flake8 src/ --max-line-length=127

# Commit
git commit -m "Feature: describe what you changed"

# Push and create PR
git push -u origin feature/your-feature
```

### 2. Running Locally
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run app
python omnix_gaming_assistant.py

# Run with debug logging
OMNIX_LOG_LEVEL=DEBUG python omnix_gaming_assistant.py

# Run headless (no GUI)
python -c "from src.ai_assistant import AIAssistant; ..."
```

### 3. Building Executable
```bash
# Windows
python build_windows_exe.py
# Output: dist/GamingAIAssistant.exe

# Cross-platform (requires pyinstaller)
pyinstaller GamingAIAssistant.spec
```

---

## KNOWN ISSUES & TODOs

### Critical (Phase 1 - Fix First)
- [ ] Import pattern inconsistency (relative vs absolute)
- [ ] Config directory hardcoding (test pollution)
- [ ] Settings tab navigation TODO unfixed
- [ ] Credential store fallback security warning missing

### Quality (Phase 2 - Improve)
- [ ] Type hints incomplete (~40% coverage)
- [ ] Error handling inconsistent (some silent fail)
- [ ] Dependency injection not implemented (tight coupling)
- [ ] Configuration scattered across multiple files

### Performance (Phase 3 - Optimize)
- [ ] Game detection polls unnecessarily (CPU waste)
- [ ] Knowledge index rebuilds entirely (O(n*m) complexity)
- [ ] No log viewer in UI (users must check file)
- [ ] No provider comparison tool

### Features (Phase 4 - Enhance)
- [ ] Web API for alternate UIs
- [ ] CLI tool
- [ ] Macro A/B testing
- [ ] Cross-platform hotkey system

---

## IMPORTANT PATHS & COMMANDS

### File Locations
```bash
# Config directory
~/.gamingaiassistant/

# Source code
./src/

# Tests
./tests/

# Build output
./dist/

# Logs
~/.gamingaiassistant/logs/
```

### Useful Commands
```bash
# Find all TODOs
grep -r "TODO\|FIXME\|XXX" src/ --include="*.py"

# Check circular imports
python test_circular_import.py

# Run specific test
pytest tests/test_file.py::TestClass::test_method -v

# Check coverage
pytest --cov=src --cov-report=term-missing

# Format code
black src/ --line-length=127

# Type check
mypy src/ --ignore-missing-imports

# Find large files
find . -type f -size +1M
```

---

## NEXT PHASE SUMMARY

### Phase 1: Critical Fixes (1-2 weeks)
- Fix import patterns and stdlib conflicts
- Inject config directories for test isolation
- Complete settings tab navigation
- Improve credential store security
- **Result:** Stable codebase, all tests passing

### Phase 2: Quality Improvements (2-3 weeks)
- Standardize error handling
- Complete type hints
- Implement dependency injection
- Improve logging
- **Result:** More maintainable, better IDE support

### Phase 3: Performance (1-2 weeks)
- Optimize game detection
- Optimize knowledge index
- Add UI logging dashboard
- **Result:** Faster, more responsive app

### Phase 4: Features (Ongoing)
- Web API
- CLI tool
- Provider comparison
- Advanced macros
- **Result:** Extensible platform

---

## QUICK REFERENCE

### Import Pattern
```python
from src.module_name import function_or_class
```

### Create New Module
```python
# src/my_new_module.py
"""Module description"""

import logging
from typing import Optional
from src.base_store import BaseStore

logger = logging.getLogger(__name__)

class MyNewClass:
    """Class description"""
    pass
```

### Add Tests
```python
# tests/test_my_new_module.py
import pytest
from src.my_new_module import MyNewClass

@pytest.fixture
def my_service(temp_config):
    return MyNewClass(config_dir=temp_config)

def test_feature(my_service):
    assert my_service.do_something() is not None
```

### Log Output
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

---

## FOR NEW DEVELOPERS

**Start here:**
1. Read this file (you are here!)
2. Read CODE_CLEANUP_AND_IMPROVEMENTS.md section "Critical Issues"
3. Review PHASE_1_QUICK_START.md for hands-on implementation
4. Check ANALYSIS_SUMMARY.md for high-level overview

**First task:**
- Fix one import pattern issue
- Run tests to verify no regressions
- Make a PR

**Questions?**
- Check CLAUDE.md for detailed architecture
- Search grep for similar code patterns
- Run `pytest tests/ -v -k your_module` for examples

---

**Good luck! 🚀 Ask questions early, commit often, run tests frequently.**
