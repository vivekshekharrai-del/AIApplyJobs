import sqlite3
import os
import webbrowser
from pathlib import Path
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), 'applypilot.db')
OUT = os.path.join(os.path.dirname(__file__), 'jobs_view.html')

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

rows = conn.execute('''
    SELECT
        fit_score, title, site, location, url, application_url,
        salary, discovered_at, scored_at, tailored_resume_path,
        cover_letter_path, applied_at, apply_status, apply_error,
        SUBSTR(score_reasoning, INSTR(score_reasoning, CHAR(10))+1, 300) as reasoning
    FROM jobs
    ORDER BY
        CASE WHEN fit_score IS NULL THEN 0 ELSE fit_score END DESC,
        discovered_at DESC
''').fetchall()
conn.close()

def score_color(s):
    if s is None: return '#888'
    if s >= 8: return '#22c55e'
    if s >= 6: return '#f59e0b'
    if s >= 4: return '#f97316'
    return '#ef4444'

def status_badge(row):
    if row['applied_at']:
        return '<span class="badge applied">Applied</span>'
    if row['apply_error']:
        return '<span class="badge error">Error</span>'
    if row['cover_letter_path']:
        return '<span class="badge cover">Cover Ready</span>'
    if row['tailored_resume_path']:
        return '<span class="badge tailored">Tailored</span>'
    if row['fit_score']:
        return '<span class="badge scored">Scored</span>'
    return '<span class="badge pending">Pending</span>'

def fmt_date(d):
    if not d: return '—'
    try: return datetime.fromisoformat(d.replace('Z','+00:00')).strftime('%b %d %H:%M')
    except: return d[:16]

def score_cell(s):
    if s is None: return '<td class="score" style="color:#888">—</td>'
    color = score_color(s)
    return f'<td class="score" style="color:{color};font-weight:700">{s}</td>'

rows_html = ''
for i, r in enumerate(rows, 1):
    link = r['application_url'] or r['url'] or '#'
    title = r['title'] or 'Unknown'
    resume_link = f'<a href="file:///{r["tailored_resume_path"]}" target="_blank">📄</a>' if r['tailored_resume_path'] else '—'
    cover_link  = f'<a href="file:///{r["cover_letter_path"]}" target="_blank">✉️</a>' if r['cover_letter_path'] else '—'
    reasoning   = (r['reasoning'] or '').replace('<','&lt;').replace('>','&gt;')[:200]
    rows_html += f'''
    <tr>
        <td class="num">{i}</td>
        {score_cell(r["fit_score"])}
        <td><a href="{link}" target="_blank">{title[:60]}</a></td>
        <td>{(r["site"] or "")[:22]}</td>
        <td>{(r["location"] or "—")[:28]}</td>
        <td>{r["salary"] or "—"}</td>
        <td>{status_badge(r)}</td>
        <td>{resume_link}</td>
        <td>{cover_link}</td>
        <td class="date">{fmt_date(r["discovered_at"])}</td>
        <td class="reason">{reasoning}</td>
    </tr>'''

total = len(rows)
scored = sum(1 for r in rows if r['fit_score'])
applied = sum(1 for r in rows if r['applied_at'])
tailored = sum(1 for r in rows if r['tailored_resume_path'])
top = sum(1 for r in rows if r['fit_score'] and r['fit_score'] >= 7)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ApplyPilot — Job Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f172a; color: #e2e8f0; }}
  header {{ background: #1e293b; padding: 24px 32px; border-bottom: 1px solid #334155; }}
  header h1 {{ font-size: 1.6rem; font-weight: 700; color: #f8fafc; }}
  header p {{ color: #94a3b8; font-size:.9rem; margin-top:4px; }}
  .stats {{ display:flex; gap:16px; padding: 20px 32px; flex-wrap:wrap; }}
  .stat {{ background:#1e293b; border:1px solid #334155; border-radius:10px; padding:14px 22px; min-width:120px; }}
  .stat .val {{ font-size:1.8rem; font-weight:700; color:#f8fafc; }}
  .stat .lbl {{ font-size:.78rem; color:#94a3b8; margin-top:2px; }}
  .controls {{ padding: 0 32px 16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
  input[type=text] {{ background:#1e293b; border:1px solid #475569; color:#e2e8f0; padding:8px 14px;
    border-radius:8px; font-size:.9rem; width:280px; outline:none; }}
  input[type=text]:focus {{ border-color:#6366f1; }}
  select {{ background:#1e293b; border:1px solid #475569; color:#e2e8f0; padding:8px 12px;
    border-radius:8px; font-size:.9rem; outline:none; cursor:pointer; }}
  .table-wrap {{ overflow-x:auto; padding: 0 32px 40px; }}
  table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  thead th {{ background:#1e293b; color:#94a3b8; font-weight:600; text-transform:uppercase;
    font-size:.72rem; letter-spacing:.05em; padding:10px 12px; border-bottom:1px solid #334155;
    position:sticky; top:0; white-space:nowrap; }}
  tbody tr {{ border-bottom:1px solid #1e293b; transition:background .15s; }}
  tbody tr:hover {{ background:#1e293b; }}
  td {{ padding:9px 12px; vertical-align:middle; }}
  td a {{ color:#818cf8; text-decoration:none; }}
  td a:hover {{ color:#a5b4fc; text-decoration:underline; }}
  .num {{ color:#475569; font-size:.8rem; text-align:right; }}
  .score {{ font-size:1.1rem; text-align:center; }}
  .date {{ color:#64748b; font-size:.78rem; white-space:nowrap; }}
  .reason {{ color:#64748b; font-size:.78rem; max-width:300px; }}
  .badge {{ display:inline-block; padding:3px 8px; border-radius:12px; font-size:.72rem; font-weight:600; white-space:nowrap; }}
  .badge.applied  {{ background:#166534; color:#86efac; }}
  .badge.error    {{ background:#7f1d1d; color:#fca5a5; }}
  .badge.cover    {{ background:#1e3a5f; color:#93c5fd; }}
  .badge.tailored {{ background:#4a1d96; color:#c4b5fd; }}
  .badge.scored   {{ background:#1c3347; color:#7dd3fc; }}
  .badge.pending  {{ background:#1e293b; color:#64748b; }}
  .hidden {{ display:none; }}
</style>
</head>
<body>
<header>
  <h1>ApplyPilot — Job Dashboard</h1>
  <p>Generated {datetime.now().strftime("%B %d, %Y at %H:%M")} &nbsp;·&nbsp; {total:,} total jobs</p>
</header>

<div class="stats">
  <div class="stat"><div class="val">{total:,}</div><div class="lbl">Total Jobs</div></div>
  <div class="stat"><div class="val">{scored:,}</div><div class="lbl">Scored</div></div>
  <div class="stat"><div class="val" style="color:#22c55e">{top:,}</div><div class="lbl">Score 7+</div></div>
  <div class="stat"><div class="val" style="color:#c4b5fd">{tailored:,}</div><div class="lbl">Tailored</div></div>
  <div class="stat"><div class="val" style="color:#86efac">{applied:,}</div><div class="lbl">Applied</div></div>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="Search title, company, location..." oninput="filterTable()">
  <select id="statusFilter" onchange="filterTable()">
    <option value="">All Statuses</option>
    <option value="Applied">Applied</option>
    <option value="Error">Error</option>
    <option value="Cover Ready">Cover Ready</option>
    <option value="Tailored">Tailored</option>
    <option value="Scored">Scored</option>
    <option value="Pending">Pending</option>
  </select>
  <select id="scoreFilter" onchange="filterTable()">
    <option value="">All Scores</option>
    <option value="8">Score 8+</option>
    <option value="7">Score 7+</option>
    <option value="5">Score 5+</option>
  </select>
  <span id="count" style="color:#64748b;font-size:.85rem;"></span>
</div>

<div class="table-wrap">
<table id="jobTable">
  <thead>
    <tr>
      <th>#</th><th>Score</th><th>Title</th><th>Company</th><th>Location</th>
      <th>Salary</th><th>Status</th><th>Resume</th><th>Cover</th><th>Found</th><th>AI Reasoning</th>
    </tr>
  </thead>
  <tbody id="tbody">
    {rows_html}
  </tbody>
</table>
</div>

<script>
function filterTable() {{
  const search = document.getElementById('search').value.toLowerCase();
  const status = document.getElementById('statusFilter').value.toLowerCase();
  const minScore = parseInt(document.getElementById('scoreFilter').value) || 0;
  const rows = document.querySelectorAll('#tbody tr');
  let visible = 0;
  rows.forEach(row => {{
    const text = row.textContent.toLowerCase();
    const scoreEl = row.querySelector('.score');
    const score = scoreEl ? parseInt(scoreEl.textContent) || 0 : 0;
    const badgeEl = row.querySelector('.badge');
    const badgeText = badgeEl ? badgeEl.textContent.toLowerCase() : '';
    const matchSearch = !search || text.includes(search);
    const matchStatus = !status || badgeText.includes(status.toLowerCase());
    const matchScore = score >= minScore;
    if (matchSearch && matchStatus && matchScore) {{ row.classList.remove('hidden'); visible++; }}
    else {{ row.classList.add('hidden'); }}
  }});
  document.getElementById('count').textContent = visible.toLocaleString() + ' jobs shown';
}}
filterTable();
</script>
</body>
</html>'''

Path(OUT).write_text(html, encoding='utf-8')
print(f"Dashboard written to {OUT}")
webbrowser.open(f'file:///{OUT}')
