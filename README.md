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

Run the platform-appropriate setup script to create a virtual environment and install dependencies:

- **Windows PowerShell**: `scripts/setup_env.ps1`
- **macOS / Linux**: `scripts/setup_env.sh`

### 3. Activate Virtual Environment

- **Windows PowerShell**: `.\.venv\Scripts\Activate.ps1`
- **macOS / Linux**: `source .venv/bin/activate`

## Usage

### Option 1: Run the Web Server

Start the FastAPI development server:

```bash
python -m uvicorn src.main:app --reload
```

Then visit:
- **Home Page**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Option 2: Use the API Directly

Make a POST request to the `/directions` endpoint:

```bash
curl -X POST "http://localhost:8000/directions" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I get from the library to the science building?"
  }'
```

### Option 3: Run the Example Script

Use the included example script for local testing without the web server:

```bash
python example_usage.py
```

This will demonstrate how to call the `get_directions()` function directly.

## Project Structure

```
Pacific-Hack-2026/
├── src/
│   ├── __init__.py
│   ├── agent.py              # Core navigation logic with LLM integration
│   ├── main.py               # FastAPI web application
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
Home page with welcome message and API information.

### POST /directions
Get campus navigation directions.

**Request:**
```json
{
  "question": "How do I get from the parking lot to the science building?"
}
```

**Response:**
```json
{
  "question": "How do I get from the parking lot to the science building?",
  "directions": "From the parking lot, head north toward the main campus entrance..."
}
```

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
