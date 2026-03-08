"""Dedicated Dice.com scraper using Playwright with correct selectors.

Searches Remote + Texas locations (including Hybrid), paginates through
all results, and stores jobs directly into applypilot.db.

Usage:
    python dice_scraper.py
"""
import os
import re
import time
import sqlite3
import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_PROJECT_DIR)
os.environ.setdefault("APPLYPILOT_DIR", _PROJECT_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DB_PATH = os.path.join(_PROJECT_DIR, "applypilot.db")

QUERIES = [
    ".NET Developer",
    ".NET Engineer",
    "Lead Software Engineer",
    "Lead Developer",
    "Senior Software Engineer .NET",
    "Full Stack Developer",
    "Full Stack .NET",
    "Software Engineer",
    "Azure Developer",
    "Azure Architect",
    "solution architect",
    "principal engineer",
    "technical lead",
    "engineering manager",
]

LOCATIONS = [
    "Remote",
    "Texas, USA",
    "Dallas, TX",
    "Austin, TX",
    "Houston, TX",
    "Plano, TX",
    "Irving, TX",
    "Fort Worth, TX",
]

DICE_BASE = "https://www.dice.com/jobs"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def store_job(conn, job: dict) -> bool:
    """Insert job into DB. Returns True if new, False if duplicate."""
    now = datetime.now(timezone.utc).isoformat()
    # Clean up the URL — strip location/query params so same job from different
    # searches doesn't get inserted twice
    url = job["url"]
    base_url = url.split("?")[0] if "?" in url else url
    try:
        conn.execute(
            """INSERT INTO jobs (url, title, salary, description, location, site, discovered_at)
               VALUES (?, ?, ?, ?, ?, 'Dice', ?)""",
            (
                base_url,
                job.get("title"),
                job.get("salary"),
                job.get("description"),
                job.get("location"),
                now,
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def extract_card(card) -> dict | None:
    """Extract job data from a Playwright card element."""
    try:
        # Title — from job-search-job-detail-link (visible heading in card)
        title_el = card.query_selector('[data-testid="job-search-job-detail-link"]')
        title = title_el.inner_text().strip() if title_el else None
        href = title_el.get_attribute("href") if title_el else None

        if not href:
            # Fallback: invisible overlay link
            link_el = card.query_selector('[data-testid="job-search-job-card-link"]')
            if link_el:
                href = link_el.get_attribute("href")
                # Extract title from aria-label: "View Details for <Title> (<hash>)"
                aria = link_el.get_attribute("aria-label") or ""
                m = re.match(r"View Details for (.+?) \([a-f0-9]{32}\)$", aria)
                if m:
                    title = m.group(1)

        if not href:
            return None

        # Location — first small grey text paragraph in the content section
        # Structure: <p class="text-sm font-normal text-zinc-600">Hybrid in Irving, Texas</p>
        loc_els = card.query_selector_all("p.text-sm.font-normal.text-zinc-600")
        location = None
        for el in loc_els:
            txt = el.inner_text().strip()
            if txt and len(txt) < 80:
                location = txt
                break

        # Salary — labelled by "salary-label"
        salary_el = card.query_selector('p[id="salary-label"]')
        salary = salary_el.inner_text().strip() if salary_el else None

        # Employment type
        emp_el = card.query_selector('p[id="employmentType-label"]')
        emp_type = emp_el.inner_text().strip() if emp_el else None
        if emp_type and salary:
            salary = f"{emp_type} | {salary}"
        elif emp_type:
            salary = emp_type

        # Short description snippet
        desc_el = card.query_selector("p.line-clamp-2")
        description = desc_el.inner_text().strip() if desc_el else None

        return {
            "url": href,
            "title": title,
            "location": location,
            "salary": salary,
            "description": description,
        }
    except Exception as e:
        log.debug("Card extract error: %s", e)
        return None


def scrape_page(page, query: str, location: str, page_num: int) -> list[dict]:
    """Scrape one Dice search results page. Returns list of job dicts."""
    url = f"{DICE_BASE}?q={quote_plus(query)}&location={quote_plus(location)}&page={page_num}"
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)
    except Exception as e:
        log.warning("  Load failed: %s", e)
        return []

    cards = page.query_selector_all('[data-testid="job-card"]')
    if not cards:
        return []

    jobs = []
    for card in cards:
        job = extract_card(card)
        if job:
            jobs.append(job)
    return jobs


def run():
    from playwright.sync_api import sync_playwright

    conn = get_db()
    total_new = 0
    total_seen = 0
    total_combos = len(QUERIES) * len(LOCATIONS)
    combo_num = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        pw_page = ctx.new_page()

        for query in QUERIES:
            for location in LOCATIONS:
                combo_num += 1
                log.info("[%d/%d] '%s' @ %s", combo_num, total_combos, query, location)

                page_num = 1
                combo_new = 0
                all_dupe_streak = 0

                while True:
                    jobs = scrape_page(pw_page, query, location, page_num)
                    if not jobs:
                        break

                    page_new = 0
                    for job in jobs:
                        total_seen += 1
                        if store_job(conn, job):
                            page_new += 1
                            total_new += 1
                            combo_new += 1

                    log.info("  p%d: %d cards, %d new", page_num, len(jobs), page_new)

                    if page_new == 0:
                        all_dupe_streak += 1
                        if all_dupe_streak >= 2:
                            break
                    else:
                        all_dupe_streak = 0

                    page_num += 1
                    time.sleep(0.8)

                log.info("  -> combo total new: %d", combo_new)

        browser.close()

    conn.close()
    log.info("")
    log.info("=" * 60)
    log.info("DONE — Dice jobs added: %d (total seen: %d)", total_new, total_seen)
    log.info("Reload dashboard: http://localhost:7322")
    log.info("=" * 60)


if __name__ == "__main__":
    run()
