# Setup Guide - Gaming AI Assistant

This guide will walk you through setting up the Gaming AI Assistant step by step.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Ollama Setup](#ollama-setup)
4. [First Run](#first-run)
5. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum
- **Internet**: Required for AI API calls

### Recommended Requirements
- **Python**: 3.10 or higher
- **RAM**: 8GB or more
- **Internet**: Stable broadband connection

## Installation

### Step 1: Install Python

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Step 2: Clone or Download the Project

#### Using Git
```bash
git clone https://github.com/yourusername/gaming-ai-assistant.git
cd gaming-ai-assistant
```

#### Or Download ZIP
1. Download the ZIP file from GitHub
2. Extract to a folder
3. Open terminal/command prompt in that folder

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Platform-Specific Notes

**Linux**: You may need additional packages:
```bash
# For PyQt6
sudo apt-get install python3-pyqt6

# For psutil
sudo apt-get install python3-dev
```

**macOS**: If you encounter issues with PyQt6:
```bash
brew install pyqt6
```

## Ollama Setup

### Using Setup Wizard (Recommended)

The **Setup Wizard** now focuses on local Ollama configuration (no API keys):

1. Run `python main.py`
2. Confirm the Ollama host (default `http://localhost:11434`)
3. Choose a model (defaults to `llama3`; pulls it if missing)
4. Run the connection test to verify the daemon is reachable
5. Configuration is saved automatically to `.env`

### Manual Configuration (Optional)

If you prefer to configure manually or skip the Setup Wizard:

1) Install Ollama and pull a model:
```bash
ollama pull llama3
```

2) Create your env file:
```bash
cp .env.example .env
```

3) Edit `.env` with your host/model:
```env
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

#### Configure `.env` File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file:
   ```bash
   # Windows: notepad .env
   # macOS/Linux: nano .env
   ```

3. Set your Ollama host/model (no API key needed):
   ```env
   AI_PROVIDER=ollama
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

## First Run

### Step 1: Launch the Application

```bash
python main.py
```

The **Setup Wizard** will automatically appear on your first run to guide you through configuration:

1. **Confirm Ollama Host** - Defaults to `http://localhost:11434`
2. **Choose Model** - Defaults to `llama3`; pulls if not present
3. **Test Connection** - Verifies the Ollama daemon is reachable
4. **Save Configuration** - Settings are automatically saved to `.env`

### Step 2: Verify Installation (Optional)

If you prefer manual verification:

```bash
# Check Python version
python --version

# Check pip installation
pip list

# Test config file
python src/config.py
```

Expected output:
```
Configuration loaded successfully:
Config(provider=ollama, hotkey=ctrl+shift+g)
Ollama reachable: Yes
```

### Step 3: Test Game Detection (Optional)

```bash
# Run game detector test
python src/game_detector.py
```

### Step 4: Start Using the Assistant

Once the Setup Wizard completes:

```
============================================================
🎮 Gaming AI Assistant
============================================================

Loading configuration...
✓ Configuration loaded
  AI Provider: ollama
  Hotkey: ctrl+shift+g

Initializing game detector...
✓ Game detector ready

Initializing AI assistant...
✓ AI assistant ready

Starting GUI...
```

The application is ready to use! Launch a game and press `Ctrl+Shift+G` to open the assistant.

## Troubleshooting

### "No module named 'PyQt6'"

**Solution**:
```bash
pip install PyQt6
```

On Linux:
```bash
sudo apt-get install python3-pyqt6
```

### "Cannot reach Ollama" / "Connection refused"

**Solution**:
1. Ensure the Ollama daemon is running (`ollama serve` or service)
2. Verify `.env` has the right host (default `http://localhost:11434`)
3. Pull the model: `ollama pull llama3`
4. Use Settings → AI Providers → Test Connection inside the app

### "Game not detected"

**Solution**:
1. Make sure the game is actually running
2. Check the game is in the supported list
3. Try adding it via the GUI: **Settings -> Game Profiles -> Add Custom Profile**

Or verify `src/game_detector.py` has the game in `common_games`.

### GUI doesn't start on Linux

**Solution**:
```bash
# Install Qt dependencies
sudo apt-get install qt6-base-dev

# Or try with X11
export DISPLAY=:0
python main.py
```

### "ModuleNotFoundError: No module named 'src'"

**Solution**:
Make sure you're running from the project root directory:
```bash
cd /path/to/gaming-ai-assistant
python main.py
```

### Performance / Model Too Slow

**Solution**:
1. Switch to a lighter model (e.g., `mistral` instead of larger models)
2. Close other heavy processes to free CPU/GPU for Ollama
3. Reduce context length in settings if available

## Advanced Configuration

### Custom Hotkey

Edit `.env`:
```env
OVERLAY_HOTKEY=ctrl+alt+g  # or any key combination
```

### Adjust Detection Interval

```env
CHECK_INTERVAL=10  # Check for games every 10 seconds instead of 5
```

### Custom Game Wikis

Edit `src/info_scraper.py` and add to `wiki_urls`:
```python
self.wiki_urls = {
    "Your Game": "https://custom-wiki-url.com/wiki/",
}
```

## Getting Help

### Documentation
- Main README: [README.md](README.md)
- This guide: [SETUP.md](SETUP.md)

### Common Issues
1. Check the [Troubleshooting](#troubleshooting) section above
2. Search existing GitHub issues
3. Create a new issue with:
   - Your OS and Python version
   - Complete error message
   - Steps to reproduce

### Community
- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share tips

## Next Steps

Once everything is working:

1. **Launch a game** - The assistant will auto-detect it
2. **Try the quick actions** - Click "Get Tips" or "Game Overview"
3. **Ask questions** - Type in the chat box
4. **Customize** - Edit configuration files to your liking
5. **Add more games** - Expand the supported games list

Happy Gaming! 🎮
