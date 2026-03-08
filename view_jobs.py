"""ApplyPilot Job Dashboard — live server with approve-to-apply feature.

Run:  python view_jobs.py
Opens http://localhost:7322/ in your browser.
Click ★ to approve a job for the apply pipeline.
Press Ctrl+C to stop.
"""

import json
import os
import sqlite3
import socket
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DB = os.path.join(os.path.dirname(__file__), 'applypilot.db')


def _get_rows():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT
            fit_score, title, site, location, url, application_url,
            salary, discovered_at, scored_at, tailored_resume_path,
            cover_letter_path, applied_at, apply_status, apply_error,
            apply_approved,
            SUBSTR(score_reasoning, INSTR(score_reasoning, CHAR(10))+1, 300) as reasoning
        FROM jobs
        ORDER BY
            CASE WHEN fit_score IS NULL THEN 0 ELSE fit_score END DESC,
            discovered_at DESC
    ''').fetchall()
    conn.close()
    return rows


def _toggle_approve(url: str, approved: int) -> bool:
    try:
        conn = sqlite3.connect(DB)
        conn.execute("UPDATE jobs SET apply_approved = ? WHERE url = ?", (approved, url))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def _toggle_manual(url: str, mark: bool) -> bool:
    try:
        conn = sqlite3.connect(DB)
        if mark:
            now = datetime.utcnow().isoformat()
            conn.execute(
                "UPDATE jobs SET apply_status = 'manual_applied', applied_at = ? WHERE url = ?",
                (now, url),
            )
        else:
            conn.execute(
                "UPDATE jobs SET apply_status = NULL, applied_at = NULL WHERE url = ? AND apply_status = 'manual_applied'",
                (url,),
            )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def score_color(s):
    if s is None: return '#888'
    if s >= 8: return '#22c55e'
    if s >= 6: return '#f59e0b'
    if s >= 4: return '#f97316'
    return '#ef4444'


def status_badge(row):
    if row['apply_status'] == 'manual_applied':
        return '<span class="badge manual">Applied Manually</span>'
    if row['applied_at']:
        return '<span class="badge applied">Applied (Bot)</span>'
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
    try: return datetime.fromisoformat(d.replace('Z', '+00:00')).strftime('%b %d %H:%M')
    except: return d[:16]


def score_cell(s):
    if s is None: return '<td class="score" style="color:#888">—</td>'
    color = score_color(s)
    return f'<td class="score" style="color:{color};font-weight:700">{s}</td>'


def _build_html() -> str:
    rows = _get_rows()
    rows_html = ''
    for i, r in enumerate(rows, 1):
        link = r['application_url'] or r['url'] or '#'
        title = r['title'] or 'Unknown'
        resume_link = f'<a href="file:///{r["tailored_resume_path"]}" target="_blank">📄</a>' if r['tailored_resume_path'] else '—'
        cover_link  = f'<a href="file:///{r["cover_letter_path"]}" target="_blank">✉️</a>' if r['cover_letter_path'] else '—'
        reasoning   = (r['reasoning'] or '').replace('<', '&lt;').replace('>', '&gt;')[:200]
        approved     = int(r['apply_approved'] or 0)
        is_manual    = (r['apply_status'] == 'manual_applied')
        url_escaped  = (r['url'] or '').replace('"', '&quot;')
        approve_cls  = 'approve-btn approved' if approved else 'approve-btn'
        approve_lbl  = '★' if approved else '☆'
        manual_cls   = 'manual-btn active' if is_manual else 'manual-btn'
        manual_title = 'Unmark manually applied' if is_manual else 'Mark as manually applied'
        row_cls      = 'manual-row' if is_manual else ('approved-row' if approved else '')

        rows_html += f'''
    <tr class="{row_cls}">
        <td class="num">{i}</td>
        {score_cell(r["fit_score"])}
        <td><a href="{link}" target="_blank">{title[:60]}</a></td>
        <td>{(r["site"] or "")[:22]}</td>
        <td>{(r["location"] or "—")[:28]}</td>
        <td>{r["salary"] or "—"}</td>
        <td>{status_badge(r)}</td>
        <td>
          <button class="{approve_cls}" data-url="{url_escaped}" data-approved="{approved}" onclick="toggleApprove(this)" title="Approve for apply pipeline">{approve_lbl}</button>
          <button class="{manual_cls}" data-url="{url_escaped}" data-manual="{1 if is_manual else 0}" onclick="markManual(this)" title="{manual_title}">✓</button>
        </td>
        <td>{resume_link}</td>
        <td>{cover_link}</td>
        <td class="date">{fmt_date(r["discovered_at"])}</td>
        <td class="reason">{reasoning}</td>
    </tr>'''

    total         = len(rows)
    scored        = sum(1 for r in rows if r['fit_score'])
    applied       = sum(1 for r in rows if r['applied_at'] and r['apply_status'] != 'manual_applied')
    manual_applied = sum(1 for r in rows if r['apply_status'] == 'manual_applied')
    tailored      = sum(1 for r in rows if r['tailored_resume_path'])
    top           = sum(1 for r in rows if r['fit_score'] and r['fit_score'] >= 7)
    approved_count = sum(1 for r in rows if r['apply_approved'])

    return f'''<!DOCTYPE html>
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
  .stat.approved-stat .val {{ color:#f59e0b; }}
  .controls {{ padding: 0 32px 16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
  input[type=text] {{ background:#1e293b; border:1px solid #475569; color:#e2e8f0; padding:8px 14px;
    border-radius:8px; font-size:.9rem; width:280px; outline:none; }}
  input[type=text]:focus {{ border-color:#6366f1; }}
  select {{ background:#1e293b; border:1px solid #475569; color:#e2e8f0; padding:8px 12px;
    border-radius:8px; font-size:.9rem; outline:none; cursor:pointer; }}
  .toggle-btn {{ background:#1e293b; border:1px solid #475569; color:#94a3b8; padding:8px 14px;
    border-radius:8px; font-size:.85rem; cursor:pointer; transition:all .15s; }}
  .toggle-btn:hover {{ border-color:#f59e0b; color:#f59e0b; }}
  .toggle-btn.active {{ background:#f59e0b22; border-color:#f59e0b; color:#f59e0b; font-weight:600; }}
  .table-wrap {{ overflow-x:auto; padding: 0 32px 40px; }}
  table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  thead th {{ background:#1e293b; color:#94a3b8; font-weight:600; text-transform:uppercase;
    font-size:.72rem; letter-spacing:.05em; padding:10px 12px; border-bottom:1px solid #334155;
    position:sticky; top:0; white-space:nowrap; }}
  tbody tr {{ border-bottom:1px solid #1e293b; transition:background .15s; }}
  tbody tr:hover {{ background:#1e293b; }}
  tbody tr.approved-row {{ background:#1c1a0a; }}
  tbody tr.approved-row:hover {{ background:#25220d; }}
  td {{ padding:9px 12px; vertical-align:middle; }}
  td a {{ color:#818cf8; text-decoration:none; }}
  td a:hover {{ color:#a5b4fc; text-decoration:underline; }}
  .num {{ color:#475569; font-size:.8rem; text-align:right; }}
  .score {{ font-size:1.1rem; text-align:center; }}
  .date {{ color:#64748b; font-size:.78rem; white-space:nowrap; }}
  .reason {{ color:#64748b; font-size:.78rem; max-width:300px; }}
  .badge {{ display:inline-block; padding:3px 8px; border-radius:12px; font-size:.72rem; font-weight:600; white-space:nowrap; }}
  .badge.applied  {{ background:#166534; color:#86efac; }}
  .badge.manual   {{ background:#14532d; color:#4ade80; border: 1px solid #22c55e; }}
  .badge.error    {{ background:#7f1d1d; color:#fca5a5; }}
  .badge.cover    {{ background:#1e3a5f; color:#93c5fd; }}
  .badge.tailored {{ background:#4a1d96; color:#c4b5fd; }}
  .badge.scored   {{ background:#1c3347; color:#7dd3fc; }}
  .badge.pending  {{ background:#1e293b; color:#64748b; }}
  /* Approve + Manual buttons */
  .approve-btn, .manual-btn {{
    background: none; border: 1px solid #334155; border-radius: 6px;
    color: #64748b; cursor: pointer; font-size: 1rem;
    padding: 2px 7px; transition: all .15s; line-height: 1.4;
  }}
  .approve-btn {{ margin-right: 3px; font-size: 1.1rem; }}
  .approve-btn:hover {{ border-color: #f59e0b; color: #f59e0b; }}
  .approve-btn.approved {{ border-color: #f59e0b; color: #f59e0b; background: #f59e0b18; }}
  .approve-btn.loading, .manual-btn.loading {{ opacity:.5; pointer-events:none; }}
  .manual-btn:hover {{ border-color: #22c55e; color: #22c55e; }}
  .manual-btn.active {{ border-color: #22c55e; color: #22c55e; background: #22c55e18; font-weight:700; }}
  tbody tr.manual-row {{ background: #0f2318; }}
  tbody tr.manual-row:hover {{ background: #142d1f; }}
  .hidden {{ display:none; }}
</style>
</head>
<body>
<header>
  <h1>ApplyPilot — Job Dashboard</h1>
  <p>Live dashboard &nbsp;·&nbsp; {total:,} total jobs &nbsp;·&nbsp; Refresh page to reload data</p>
</header>

<div class="stats">
  <div class="stat"><div class="val">{total:,}</div><div class="lbl">Total Jobs</div></div>
  <div class="stat"><div class="val">{scored:,}</div><div class="lbl">Scored</div></div>
  <div class="stat"><div class="val" style="color:#22c55e">{top:,}</div><div class="lbl">Score 7+</div></div>
  <div class="stat"><div class="val" style="color:#c4b5fd">{tailored:,}</div><div class="lbl">Tailored</div></div>
  <div class="stat"><div class="val" style="color:#86efac">{applied:,}</div><div class="lbl">Applied (Bot)</div></div>
  <div class="stat"><div class="val" style="color:#4ade80">{manual_applied:,}</div><div class="lbl">Applied Manually</div></div>
  <div class="stat approved-stat"><div class="val">{approved_count:,}</div><div class="lbl">Approved to Apply</div></div>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="Search title, company, location..." oninput="filterTable()">
  <select id="statusFilter" onchange="filterTable()">
    <option value="">All Statuses</option>
    <option value="Applied Manually">Applied Manually</option>
    <option value="Applied (Bot)">Applied (Bot)</option>
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
  <button class="toggle-btn" id="approvedFilterBtn" onclick="toggleApprovedFilter()">★ Approved Only</button>
  <span id="count" style="color:#64748b;font-size:.85rem;"></span>
</div>

<div class="table-wrap">
<table id="jobTable">
  <thead>
    <tr>
      <th>#</th><th>Score</th><th>Title</th><th>Company</th><th>Location</th>
      <th>Salary</th><th>Status</th><th>★</th><th>Resume</th><th>Cover</th><th>Found</th><th>AI Reasoning</th>
    </tr>
  </thead>
  <tbody id="tbody">
    {rows_html}
  </tbody>
</table>
</div>

<script>
let approvedOnly = false;

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
    const approveBtn = row.querySelector('.approve-btn');
    const isApproved = approveBtn && approveBtn.dataset.approved === '1';
    const matchSearch = !search || text.includes(search);
    const matchStatus = !status || badgeText.includes(status.toLowerCase());
    const matchScore = score >= minScore;
    const matchApproved = !approvedOnly || isApproved;
    if (matchSearch && matchStatus && matchScore && matchApproved) {{
      row.classList.remove('hidden'); visible++;
    }} else {{
      row.classList.add('hidden');
    }}
  }});
  document.getElementById('count').textContent = visible.toLocaleString() + ' jobs shown';
}}

function toggleApprovedFilter() {{
  approvedOnly = !approvedOnly;
  const btn = document.getElementById('approvedFilterBtn');
  btn.classList.toggle('active', approvedOnly);
  filterTable();
}}

function toggleApprove(btn) {{
  const url = btn.dataset.url;
  const current = parseInt(btn.dataset.approved) || 0;
  const newVal = current ? 0 : 1;
  btn.classList.add('loading');
  fetch('/approve', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{url: url, approved: newVal}})
  }})
  .then(r => r.json())
  .then(d => {{
    if (d.ok) {{
      btn.dataset.approved = newVal;
      btn.textContent = newVal ? '\u2605' : '\u2606';
      if (newVal) {{
        btn.classList.add('approved');
        btn.closest('tr').classList.add('approved-row');
      }} else {{
        btn.classList.remove('approved');
        btn.closest('tr').classList.remove('approved-row');
      }}
      if (approvedOnly) filterTable();
    }} else {{
      alert('Failed to update: ' + (d.error || 'unknown error'));
    }}
  }})
  .catch(e => alert('Server error: ' + e))
  .finally(() => btn.classList.remove('loading'));
}}

function markManual(btn) {{
  const url = btn.dataset.url;
  const current = parseInt(btn.dataset.manual) || 0;
  const newVal = current ? 0 : 1;
  btn.classList.add('loading');
  fetch('/mark_manual', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{url: url, mark: newVal}})
  }})
  .then(r => r.json())
  .then(d => {{
    if (d.ok) {{
      btn.dataset.manual = newVal;
      const row = btn.closest('tr');
      const badge = row.querySelector('.badge');
      if (newVal) {{
        btn.classList.add('active');
        btn.title = 'Unmark manually applied';
        row.classList.add('manual-row');
        row.classList.remove('approved-row');
        if (badge) {{ badge.className = 'badge manual'; badge.textContent = 'Applied Manually'; }}
      }} else {{
        btn.classList.remove('active');
        btn.title = 'Mark as manually applied';
        row.classList.remove('manual-row');
        if (badge) {{ badge.className = 'badge pending'; badge.textContent = 'Pending'; }}
      }}
      filterTable();
    }} else {{
      alert('Failed to update: ' + (d.error || 'unknown error'));
    }}
  }})
  .catch(e => alert('Server error: ' + e))
  .finally(() => btn.classList.remove('loading'));
}}

filterTable();
</script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # quiet

    def do_GET(self):
        if self.path in ('/', '/jobs_view.html'):
            try:
                body = _build_html().encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err = f'<pre>Error: {e}</pre>'.encode()
                self.send_response(500)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(err)))
                self.end_headers()
                self.wfile.write(err)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/approve':
            length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(length))
                ok = _toggle_approve(data.get('url', ''), 1 if data.get('approved') else 0)
                resp = json.dumps({'ok': ok}).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                resp = json.dumps({'ok': False, 'error': str(e)}).encode()
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
        elif self.path == '/mark_manual':
            length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(length))
                ok = _toggle_manual(data.get('url', ''), bool(data.get('mark')))
                resp = json.dumps({'ok': ok}).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                resp = json.dumps({'ok': False, 'error': str(e)}).encode()
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
        else:
            self.send_response(404)
            self.end_headers()


def _free_port(preferred=7322):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', preferred))
            return preferred
        except OSError:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]


if __name__ == '__main__':
    port = _free_port(7322)
    server = HTTPServer(('127.0.0.1', port), _Handler)
    url = f'http://localhost:{port}/'
    print(f'Dashboard: {url}')
    print('Click the star on any job row to approve it for the apply pipeline.')
    print('Press Ctrl+C to stop.')
    threading.Thread(target=lambda: (
        __import__('time').sleep(0.5), webbrowser.open(url)
    ), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.server_close()
