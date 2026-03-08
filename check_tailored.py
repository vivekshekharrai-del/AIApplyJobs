import sqlite3
conn = sqlite3.connect(r'C:\Users\vivek\Jobs\applypilot.db')
cur = conn.cursor()

print("=== All tailored jobs ===")
cur.execute("""
    SELECT title, apply_status, tailored_resume_path, cover_letter_path, fit_score, apply_error
    FROM jobs WHERE tailored_at IS NOT NULL ORDER BY tailored_at DESC;
""")
rows = cur.fetchall()
for r in rows:
    print(f"  [{r[1] or 'pending'}] score={r[4]} | {r[0][:60]}")
    if r[5]:
        print(f"    ERROR: {r[5]}")

print(f"\nTotal tailored: {len(rows)}")

pending = [r for r in rows if r[1] is None]
print(f"Pending (not yet applied): {len(pending)}")
for r in pending:
    print(f"  - {r[0][:70]}")
    print(f"    resume: {r[2]}")
    print(f"    cover: {r[3]}")

conn.close()
