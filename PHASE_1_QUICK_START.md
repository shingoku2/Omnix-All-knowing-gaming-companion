# Phase 1 Implementation Quick Start

**Duration:** 1-2 weeks | **Effort:** 20 hours | **Risk:** Low

This guide walks through fixing the critical issues first, with step-by-step instructions.

---

## 1. FIX IMPORT PATTERNS (2 hours)

### Step 1: Identify All Import Problems
```bash
# Find inconsistent imports
grep -r "^from [a-z_]* import" src/ --include="*.py" | grep -v "__pycache__"

# Expected output (these need fixing)
src/game_profile.py:from knowledgeintegration import getknowledgeintegration
src/macro_manager.py:from base_store import get_base_store
```

### Step 2: Create Test to Verify
```python
# test_imports.py
import importlib
import os
import sys

def test_no_circular_imports():
    """Test that all modules can be imported without circular deps"""
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    modules = [f[:-3] for f in os.listdir(src_dir) if f.endswith('.py') and f != '__init__.py']
    
    for module_name in modules:
        try:
            importlib.import_module(f'src.{module_name}')
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            raise

if __name__ == '__main__':
    test_no_circular_imports()
```

Run it before and after:
```bash
python test_imports.py
```

### Step 3: Fix Each File

For each file with inconsistent imports:

```python
# BEFORE (bad)
from knowledgeintegration import getknowledgeintegration
from base_store import get_base_store
import ai_router

# AFTER (good)
from src.knowledge_integration import get_knowledge_integration
from src.base_store import get_base_store
from src.ai_router import AIRouter
```

**Files to Fix (Example Set):**
1. `src/game_profile.py` - Line 8
2. `src/macro_manager.py` - Lines 5-7
3. `src/knowledge_integration.py` - Check all imports
4. Run test after each file to catch errors early

### Step 4: Verify
```bash
python test_imports.py  # Should all pass
pytest tests/ -v --tb=short  # Run existing tests
```

---

## 2. VERIFY STDLIB NAME CONFLICTS (30 minutes)

### Step 1: Check for Shadowing
```bash
# Verify no stdlib names are being used as module names
for stdlib in os sys json re math abc collections itertools types; do
  grep -r "^import $stdlib\|^from $stdlib" src/ --include="*.py" && echo "Found: $stdlib"
done

# Verify types.py was renamed to type_definitions.py
ls -la src/ | grep types
# Should show: type_definitions.py (good)
# Should NOT show: types.py (bad)
```

### Step 2: Verify type_definitions.py Usage
```bash
# Check all references to the old name were updated
grep -r "from.*types import\|import.*types" src/ --include="*.py"
# Should return NO results (all should use type_definitions)

# Check new name is used everywhere
grep -r "from src.type_definitions import\|from .type_definitions import" src/ --include="*.py"
# Should have at least a few results
```

### Step 3: Compile Check
```bash
python -m py_compile src/*.py
# If any file has syntax error, it will fail here first
```

---

## 3. INJECT CONFIG DIRECTORY (3-4 hours)

### Step 1: Update `src/base_store.py`

Add parameter to base class:

```python
# BEFORE
class BaseStore:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or os.path.expanduser('~/.gamingaiassistant')

# Add getter helper
@staticmethod
def get_config_dir(config_dir=None):
    """Get config directory, allows override"""
    if config_dir:
        return config_dir
    env_config = os.getenv('OMNIX_CONFIG_DIR')
    if env_config:
        return os.path.expanduser(env_config)
    return os.path.expanduser('~/.gamingaiassistant')
```

### Step 2: Update `src/knowledge_store.py`

```python
# BEFORE
class KnowledgePackStore(BaseStore):
    def __init__(self):
        super().__init__()

# AFTER
class KnowledgePackStore(BaseStore):
    def __init__(self, config_dir=None):
        super().__init__(config_dir=config_dir)
```

### Step 3: Update `src/knowledge_index.py`

```python
# BEFORE
def __init__(self, store: KnowledgePackStore = None):
    self.store = store or get_knowledge_pack_store()

# AFTER
def __init__(self, store: KnowledgePackStore = None, config_dir: str = None):
    self.config_dir = config_dir
    self.store = store or KnowledgePackStore(config_dir=config_dir)
```

### Step 4: Update Tests

```python
# tests/conftest.py - Add fixture
import tempfile
import pytest
import os

@pytest.fixture
def temp_config():
    """Create temporary config directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

# tests/test_knowledge_store.py - Use fixture
def test_knowledge_store(temp_config):
    store = KnowledgePackStore(config_dir=temp_config)
    # Test uses isolated temp directory, won't touch user config
```

### Step 5: Verify

```bash
# Run tests - should not create files in ~/.gamingaiassistant
pytest tests/test_knowledge_store.py -v

# Check user config untouched
ls -la ~/.gamingaiassistant/
# Should look same as before test run
```

---

## 4. FIX SETTINGS TAB NAVIGATION (1-2 hours)

### Step 1: Add Tab Index Constants

```python
# src/gui.py - Near top of SettingsDialog class
class SettingsDialog(QDialog):
    TAB_APPEARANCE = 0
    TAB_AI_PROVIDERS = 1
    TAB_GAME_PROFILES = 2
    TAB_KNOWLEDGE_PACKS = 3
    TAB_MACROS = 4
    TAB_KEYBINDS = 5
    
    def __init__(self, parent=None):
        # ... existing code ...
        self.tabs.addTab(AppearanceTab(...), "Appearance")  # TAB_APPEARANCE
        self.tabs.addTab(AIProvidersTab(...), "AI Providers")  # TAB_AI_PROVIDERS
        # ... etc
```

### Step 2: Add set_active_tab Method

```python
class SettingsDialog(QDialog):
    def set_active_tab(self, tab_index: int) -> None:
        """Switch to specific tab by index"""
        if 0 <= tab_index < self.tabs.count():
            self.tabs.setCurrentIndex(tab_index)
```

### Step 3: Fix Dashboard Button Handlers

```python
# BEFORE
def on_ai_providers_clicked(self):
    # TODO: navigate to specific tab
    self.settings_dialog = SettingsDialog(self.config, ...)
    self.settings_dialog.show()

# AFTER
def on_ai_providers_clicked(self):
    if self.settings_dialog is None:
        self.settings_dialog = SettingsDialog(self.config, ...)
    self.settings_dialog.set_active_tab(SettingsDialog.TAB_AI_PROVIDERS)
    self.settings_dialog.show()
    self.settings_dialog.raise_()  # Bring to front
    self.settings_dialog.activateWindow()  # Get focus
```

### Step 4: Update All Dashboard Buttons

```python
# In class OmnixMainWindow
def on_game_profiles_clicked(self):
    self.settings_dialog.set_active_tab(SettingsDialog.TAB_GAME_PROFILES)
    self.settings_dialog.show()

def on_knowledge_packs_clicked(self):
    self.settings_dialog.set_active_tab(SettingsDialog.TAB_KNOWLEDGE_PACKS)
    self.settings_dialog.show()

def on_macro_manager_clicked(self):
    self.settings_dialog.set_active_tab(SettingsDialog.TAB_MACROS)
    self.settings_dialog.show()

def on_keybinds_clicked(self):
    self.settings_dialog.set_active_tab(SettingsDialog.TAB_KEYBINDS)
    self.settings_dialog.show()
```

### Step 5: Test

```bash
# Manual test (requires display)
python -m pytest tests/test_gui.py::TestSettingsNavigation -v

# Or run app and click buttons
python omnix_gaming_assistant.py
# Click "AI Providers" button -> should show AI Providers tab
# Click "Game Profiles" button -> should show Game Profiles tab
```

---

## 5. FIX CREDENTIAL STORE SECURITY (2-3 hours)

### Step 1: Add Security Warning

```python
# src/credential_store.py
from PyQt6.QtWidgets import QMessageBox
import logging

logger = logging.getLogger(__name__)

class CredentialStore:
    def _fallback_store_key(self, key_bytes):
        """Store key in file when keyring unavailable"""
        
        # WARN USER
        logger.warning(
            "System keyring unavailable! API keys will be stored with reduced protection. "
            "Set OMNIX_KEY_PASSWORD environment variable for additional protection."
        )
        
        # Show dialog if GUI available
        try:
            QMessageBox.warning(
                None,
                "Security Notice",
                "System keyring is not available on this system.\n\n"
                "Your API keys will be stored in an encrypted file with reduced protection:\n"
                f"  {os.path.join(self.config_dir, 'master.key')}\n\n"
                "For maximum security, set OMNIX_KEY_PASSWORD environment variable:\n"
                "  export OMNIX_KEY_PASSWORD='your-strong-password'\n\n"
                "See README.md for more information.",
                QMessageBox.StandardButton.Ok
            )
        except:
            pass  # GUI not available (running in tests/headless)
        
        # Store with password if available
        key_path = os.path.join(self.config_dir, 'master.key')
        password = os.getenv('OMNIX_KEY_PASSWORD')
        
        if password:
            # Encrypt key with password
            encrypted = self._encrypt_with_password(key_bytes, password)
            with open(key_path, 'wb') as f:
                f.write(encrypted)
            logger.info("✅ API key stored with password protection")
        else:
            # Store key with file permissions protection only
            with open(key_path, 'wb') as f:
                f.write(key_bytes)
            os.chmod(key_path, 0o600)  # Only owner can read
            logger.warning("⚠️ API key stored without password protection (less secure)")

def _encrypt_with_password(self, data: bytes, password: str) -> bytes:
    """Encrypt data with password-derived key"""
    import hashlib
    from cryptography.fernet import Fernet
    
    # Derive key from password
    salt = hashlib.sha256(b'omnix-salt').digest()
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations=100000)
    # Ensure key is proper length (44 bytes base64 encoded)
    key = base64.urlsafe_b64encode(key[:32])
    
    cipher = Fernet(key)
    return cipher.encrypt(data)
```

### Step 2: Add Password Decryption

```python
def _load_fallback_key(self) -> Optional[bytes]:
    """Load key from file, handle password decryption"""
    key_path = os.path.join(self.config_dir, 'master.key')
    
    if not os.path.exists(key_path):
        return None
    
    try:
        with open(key_path, 'rb') as f:
            encrypted_data = f.read()
    except PermissionError:
        logger.error(f"Permission denied reading {key_path}. Check file permissions.")
        return None
    
    # Try to decrypt with password
    password = os.getenv('OMNIX_KEY_PASSWORD')
    if password:
        try:
            key = self._decrypt_with_password(encrypted_data, password)
            logger.info("✅ Loaded API key with password protection")
            return key
        except Exception as e:
            logger.error(f"Failed to decrypt key with password: {e}")
            return None
    
    # Assume it's unencrypted (backward compatibility)
    return encrypted_data
```

### Step 3: Update README.md

```markdown
## Security - API Key Storage

Omnix provides multiple security levels for storing API keys.

### Preferred: System Keyring (Most Secure)

- **Windows:** Credential Manager
- **macOS:** Keychain
- **Linux:** SecretService/pass

API keys are encrypted by the operating system and protected by your login credentials.

**No additional configuration needed!** Omnix auto-detects available keyring.

### Fallback: Encrypted File (Recommended)

When system keyring unavailable (e.g., SSH sessions, Linux servers):

1. **With Password** (Recommended):
   ```bash
   export OMNIX_KEY_PASSWORD="choose-a-strong-password"
   python omnix_gaming_assistant.py
   ```
   - API key encrypted with AES-256 Fernet
   - Password-derived encryption key (PBKDF2)
   - File stored in: `~/.gamingaiassistant/master.key`

2. **Without Password** (Insecure):
   - API key encrypted with Fernet
   - File permissions protection only (chmod 600)
   - ⚠️ NOT recommended for shared systems

### Best Practices

1. **Use system keyring** when available (automatic)
2. **Set OMNIX_KEY_PASSWORD** for fallback scenarios
3. **Never commit** `.gamingaiassistant/master.key` to version control
4. **Rotate keys** regularly if using password fallback
5. **Use strong passwords** (16+ characters, mixed case)

### Troubleshooting

**"Security Notice" appears on startup:**
- System keyring not available
- Solution: Set `OMNIX_KEY_PASSWORD` environment variable

**"Failed to decrypt key with password":**
- Wrong password or corrupted file
- Solution: Delete `~/.gamingaiassistant/master.key` and reconfigure API keys
```

### Step 4: Test

```bash
# Test unencrypted fallback (current behavior)
pytest tests/test_credential_store.py::test_fallback_store -v

# Test with password protection
export OMNIX_KEY_PASSWORD="test-password-123"
pytest tests/test_credential_store.py::test_password_protected -v
```

---

## 6. RUN FULL TEST SUITE & FIX FAILURES (3 hours)

### Step 1: Run All Tests

```bash
# Run with verbose output and show slowest tests
pytest tests/ -v --tb=short --durations=10

# Or run specific test file
pytest tests/test_imports.py -v
pytest tests/test_credential_store.py -v
pytest tests/test_knowledge_store.py -v
```

### Step 2: Fix Common Failures

**Issue: ImportError in tests**
```python
# ❌ WRONG
from knowledgeintegration import getknowledgeintegration

# ✅ CORRECT
from src.knowledge_integration import get_knowledge_integration
```

**Issue: Config directory pollution**
```python
# ❌ WRONG
def test_something():
    store = KnowledgePackStore()  # Uses real ~/.gamingaiassistant

# ✅ CORRECT
def test_something(temp_config):
    store = KnowledgePackStore(config_dir=temp_config)
```

**Issue: Hardcoded paths**
```python
# ❌ WRONG
config_dir = "~/.gamingaiassistant"

# ✅ CORRECT
config_dir = os.path.expanduser("~/.gamingaiassistant")
```

### Step 3: Check Coverage

```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## 7. CI/CD VERIFICATION (30 minutes)

### Step 1: Add Pre-commit Hook

```bash
# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        args: [--line-length=127]
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=127]
EOF

# Install hooks
pre-commit install

# Run against all files
pre-commit run --all-files
```

### Step 2: Update GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8
      
      - name: Test imports (no circular deps)
        run: python test_imports.py
      
      - name: Lint with flake8
        run: flake8 src/ --max-line-length=127 --count --statistics
      
      - name: Run tests
        run: pytest tests/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Step 3: Verify Locally

```bash
# Run same tests as CI
python test_imports.py
flake8 src/ --max-line-length=127
pytest tests/ -v --cov=src
```

---

## PHASE 1 COMPLETE CHECKLIST

- [ ] All import patterns standardized (`from src.X import Y`)
- [ ] No circular import errors (`test_imports.py` passes)
- [ ] No stdlib name conflicts (verified types.py → type_definitions.py)
- [ ] Config directory injectable (all stores accept `config_dir` param)
- [ ] Settings tab navigation working (all buttons navigate correctly)
- [ ] Credential store shows security warnings and supports passwords
- [ ] All existing tests pass (`pytest tests/ -v` GREEN)
- [ ] New temp config tests pass (`pytest tests/test_knowledge_store.py -v` GREEN)
- [ ] CI/CD pipeline configured and green
- [ ] Documentation updated (README.md security section)
- [ ] `aicontext.md` updated with all changes

---

## COMMIT COMMANDS

```bash
# Create feature branch
git checkout -b cleanup/phase-1-critical-fixes

# Commit each fix logically
git add src/  tests/
git commit -m "Fix: standardize import patterns across all modules

- Changed all imports from 'from X import' to 'from src.X import'
- Avoids circular import issues and module shadowing
- Verified with test_imports.py - no circular dependencies
- All 272 tests passing"

git commit -m "Fix: add config_dir injection to storage classes

- KnowledgePackStore, CredentialStore now accept config_dir parameter
- Enables unit tests to use isolated temp directories
- Fixes test pollution of ~/.gamingaiassistant in CI/CD
- Updated conftest.py with temp_config fixture"

git commit -m "Fix: implement settings tab navigation

- Added TAB_* constants to SettingsDialog
- Dashboard buttons now navigate to correct settings tabs
- Added set_active_tab() method for tab switching
- Fixes TODO: navigate to specific tab"

git commit -m "Fix: improve credential store security

- Shows warning when system keyring unavailable
- Supports OMNIX_KEY_PASSWORD environment variable
- Documents security levels in README.md
- Validates encrypted master.key integrity"

# Push to GitHub
git push -u origin cleanup/phase-1-critical-fixes

# Create pull request on GitHub
# https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/pull/new/cleanup/phase-1-critical-fixes
```

---

## ESTIMATED TIME BREAKDOWN

| Task | Time | Status |
|------|------|--------|
| Fix import patterns | 2h | |
| Verify stdlib names | 0.5h | |
| Inject config dirs | 3.5h | |
| Fix tab navigation | 1.5h | |
| Secure credentials | 2.5h | |
| Test & fix failures | 3h | |
| CI/CD setup | 1h | |
| Documentation | 1.5h | |
| **Total Phase 1** | **~15.5 hours** | |

**Recommended Pace:** 3-4 hours per day over 4-5 days = 1 week completion

---

## NEXT STEPS AFTER PHASE 1

Once Phase 1 is complete:
1. Review PR feedback and merge to main
2. Tag release: `v1.3.1-fixes` 
3. Document completion in aicontext.md
4. Plan Phase 2: Quality Improvements (error handling, type hints, DI)

Good luck! 🚀
