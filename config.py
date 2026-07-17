from pathlib import Path

# -------------------------
# Project Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

TRACKS_FILE = DATA_DIR / "tracks.json"
ROI_FILE = DATA_DIR / "roi.json"
TIMELINE_FILE = DATA_DIR / "timeline.json"

# -------------------------
# Zone Names
# -------------------------
OUTSIDE = "Outside"
ENTRANCE = "Entrance"
EXIT = "Exit"
CHECKOUT = "Checkout"

SPECIAL_ZONES = {
    OUTSIDE,
    ENTRANCE,
    EXIT,
    CHECKOUT,
}

# -------------------------
# Event Names
# -------------------------
EVENT_ENTER = "Entered"
EVENT_EXIT = "Exited"
EVENT_CHECKOUT = "Entered Checkout"
EVENT_ZONE_VISIT = "Visited Zone"
EVENT_ZONE_CHANGE = "Moved"

# -------------------------
# Future Thresholds
# -------------------------
BROWSING_TIME = 20
QUEUE_TIME = 30