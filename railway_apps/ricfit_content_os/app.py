#!/usr/bin/env python3
"""RicFit Content OS — Video Content Calendar & Distribution"""

import os, sqlite3, secrets, calendar, json
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template_string, request, jsonify, session, redirect, g

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'ricfit2024')
DB_PATH = os.getenv('DB_PATH', 'content_os.db')
EDITORS = ['vlad', 'richard', 'cgl']

calendar.setfirstweekday(0)  # Monday first

# ── DB ──────────────────────────────────────────────────────────────────────

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute('''CREATE TABLE IF NOT EXISTS videos (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        drive_link  TEXT    NOT NULL,
        editor      TEXT    NOT NULL,
        post_date   DATE    NOT NULL,
        posted      INTEGER DEFAULT 0,
        views       INTEGER,
        likes       INTEGER,
        comments    INTEGER,
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()
    db.close()

init_db()

# ── AUTH ────────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def d(*a, **kw):
        if not session.get('auth'): return redirect('/login')
        return f(*a, **kw)
    return d

# ── ROUTES ──────────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    return 'ok', 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    err = None
    if request.method == 'POST':
        if request.form.get('pw') == ADMIN_PASSWORD:
            session['auth'] = True
            return redirect('/')
        err = 'Incorrect password'
    return render_template_string(LOGIN_HTML, err=err)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
@login_required
def dashboard():
    today = date.today()
    m = int(request.args.get('m', today.month))
    y = int(request.args.get('y', today.year))
    ym = f"{y}-{m:02d}"
    db = get_db()

    rows = db.execute(
        "SELECT * FROM videos WHERE post_date LIKE ? ORDER BY post_date, id",
        (ym + '-%',)
    ).fetchall()
    videos = [dict(r) for r in rows]

    vbd = {}
    for v in videos:
        vbd.setdefault(v['post_date'], []).append(v)

    wk_start = today - timedelta(days=today.weekday())
    wk_end   = wk_start + timedelta(days=6)
    wk = dict(db.execute("""
        SELECT COUNT(*) as total, COALESCE(SUM(posted),0) as posted,
               COALESCE(SUM(CASE WHEN posted=1 THEN views    ELSE 0 END),0) as views,
               COALESCE(SUM(CASE WHEN posted=1 THEN likes    ELSE 0 END),0) as likes,
               COALESCE(SUM(CASE WHEN posted=1 THEN comments ELSE 0 END),0) as comments
        FROM videos WHERE post_date BETWEEN ? AND ?
    """, (wk_start.isoformat(), wk_end.isoformat())).fetchone())

    totals = dict(db.execute("""
        SELECT COALESCE(SUM(posted),0) as posted,
               COALESCE(SUM(CASE WHEN posted=1 THEN views    ELSE 0 END),0) as views,
               COALESCE(SUM(CASE WHEN posted=1 THEN likes    ELSE 0 END),0) as likes,
               COALESCE(SUM(CASE WHEN posted=1 THEN comments ELSE 0 END),0) as comments
        FROM videos
    """).fetchone())

    weekly = [dict(r) for r in db.execute("""
        SELECT strftime('%W', post_date) as wk,
               MIN(post_date) as wk_start,
               COUNT(*) as total,
               COALESCE(SUM(posted),0) as posted,
               COALESCE(SUM(CASE WHEN posted=1 THEN views    ELSE 0 END),0) as views,
               COALESCE(SUM(CASE WHEN posted=1 THEN likes    ELSE 0 END),0) as likes,
               COALESCE(SUM(CASE WHEN posted=1 THEN comments ELSE 0 END),0) as comments
        FROM videos WHERE post_date LIKE ?
        GROUP BY wk ORDER BY wk
    """, (ym + '-%',)).fetchall()]

    cal_data = calendar.monthcalendar(y, m)
    pm, py = (m-1, y) if m > 1 else (12, y-1)
    nm, ny = (m+1, y) if m < 12 else (1,  y+1)

    return render_template_string(DASH_HTML,
        cal=cal_data, vbd=vbd,
        today=today.isoformat(),
        m=m, y=y, mname=calendar.month_name[m],
        pm=pm, py=py, nm=nm, ny=ny,
        wk=wk, totals=totals, weekly=weekly,
        editors=EDITORS,
        videos_json=json.dumps({v['id']: v for v in videos})
    )

@app.route('/api/videos', methods=['POST'])
@login_required
def add_video():
    d = request.json or {}
    for k in ['name', 'drive_link', 'editor', 'post_date']:
        if not d.get(k): return jsonify(error=f'Missing {k}'), 400
    if d['editor'] not in EDITORS: return jsonify(error='Invalid editor'), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO videos (name,drive_link,editor,post_date) VALUES (?,?,?,?)",
        (d['name'].strip(), d['drive_link'].strip(), d['editor'], d['post_date'])
    )
    db.commit()
    return jsonify(id=cur.lastrowid, success=True)

@app.route('/api/videos/<int:vid>/toggle', methods=['POST'])
@login_required
def toggle(vid):
    db = get_db()
    row = db.execute("SELECT posted FROM videos WHERE id=?", (vid,)).fetchone()
    if not row: return jsonify(error='Not found'), 404
    new = 1 - row['posted']
    db.execute("UPDATE videos SET posted=? WHERE id=?", (new, vid))
    db.commit()
    return jsonify(posted=new)

@app.route('/api/videos/<int:vid>/stats', methods=['POST'])
@login_required
def update_stats(vid):
    d = request.json or {}
    db = get_db()
    db.execute("UPDATE videos SET views=?,likes=?,comments=? WHERE id=?",
               (d.get('views') or None, d.get('likes') or None, d.get('comments') or None, vid))
    db.commit()
    return jsonify(success=True)

@app.route('/api/videos/<int:vid>', methods=['DELETE'])
@login_required
def delete_video(vid):
    db = get_db()
    db.execute("DELETE FROM videos WHERE id=?", (vid,))
    db.commit()
    return jsonify(success=True)

@app.route('/editor/<name>')
def editor_view(name):
    name = name.lower()
    if name not in EDITORS: return "Editor not found", 404
    db   = get_db()
    today = date.today().isoformat()
    upcoming = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE editor=? AND post_date >= ? ORDER BY post_date", (name, today)
    ).fetchall()]
    past = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE editor=? AND post_date < ? ORDER BY post_date DESC LIMIT 30", (name, today)
    ).fetchall()]
    colors = {'vlad': '#C1F000', 'richard': '#FFFFFF', 'cgl': '#7EC8E3'}
    return render_template_string(EDITOR_HTML,
        editor=name.capitalize(), color=colors.get(name, '#C1F000'),
        upcoming=upcoming, past=past, today=today
    )

if __name__ == '__main__':
    app.run(debug=True)

# ── TEMPLATES ───────────────────────────────────────────────────────────────

LOGIN_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RicFit Content OS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#F2F2F2;color:#111;min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#FFFFFF;border:1px solid #E2E2E2;border-radius:14px;padding:48px 40px;width:380px;box-shadow:0 2px 20px rgba(0,0,0,.06)}
.logo{font-size:26px;font-weight:800;letter-spacing:-0.5px;margin-bottom:6px}.logo span{color:#C1F000}
.sub{color:rgba(0,0,0,0.38);font-size:13px;margin-bottom:32px}
label{display:block;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:rgba(0,0,0,0.4);margin-bottom:6px}
input{width:100%;background:#F8F8F8;border:1px solid #D8D8D8;border-radius:8px;padding:12px 14px;color:#111;font-family:'Inter',sans-serif;font-size:14px;outline:none}
input:focus{border-color:#C1F000}
.btn{width:100%;margin-top:20px;background:#C1F000;color:#0D0D0D;font-family:'Inter',sans-serif;font-weight:700;font-size:14px;padding:13px;border:none;border-radius:8px;cursor:pointer}
.btn:hover{background:#d4ff00}
.err{color:#cc2200;font-size:13px;margin-top:12px}
</style>
</head>
<body>
<div class="card">
  <div class="logo">Ric<span>Fit</span></div>
  <div class="sub">Content OS — Admin</div>
  <form method="post">
    <label>Password</label>
    <input type="password" name="pw" placeholder="Enter password" autofocus>
    <button class="btn">Sign In</button>
    {% if err %}<div class="err">{{ err }}</div>{% endif %}
  </form>
</div>
</body>
</html>'''

DASH_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RicFit Content OS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#F2F2F2;color:#111;min-height:100vh}
:root{
  --lime:#C1F000;--lime-dim:rgba(193,240,0,.2);--lime-border:rgba(150,185,0,.35);
  --bg:#F2F2F2;--bg2:#FFFFFF;--bg3:#EBEBEB;
  --border:#E2E2E2;--border2:#D2D2D2;--muted:rgba(0,0,0,.38)
}
a{color:inherit;text-decoration:none}

/* NAV */
.nav{position:sticky;top:0;z-index:50;background:rgba(242,242,242,.97);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);padding:0 24px;
  display:flex;align-items:center;justify-content:space-between;height:56px}
.nav-left{display:flex;align-items:center;gap:20px}
.logo{font-size:18px;font-weight:800;letter-spacing:-.3px}.logo span{color:var(--lime)}
.month-nav{display:flex;align-items:center;gap:8px}
.mnav-btn{background:none;border:1px solid var(--border2);color:var(--muted);cursor:pointer;
  width:28px;height:28px;border-radius:6px;font-size:15px;display:flex;align-items:center;justify-content:center}
.mnav-btn:hover{border-color:#7CB800;color:#7CB800}
.mname{font-size:14px;font-weight:700;min-width:120px;text-align:center}
.nav-right{display:flex;align-items:center;gap:10px}
.btn-add{background:var(--lime);color:#0D0D0D;font-family:'Inter',sans-serif;font-weight:700;
  font-size:13px;padding:7px 16px;border:none;border-radius:7px;cursor:pointer}
.btn-add:hover{background:#d4ff00}
.nav-logout{color:var(--muted);font-size:12px}
.nav-logout:hover{color:#111}
.editor-links{display:flex;gap:6px}
.editor-link{font-size:11px;font-weight:600;padding:5px 10px;border-radius:6px;background:var(--bg3);color:var(--muted)}
.editor-link:hover{color:#111}

/* STATS BAR */
.stats-bar{background:var(--bg2);border-bottom:1px solid var(--border);
  padding:12px 24px;display:flex;gap:24px;flex-wrap:wrap;align-items:center}
.stat{display:flex;flex-direction:column;gap:2px}
.stat-lbl{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.stat-val{font-size:20px;font-weight:800}.stat-val.lime{color:#6A9E00}
.sdiv{width:1px;background:var(--border2);align-self:stretch}

/* MAIN */
.main{padding:18px 24px 60px}

/* CALENDAR HEADERS */
.cal-hdr{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;margin-bottom:2px}
.cal-hdr-cell{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);padding:6px 8px;text-align:center}

/* CALENDAR GRID */
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.day{min-height:110px;background:var(--bg2);border:1px solid var(--border);
  border-radius:6px;padding:6px;position:relative;cursor:pointer;transition:border-color .15s}
.day:hover{border-color:#C1F000}
.day.empty{background:transparent;border-color:transparent;min-height:0;cursor:default}
.day.empty:hover{border-color:transparent}
.day.today{border-color:#C1F000}
.day.past{opacity:.65}
.day-num{font-size:11px;font-weight:700;color:var(--muted);
  position:absolute;top:6px;right:7px}
.day.today .day-num{color:var(--lime)}
.vcards{margin-top:18px;display:flex;flex-direction:column;gap:2px}

/* VIDEO CARD */
.vcard{background:var(--bg3);border:1px solid var(--border);border-radius:4px;
  padding:5px 7px;cursor:pointer;display:flex;align-items:center;gap:4px;
  transition:border-color .15s}
.vcard:hover{border-color:rgba(255,255,255,.2)}
.vcard.posted{background:rgba(193,240,0,.05);border-color:rgba(193,240,0,.2)}
.vbadge{font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;
  padding:2px 5px;border-radius:3px;flex-shrink:0}
.vb-vlad{color:#6A9E00;background:rgba(193,240,0,.3)}
.vb-richard{color:#444;background:rgba(0,0,0,.07)}
.vb-cgl{color:#2278A0;background:rgba(126,200,227,.25)}
.vname{flex:1;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  color:rgba(255,255,255,.8)}
.vcheck{width:13px;height:13px;flex-shrink:0;accent-color:var(--lime);cursor:pointer}

/* WEEKLY TABLE */
.sec-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin:32px 0 12px}
.wtable{width:100%;border-collapse:collapse;font-size:13px}
.wtable th{text-align:left;font-size:10px;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;color:var(--muted);padding:8px 12px;border-bottom:1px solid var(--border)}
.wtable td{padding:10px 12px;border-bottom:1px solid var(--border)}
.wtable tr:hover td{background:var(--bg2)}
.posted-pill{display:inline-block;background:var(--lime-dim);color:#6A9E00;
  font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px}
.cv{color:#6A9E00;font-weight:700}

/* PANEL */
.p-overlay{position:fixed;inset:0;background:rgba(0,0,0,0);pointer-events:none;z-index:100;transition:background .25s}
.p-overlay.open{background:rgba(0,0,0,.55);pointer-events:all}
.panel{position:fixed;top:0;right:0;bottom:0;width:360px;background:#FFFFFF;
  border-left:1px solid var(--border2);transform:translateX(100%);
  transition:transform .25s cubic-bezier(.4,0,.2,1);z-index:101;overflow-y:auto;padding:28px 24px}
.panel.open{transform:translateX(0)}
.panel-hdr{font-size:16px;font-weight:800;margin-bottom:24px;
  display:flex;align-items:center;justify-content:space-between}
.x-btn{background:none;border:none;color:var(--muted);cursor:pointer;font-size:22px;line-height:1}
.x-btn:hover{color:#fff}

/* FIELDS */
.field{margin-bottom:16px}
.field label{display:block;font-size:11px;font-weight:600;text-transform:uppercase;
  letter-spacing:.08em;color:var(--muted);margin-bottom:6px}
.field input,.field select{width:100%;background:#F8F8F8;border:1px solid var(--border2);
  border-radius:7px;padding:11px 12px;color:#111;font-family:'Inter',sans-serif;font-size:13px;outline:none}
.field input:focus,.field select:focus{border-color:var(--lime)}
.field select option{background:#141414}
.btn-lime{width:100%;margin-top:8px;background:var(--lime);color:#0D0D0D;
  font-family:'Inter',sans-serif;font-weight:700;font-size:14px;padding:13px;
  border:none;border-radius:8px;cursor:pointer}
.btn-lime:hover{background:#d4ff00}

/* MODAL */
.m-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);
  z-index:200;display:none;align-items:center;justify-content:center}
.m-overlay.open{display:flex}
.modal{background:#FFFFFF;border:1px solid var(--border2);border-radius:12px;
  padding:28px;width:430px;max-width:calc(100vw - 32px)}
.modal-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:4px}
.modal-title{font-size:15px;font-weight:800;line-height:1.3}
.modal-meta{font-size:12px;color:var(--muted);margin-bottom:16px}
.drive-btn{display:inline-flex;align-items:center;gap:6px;color:var(--lime);
  font-size:12px;font-weight:700;padding:7px 12px;background:var(--lime-dim);
  border-radius:6px;margin-bottom:16px}
.drive-btn:hover{background:rgba(193,240,0,.18)}
.posted-row{display:flex;align-items:center;gap:10px;padding:10px 12px;
  background:var(--bg3);border:1px solid var(--border);border-radius:7px;
  cursor:pointer;margin-bottom:16px;user-select:none}
.posted-row:hover{border-color:var(--lime)}
.pcheck{width:15px;height:15px;accent-color:var(--lime);pointer-events:none}
.plabel{font-size:13px;font-weight:600}
.inline-row{display:flex;gap:12px}
.inline-row .field{flex:1}
.ratio-box{margin-top:4px;padding:9px 12px;background:var(--lime-dim);border-radius:6px;
  font-size:13px;font-weight:700;color:#6A9E00;display:none}
.modal-footer{display:flex;gap:8px;margin-top:20px}
.btn-primary{flex:1;background:var(--lime);color:#0D0D0D;font-family:'Inter',sans-serif;
  font-weight:700;font-size:13px;padding:11px;border:none;border-radius:7px;cursor:pointer}
.btn-primary:hover{background:#d4ff00}
.btn-ghost{background:none;color:var(--muted);font-family:'Inter',sans-serif;font-size:13px;
  padding:11px 14px;border:1px solid var(--border2);border-radius:7px;cursor:pointer}
.btn-ghost:hover{color:#111;border-color:#111}
.btn-danger{background:rgba(255,59,59,.1);color:#ff4444;font-family:'Inter',sans-serif;
  font-size:13px;padding:11px 14px;border:1px solid rgba(255,59,59,.2);border-radius:7px;cursor:pointer}
.btn-danger:hover{background:rgba(255,59,59,.2)}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav">
  <div class="nav-left">
    <div class="logo">Ric<span>Fit</span></div>
    <div class="month-nav">
      <a href="/?m={{ pm }}&y={{ py }}"><button class="mnav-btn">‹</button></a>
      <div class="mname">{{ mname }} {{ y }}</div>
      <a href="/?m={{ nm }}&y={{ ny }}"><button class="mnav-btn">›</button></a>
    </div>
  </div>
  <div class="nav-right">
    <div class="editor-links">
      {% for e in editors %}
      <a class="editor-link" href="/editor/{{ e }}" target="_blank">{{ e.capitalize() }}</a>
      {% endfor %}
    </div>
    <button class="btn-add" onclick="openPanel()">+ Add Video</button>
    <a class="nav-logout" href="/logout">Logout</a>
  </div>
</nav>

<!-- STATS BAR -->
<div class="stats-bar">
  <div class="stat">
    <div class="stat-lbl">This Week</div>
    <div class="stat-val lime">{{ wk.posted or 0 }} <span style="font-size:13px;color:var(--muted);font-weight:500">/ {{ wk.total or 0 }} posted</span></div>
  </div>
  <div class="sdiv"></div>
  <div class="stat">
    <div class="stat-lbl">All-Time Views</div>
    <div class="stat-val">{{ "{:,}".format(totals.views or 0) }}</div>
  </div>
  <div class="stat">
    <div class="stat-lbl">All-Time Likes</div>
    <div class="stat-val">{{ "{:,}".format(totals.likes or 0) }}</div>
  </div>
  <div class="stat">
    <div class="stat-lbl">All-Time Comments</div>
    <div class="stat-val">{{ "{:,}".format(totals.comments or 0) }}</div>
  </div>
  {% if totals.views and totals.views > 0 %}
  <div class="sdiv"></div>
  <div class="stat">
    <div class="stat-lbl">Avg C/V Ratio</div>
    <div class="stat-val lime">{{ "%.1f"|format((totals.comments or 0) / totals.views * 100) }}%</div>
  </div>
  {% endif %}
</div>

<!-- MAIN -->
<div class="main">

  <!-- DAY HEADERS -->
  <div class="cal-hdr">
    {% for d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] %}
    <div class="cal-hdr-cell">{{ d }}</div>
    {% endfor %}
  </div>

  <!-- CALENDAR -->
  <div class="cal-grid">
    {% for week in cal %}
      {% for day in week %}
        {% if day %}
          {% set dstr = "%04d-%02d-%02d" % (y, m, day) %}
          <div class="day {{ 'today' if dstr == today else ('past' if dstr < today else '') }}"
               onclick="openPanelForDate('{{ dstr }}')">
            <div class="day-num">{{ day }}</div>
            <div class="vcards">
              {% for v in vbd.get(dstr, []) %}
              <div class="vcard {{ 'posted' if v.posted else '' }}"
                   onclick="event.stopPropagation(); openModal({{ v.id }})">
                <span class="vbadge vb-{{ v.editor }}">{{ v.editor[:3] }}</span>
                <span class="vname">{{ v.name }}</span>
                <input class="vcheck" type="checkbox" {{ 'checked' if v.posted else '' }}
                       onclick="event.stopPropagation(); togglePosted(event, {{ v.id }})">
              </div>
              {% endfor %}
            </div>
          </div>
        {% else %}
          <div class="day empty"></div>
        {% endif %}
      {% endfor %}
    {% endfor %}
  </div>

  <!-- WEEKLY BREAKDOWN -->
  {% if weekly %}
  <div class="sec-title">Weekly Breakdown — {{ mname }} {{ y }}</div>
  <table class="wtable">
    <thead>
      <tr>
        <th>Week Starting</th><th>Scheduled</th><th>Posted</th>
        <th>Views</th><th>Likes</th><th>Comments</th><th>C/V Ratio</th>
      </tr>
    </thead>
    <tbody>
      {% for w in weekly %}
      <tr>
        <td>{{ w.wk_start }}</td>
        <td>{{ w.total }}</td>
        <td><span class="posted-pill">{{ w.posted or 0 }}</span></td>
        <td>{{ "{:,}".format(w.views or 0) }}</td>
        <td>{{ "{:,}".format(w.likes or 0) }}</td>
        <td>{{ "{:,}".format(w.comments or 0) }}</td>
        <td class="cv">
          {% if w.views and w.views > 0 %}{{ "%.1f"|format((w.comments or 0) / w.views * 100) }}%{% else %}—{% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}

</div>

<!-- ADD VIDEO PANEL -->
<div class="p-overlay" id="pOverlay" onclick="closePanel()"></div>
<div class="panel" id="panel">
  <div class="panel-hdr">
    Add Video
    <button class="x-btn" onclick="closePanel()">×</button>
  </div>
  <div class="field">
    <label>Video Name</label>
    <input type="text" id="vName" placeholder="e.g. 5 Habits for Fat Loss">
  </div>
  <div class="field">
    <label>Google Drive Link</label>
    <input type="url" id="vLink" placeholder="https://drive.google.com/...">
  </div>
  <div class="field">
    <label>Assign Editor</label>
    <select id="vEditor">
      <option value="">— Select —</option>
      {% for e in editors %}
      <option value="{{ e }}">{{ e.capitalize() }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="field">
    <label>Post Date</label>
    <input type="date" id="vDate">
  </div>
  <button class="btn-lime" onclick="addVideo()">Add to Calendar</button>
</div>

<!-- VIDEO MODAL -->
<div class="m-overlay" id="mOverlay" onclick="closeModal(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <div class="modal-top">
      <div class="modal-title" id="mTitle"></div>
      <button class="x-btn" onclick="closeModal()">×</button>
    </div>
    <div class="modal-meta" id="mMeta"></div>
    <a class="drive-btn" id="mDrive" href="#" target="_blank">▶ Open in Drive</a>

    <div class="posted-row" onclick="togglePostedModal()">
      <input class="pcheck" type="checkbox" id="mPostedChk">
      <span class="plabel" id="mPostedLbl">Mark as posted</span>
    </div>

    <div class="field">
      <label>Views</label>
      <input type="number" id="mViews" placeholder="0" min="0" oninput="calcRatio()">
    </div>
    <div class="inline-row">
      <div class="field">
        <label>Likes</label>
        <input type="number" id="mLikes" placeholder="0" min="0">
      </div>
      <div class="field">
        <label>Comments</label>
        <input type="number" id="mComments" placeholder="0" min="0" oninput="calcRatio()">
      </div>
    </div>
    <div class="ratio-box" id="ratioBox"></div>

    <div class="modal-footer">
      <button class="btn-primary" onclick="saveStats()">Save Stats</button>
      <button class="btn-ghost"   onclick="closeModal()">Cancel</button>
      <button class="btn-danger"  onclick="deleteVideo()">Delete</button>
    </div>
  </div>
</div>

<script>
const VD = {{ videos_json | safe }};
let activeId = null;

function openPanel() {
  const t = new Date(); t.setMinutes(t.getMinutes() - t.getTimezoneOffset());
  openPanelForDate(t.toISOString().slice(0,10));
}
function openPanelForDate(dateStr) {
  document.getElementById('panel').classList.add('open');
  document.getElementById('pOverlay').classList.add('open');
  document.getElementById('vDate').value = dateStr;
  document.getElementById('vName').focus();
}
function closePanel() {
  document.getElementById('panel').classList.remove('open');
  document.getElementById('pOverlay').classList.remove('open');
}

async function addVideo() {
  const name   = document.getElementById('vName').value.trim();
  const link   = document.getElementById('vLink').value.trim();
  const editor = document.getElementById('vEditor').value;
  const date   = document.getElementById('vDate').value;
  if (!name||!link||!editor||!date) { alert('Fill in all fields'); return; }
  const r = await fetch('/api/videos',{
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({name, drive_link:link, editor, post_date:date})
  });
  if (r.ok) { closePanel(); location.reload(); }
  else { const e=await r.json(); alert(e.error||'Error'); }
}

async function togglePosted(event, id) {
  const r = await fetch(`/api/videos/${id}/toggle`,{method:'POST'});
  if (!r.ok) { event.target.checked = !event.target.checked; return; }
  const data = await r.json();
  const card = event.target.closest('.vcard');
  card.classList.toggle('posted', !!data.posted);
  if (VD[id]) VD[id].posted = data.posted;
}

function openModal(id) {
  const v = VD[id]; if (!v) return;
  activeId = id;
  document.getElementById('mTitle').textContent   = v.name;
  document.getElementById('mMeta').textContent    = `${v.editor.charAt(0).toUpperCase()+v.editor.slice(1)}  ·  ${v.post_date}`;
  document.getElementById('mDrive').href          = v.drive_link;
  document.getElementById('mPostedChk').checked   = !!v.posted;
  document.getElementById('mPostedLbl').textContent = v.posted ? '✓ Posted' : 'Mark as posted';
  document.getElementById('mViews').value    = v.views    || '';
  document.getElementById('mLikes').value    = v.likes    || '';
  document.getElementById('mComments').value = v.comments || '';
  calcRatio();
  document.getElementById('mOverlay').classList.add('open');
}
function closeModal(e) {
  if (e && e.target !== document.getElementById('mOverlay')) return;
  document.getElementById('mOverlay').classList.remove('open');
  activeId = null;
}

async function togglePostedModal() {
  if (!activeId) return;
  const r = await fetch(`/api/videos/${activeId}/toggle`,{method:'POST'});
  if (!r.ok) return;
  const data = await r.json();
  if (VD[activeId]) VD[activeId].posted = data.posted;
  document.getElementById('mPostedChk').checked = !!data.posted;
  document.getElementById('mPostedLbl').textContent = data.posted ? '✓ Posted' : 'Mark as posted';
  const card = document.querySelector(`.vcard[onclick="openModal(${activeId})"]`);
  if (card) {
    card.classList.toggle('posted', !!data.posted);
    const cb = card.querySelector('.vcheck'); if (cb) cb.checked = !!data.posted;
  }
}

function calcRatio() {
  const v = parseInt(document.getElementById('mViews').value)    || 0;
  const c = parseInt(document.getElementById('mComments').value) || 0;
  const el = document.getElementById('ratioBox');
  if (v > 0) { el.style.display='block'; el.textContent=`C/V Ratio: ${(c/v*100).toFixed(1)}%`; }
  else el.style.display='none';
}

async function saveStats() {
  if (!activeId) return;
  const views    = parseInt(document.getElementById('mViews').value)    || null;
  const likes    = parseInt(document.getElementById('mLikes').value)    || null;
  const comments = parseInt(document.getElementById('mComments').value) || null;
  const r = await fetch(`/api/videos/${activeId}/stats`,{
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({views, likes, comments})
  });
  if (r.ok) { document.getElementById('mOverlay').classList.remove('open'); location.reload(); }
}

async function deleteVideo() {
  if (!activeId) return;
  if (!confirm(`Delete "${VD[activeId]?.name}"?`)) return;
  const r = await fetch(`/api/videos/${activeId}`,{method:'DELETE'});
  if (r.ok) { document.getElementById('mOverlay').classList.remove('open'); location.reload(); }
}

document.addEventListener('keydown', e => {
  if (e.key==='Escape') { closePanel(); document.getElementById('mOverlay').classList.remove('open'); }
});
</script>
</body>
</html>'''

EDITOR_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ editor }} — RicFit Content OS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#F2F2F2;color:#111;min-height:100vh;padding:0}
:root{--accent:{{ color }};--bg2:#FFFFFF;--bg3:#EBEBEB;--border:#E2E2E2;--muted:rgba(0,0,0,.38)}
.nav{background:#FFFFFF;border-bottom:1px solid var(--border);padding:0 24px;
  display:flex;align-items:center;height:56px;gap:12px}
.logo{font-size:18px;font-weight:800}.logo span{color:var(--accent)}
.divider{color:#333}
.editor-tag{color:var(--accent);font-size:14px;font-weight:700}
.main{padding:28px 24px 60px;max-width:900px}
h2{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin:28px 0 12px}
h2:first-child{margin-top:0}
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);padding:8px 14px;border-bottom:1px solid var(--border)}
td{padding:13px 14px;border-bottom:1px solid var(--border);font-size:13px}
tr:hover td{background:var(--bg2)}
.date{font-weight:700;color:#111}
.past-date{color:var(--muted)}
.vname{font-weight:500}
.drive-link{color:var(--accent);font-weight:700;font-size:12px;display:inline-flex;align-items:center;gap:4px}
.drive-link:hover{text-decoration:underline}
.badge{display:inline-block;padding:3px 9px;border-radius:20px;font-size:11px;font-weight:600}
.badge-pending{background:rgba(255,255,255,.07);color:rgba(255,255,255,.45)}
.badge-posted{color:var(--accent);background:rgba(193,240,0,.1)}
.empty{color:var(--muted);font-size:13px;padding:16px 0}
.today-row td{background:rgba(193,240,0,.04)}
.count-chip{display:inline-block;background:rgba(255,255,255,.07);color:var(--muted);
  font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;margin-left:6px}
</style>
</head>
<body>
<nav class="nav">
  <div class="logo">Ric<span>Fit</span></div>
  <div class="divider">|</div>
  <div class="editor-tag">{{ editor }}</div>
</nav>
<div class="main">
  <h2>Upcoming <span class="count-chip">{{ upcoming|length }}</span></h2>
  {% if upcoming %}
  <table>
    <thead><tr><th>Post Date</th><th>Video</th><th>Drive</th><th>Status</th></tr></thead>
    <tbody>
    {% for v in upcoming %}
    <tr class="{{ 'today-row' if v.post_date == today else '' }}">
      <td class="date">{{ v.post_date[8:10] }}/{{ v.post_date[5:7] }}/{{ v.post_date[:4] }}</td>
      <td class="vname">{{ v.name }}</td>
      <td><a class="drive-link" href="{{ v.drive_link }}" target="_blank">▶ Open</a></td>
      <td><span class="badge {{ 'badge-posted' if v.posted else 'badge-pending' }}">{{ 'Posted' if v.posted else 'Pending' }}</span></td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div class="empty">No upcoming videos assigned yet.</div>
  {% endif %}

  {% if past %}
  <h2>Past 30 Days <span class="count-chip">{{ past|length }}</span></h2>
  <table>
    <thead><tr><th>Post Date</th><th>Video</th><th>Drive</th><th>Status</th></tr></thead>
    <tbody>
    {% for v in past %}
    <tr>
      <td class="past-date">{{ v.post_date[8:10] }}/{{ v.post_date[5:7] }}/{{ v.post_date[:4] }}</td>
      <td class="vname" style="opacity:.6">{{ v.name }}</td>
      <td><a class="drive-link" href="{{ v.drive_link }}" target="_blank">▶ Open</a></td>
      <td><span class="badge {{ 'badge-posted' if v.posted else 'badge-pending' }}">{{ 'Posted' if v.posted else 'Pending' }}</span></td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% endif %}
</div>
</body>
</html>'''
