"""Run Dice-only job discovery and add jobs to the dashboard DB.

Usage:
    python run_dice.py
"""
import os
import logging

# Set working dir to project root AND point APPLYPILOT_DIR to it so the
# applypilot package uses C:\Users\vivek\Jobs\applypilot.db, not ~/.applypilot
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_PROJECT_DIR)
os.environ.setdefault("APPLYPILOT_DIR", _PROJECT_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Bootstrap
from applypilot.config import load_env, ensure_dirs
from applypilot.database import init_db, get_stats

load_env()
ensure_dirs()
init_db()

dice_site = [
    {
        "name": "Dice",
        "url": "https://www.dice.com/jobs?q={query_encoded}&location=Remote&pageSize=100",
        "type": "search",
    }
]

# ── Discover (Dice only) ──────────────────────────────────────────────────────
log.info("=" * 60)
log.info("Dice discovery — writing to: %s", os.path.join(_PROJECT_DIR, "applypilot.db"))
log.info("=" * 60)

from applypilot.discovery.smartextract import run_smart_extract

before = get_stats()
result = run_smart_extract(sites=dice_site)
after = get_stats()

new_jobs = after["total"] - before["total"]
log.info("=" * 60)
log.info("DONE — new Dice jobs added: %d (total in DB: %d)", new_jobs, after["total"])
log.info("Open dashboard: python view_jobs.py  →  http://localhost:7322")
log.info("Run fix_dice_titles.py next to recover job titles from detail pages")
log.info("=" * 60)
