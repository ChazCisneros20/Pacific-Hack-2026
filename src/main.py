from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from src.agent import get_directions
import uvicorn

# Initialize FastAPI application
app = FastAPI(
    title="myTigerTrail",
    description="Campus Navigation Assistant for UOP Stockton",
    version="1.0.0"
)


class DirectionRequest(BaseModel):
    """Request model for direction queries."""
    question: str


class DirectionResponse(BaseModel):
    """Response model for directions."""
    question: str
    directions: str


@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Serve the main landing page with information about the app.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>myTigerTrail - UOP Campus Navigation</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
                text-align: center;
            }
            
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            
            .description {
                color: #555;
                line-height: 1.8;
                margin-bottom: 30px;
                text-align: left;
            }
            
            .features {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin-bottom: 30px;
                border-radius: 6px;
                text-align: left;
            }
            
            .features h3 {
                color: #667eea;
                margin-bottom: 12px;
            }
            
            .features ul {
                list-style: none;
                padding-left: 0;
            }
            
            .features li {
                color: #666;
                margin-bottom: 8px;
                padding-left: 20px;
                position: relative;
            }
            
            .features li:before {
                content: "✓";
                color: #667eea;
                font-weight: bold;
                position: absolute;
                left: 0;
            }
            
            .usage-section {
                background: #f8f9fa;
                border-left: 4px solid #764ba2;
                padding: 20px;
                margin-bottom: 30px;
                border-radius: 6px;
                text-align: left;
            }
            
            .usage-section h3 {
                color: #764ba2;
                margin-bottom: 12px;
            }
            
            .code-block {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                overflow-x: auto;
                margin-bottom: 10px;
            }
            
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-size: 1em;
                cursor: pointer;
                text-decoration: none;
                transition: transform 0.2s, box-shadow 0.2s;
                margin-right: 10px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .btn-secondary {
                background: #6c757d;
            }
            
            .btn-secondary:hover {
                box-shadow: 0 10px 20px rgba(108, 117, 125, 0.3);
            }
            
            .button-group {
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ myTigerTrail</h1>
            <p class="subtitle">UOP Stockton Campus Navigation Assistant</p>
            
            <div class="description">
                <p>Welcome to myTigerTrail! We're here to help you navigate the University of the Pacific Stockton campus with ease. Whether you're looking for your first class, trying to find the library, or exploring campus landmarks, we've got you covered.</p>
            </div>
            
            <div class="features">
                <h3>What We Offer</h3>
                <ul>
                    <li>Real-time campus navigation based on our detailed map</li>
                    <li>Step-by-step directions from any location to another</li>
                    <li>Building and landmark identification</li>
                    <li>Friendly, helpful guidance 24/7</li>
                </ul>
            </div>
            
            <div class="usage-section">
                <h3>How to Use</h3>
                <p><strong>Send us a direction query via our API:</strong></p>
                <div class="code-block">
POST /directions<br/>
{<br/>
&nbsp;&nbsp;&nbsp;&nbsp;"question": "How do I get from the library to the science building?"<br/>
}
                </div>
                <p style="margin-top: 15px; color: #666; font-size: 0.95em;">
                    We'll analyze the campus map and provide you with clear, easy-to-follow directions!
                </p>
            </div>
            
            <div class="button-group">
                <a href="/docs" class="btn">📖 API Documentation</a>
                <a href="https://github.com" class="btn btn-secondary">💻 View on GitHub</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.post("/directions", response_model=DirectionResponse)
async def request_directions(request: DirectionRequest):
    """
    Get campus navigation directions based on a student's question.
    
    Request body:
        - question: The student's direction question (e.g., "How do I get from the library to the science building?")
    
    Returns:
        - question: The original question
        - directions: Step-by-step directions based on the campus map
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
            raise HTTPException(
                status_code=500,
                detail="Unable to generate directions. Please try again."
            )
        
        return DirectionResponse(
            question=request.question,
            directions=directions
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Campus map image not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing direction request: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "myTigerTrail"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
