# myTigerTrail - Campus Navigation Assistant

An intelligent campus navigation application for the University of the Pacific Stockton campus. This AI-powered assistant helps students navigate campus by analyzing a detailed map and providing step-by-step directions based on natural language questions.

## Features

- 🗺️ **AI-Powered Navigation**: Uses Ollama with the Gemma3 LLM to analyze campus maps
- ❓ **Natural Language Queries**: Students ask direction questions in plain English
- 📍 **Visual Map Analysis**: Leverages the actual campus map image for accurate directions
- 🌐 **Web API**: FastAPI-based REST API for easy integration
- 🎨 **Interactive UI**: Welcoming landing page for students

## Setup

### 1. Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running locally
- The Gemma3 model pulled: `ollama pull gemma3:latest`

### 2. Environment Setup

Run the setup script to create a virtual environment and install dependencies:

**On Windows (PowerShell):**
```powershell
.\scripts\setup_env.ps1
```

**On macOS/Linux (Bash):**
```bash
./scripts/setup_env.sh
```

This will create a `.venv` virtual environment and install all required packages.

### 3. Activate the Virtual Environment

After setup, activate the virtual environment:

**On Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**On macOS/Linux (Bash):**
```bash
source .venv/bin/activate
```

### 4. Pull the AI Model

Ensure Ollama is running and pull the Gemma3 model:

```bash
ollama pull gemma3:latest
```

## Usage

### Start the Web Application

After setting up the environment, you can run the application using the provided scripts:

**On Windows (PowerShell):**
```powershell
.\run.ps1
```

**On macOS/Linux (Bash):**
```bash
./run.sh
```

Alternatively, manually activate the virtual environment and run:

1. Activate the virtual environment:

   **On Windows (PowerShell):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **On macOS/Linux (Bash):**
   ```bash
   source .venv/bin/activate
   ```

2. Run the app:

   ```bash
   cd src
   python app.py
   ```

Then visit:
- **3D Campus Map**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features

### 3D Campus Map Interface
- **Interactive 3D Campus**: Explore the University of the Pacific Stockton campus in 3D
- **Building Information**: Click on buildings to see details and information
- **Search Functionality**: Search for specific buildings and locations
- **AI Navigation Panel**: Ask myTigerTrail AI for directions using natural language
- **Real-time Responses**: Get step-by-step directions based on the actual campus map

### AI-Powered Navigation
- **Dual Data Sources**: Uses both visual map analysis and PDF text context
- **Natural Language Queries**: Ask questions like "How do I get from the library to the science building?"
- **Contextual Responses**: AI considers building locations, pathways, and landmarks
- **Multiple Access Methods**: Web interface, API, or command line

### Option 2: API-Only Server

Run just the FastAPI server without the 3D interface:

```bash
python -m uvicorn src.main:app --reload
```

### Option 3: Command Line Agent

Use the agent directly from command line:

```bash
python src/agent.py "How do I get from the library to the science building?"
```

This will demonstrate how to call the `get_directions()` function directly.

## Project Structure

```
Pacific-Hack-2026/
├── src/
│   ├── __init__.py
│   ├── agent.py              # Core navigation logic with LLM integration
│   ├── main.py               # FastAPI API-only server
│   ├── app.py                # Full web app with 3D interface
│   ├── index.html            # 3D campus map interface
│   ├── pacific_map.png       # Campus map image for visual analysis
│   └── Pacific-Stk-CampusMap.pdf  # Campus map PDF for text context
├── scripts/
│   ├── setup_env.ps1         # Windows environment setup
│   └── setup_env.sh          # macOS/Linux environment setup
├── requirements.txt          # Python dependencies
├── example_usage.py          # Example usage script
└── README.md                 # This file
```

## How It Works

1. **Dual Data Sources**: The application uses both `src/pacific_map.png` (visual map) and `src/Pacific-Stk-CampusMap.pdf` (text context)
2. **Text Extraction**: Extracts detailed text content from the PDF for enhanced context about campus locations
3. **User Query**: Students submit direction questions (e.g., "How do I get from the library to the engineering building?")
4. **LLM Analysis**: Ollama's Gemma3 model analyzes both the map image and extracted text context
5. **Direction Generation**: The model provides detailed, step-by-step directions based on visual and textual information
6. **Response**: Clear directions are returned to the student

## API Endpoints

### GET /
Serve the 3D campus map interface with myTigerTrail navigation.

### POST /api/directions
Get campus navigation directions from the AI agent.

**Request:**
```json
{
  "question": "How do I get from the library to the science building?"
}
```

**Response:**
```json
{
  "question": "How do I get from the library to the science building?",
  "directions": "From the library, head east across the central quad...",
  "success": true
}
```

### GET /api/buildings
Get a list of campus buildings for the 3D interface.

### GET /health
Health check endpoint.

## Requirements

See [requirements.txt](requirements.txt) for the full list of dependencies:
- FastAPI 0.99.0
- Uvicorn 0.22.0
- Ollama Python client
- Python utilities for development (pytest, black, isort, flake8)

## Troubleshooting

### "Campus map image not found"
- Ensure `pacific_map.png` exists in the `src/` directory

### "PDF context not available"
- The PDF text extraction is optional - the app will still work with just the image
- If you want enhanced context, ensure `Pacific-Stk-CampusMap.pdf` exists in the `src/` directory

### Ollama connection errors
- Make sure Ollama is running: `ollama serve`
- Verify the model is downloaded: `ollama pull gemma3:latest`

### Slow responses
- First request may take longer while the model loads into memory
- Subsequent requests should be faster

## Contributing

Improvements and suggestions are welcome! Areas for enhancement:
- Add support for multiple campus maps
- Implement building search functionality
- Add estimated walk time calculations
- Create a mobile-friendly frontend

## License

This project was created for the Pacific Hack 2026 hackathon.

---

**Enjoy navigating campus with myTigerTrail! 🐯**
