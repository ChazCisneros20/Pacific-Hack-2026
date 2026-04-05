"""
Library hours and study room availability for University of the Pacific.
Data sourced from LibCal (Springshare) — no API key required.
"""

import time
import requests
from datetime import datetime, timedelta

HOURS_URL = "https://pacific.libcal.com/api_hours_today.php?iid=1171&lid=0&format=json"
SPACES_URL = "https://pacific.libcal.com/spaces/availability/grid"
SPACES_LID  = 15370
TOTAL_ROOMS = 22

CACHE_TTL = 300  # 5-minute cache (rooms change fast)
_cache = {"data": None, "ts": 0}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://pacific.libcal.com/spaces",
}


def _fetch_hours() -> dict:
    """Fetch today's hours for all library locations."""
    try:
        r = requests.get(HOURS_URL, timeout=8)
        r.raise_for_status()
        locations = r.json().get("locations", [])
        # Focus on main Stockton library (lid 886)
        main = next((l for l in locations if l["lid"] == 886), None)
        if not main:
            main = locations[0] if locations else {}

        hours_str = ""
        times = main.get("times", {})
        if times.get("status") == "open":
            hours_list = times.get("hours", [])
            if hours_list:
                h = hours_list[0]
                hours_str = f"{h.get('from','')} – {h.get('to','')}"
        elif times.get("status") == "text":
            hours_str = times.get("text", "")

        return {
            "open": bool(times.get("currently_open")),
            "status": times.get("status", "unknown"),
            "hours": hours_str,
            "name": main.get("name", "Library & Learning Center"),
        }
    except Exception as e:
        return {"open": None, "status": "unknown", "hours": "", "name": "Library", "error": str(e)}


def _fetch_rooms() -> dict:
    """Fetch study room availability for the next booking window."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        r = requests.post(
            SPACES_URL,
            headers=HEADERS,
            data={
                "lid": SPACES_LID,
                "gid": 0,
                "eid": -1,
                "seat": 0,
                "seatId": 0,
                "zone": 0,
                "start": today,
                "end": tomorrow,
                "pageIndex": 0,
                "pageSize": TOTAL_ROOMS,
            },
            timeout=8,
        )
        r.raise_for_status()
        slots = r.json().get("slots", [])

        now = datetime.now()
        # Round up to next 30-min boundary
        minutes = now.minute
        if minutes < 30:
            next_slot = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_slot = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        next_slot_str = next_slot.strftime("%Y-%m-%d %H:%M")

        # Find slots for the next time window
        window_slots = [s for s in slots if s["start"][:16] == next_slot_str]

        if not window_slots:
            # Fall back to any upcoming slot
            upcoming = sorted([s for s in slots if s["start"] >= now.strftime("%Y-%m-%d %H:%M")],
                              key=lambda s: s["start"])
            if upcoming:
                first_time = upcoming[0]["start"][:16]
                window_slots = [s for s in upcoming if s["start"][:16] == first_time]

        total_in_window = len(set(s["itemId"] for s in window_slots))
        booked = len([s for s in window_slots if s.get("className", "")])
        available = total_in_window - booked if total_in_window else 0

        # If no window slots found, count all unique rooms and assume available
        if not window_slots:
            all_rooms = len(set(s["itemId"] for s in slots))
            return {
                "total": all_rooms or TOTAL_ROOMS,
                "available": None,  # Unknown right now
                "booked": None,
                "next_slot": None,
            }

        return {
            "total": TOTAL_ROOMS,
            "available": available,
            "booked": booked,
            "next_slot": next_slot_str,
        }
    except Exception as e:
        return {"total": TOTAL_ROOMS, "available": None, "booked": None, "next_slot": None, "error": str(e)}


def get_library_status(force_refresh: bool = False) -> dict:
    """Return combined library hours + room availability. Cached for 5 minutes."""
    now = time.time()
    if not force_refresh and _cache["data"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["data"]

    hours = _fetch_hours()
    rooms = _fetch_rooms()

    result = {
        "hours": hours,
        "rooms": rooms,
        "success": True,
        "cached_at": datetime.now().isoformat(),
    }
    _cache["data"] = result
    _cache["ts"] = now
    return result
