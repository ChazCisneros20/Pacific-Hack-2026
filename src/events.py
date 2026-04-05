"""
Campus event scraper for University of the Pacific calendar.
Scrapes https://www.pacific.edu/calendar and maps locations to 3D coords.
"""

import time
import requests
from bs4 import BeautifulSoup

CALENDAR_URL = "https://www.pacific.edu/calendar/all/all/all/all"
CACHE_TTL = 1800  # 30 minutes
_cache = {"data": None, "ts": 0}

# Maps lowercase location substrings → 3D map coordinates + display name
LOCATION_MAP = {
    # ── Central Campus ──
    "burns tower":           {"x": 31,  "z": 7,   "name": "Robert E. Burns Tower",               "num": "10"},
    "robert e burns":        {"x": 31,  "z": 7,   "name": "Robert E. Burns Tower",               "num": "10"},
    "buck memorial":         {"x": 24,  "z": 10,  "name": "Buck Memorial Hall",                  "num": "12"},
    "conservatory":          {"x": 29,  "z": 14,  "name": "Conservatory of Music",               "num": "14"},
    "faye spanos concert":   {"x": 29,  "z": 14,  "name": "Faye Spanos Concert Hall",            "num": "14"},
    "rehearsal hall":        {"x": 24,  "z": 15,  "name": "Rehearsal Hall",                      "num": "15"},
    "recital hall":          {"x": 21,  "z": 12,  "name": "Recital Hall",                        "num": "16"},
    "holt memorial library": {"x": 18,  "z": 10,  "name": "William Knox Holt Memorial Library",  "num": "18"},
    "library":               {"x": 18,  "z": 10,  "name": "William Knox Holt Memorial Library",  "num": "18"},
    "anderson hall":         {"x": 12,  "z": 3,   "name": "Anderson Hall",                       "num": "27"},
    "baun hall":             {"x": 9,   "z": 5,   "name": "Baun Hall",                           "num": "28"},
    "hydraulics":            {"x": 6,   "z": 3,   "name": "Hydraulics Laboratory",               "num": "29"},
    "finance center":        {"x": 4,   "z": 3,   "name": "Finance Center / West Memorial Hall", "num": "30"},
    "west memorial":         {"x": 4,   "z": 3,   "name": "Finance Center / West Memorial Hall", "num": "30"},
    "southwest hall":        {"x": 4,   "z": 6,   "name": "Southwest Hall",                      "num": "31"},
    "khoury hall":           {"x": 7,   "z": 6.5, "name": "Khoury Hall",                         "num": "32"},
    "human resources":       {"x": 10,  "z": 7,   "name": "Human Resources",                     "num": "33"},
    "chambers technology":   {"x": 10,  "z": 10,  "name": "John T. Chambers Technology Center",  "num": "34"},
    "technology center":     {"x": 10,  "z": 10,  "name": "John T. Chambers Technology Center",  "num": "34"},
    "tower view":            {"x": 24,  "z": 18,  "name": "Tower View Apartments",               "num": "35"},
    "pacific house":         {"x": 34,  "z": -6,  "name": "Pacific House",                       "num": "1"},
    "phi delta chi":         {"x": 34,  "z": 2,   "name": "Phi Delta Chi",                       "num": "2"},
    "mcconchie":             {"x": 34,  "z": 8,   "name": "McConchie Hall",                      "num": "7"},
    "kappa psi":             {"x": 34,  "z": 14,  "name": "Kappa Psi",                           "num": "8"},
    "weber hall":            {"x": 19,  "z": -2,  "name": "Eberhardt School of Business",        "num": "23"},
    "eberhardt":             {"x": 19,  "z": -2,  "name": "Eberhardt School of Business",        "num": "23"},
    "morris chapel":         {"x": 22,  "z": -4,  "name": "Morris Chapel",                       "num": "40"},
    "sears hall":            {"x": 22,  "z": -4,  "name": "Sears Hall / Colliver Hall",          "num": "40"},
    "colliver":              {"x": 22,  "z": -4,  "name": "Colliver Hall",                       "num": "40"},
    "knoles hall":           {"x": 15,  "z": 3,   "name": "Knoles Hall",                         "num": "24"},
    "derosa university":     {"x": 8,   "z": 0,   "name": "DeRosa University Center",            "num": "60"},
    "university center":     {"x": 8,   "z": 0,   "name": "DeRosa University Center",            "num": "60"},
    "the lair":              {"x": 8,   "z": 0,   "name": "The Lair (DeRosa Center)",            "num": "60"},
    "mccaffrey center":      {"x": 8,   "z": 0,   "name": "McCaffrey Center",                    "num": "60"},
    "mccaffrey grove":       {"x": 8,   "z": 0,   "name": "McCaffrey Grove",                     "num": "60"},
    "center for identity":   {"x": 8,   "z": 0,   "name": "Center for Identity and Inclusion",   "num": "60"},
    "baun fitness":          {"x": -2,  "z": -4,  "name": "Baun Fitness Center",                 "num": "61"},
    "bannister":             {"x": -2,  "z": -8,  "name": "Bannister Hall",                      "num": "62"},
    "owen hall":             {"x": 2,   "z": -8,  "name": "Owen Hall",                           "num": "63"},
    "main gymnasium":        {"x": 2,   "z": 2,   "name": "Main Gymnasium",                      "num": "64"},
    "wendell phillips":      {"x": -4,  "z": 2,   "name": "Wendell Phillips Center",             "num": "68"},
    "college of the pacific":{"x": -4,  "z": 2,   "name": "College of the Pacific",             "num": "68"},
    "john ballantyne":       {"x": -6,  "z": -2,  "name": "John Ballantyne Hall",                "num": "70"},
    "george wilson":         {"x": -6,  "z": 2,   "name": "George Wilson Hall",                  "num": "71"},
    "international studies": {"x": -6,  "z": 2,   "name": "School of International Studies",    "num": "71"},
    "jessie ballantyne":     {"x": -10, "z": -2,  "name": "Jessie Ballantyne Hall",              "num": "72"},
    "bechtel":               {"x": -5,  "z": 6,   "name": "Bechtel International Center",        "num": "73"},
    "callison":              {"x": -8,  "z": 5,   "name": "Callison Hall",                       "num": "77"},
    "elbert covell":         {"x": -8,  "z": 10,  "name": "Elbert Covell Hall",                  "num": "78"},
    "raymond great hall":    {"x": -8,  "z": 10,  "name": "Raymond Great Hall",                  "num": "78"},
    "grace covell":          {"x": 20,  "z": -5,  "name": "Grace Covell Hall",                   "num": "41"},
    "hand hall":             {"x": 15,  "z": -8,  "name": "Hand Hall",                           "num": "42"},
    "raymond lodge":         {"x": -14, "z": 10,  "name": "Raymond Lodge",                       "num": "80"},
    "ritter house":          {"x": -12, "z": 10,  "name": "Ritter House",                        "num": "82"},
    "carter house":          {"x": -10, "z": -5,  "name": "Carter House",                        "num": "76"},
    "casa jackson":          {"x": -1,  "z": 10,  "name": "Casa Jackson",                        "num": "74"},
    "casa werner":           {"x": -7,  "z": 10,  "name": "Casa Werner",                         "num": "75"},
    # ── Residential / Greek ──
    "delta delta delta":     {"x": 27,  "z": -16, "name": "Delta Delta Delta",                   "num": "44"},
    "kappa alpha theta":     {"x": 21,  "z": -12, "name": "Kappa Alpha Theta",                   "num": "45"},
    "delta gamma":           {"x": 18,  "z": -12, "name": "Delta Gamma",                         "num": "46"},
    "sigma chi":             {"x": 15,  "z": -12, "name": "Sigma Chi",                           "num": "47"},
    "beta theta pi":         {"x": 12,  "z": -12, "name": "Beta Theta Pi",                       "num": "48"},
    "alpha phi":             {"x": 9,   "z": -12, "name": "Alpha Phi",                           "num": "49"},
    "theta chi":             {"x": -22, "z": -15, "name": "Theta Chi",                           "num": "165"},
    # ── South Campus ──
    "benerd":                {"x": 5,   "z": 20,  "name": "Benerd College",                      "num": "101"},
    "biological sciences":   {"x": 9,   "z": 25,  "name": "Biological Sciences Center",          "num": "103"},
    "classroom building":    {"x": 5,   "z": 31,  "name": "Classroom Building",                  "num": "107"},
    "olson hall":            {"x": 0,   "z": 32,  "name": "Olson Hall",                          "num": "109"},
    "biological laboratories":{"x": 5,  "z": 26,  "name": "Biological Laboratories",             "num": "110"},
    "demarcus brown":        {"x": 2,   "z": 23,  "name": "DeMarcus Brown Studio Theatre Arts",  "num": "111"},
    "theatre arts":          {"x": 2,   "z": 23,  "name": "DeMarcus Brown Studio Theatre Arts",  "num": "111"},
    "alumni house":          {"x": 2,   "z": 18,  "name": "Alex and Jeri Vereschagin Alumni House","num": "112"},
    "vereschagin":           {"x": 2,   "z": 18,  "name": "Alex and Jeri Vereschagin Alumni House","num": "112"},
    "long theatre":          {"x": -3,  "z": 21,  "name": "Long Theatre",                        "num": "115"},
    "communication department":{"x": -7,"z": 27,  "name": "Communication Department",            "num": "116"},
    "south campus labs":     {"x": -10, "z": 26,  "name": "Engineering & CS South Campus Labs",  "num": "118"},
    "geosciences":           {"x": -8,  "z": 32,  "name": "Pacific Geosciences Center",          "num": "120"},
    "reynolds art gallery":  {"x": -8,  "z": 32,  "name": "Reynolds Art Gallery",               "num": "120"},
    "jeannette powell":      {"x": -12, "z": 33,  "name": "Jeannette Powell Art Center",         "num": "122"},
    "ceramics studio":       {"x": -15, "z": 32,  "name": "Ceramics Studio",                     "num": "124"},
    # ── Athletic Campus ──
    "janssen":               {"x": -10, "z": 20,  "name": "Janssen-Lagorio Gymnasium",           "num": "130"},
    "lagorio":               {"x": -10, "z": 20,  "name": "Janssen-Lagorio Gymnasium",           "num": "130"},
    "dance studio":          {"x": -12, "z": 22,  "name": "Dance Studio / South Campus Gym",     "num": "132"},
    "pacific intercollegiate":{"x": -16,"z": 25,  "name": "Pacific Intercollegiate Athletics",   "num": "134"},
    "spanos center":         {"x": -16, "z": 16,  "name": "Alex G. Spanos Center",               "num": "135"},
    "alex g. spanos":        {"x": -16, "z": 16,  "name": "Alex G. Spanos Center",               "num": "135"},
    "kjeldsen pool":         {"x": -18, "z": 14,  "name": "Chris Kjeldsen Pool",                 "num": "146"},
    "aquatics center":       {"x": -22, "z": 14,  "name": "Pacific Aquatics Center",             "num": "145"},
    "sand volleyball":       {"x": -36, "z": 22,  "name": "Raney Sand Volleyball Courts",        "num": "142"},
    "tennis clubhouse":      {"x": -36, "z": 18,  "name": "Roy and Jean Sanders Tennis Clubhouse","num": "153"},
    "zimmerman tennis":      {"x": -28, "z": 8,   "name": "Eve Zimmerman Tennis Center",         "num": "152"},
    # ── Athletic Fields ──
    "knoles field":          {"x": -18, "z": 5,   "name": "Knoles Field",                        "num": "150"},
    "bill simoni":           {"x": -24, "z": 5,   "name": "Bill Simoni Field",                   "num": "148"},
    "simoni field":          {"x": -24, "z": 5,   "name": "Bill Simoni Field",                   "num": "148"},
    "zuckerman field":       {"x": -30, "z": 0,   "name": "Zuckerman Field",                     "num": "155"},
    "field hockey":          {"x": -30, "z": -5,  "name": "Field Hockey Turf",                   "num": "157"},
    "klein family":          {"x": -30, "z": 10,  "name": "Klein Family Field",                  "num": "140"},
    "gardemeyer":            {"x": -2,  "z": -38, "name": "Alan and Olive Gardemeyer Field",      "num": "175"},
    "brookside field":       {"x": -20, "z": -22, "name": "Brookside Field",                     "num": "163"},
    "covered performance":   {"x": -36, "z": 35,  "name": "Covered Performance Center",          "num": "141"},
    # ── North Campus / Health Sciences ──
    "cowell wellness":       {"x": -15, "z": -30, "name": "Cowell Wellness Center",              "num": "170"},
    "wellness center":       {"x": -15, "z": -30, "name": "Cowell Wellness Center",              "num": "170"},
    "public safety":         {"x": -15, "z": -30, "name": "Public Safety",                       "num": "170"},
    "monagan hall":          {"x": -4,  "z": -28, "name": "Monagan Hall",                        "num": "171"},
    "chan family":           {"x": 5,   "z": -28, "name": "Chan Family Hall",                    "num": "172"},
    "health sciences":       {"x": 14,  "z": -30, "name": "Health Sciences Learning Center",     "num": "178"},
    "long memorial":         {"x": 20,  "z": -30, "name": "Long Memorial Hall / School of Pharmacy","num": "179"},
    "pharmacy":              {"x": 20,  "z": -30, "name": "School of Pharmacy",                  "num": "179"},
    "physician assistant":   {"x": 20,  "z": -30, "name": "Physician Assistant Program",         "num": "179"},
    "rotunda":               {"x": 25,  "z": -28, "name": "Rotunda",                             "num": "180"},
    "calaveras hall":        {"x": -18, "z": -15, "name": "Calaveras Hall",                      "num": "166"},
    "support services":      {"x": -12, "z": -18, "name": "Support Services / Physical Plant",   "num": "168"},
    "university townhouses": {"x": -32, "z": -18, "name": "University Townhouses",               "num": "160"},
}

CATEGORY_COLORS = {
    "recreational sports": "#f97316",
    "sports":              "#ef4444",
    "softball":            "#ef4444",
    "baseball":            "#ef4444",
    "social":              "#a855f7",
    "diversity":           "#10b981",
    "equity":              "#10b981",
    "inclusion":           "#10b981",
    "graduate admissions": "#3b82f6",
    "information session": "#3b82f6",
    "webinar":             "#64748b",
    "virtual":             "#64748b",
    "community":           "#22d3ee",
    "arts":                "#ec4899",
    "music":               "#ec4899",
    "theatre":             "#ec4899",
    "academic":            "#6366f1",
}


def resolve_location(location_str: str) -> dict | None:
    """Fuzzy-match a calendar location string to a 3D map coordinate."""
    loc = location_str.lower().strip()
    # Exact or substring match (longest key wins to avoid false positives)
    best_key = None
    best_len = 0
    for key in LOCATION_MAP:
        if key in loc and len(key) > best_len:
            best_key = key
            best_len = len(key)
    return LOCATION_MAP[best_key] if best_key else None


def category_color(category: str) -> str:
    cat = category.lower()
    for key, color in CATEGORY_COLORS.items():
        if key in cat:
            return color
    return "#f59e0b"  # amber default


def scrape_events(max_pages: int = 3) -> list[dict]:
    """Scrape up to max_pages of the UOP calendar."""
    events = []
    headers = {"User-Agent": "Mozilla/5.0 (myTigerTrail campus nav app)"}

    for page in range(max_pages):
        url = f"{CALENDAR_URL}?page={page}" if page > 0 else CALENDAR_URL
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"[events] fetch error page {page}: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        # Real structure: div.event-row.views-row contains each event card
        rows = soup.find_all("div", class_="views-row")

        if not rows:
            break

        for row in rows:
            # Title + URL
            title_el = row.find("h2", class_="event-title")
            if not title_el:
                continue
            title_link = title_el.find("a")
            title    = title_el.get_text(strip=True)
            url_path = "https://www.pacific.edu" + (title_link["href"] if title_link else "")

            # Category
            cat_el   = row.find("div", class_="event-category")
            category = cat_el.get_text(strip=True) if cat_el else ""

            # Date range (first .event-time-range span)
            time_ranges = row.find_all("div", class_="event-time-range")
            date     = time_ranges[0].get_text(strip=True) if len(time_ranges) > 0 else ""
            time_str = time_ranges[1].get_text(strip=True) if len(time_ranges) > 1 else ""

            # Location
            loc_el   = row.find("div", class_="views-field-field-location")
            location = loc_el.get_text(strip=True) if loc_el else ""

            coords = resolve_location(location)

            events.append({
                "title":    title,
                "date":     date,
                "time":     time_str,
                "location": location,
                "category": category,
                "color":    category_color(category),
                "url":      url_path,
                "coords":   coords,   # None if off-campus / unrecognised
            })

    return events


def get_events(force_refresh: bool = False) -> list[dict]:
    """Return cached events, refreshing if stale."""
    now = time.time()
    if force_refresh or _cache["data"] is None or (now - _cache["ts"]) > CACHE_TTL:
        print("[events] scraping UOP calendar…")
        _cache["data"] = scrape_events()
        _cache["ts"] = now
        print(f"[events] fetched {len(_cache['data'])} events")
    return _cache["data"]
