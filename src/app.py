"""
myTigerTrail Web Application
Serves the 3D campus map interface and provides API access to the navigation agent.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
from agent import get_directions
from events import get_events
from library import get_library_status
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


@app.get("/api/events")
async def campus_events(refresh: bool = False):
    """
    Return live UOP campus events scraped from pacific.edu/calendar.
    Each event includes title, date, time, location, category, color, url,
    and coords {x, z} for 3D map placement (None if off-campus).
    Query param ?refresh=true forces a cache refresh.
    """
    try:
        events = get_events(force_refresh=refresh)
        on_campus  = [e for e in events if e["coords"] is not None]
        off_campus = [e for e in events if e["coords"] is None]
        return JSONResponse(status_code=200, content={
            "events":      events,
            "on_campus":   on_campus,
            "off_campus":  off_campus,
            "total":       len(events),
            "mapped":      len(on_campus),
            "success":     True,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@app.get("/api/library")
async def library_status(refresh: bool = False):
    """
    Return live library hours and study room availability.
    Sources: LibCal hours API + spaces availability grid.
    Query param ?refresh=true forces a cache refresh.
    """
    try:
        data = get_library_status(force_refresh=refresh)
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching library status: {str(e)}")


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


EVENTS_URL = "https://www.pacific.edu/calendar/all/all/all/all"
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text or "")
    text = re.sub(r"[\s_-]+", "-", text.strip().lower())
    return text.strip("-")


def parse_event_month(text: str) -> str | None:
    months = parse_event_months(text)
    return months[-1] if months else None


def parse_event_months(text: str) -> list[str]:
    if not text:
        return []
    pattern_parts = [re.escape(m) for m in MONTHS] + [re.escape(m[:3]) for m in MONTHS]
    pattern = rf"\b({'|'.join(pattern_parts)})\b"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    months = []
    abbreviations = {month[:3].lower(): month for month in MONTHS}
    for token in matches:
        token_lower = token.lower()
        if token_lower in abbreviations:
            month = abbreviations[token_lower]
        else:
            month = next((m for m in MONTHS if m.lower() == token_lower), None)
        if month and month not in months:
            months.append(month)
    return months


def resolve_event_url(url: str) -> str:
    if not url:
        return ""
    if url.startswith("http"):
        return url
    if url.startswith("/"):
        return f"https://www.pacific.edu{url}"
    return url


def extract_events_from_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    events = []
    seen = set()

    for candidate in soup.select(".event-row"):
        title_elem = candidate.select_one(".event-title a")
        if not title_elem:
            continue

        title = title_elem.get_text(" ", strip=True)
        if not title or title in seen:
            continue

        link = resolve_event_url(title_elem.get("href", ""))
        date_text = " ".join(
            part.get_text(" ", strip=True)
            for part in candidate.select(".event-time-range .field-content")
            if part.get_text(strip=True)
        ).strip()
        location_elem = candidate.select_one(".views-field-field-location .field-content")
        location_text = location_elem.get_text(" ", strip=True) if location_elem else ""

        month = parse_event_month(date_text) or parse_event_month(title) or parse_event_month(location_text)
        if not month:
            continue

        event_id = slugify(f"{month}-{title}-{date_text}")
        events.append({
            "id": event_id,
            "title": title,
            "date": date_text,
            "location": location_text,
            "link": link,
            "month": month,
        })
        seen.add(title)

    return events


def fallback_events() -> list[dict]:
    current_month = datetime.now().month
    return [
        {"id": "spring-open-house", "title": "Spring Campus Open House", "date": "April 12", "location": "William Knox Holt Memorial Library", "link": "https://www.pacific.edu/about-pacific/news-events/events", "month": "April"},
        {"id": "art-gallery-night", "title": "Reynolds Art Gallery Reception", "date": "May 3", "location": "Pacific Geosciences Center, Reynolds Art Gallery", "link": "https://www.pacific.edu/about-pacific/news-events/events", "month": "May"},
        {"id": "summer-tech-talk", "title": "Computer Science Guest Lecture", "date": "June 18", "location": "Benerd College", "link": "https://www.pacific.edu/about-pacific/news-events/events", "month": "June"},
        {"id": "fall-music-fest", "title": "Fall Music Festival", "date": "September 14", "location": "Faye Spanos Concert Hall", "link": "https://www.pacific.edu/about-pacific/news-events/events", "month": "September"},
        {"id": "winter-holiday-concert", "title": "Winter Campus Concert", "date": "December 8", "location": "Conservatory of Music", "link": "https://www.pacific.edu/about-pacific/news-events/events", "month": "December"},
    ]


def get_filtered_events(events: list[dict]) -> list[dict]:
    current_month = datetime.now().month
    valid_months = MONTHS[current_month - 1 :]
    return [event for event in events if event.get("month") in valid_months]


def group_events_by_month(events: list[dict]) -> dict:
    grouped = {}
    for event in events:
        month = event.get("month")
        if month:
            grouped.setdefault(month, []).append(event)
    return grouped


def fetch_uop_events() -> list[dict]:
    try:
        response = requests.get(
            EVENTS_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"},
            timeout=12
        )
        response.raise_for_status()
        events = extract_events_from_html(response.text)
        filtered = get_filtered_events(events)
        return filtered if filtered else fallback_events()
    except Exception:
        return fallback_events()


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