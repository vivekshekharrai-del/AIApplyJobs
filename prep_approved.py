"""Pre-score approved+unscored jobs so tailor/cover pipeline picks them up."""
import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect(r'C:\Users\vivek\Jobs\applypilot.db')
now = datetime.now(timezone.utc).isoformat()

# Set fit_score = 8 for approved jobs that have no score yet
result = conn.execute("""
    UPDATE jobs
    SET fit_score = 8,
        score_reasoning = 'Manually approved by user — auto-scored 8',
        scored_at = ?
    WHERE apply_approved = 1
      AND fit_score IS NULL
""", (now,))
conn.commit()
print(f"Pre-scored {result.rowcount} approved jobs -> fit_score=8")

# Verify
r = conn.execute("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN full_description IS NOT NULL THEN 1 ELSE 0 END) as enriched,
        SUM(CASE WHEN fit_score IS NOT NULL THEN 1 ELSE 0 END) as scored,
        SUM(CASE WHEN tailored_resume_path IS NOT NULL THEN 1 ELSE 0 END) as tailored
    FROM jobs WHERE apply_approved = 1
""").fetchone()
print(f"Approved: {r[0]} total | {r[1]} enriched | {r[2]} scored | {r[3]} tailored")
conn.close()
