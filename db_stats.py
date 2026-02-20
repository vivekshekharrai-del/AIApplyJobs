import sqlite3, os
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'applypilot.db'))
total = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
scored = conn.execute('SELECT COUNT(*) FROM jobs WHERE fit_score IS NOT NULL').fetchone()[0]
top = conn.execute('SELECT COUNT(*) FROM jobs WHERE fit_score >= 7').fetchone()[0]
tailored = conn.execute('SELECT COUNT(*) FROM jobs WHERE tailored_resume_path IS NOT NULL').fetchone()[0]
cover = conn.execute('SELECT COUNT(*) FROM jobs WHERE cover_letter_path IS NOT NULL').fetchone()[0]
applied = conn.execute('SELECT COUNT(*) FROM jobs WHERE applied_at IS NOT NULL').fetchone()[0]
print(f'Total jobs:     {total:,}')
print(f'Scored:         {scored:,}')
print(f'Score 7+:       {top:,}')
print(f'Tailored:       {tailored:,}')
print(f'Cover letters:  {cover:,}')
print(f'Applied:        {applied:,}')
conn.close()
