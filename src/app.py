"""
myTigerTrail Web Application
Serves the 3D campus map interface and provides API access to the navigation agent.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import get_directions
import uvicorn

# Initialize FastAPI application
app = FastAPI(
    title="myTigerTrail - 3D Campus Navigation",
    description="Interactive 3D campus map with AI-powered navigation assistance",
    version="1.0.0"
)

# Add CORS middleware for web requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class DirectionRequest(BaseModel):
    """Request model for direction queries."""
    question: str


class DirectionResponse(BaseModel):
    """Response model for directions."""
    question: str
    directions: str
    success: bool


@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Serve the main 3D campus map interface.
    """
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>myTigerTrail - Campus Navigation</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>myTigerTrail</h1>
            <p class="error">3D Campus Map interface not found. Please ensure index.html exists in the src directory.</p>
            <p><a href="/docs">View API Documentation</a></p>
        </body>
        </html>
        """


@app.post("/api/directions", response_model=DirectionResponse)
async def request_directions(request: DirectionRequest):
    """
    Get campus navigation directions based on a student's question.

    Request body:
        - question: The student's direction question (e.g., "How do I get from the library to the science building?")

    Returns:
        - question: The original question
        - directions: Step-by-step directions based on the campus map
        - success: Whether the request was successful
    """
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty. Please ask a specific direction question."
            )

        # Get directions from the AI model based on the map
        directions = get_directions(request.question)

        if not directions:
            return DirectionResponse(
                question=request.question,
                directions="I apologize, but I couldn't generate directions for that request. Please try rephrasing your question.",
                success=False
            )

        return DirectionResponse(
            question=request.question,
            directions=directions,
            success=True
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Campus map files not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing direction request: {str(e)}"
        )


@app.get("/api/buildings")
async def get_buildings():
    """
    Get a list of all campus buildings for the 3D map interface.
    """
    # This could be expanded to return actual building data
    # For now, return a simple response
    return JSONResponse(
        status_code=200,
        content={
            "buildings": [
                {"name": "William Knox Holt Memorial Library", "id": "18"},
                {"name": "Robert E. Burns Tower", "id": "10"},
                {"name": "Conservatory of Music", "id": "14"},
                {"name": "Anderson Hall", "id": "27"},
                {"name": "Baun Hall", "id": "28"},
                {"name": "Khoury Hall", "id": "32"},
                {"name": "Finance Center", "id": "30"}
            ],
            "success": True
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "myTigerTrail-3D"}
    )


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon if it exists."""
    favicon_path = Path(__file__).parent / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    else:
        return JSONResponse(status_code=404, content={"error": "Favicon not found"})


if __name__ == "__main__":
    print("🐯 Starting myTigerTrail 3D Campus Navigation...")
    print("📍 Visit: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print()

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )