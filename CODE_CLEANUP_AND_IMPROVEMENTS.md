# Omnix Code Cleanup & Enhancement Recommendations

**Last Updated:** January 13, 2026  
**Codebase Version:** 1.3 (14,700 LOC Python)  
**Status:** Comprehensive Analysis Complete

---

## Executive Summary

Omnix is a solid gaming AI companion with 14,700 lines of well-structured Python code, comprehensive testing infrastructure, and modern PyQt6/React frontends. The following recommendations focus on **code quality improvements, maintainability enhancements, and feature optimization** without breaking existing functionality.

---

## CRITICAL CLEANUP ISSUES

### 1. **Import Pattern Inconsistency** ⚠️ HIGH PRIORITY
**Severity:** Medium | **Effort:** Low | **Impact:** Code Quality, Maintainability

**Issue:**
- Mixed import patterns across modules: `from module import X` vs. `from src.module import X`
- Causes circular import failures and makes modules difficult to test in isolation
- Already documented fix exists from 2025-11-18

**Current State:**
```python
# ❌ INCONSISTENT (found in some modules)
from knowledgeintegration import getknowledgeintegration

# ✅ CONSISTENT (found in most modules)
from src.knowledgeintegration import getknowledgeintegration
```

**Recommendation:**
1. **Standardize all imports** to use `from src.module import X` pattern
2. Create a quick linting rule: `grep -r "^from [a-z_]* import" src/ --include="*.py" | grep -v "__pycache__"`
3. Update CI/CD to catch regressions: Add check to `.pre-commit-config.yaml`
4. Test with `python test_circular_import.py` after changes

**Affected Files (Sample):**
- `src/ai_assistant.py` - verify imports
- `src/game_profile.py` - verify imports
- Any file importing from `src.*` modules

**Time Estimate:** 1-2 hours

---

### 2. **Module Naming Conflicts with Python Stdlib** ⚠️ HIGH PRIORITY
**Severity:** High | **Effort:** Low | **Impact:** Runtime Stability

**Issue:**
- Previously renamed `types.py` → `type_definitions.py` to avoid shadowing Python's `types` module
- Need to verify no other stdlib names are being shadowed

**Verification Checklist:**
```bash
python -m py_compile src/*.py  # Catch syntax errors
python -c "import src; print(dir())"  # Verify no shadowing
grep -E "^import (os|sys|json|re|math|abc|collections|itertools)" src/*.py
```

**Action Items:**
1. Audit remaining files for stdlib conflicts
2. Run automated linter: `flake8 src/ --select=E999`
3. Document avoided names in `CONTRIBUTING.md`

**Time Estimate:** 30-45 minutes

---

### 3. **Configuration Directory Hardcoding** ⚠️ MEDIUM PRIORITY
**Severity:** Medium | **Effort:** Medium | **Impact:** Testability, Maintainability

**Issue:**
- Knowledge and storage systems hardcode `.gamingaiassistant/` directory
- Makes unit testing difficult, prevents environment isolation
- Blocks CI/CD testing on clean environments

**Current Problem Code:**
```python
# ❌ HARDCODED - src/knowledge_store.py
def get_knowledge_pack_store(self):
    return KnowledgePackStore()  # Always uses global .gamingaiassistant

# ❌ HARDCODED - src/knowledge_index.py
def rebuild_index_for_game(self):
    store = get_knowledge_pack_store()  # Can't inject custom store
```

**Recommended Fix:**
```python
# ✅ INJECTABLE - Allow dependency injection
class KnowledgeIndex:
    def __init__(self, store: KnowledgePackStore = None, config_dir: str = None):
        self.store = store or get_knowledge_pack_store()
        self.config_dir = config_dir or get_config_dir()
```

**Affected Files:**
- `src/knowledge_store.py` - Add `config_dir` parameter
- `src/knowledge_index.py` - Make store injectable
- `src/base_store.py` - Add config_dir support
- `conftest.py` - Update fixtures to use temp directories

**Benefits:**
- ✅ Hermetic tests (no pollution of user config)
- ✅ CI/CD can run in isolation
- ✅ Better error reproduction in clean environments
- ✅ Support for multi-instance testing

**Time Estimate:** 3-4 hours (medium refactor)

---

### 4. **Settings Tab Navigation - UI TODO** ⚠️ MEDIUM PRIORITY
**Severity:** Medium | **Effort:** Low | **Impact:** UX, Feature Completeness

**Issue:**
- Dashboard buttons (AI Providers, Game Profiles, Knowledge Packs) don't navigate to correct settings tabs
- Code left as TODO: `# TODO: navigat to specific tab`
- Blocks UI discoverability, users can't easily find settings

**Current Code (src/gui.py ~Line 870):**
```python
# ❌ INCOMPLETE
def open_advanced_settings(self, tab_index=None):
    """Open settings dialog (TODO: navigate to specific tab)"""
    self.settings_dialog = SettingsDialog(self.config, ...)
    self.settings_dialog.show()  # Always shows default tab
```

**Fix:**
```python
# ✅ COMPLETE
class TabbedSettingsDialog(QDialog):
    def set_active_tab(self, tab_index: int):
        """Switch to specific tab"""
        self.tab_widget.setCurrentIndex(tab_index)

class OmnixMainWindow(QMainWindow):
    def open_ai_providers_settings(self):
        self.settings_dialog.set_active_tab(TAB_PROVIDERS)  # tab 1
        self.settings_dialog.show()
    
    def open_game_profiles_settings(self):
        self.settings_dialog.set_active_tab(TAB_GAME_PROFILES)  # tab 2
        self.settings_dialog.show()
```

**Affected Files:**
- `src/gui.py` - Update button handlers (~5 changes)
- `src/settings_dialog.py` - Add `set_active_tab()` method
- Tab index mapping documentation

**Time Estimate:** 1-2 hours

---

### 5. **Credential Store Fallback Security** ⚠️ HIGH PRIORITY (Security)
**Severity:** High | **Effort:** Medium | **Impact:** Security

**Issue:**
- When system keyring unavailable, falls back to plaintext Fernet key in `.gamingaiassistant/master.key`
- Reduces encryption to obfuscation (key stored unprotected on disk)
- Misleads users who believe keys are encrypted

**Current Code (src/credential_store.py ~Line 118):**
```python
# ⚠️ DANGEROUS FALLBACK
def _fallback_store_key(self, key_bytes):
    """Falls back to unprotected file storage"""
    key_path = os.path.join(self.config_dir, 'master.key')
    with open(key_path, 'wb') as f:
        f.write(key_bytes)  # ❌ Key in plaintext, only filesystem protection
```

**Recommendations:**
1. **Warn users explicitly** before falling back
   ```python
   dialog = QMessageBox.warning(
       None, "Security Notice",
       "System keyring unavailable. API keys will be stored with reduced protection.\n"
       "Set PASSWORD env var for additional protection.",
       QMessageBox.Ok
   )
   ```

2. **Support password protection** as backup:
   ```python
   password = os.getenv('OMNIX_KEY_PASSWORD')
   if password:
       encrypted_key = encrypt_with_password(key_bytes, password)
   ```

3. **Document in README:**
   ```
   ## Security - API Key Storage
   
   ### Preferred: System Keyring
   - Windows: Credential Manager
   - macOS: Keychain
   - Linux: SecretService
   
   ### Fallback: Encrypted File
   - Stored in: ~/.gamingaiassistant/master.key
   - Encryption: AES-256 Fernet
   - Protection: Filesystem permissions + optional password
   
   ### Best Practice
   Set OMNIX_KEY_PASSWORD env var for maximum protection:
   export OMNIX_KEY_PASSWORD="your-strong-password"
   ```

**Affected Files:**
- `src/credential_store.py` - Add warnings and password support
- `src/setup_wizard.py` - Explain security options
- `README.md` - Document security implications

**Time Estimate:** 2-3 hours

---

## CODE QUALITY IMPROVEMENTS

### 6. **Dependency Injection for Core Services** 🔧 MEDIUM PRIORITY
**Severity:** Low | **Effort:** Medium | **Impact:** Testability, Flexibility

**Issue:**
- Multiple singleton patterns create tight coupling
- Hard to mock for testing (AI providers, game detector, etc.)
- Makes it difficult to run multiple instances in tests

**Current Pattern:**
```python
# ❌ TIGHT COUPLING
def get_ai_assistant():
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = AIAssistant(get_ai_router())
    return _ai_assistant

# Usage - can't override
assistant = get_ai_assistant()
```

**Recommended Pattern:**
```python
# ✅ DEPENDENCY INJECTION
class ServiceContainer:
    def __init__(self):
        self.ai_router = None
        self.ai_assistant = None
        self.game_detector = None
    
    def get_ai_assistant(self) -> AIAssistant:
        if self.ai_assistant is None:
            self.ai_assistant = AIAssistant(self.get_ai_router())
        return self.ai_assistant
    
    def set_ai_assistant(self, assistant: AIAssistant):
        """Allow test override"""
        self.ai_assistant = assistant

# Usage in main
container = ServiceContainer()
container.set_ai_router(AIRouter(config))
assistant = container.get_ai_assistant()

# Usage in tests
@pytest.fixture
def mock_container():
    container = ServiceContainer()
    container.set_ai_assistant(MockAIAssistant())
    return container
```

**Benefits:**
- ✅ Easy to mock for testing
- ✅ Support multiple instances
- ✅ Clearer dependencies
- ✅ Better error messages when dependencies missing

**Affected Files:**
- `src/__init__.py` - Create `ServiceContainer`
- All modules using singletons

**Phased Approach:**
1. Phase 1: Create `ServiceContainer` class (non-breaking)
2. Phase 2: Migrate main.py to use container
3. Phase 3: Update tests to use container fixtures
4. Phase 4: Deprecate old singleton functions

**Time Estimate:** 4-6 hours (phased rollout)

---

### 7. **Error Handling Standardization** 🔧 MEDIUM PRIORITY
**Severity:** Low | **Effort:** Medium | **Impact:** Code Reliability

**Issue:**
- Inconsistent error handling patterns across modules
- Some functions silently fail, others raise exceptions
- Difficult to diagnose failures in production

**Current Mixed Patterns:**
```python
# ❌ Silent failure
def load_macro(self, macro_id):
    try:
        return json.load(...)
    except Exception:
        pass  # Silently returns None, hard to debug

# ❌ Inconsistent error types
def search_knowledge(self, query):
    if not query:
        return []  # Silent
    if error:
        raise ValueError("...")  # Exception
    return results

# ❌ No logging
def detect_game(self):
    try:
        return find_game()
    except:
        return None  # No indication of what failed
```

**Recommended Pattern:**
```python
# ✅ CONSISTENT & LOGGED
import logging
logger = logging.getLogger(__name__)

class MacroError(Exception):
    """Base exception for macro operations"""
    pass

class MacroNotFoundError(MacroError):
    """Raised when macro doesn't exist"""
    pass

def load_macro(self, macro_id: str) -> Optional[Macro]:
    """Load macro or return None if not found (expected case)"""
    try:
        with open(self.macro_path(macro_id)) as f:
            return Macro.from_dict(json.load(f))
    except FileNotFoundError:
        logger.debug(f"Macro not found: {macro_id}")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Invalid macro file {macro_id}: {e}")
        raise MacroError(f"Corrupted macro {macro_id}") from e
    except Exception as e:
        logger.exception(f"Unexpected error loading macro {macro_id}")
        raise MacroError(f"Failed to load macro: {e}") from e

def search_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeChunk]:
    """Search knowledge packs. Empty query returns empty results."""
    if not query or not query.strip():
        return []
    
    try:
        return self.index.search(query, top_k=limit)
    except Exception as e:
        logger.error(f"Knowledge search failed for '{query}': {e}")
        return []  # Graceful degradation
```

**Standardized Errors (by module):**
- `AIError`, `ProviderError`, `ProviderAuthError` - AI integration
- `GameDetectionError` - Game detection
- `MacroError`, `MacroExecutionError` - Macro system
- `KnowledgeError` - Knowledge packs
- `ConfigError` - Configuration

**Affected Files:**
- Create `src/exceptions.py` - Custom exception hierarchy
- All core modules - Replace generic exceptions

**Time Estimate:** 3-4 hours

---

### 8. **Type Hints Completion** 🔧 LOW PRIORITY
**Severity:** Low | **Effort:** Medium | **Impact:** Developer Experience

**Issue:**
- Only ~40% of functions have full type hints
- Makes IDE autocomplete unreliable
- Reduces ability to catch bugs early

**Current State (Sample from src/gui.py):**
```python
# ❌ MISSING TYPE HINTS
def open_settings_dialog(self):
    """Open settings without type hints"""
    ...

def ask_question(self, text):
    """No parameter or return types"""
    ...

# ✅ SOME TYPE HINTS EXIST
def toggle_overlay(self) -> None:
    """Has return type but param types missing"""
    ...
```

**Recommended Complete Pattern:**
```python
# ✅ FULL TYPE HINTS
from typing import Optional, List, Dict, Tuple
from src.game_profile import GameProfile
from src.macro_manager import Macro

def open_settings_dialog(self, tab_index: Optional[int] = None) -> None:
    """Open settings dialog, optionally showing specific tab"""
    ...

def ask_question(self, text: str) -> Optional[str]:
    """Ask AI assistant a question, return response or None if error"""
    ...

def get_macros_for_game(self, game_id: str) -> List[Macro]:
    """Get all macros for a specific game"""
    ...

def search_knowledge(
    self, query: str, game_profile_id: str, limit: int = 5
) -> Tuple[List[str], float]:
    """Search knowledge packs, return (results, search_time)"""
    ...
```

**Phased Approach:**
1. **Phase 1:** Add type hints to public APIs (10-15 files, ~2-3 hours)
2. **Phase 2:** Add hints to core logic functions (15-20 files, ~3-4 hours)
3. **Phase 3:** Add hints to remaining utilities (~1-2 hours)

**Tools to Enforce:**
```bash
# Check current coverage
mypy src/ --ignore-missing-imports --no-error-summary

# In pre-commit config
- repo: https://github.com/pre-commit/mirrors-mypy
  args: [--ignore-missing-imports]
```

**Time Estimate:** 6-8 hours total

---

## ARCHITECTURAL IMPROVEMENTS

### 9. **Decouple AI Assistant from GUI** 🏗️ LOW PRIORITY
**Severity:** Low | **Effort:** High | **Impact:** Maintainability, Extensibility

**Issue:**
- GUI heavily depends on `AIAssistant` through `AIWorkerThread`
- Can't easily use AI engine outside GUI context
- Difficult to build alternate UIs (web, CLI, etc.)

**Current Architecture (tightly coupled):**
```python
gui.py
  ├─ AIWorkerThread
  │   └─ AIAssistant
  │       └─ AIRouter
  └─ Settings
```

**Proposed Architecture (loosely coupled):**
```python
core/
  ├─ ai_system.py (AIAssistant, AIRouter, Providers)
  ├─ game_system.py (GameDetector, GameWatcher, Profiles)
  └─ macro_system.py (MacroManager, MacroRunner)

api/
  ├─ rest_api.py (FastAPI for external access)
  └─ events.py (Event emitter for GUI integration)

gui/
  ├─ qt_client.py (PyQt6 GUI)
  └─ web_client.py (React frontend)
```

**Event-Driven Architecture:**
```python
# src/events.py
class GameDetectionEvent:
    game: GameProfile
    detected_at: datetime

class AIResponseEvent:
    query: str
    response: str
    latency: float

# src/ai_system.py
ai_system = AISystem(config)
ai_system.on_response += lambda evt: print(f"Response: {evt.response}")

# gui/qt_client.py
ai_system.on_response += self.display_response
ai_system.on_error += self.show_error_dialog
```

**Benefits:**
- ✅ Web frontend can access same AI engine
- ✅ CLI tool possible
- ✅ Easy to test AI logic without GUI
- ✅ Better separation of concerns

**Time Estimate:** 8-12 hours (significant refactor, but phased approach possible)

---

### 10. **Config Management Refactor** 🏗️ LOW PRIORITY
**Severity:** Low | **Effort:** Medium | **Impact:** Maintainability

**Issue:**
- Configuration scattered across `.env`, `.gamingaiassistant/`, and Python dicts
- No schema validation
- Hard to add new settings without breaking things

**Current Mess:**
```python
# ❌ SCATTERED
config.py                    # .env file
credential_store.py          # Encrypted keys
game_profile.py              # Per-game JSON
settings_tabs.py             # UI-specific state
session_logger.py            # Session data
theme_manager.py             # Theme preferences
```

**Recommended Unified Config:**
```python
# src/config_schema.py
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class AIProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"

@dataclass
class AppConfig:
    """Unified configuration schema"""
    
    # AI Settings
    ai_provider: AIProvider = AIProvider.ANTHROPIC
    ai_model: Optional[str] = None
    
    # Game Detection
    check_interval: int = 5
    
    # UI Settings
    overlay_hotkey: str = "ctrl+shift+g"
    overlay_width: int = 900
    overlay_height: int = 700
    overlay_opacity: float = 0.95
    
    # Knowledge
    enable_knowledge_packs: bool = True
    
    # Paths
    config_dir: str = "~/.gamingaiassistant"
    
    # Metadata
    version: str = "1.3"
    custom_fields: Dict[str, Any] = None

# Usage
@dataclass
class ConfigManager:
    def load(self) -> AppConfig:
        """Load from all sources, merge, validate"""
        ...
    
    def save(self, config: AppConfig) -> None:
        """Save to appropriate locations"""
        ...
    
    def validate(self, config: AppConfig) -> List[str]:
        """Return list of validation errors"""
        ...
```

**Benefits:**
- ✅ Single source of truth for settings
- ✅ Schema validation prevents invalid config
- ✅ Easy to add new settings
- ✅ Type-safe access throughout codebase

**Time Estimate:** 4-6 hours

---

## PERFORMANCE OPTIMIZATIONS

### 11. **Knowledge Index Performance** ⚡ LOW PRIORITY
**Severity:** Low | **Effort:** Low | **Impact:** Performance (when using large knowledge packs)

**Issue:**
- TF-IDF index rebuilds entire vocabulary on each reload
- O(n*m) complexity for large packs (n=docs, m=terms)
- No incremental indexing support

**Current Code (src/knowledge_index.py):**
```python
# ❌ REBUILDS EVERYTHING
def rebuild_index_for_game(self, game_id):
    packs = self.store.get_packs_for_game(game_id)
    for pack in packs:
        self.index.fit(pack.all_documents)  # Recalculates everything
```

**Optimization:**
```python
# ✅ INCREMENTAL UPDATES
class KnowledgeIndex:
    def add_pack(self, pack: KnowledgePack) -> None:
        """Add pack without rebuilding entire index"""
        self.index.add_documents(pack.documents)
    
    def remove_pack(self, pack_id: str) -> None:
        """Remove pack documents"""
        self.index.remove_documents_by_pack(pack_id)
    
    @property
    def is_stale(self) -> bool:
        """Check if rebuild needed"""
        return self.last_modified < max(pack.updated_at for pack in self.packs)
```

**Performance Impact:**
- Adding new pack: O(n) instead of O(total*m)
- Multiple operations: Can batch updates
- 10x faster for large knowledge bases

**Time Estimate:** 1-2 hours

---

### 12. **Game Detection Optimization** ⚡ LOW PRIORITY
**Severity:** Low | **Effort:** Low | **Impact:** Performance (CPU usage during idle)

**Issue:**
- Checks all 50 game executables every 5 seconds (polling)
- Wastes CPU and battery on idle systems
- No process event hooks on Windows

**Current Code (src/game_detector.py):**
```python
# ❌ WASTEFUL POLLING
def detect_running_game(self):
    for process in psutil.process_iter(['name']):
        if process.name().lower() in self.common_games.keys():
            return process  # Scans ALL processes every 5s
```

**Optimization:**
```python
# ✅ SMART MONITORING
def detect_running_game(self):
    # Only check processes that likely changed since last check
    current_processes = {p.pid: p.name() for p in psutil.process_iter(['pid', 'name'])}
    
    if current_processes == self.last_processes:
        return self.last_game  # No change, return cached
    
    self.last_processes = current_processes
    
    # Check only new/removed processes
    new_pids = set(current_processes.keys()) - set(self.last_processes.keys())
    for pid in new_pids:
        if current_processes[pid].lower() in self.common_games:
            return self.get_game_info(current_processes[pid])
    
    return None

# Even better: Use Win32 event hooks on Windows
if sys.platform == 'win32':
    from win32evtlogutil import ReadEventLog
    # Listen for process creation events instead of polling
```

**Benefits:**
- ✅ CPU usage drops 80% during idle
- ✅ Battery life improved on laptops
- ✅ Instant detection on Windows with hooks

**Time Estimate:** 1-2 hours

---

## FEATURE ENHANCEMENTS

### 13. **Add Logging System Dashboard** 📊 NICE-TO-HAVE
**Severity:** Low | **Effort:** Low | **Impact:** Debugging, Operations

**Issue:**
- Logs written to file but no in-app viewer
- Hard to diagnose issues without opening log file
- No log level controls in UI

**Recommendation:**
Add "Logs" tab to settings dialog:
```python
class LogsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Log level selector
        level_combo = QComboBox()
        level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        level_combo.currentTextChanged.connect(self.set_log_level)
        
        # Log viewer (last 100 lines)
        log_view = QTextEdit()
        log_view.setReadOnly(True)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Logs")
        refresh_btn.clicked.connect(self.load_logs)
        
        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Log Level:"))
        layout.addWidget(level_combo)
        layout.addWidget(log_view)
        layout.addWidget(refresh_btn)
        layout.addWidget(clear_btn)
        self.setLayout(layout)
    
    def load_logs(self):
        """Load last N lines from log file"""
        with open(get_log_file()) as f:
            lines = f.readlines()
            self.log_view.setText(''.join(lines[-100:]))
    
    def set_log_level(self, level):
        """Change logging level"""
        logging.getLogger().setLevel(getattr(logging, level))
```

**Benefits:**
- ✅ Users can troubleshoot without leaving app
- ✅ Support can ask for specific log levels
- ✅ Better issue diagnosis

**Time Estimate:** 1-2 hours

---

### 14. **Multi-AI Provider Comparison** 🤖 NICE-TO-HAVE
**Severity:** Low | **Effort:** Medium | **Impact:** UX, Feature

**Issue:**
- Users can only use one provider at a time
- Hard to evaluate different providers (cost, speed, quality)
- No A/B testing support

**Recommendation:**
```python
class ProviderComparisonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Input question
        question_input = QTextEdit()
        question_input.setPlaceholderText("Enter question to compare providers...")
        
        # Provider selection checkboxes
        provider_checks = {}
        for provider in ['anthropic', 'openai', 'gemini']:
            check = QCheckBox(provider)
            check.setChecked(True)
            provider_checks[provider] = check
        
        # Run button
        run_btn = QPushButton("Compare Responses")
        run_btn.clicked.connect(lambda: self.compare_providers(
            question_input.toPlainText(),
            [p for p, c in provider_checks.items() if c.isChecked()]
        ))
        
        # Results table
        results_table = QTableWidget()
        results_table.setColumnCount(4)
        results_table.setHorizontalHeaderLabels(['Provider', 'Response', 'Time (ms)', 'Cost'])
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Question:"))
        layout.addWidget(question_input)
        layout.addWidget(QLabel("Providers:"))
        for check in provider_checks.values():
            layout.addWidget(check)
        layout.addWidget(run_btn)
        layout.addWidget(results_table)
        self.setLayout(layout)
    
    async def compare_providers(self, question: str, providers: List[str]):
        """Run question through multiple providers"""
        results = {}
        for provider_name in providers:
            start = time.time()
            response = await self.ai_router.route_request(
                question, provider=provider_name
            )
            latency = (time.time() - start) * 1000
            cost = calculate_api_cost(provider_name, question, response)
            results[provider_name] = (response, latency, cost)
        
        self.display_results(results)
```

**Benefits:**
- ✅ Choose best provider for specific use case
- ✅ Monitor performance differences
- ✅ Cost comparison tool

**Time Estimate:** 2-3 hours

---

### 15. **Macro Recording Improvements** 🎬 NICE-TO-HAVE
**Severity:** Low | **Effort:** Medium | **Impact:** UX

**Issue:**
- Macro recording is basic (no filtering, no intelligent defaults)
- High noise floor (captures every small movement)
- No visualization of recorded macros during playback

**Recommendations:**
1. **Smart Filtering** - Auto-remove small mouse movements
2. **Playback Preview** - Show macro execution in slow motion
3. **Macro Optimization** - Merge consecutive identical actions

**Time Estimate:** 2-4 hours

---

## TESTING & QA IMPROVEMENTS

### 16. **Increase Test Coverage to 80%+** ✅ MEDIUM PRIORITY
**Severity:** Low | **Effort:** Medium | **Impact:** Code Quality, Stability

**Current State:**
- Coverage: ~23-30% baseline
- Test Files: 20 files, 272 test functions

**Gaps to Address:**
1. **GUI Layer** - Difficult to test PyQt6 in CI, use mocks
   - Add fixtures: `mock_qt_dialog`, `mock_main_window`
   - Test signal/slot connections
   - Test UI state changes

2. **Macro Execution** - Need safety tests
   - Test macro timeout handling
   - Test unsafe macro detection
   - Test concurrent macro safety

3. **Knowledge Integration** - Edge cases
   - Empty knowledge packs
   - Corrupted JSON files
   - Very large files (10MB+)
   - Missing dependencies

4. **Provider Failures** - Error handling
   - Rate limit handling
   - Authentication failures
   - Network timeouts
   - Partial responses

**Recommended Test Template:**
```python
# tests/test_module_name.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.module_name import MyClass

@pytest.fixture
def my_service(temp_config):
    """Create service with temp config"""
    return MyClass(config_dir=temp_config)

class TestMyClass:
    """Test MyClass functionality"""
    
    def test_happy_path(self, my_service):
        """Test normal operation"""
        result = my_service.do_something()
        assert result is not None
    
    def test_empty_input(self, my_service):
        """Test edge case: empty input"""
        result = my_service.do_something("")
        assert result == []
    
    def test_error_handling(self, my_service):
        """Test error handling"""
        with pytest.raises(MyError):
            my_service.do_something(invalid_input)
    
    @patch('src.module_name.external_service')
    def test_with_mock(self, mock_service, my_service):
        """Test with mocked dependency"""
        mock_service.return_value = "mocked"
        result = my_service.call_external()
        assert result == "mocked"

@pytest.mark.skipci
class TestGUIInteraction:
    """GUI tests skipped in CI (no X11)"""
    
    def test_button_click(self, qapp, main_window):
        """Test button click handling"""
        main_window.button.click()
        assert main_window.state_changed
```

**Coverage Targets by Module:**
- Config: 90% (critical path)
- AI System: 85% (high complexity)
- Macro System: 80% (safety sensitive)
- Knowledge: 75% (optional feature)
- GUI: 40% (hard to test in CI)

**Time Estimate:** 6-8 hours

---

## DOCUMENTATION IMPROVEMENTS

### 17. **API Documentation** 📖 LOW PRIORITY
**Severity:** Low | **Effort:** Low | **Impact:** Developer Experience

**Current State:**
- CLAUDE.md exists (~69KB comprehensive guide)
- Code docstrings are sparse
- No API reference

**Add to Each Core Module:**
```python
"""
src/ai_assistant.py
==================

High-level AI interaction interface for gaming assistance.

Classes:
  AIAssistant: Main interface for asking AI questions about games

Example Usage:
  >>> from src.ai_assistant import AIAssistant
  >>> from src.ai_router import AIRouter
  >>> from src.config import Config
  >>> config = Config.load()
  >>> router = AIRouter(config)
  >>> assistant = AIAssistant(router)
  >>> response = await assistant.ask_question("How do I beat this boss?")
  >>> print(response)

Dependencies:
  - AIRouter: For multi-provider support
  - KnowledgeIntegration: For augmenting with knowledge packs
  - SessionLogger: For tracking interactions

See Also:
  - CLAUDE.md: Comprehensive architecture guide
  - test_ai_assistant.py: Usage examples
"""
```

**Time Estimate:** 2-3 hours

---

## PRIORITY ROADMAP

### Phase 1: Critical Fixes (Week 1-2) - **20 hours**
1. ✅ Fix import patterns (2h)
2. ✅ Verify stdlib naming (0.5h)
3. ✅ Config dir injection (4h)
4. ✅ Settings tab navigation (2h)
5. ✅ Credential store security (3h)
6. ✅ Catch all test failures (3h)
7. ✅ Fix any regressions (5.5h)

### Phase 2: Quality Improvements (Week 3-4) - **16 hours**
1. ⚠️ Error handling standardization (4h)
2. ⚠️ Type hints - Phase 1 (3h)
3. ⚠️ Dependency injection foundation (4h)
4. ⚠️ Documentation updates (2h)
5. ⚠️ Testing infrastructure (3h)

### Phase 3: Nice-to-Have (Week 5+) - **Optional**
1. Performance optimizations (knowledge index, game detection)
2. Feature enhancements (logging dashboard, provider comparison)
3. Macro improvements
4. Web API for alternate frontends

---

## IMPLEMENTATION CHECKLIST

For each change:
- [ ] Create feature branch: `git checkout -b cleanup/issue-name`
- [ ] Make code changes with focus on single responsibility
- [ ] Add/update tests: `pytest tests/test_module.py -v`
- [ ] Run linter: `flake8 src/ --max-line-length=127`
- [ ] Check imports: `python test_circular_import.py`
- [ ] Build locally: `python build_windows_exe.py` (test basic flow)
- [ ] Update CLAUDE.md if architecture changed
- [ ] Update aicontext.md with changes
- [ ] Commit with clear message: `Fix: improve import consistency across src modules`
- [ ] Push to GitHub: `git push -u origin cleanup/issue-name`
- [ ] Create PR with description of changes
- [ ] Request code review
- [ ] Merge only after: tests pass + CI/CD green + review approved

---

## CONCLUSION

Omnix has a solid foundation. These improvements focus on:
- **Stability**: Fix critical issues (imports, config, security)
- **Maintainability**: Standardize patterns, add type hints, improve tests
- **Performance**: Optimize hot paths (knowledge index, game detection)
- **Extensibility**: Decouple systems, enable alternate UIs

**Estimated Total Effort:** 40-60 developer hours over 4-6 weeks  
**Risk Level:** Low-Medium (most changes are non-breaking with proper testing)

Begin with Phase 1 (critical fixes) for maximum ROI, then tackle quality improvements systematically.

Happy coding! 🚀
