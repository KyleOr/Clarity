# 🌟 Clarity – Building Digital Confidence Online

The internet powers communication, services, and community — but it’s also filled with risks: phishing scams, fake ads, ransomware, and misinformation that erodes trust. These challenges are hardest on **vulnerable groups** like children, the elderly, minority communities, and people who are digitally inexperienced. Without the right tools, they are left more exposed to online manipulation and fraud.

**Clarity** is my response to the GovHack 2025 challenge: a browser extension built to **restore trust, enhance safety, and empower everyday users**. By combining real-time cyberthreat detection, misinformation analysis with government datasets, and an approachable AI assistant, I aim to make online participation more **secure, inclusive, and confident** for everyone.

---

## ✨ What Clarity Does

- **🛡️ Real-time Threat Detection** – Flags phishing attempts, malicious links, and scammy popups before they cause harm  
- **📊 Misinformation Analysis** – Cross-checks online claims against trusted government data (e.g., ABS housing statistics) to spot misleading narratives  
- **🤖 AI Chatbot Assistant ("Clarity")** – Provides simple, accessible explanations and guidance, powered locally with GGUF models and CUDA acceleration  
- **📈 Rich Context Integration** – Brings together insights from cyber and misinformation analysis in one clear view  
- **🌐 Browser Extension** – Runs seamlessly alongside everyday browsing, always ready when users need it  
- **🔒 Privacy-First** – No data leaves your machine; all processing is local for maximum trust and security  

---

## 💡 Why It Matters

Digital safety isn’t just a technical issue — it’s a human one. When people can’t trust what they see online, they withdraw from digital spaces, miss out on government services, and become more vulnerable to exploitation. My goal with Clarity is to **give users confidence back**: children learn what to avoid, seniors feel safer navigating the web, and communities can engage online without fear of scams or misinformation. By centering on **inclusivity, trust, and practical protection**, Clarity directly addresses the challenge of enabling secure and meaningful online participation.

---

## ⚙️ How It Works

### 1. Scan the Page
As you browse, Clarity scans the page in real-time, looking at text, links, ads, and popups.

### 2. Threat Detection
Using a library of patterns (phishing phrases, suspicious domains, scammy ad language), Clarity flags potential cyberthreats like fake login requests, malicious downloads, or misleading advertisements.

### 3. Misinformation Check (Government Data)
Claims in the page are compared against trusted government datasets. For example, if an article claims _“housing prices are falling”_, but official ABS data shows the opposite trend, Clarity highlights the contradiction.

### 4. AI-Powered Insights
All detected risks and mismatches are passed into the Clarity Assistant chatbot. Users can ask questions about the page in **plain English**, and the bot explains:
- Why something might be misleading or dangerous  
- How it connects to government data  
- Safer alternatives or official sources to consult  

### 5. User-Friendly Explanations
Instead of jargon-heavy warnings, Clarity translates findings into **simple, approachable language**, helping vulnerable users — children, seniors, or anyone less digitally experienced — to understand risks without fear or confusion.

---

### Example Flow
1. You open a news article.  
2. Clarity flags:  
   - ⚠ “Your account has been suspended” → *common phishing phrase*  
   - ⚠ “Housing prices are crashing” → *contradicts official ABS housing dataset*  
3. The chatbot explains:  
   > “This phrase is often used in phishing scams. Don’t click links like these. Also, according to the ABS, housing prices have actually increased in the last quarter. Here’s the official chart.”  


## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **CUDA-compatible GPU** (recommended for AI chatbot performance)
- **Visual Studio Build Tools** (for llama.cpp compilation)
- **Git** for cloning the repository

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/KyleOr/clarity.git
   cd safesearch
   ```

2. **Create and activate virtual environment**

   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the AI chatbot model**

   - Download a GGUF model (I recommend **OpenHermes 2.5 Mistral 7B**)
   - Place the `.gguf` file in `chatbot/models/`
   - The system will automatically detect and use the model

5. **Install browser extension**
   - Open Chrome/Edge and navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `extension/` folder

### 🎯 Starting Clarity

Launch all Clarity services with a single command:

```powershell
venv\Scripts\Activate.ps1; python scripts\start_clarity.py
```

This will start:

- **Analysis Server** (port 8888) - Misinformation detection and threat analysis
- **Chatbot Web Server** (port 5000) - AI assistant with CUDA acceleration

## 🔧 Configuration

### AI Model Setup

Clarity uses local GGUF models for privacy and performance. Here's how to set them up:

1. **Download a GGUF model** from Hugging Face:

   - **Recommended**: [OpenHermes-2.5-Mistral-7B-GGUF](https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF)
   - **Alternative**: Any compatible GGUF model (7B-13B parameters work well)

2. **Place the model file**:

   ```
   chatbot/
   └── models/
       └── your-model-name.gguf
   ```

3. **CUDA Acceleration** (optional but recommended):
   - Ensure CUDA toolkit is installed
   - The system will automatically detect and use GPU acceleration
   - Falls back to CPU if CUDA is not available

### Model Selection

The system automatically detects available models in the `chatbot/models/` directory. To use a specific model:

1. Place your `.gguf` file in `chatbot/models/`
2. The latest model will be automatically selected
3. Check `chatbot/controller.py` to verify model detection

### Browser Extension Configuration

The extension connects to:

- **Analysis API**: `http://localhost:8888`
- **Chatbot API**: `http://localhost:5000`

Ensure both servers are running before using the extension.

## 📁 Project Structure

```
clarity/
├── extension/             # Browser extension files
│   ├── manifest.json      # Extension manifest
│   ├── content.js         # Content script
│   ├── background.js      # Background script
│   ├── chatbot.js         # Chatbot interface
│   └── sidebar.css        # Extension styling
├── scripts/               # Analysis and utility scripts
│   ├── start_clarity.py   # Main startup script
│   ├── process_single_file.py
│   ├── threat_detector.py
│   └── compile_context.py
├── chatbot/               # AI chatbot system
│   ├── web_server.py      # Flask API server
│   ├── chatbot.py         # Core chatbot logic
│   ├── model_processor.py # GGUF model handling
│   └── prompt.txt         # AI personality definition
├── dataset/               # ABS data sources
└── venv/                  # Virtual environment (auto-generated)
```

## 🛠️ Development

### Adding New Analysis Features

1. Create analysis logic in `scripts/`
2. Add API endpoints in `scripts/start_clarity.py`
3. Update browser extension to call new endpoints

### Customizing the AI Assistant

1. **Modify personality**: Edit `chatbot/prompt.txt`
2. **Add new capabilities**: Extend `chatbot/chatbot.py`
3. **Change model**: Replace files in `chatbot/models/`

### Testing

- **Analysis API**: `curl http://localhost:8888/status`
- **Chatbot API**: `curl http://localhost:5000/health`
- **Controller test**: `python chatbot/controller.py`

## 🔍 API Endpoints

### Analysis Server (Port 8888)

| Endpoint                  | Method | Description                                |
| ------------------------- | ------ | ------------------------------------------ |
| `/status`                 | GET    | Server health check                        |
| `/analyze`                | POST   | Submit content for misinformation analysis |
| `/threat-analyze`         | POST   | Submit content for threat analysis         |
| `/results?id=<id>`        | GET    | Get misinformation analysis results        |
| `/threat-results?id=<id>` | GET    | Get threat analysis results                |

### Chatbot Server (Port 5000)

| Endpoint         | Method | Description                      |
| ---------------- | ------ | -------------------------------- |
| `/health`        | GET    | Chatbot health check             |
| `/chat`          | POST   | Send message to AI assistant     |
| `/analyze`       | POST   | Analyze content with AI insights |
| `/context/<url>` | GET    | Get context data for URL         |
| `/status`        | GET    | Model and system status          |

## 🎨 Browser Extension Usage

1. **Install** the extension from `extension/` folder
2. **Navigate** to any webpage
3. **Click** the Clarity icon or use the sidebar
4. **Analyze** content for misinformation and threats
5. **Chat** with the AI assistant for insights and explanations

### Extension Features

- **Automatic Content Analysis** - Scans pages for suspicious content
- **Interactive Sidebar** - Clean, expandable interface
- **Real-time Chat** - Instant AI responses with rich context
- **Security Indicators** - Visual warnings for detected threats
- **Educational Tips** - Learn about digital safety best practices

## 🔒 Privacy & Security

- **Local Processing** - All AI processing happens on your machine
- **No Data Collection** - No personal data sent to external servers
- **Open Source** - Full transparency in code and functionality
- **HTTPS Only** - Secure connections for all web requests

## 📊 Data Sources

Clarity uses official Australian data sources for fact-checking:

- **Australian Bureau of Statistics (ABS)**
- **Government datasets and publications**
- **Verified news sources and academic papers**

## ⚙️ System Requirements

### Minimum Requirements

- **OS**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: 8GB (16GB recommended for AI chatbot)
- **Storage**: 5GB free space (including model files)
- **Python**: 3.8 or higher

### Recommended for AI Features

- **GPU**: CUDA-compatible NVIDIA GPU with 6GB+ VRAM
- **RAM**: 16GB+ for optimal model performance
- **CPU**: Multi-core processor (8+ cores recommended)

## 🚨 Troubleshooting

### Common Issues

**Extension not connecting:**

- Verify both servers are running (`start_clarity.py`)
- Check firewall settings for ports 5000 and 8888

**AI chatbot errors:**

- Ensure GGUF model is in `chatbot/models/`
- Check CUDA installation if using GPU acceleration
- Run `python chatbot/controller.py` to diagnose

**Analysis not working:**

- Check `scripts/` dependencies are installed
- Verify ABS dataset files are present
- Review server logs for specific errors

### Getting Help

1. Check the **console logs** in browser developer tools
2. Review **server output** when running `start_clarity.py`
3. Run **diagnostic tests** in `chatbot/controller.py`

## 🙏 Acknowledgments

- **llama.cpp** - Efficient LLM inference engine
- **Australian Bureau of Statistics** - Official data sources
- **OpenHermes models** - High-quality language model
- **Chrome Extensions API** - Browser integration platform

---

**Protecting you from scams (and bad headlines)**
