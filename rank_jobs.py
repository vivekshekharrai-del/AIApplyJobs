import sqlite3, os

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'applypilot.db'))
rows = conn.execute('''
    SELECT fit_score, title, site, location, url
    FROM jobs
    WHERE fit_score IS NOT NULL AND fit_score > 0
    ORDER BY fit_score DESC, scored_at DESC
    LIMIT 60
''').fetchall()

print(f"{'#':<4} {'Score':<7} {'Title':<55} {'Company':<22} {'Location'}")
print('-'*130)
for i, r in enumerate(rows, 1):
    score, title, site, loc, url = r
    title = (title or '')[:53]
    site = (site or '')[:20]
    loc = (loc or 'N/A')[:28]
    print(f"{i:<4} {score:<7} {title:<55} {site:<22} {loc}")

conn.close()
