"""Fix missing titles for Dice jobs by extracting them from job detail pages.

Dice job detail pages have JSON-LD with the full title, or at minimum a
<title> tag like "Software Engineer at Acme Corp | Dice.com".

Run this AFTER run_dice.py to patch up any Dice jobs with NULL titles.
"""
import os
import re
import json
import sqlite3
import logging
import time

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_PROJECT_DIR)
os.environ.setdefault("APPLYPILOT_DIR", _PROJECT_DIR)

import httpx
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "applypilot.db")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def extract_title_from_page(html: str, url: str) -> str | None:
    """Try JSON-LD first, then <title> tag."""
    soup = BeautifulSoup(html, "html.parser")

    # 1. Try JSON-LD JobPosting
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                data = data[0]
            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                title = data.get("title") or data.get("name")
                if title:
                    return title.strip()
        except Exception:
            pass

    # 2. Try <title> tag: "Job Title at Company | Dice.com" or "Job Title | Dice"
    title_tag = soup.find("title")
    if title_tag:
        raw = title_tag.get_text(strip=True)
        # Remove trailing " | Dice.com", " | Dice", " - Dice" etc.
        cleaned = re.sub(r"\s*[|\-]\s*(Dice\.com|Dice)\s*$", "", raw, flags=re.IGNORECASE)
        # Remove trailing "at Company" if it still looks like "Title at Company"
        if cleaned and len(cleaned) < 200:
            return cleaned.strip()

    # 3. Try og:title meta tag
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        raw = og["content"]
        cleaned = re.sub(r"\s*[|\-]\s*(Dice\.com|Dice)\s*$", "", raw, flags=re.IGNORECASE)
        if cleaned:
            return cleaned.strip()

    return None


def fix_dice_titles():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT url FROM jobs WHERE (title IS NULL OR title = '') AND site = 'Dice'"
    ).fetchall()

    if not rows:
        log.info("No Dice jobs with missing titles found.")
        return

    log.info("Found %d Dice jobs with missing titles. Fetching...", len(rows))

    fixed = 0
    failed = 0

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15) as client:
        for i, row in enumerate(rows):
            url = row["url"]
            log.info("[%d/%d] %s", i + 1, len(rows), url[:80])
            try:
                resp = client.get(url)
                if resp.status_code != 200:
                    log.warning("HTTP %d for %s", resp.status_code, url)
                    failed += 1
                    continue

                title = extract_title_from_page(resp.text, url)
                if title:
                    conn.execute("UPDATE jobs SET title = ? WHERE url = ?", (title, url))
                    conn.commit()
                    log.info("  -> %s", title[:80])
                    fixed += 1
                else:
                    log.warning("  -> Could not extract title")
                    failed += 1

                time.sleep(0.5)  # polite delay

            except Exception as e:
                log.error("  -> Error: %s", e)
                failed += 1

    conn.close()
    log.info("Done. Fixed: %d | Failed: %d", fixed, failed)


if __name__ == "__main__":
    fix_dice_titles()
