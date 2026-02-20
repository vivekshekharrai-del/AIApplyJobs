import sqlite3, os

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'applypilot.db'))

dice = conn.execute("SELECT COUNT(*) FROM jobs WHERE site LIKE '%dice%' OR url LIKE '%dice.com%'").fetchone()[0]
print(f"Dice jobs in DB: {dice}")

print("\nAll sources:")
sites = conn.execute("SELECT site, COUNT(*) as c FROM jobs GROUP BY site ORDER BY c DESC").fetchall()
for s in sites:
    print(f"  {s[0]}: {s[1]}")

if dice > 0:
    print("\nSample Dice jobs:")
    sample = conn.execute("SELECT title, site, location, url FROM jobs WHERE site LIKE '%dice%' OR url LIKE '%dice.com%' LIMIT 10").fetchall()
    for j in sample:
        print(f"  [{j[1]}] {j[0]} — {j[2]}")
        print(f"    {j[3][:80]}")

conn.close()
