import sqlite3
conn = sqlite3.connect('C:/Users/vivek/Jobs/applypilot.db')
c = conn.cursor()

# Check the actual date range in discovered_at
c.execute("SELECT date(discovered_at), COUNT(*) FROM jobs GROUP BY date(discovered_at) ORDER BY date(discovered_at) DESC LIMIT 10")
print("Jobs by discovered date (recent first):")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]} jobs")

print()
c.execute("SELECT COUNT(*) FROM jobs")
print(f"Total: {c.fetchone()[0]}")

# Check rowid range
c.execute("SELECT MIN(rowid), MAX(rowid) FROM jobs")
print(f"Rowid range: {c.fetchone()}")
