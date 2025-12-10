# Gaming AI Assistant - Windows Release

**Your AI Gaming Companion** 🎮

Automatically detects your game and provides real-time AI assistance using Ollama (local AI).

---

## 📥 Installation (For Users)

### Prerequisites

1. **Install Ollama** (Required for AI)
   - Download from: https://ollama.com/download
   - Install and run it
   - Open Command Prompt and run: `ollama pull llama3`

### Run the App

1. **Extract the zip file**
   - Extract `GamingAIAssistant.zip` to any folder

2. **Run the application**
   - Double-click `GamingAIAssistant.exe`
   - The Setup Wizard will appear automatically on first run

3. **Complete Setup Wizard**
   - Confirm Ollama host (default `http://localhost:11434`)
   - Choose your model (e.g., `llama3`)
   - No API keys required!

4. **Play your game**
   - Launch any supported game
   - Press **Ctrl+Shift+G** to open the AI assistant

---

## 🎮 Supported Games (37+)

**MOBAs & Shooters:**
- League of Legends
- VALORANT
- Dota 2
- Counter-Strike 2
- Overwatch
- Apex Legends
- Fortnite

**RPGs:**
- Elden Ring
- Dark Souls 3
- Skyrim Special Edition
- The Witcher 3
- Cyberpunk 2077
- Fallout 4

**MMOs:**
- World of Warcraft
- Final Fantasy XIV
- Elder Scrolls Online
- Guild Wars 2

**Others:**
- Minecraft
- Rocket League
- Grand Theft Auto V
- Red Dead Redemption 2
- Palworld
- Helldivers 2

...and more!

---

## 🚀 How to Use

1. **Launch the app** - Double-click `GamingAIAssistant.exe`

2. **Start your game** - The app auto-detects when you launch a supported game

3. **Press Ctrl+Shift+G** - Opens the AI assistant overlay

4. **Ask questions** like:
   - "What are the best beginner tips?"
   - "How do I beat this boss?"
   - "What's the current meta?"
   - "Explain this game mechanic"
   - "Best character builds?"

5. **Get instant AI responses** from your local AI!

---

## ⚙️ Features

✅ **Auto Game Detection** - Automatically knows what you're playing
✅ **Real-Time AI Assistance** - Powered by local Ollama AI
✅ **Game-Specific Knowledge** - Context-aware responses
✅ **Web Scraping** - Pulls info from wikis and forums
✅ **Dark Theme GUI** - Easy on the eyes
✅ **System Tray** - Runs in background
✅ **Hotkey Access** - Ctrl+Shift+G anytime
✅ **Conversation History** - Remembers context
✅ **Privacy First** - All AI processing runs locally

---

## 🔧 Requirements

- **Windows 10 or 11**
- **Ollama** installed and running
- **4GB+ RAM** (8GB+ recommended for AI models)

---

## 📁 File Structure

```
GamingAIAssistant/
├── GamingAIAssistant.exe    # Main application
├── START_HERE.txt            # Quick start guide
├── README.md                 # Full documentation
├── SETUP.md                  # Detailed setup guide
└── [library files]           # Python dependencies
```

---

## 🐛 Troubleshooting

### App won't start
- Check if antivirus blocked it
- Run as Administrator
- Check that Setup Wizard completed successfully

### "Cannot connect to Ollama"
- Ensure Ollama app is running in the system tray
- Run `ollama list` in command prompt to verify models are installed
- Check settings in the app

### Game not detected
- Check if game is in the supported list
- Game must be running
- Try restarting the app

### AI not responding
- Verify Ollama is running
- Try asking a different question
- Check if your PC has enough free RAM

### Hotkey not working
- Check if another app uses Ctrl+Shift+G
- Try clicking the system tray icon instead
- Restart the app

---

## 🔒 Privacy & Security

- **Local AI**: All processing happens on your machine
- **No data is sent** to the cloud
- **Conversation history** is stored locally
- **No telemetry or tracking**
- **Open source** - check the code on GitHub

---

## 🎯 Tips for Best Experience

1. **Be specific** in your questions
   - Good: "What are the best ADC champions in League?"
   - Better: "What are the top 3 ADC champions for beginners in current meta?"

2. **Provide context** when needed
   - "I'm playing Elden Ring and stuck at Margit, any tips?"

3. **Use follow-up questions**
   - The AI remembers conversation context

4. **Ask for builds**
   - "Show me a tanky build for Skyrim"

5. **Request strategies**
   - "How do I farm efficiently in Minecraft?"

---

## 🔄 Updates

To check for updates:
1. Visit the GitHub repository
2. Download the latest release
3. Replace the old files with new ones

---

## 📝 License

MIT License - Free to use and modify

---

## 🙏 Credits

- **AI Provider**: Ollama (Local LLMs)
- **GUI Framework**: PyQt6
- **Game Detection**: psutil
- **Web Scraping**: BeautifulSoup4

---

## 📧 Support

For issues or questions:
- Check TROUBLESHOOTING section above
- Review SETUP.md for detailed setup
- Visit the GitHub repository for updates

---

## 🎮 Happy Gaming!

Enjoy your AI-powered gaming companion!

Press **Ctrl+Shift+G** anytime in-game for instant assistance.

---

**Version**: 2.0.0
**Built with**: Python, PyQt6, Ollama
**Status**: Production Ready ✅