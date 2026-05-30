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
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT    NOT NULL,
        drive_link    TEXT    NOT NULL,
        editor        TEXT    NOT NULL,
        post_date     DATE    NOT NULL,
        posted        INTEGER DEFAULT 0,
        views         INTEGER,
        likes         INTEGER,
        comments      INTEGER,
        editor_done   INTEGER DEFAULT 0,
        finished_link TEXT,
        created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    for col, defn in [('editor_done','INTEGER DEFAULT 0'), ('finished_link','TEXT'), ('in_progress','INTEGER DEFAULT 0')]:
        try:
            db.execute(f"ALTER TABLE videos ADD COLUMN {col} {defn}")
        except Exception:
            pass
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

@app.route('/api/videos/<int:vid>/editor-done', methods=['POST'])
def editor_done(vid):
    db = get_db()
    row = db.execute("SELECT editor_done FROM videos WHERE id=?", (vid,)).fetchone()
    if not row: return jsonify(error='Not found'), 404
    new = 1 - (row['editor_done'] or 0)
    db.execute("UPDATE videos SET editor_done=? WHERE id=?", (new, vid))
    db.commit()
    return jsonify(done=new)

@app.route('/api/videos/<int:vid>/finished-link', methods=['POST'])
def finished_link(vid):
    d = request.json or {}
    link = d.get('link', '').strip()
    db = get_db()
    db.execute("UPDATE videos SET finished_link=? WHERE id=?", (link or None, vid))
    db.commit()
    return jsonify(success=True)

@app.route('/api/videos/<int:vid>', methods=['DELETE'])
@login_required
def delete_video(vid):
    db = get_db()
    db.execute("DELETE FROM videos WHERE id=?", (vid,))
    db.commit()
    return jsonify(success=True)

@app.route('/api/pipeline')
@login_required
def pipeline_data():
    db  = get_db()
    today      = date.today()
    seven_ago  = (today - timedelta(days=7)).isoformat()
    fourteen_ago = (today - timedelta(days=14)).isoformat()
    t = today.isoformat()

    queued = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE in_progress=0 AND editor_done=0 AND posted=0 AND post_date>=? ORDER BY post_date",
        (seven_ago,)).fetchall()]
    in_prog = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE in_progress=1 AND editor_done=0 AND posted=0 ORDER BY post_date"
        ).fetchall()]
    ready = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE (editor_done=1 OR finished_link IS NOT NULL) AND posted=0 ORDER BY post_date"
        ).fetchall()]
    posted = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE posted=1 AND post_date>=? ORDER BY post_date DESC",
        (fourteen_ago,)).fetchall()]
    return jsonify(queued=queued, in_progress=in_prog, ready=ready, posted=posted)

@app.route('/api/editor-pipeline/<name>')
def editor_pipeline(name):
    name = name.lower()
    if name not in EDITORS: return jsonify(error='Not found'), 404
    db = get_db()
    today     = date.today()
    seven_ago = (today - timedelta(days=7)).isoformat()

    to_edit = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE editor=? AND in_progress=0 AND editor_done=0 AND posted=0 AND post_date>=? ORDER BY post_date",
        (name, seven_ago)).fetchall()]
    in_prog = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE editor=? AND in_progress=1 AND editor_done=0 ORDER BY post_date",
        (name,)).fetchall()]
    done = [dict(r) for r in db.execute(
        "SELECT * FROM videos WHERE editor=? AND (editor_done=1 OR finished_link IS NOT NULL) ORDER BY post_date DESC LIMIT 30",
        (name,)).fetchall()]
    return jsonify(to_edit=to_edit, in_progress=in_prog, done=done)

@app.route('/api/videos/<int:vid>/start', methods=['POST'])
def start_editing(vid):
    db = get_db()
    if not db.execute("SELECT id FROM videos WHERE id=?", (vid,)).fetchone():
        return jsonify(error='Not found'), 404
    db.execute("UPDATE videos SET in_progress=1 WHERE id=?", (vid,))
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
  --border:#E2E2E2;--border2:#D2D2D2;--muted:rgba(0,0,0,.52)
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
.day-num{font-size:11px;font-weight:700;color:#555;
  position:absolute;top:6px;right:7px}
.day.today .day-num{color:#6A9E00;font-size:12px}
.vcards{margin-top:18px;display:flex;flex-direction:column;gap:2px}

/* VIDEO CARD */
.vcard{background:var(--bg3);border:1px solid var(--border);border-radius:4px;
  padding:5px 7px;cursor:pointer;display:flex;align-items:center;gap:4px;
  transition:border-color .15s}
.vcard:hover{border-color:rgba(255,255,255,.2)}
.vcard.posted{background:rgba(193,240,0,.08);border-color:rgba(150,185,0,.3)}
.vcard.editor-done-card{border-left:3px solid #C1F000}
.vbadge{font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;
  padding:2px 5px;border-radius:3px;flex-shrink:0}
.vb-vlad{color:#6A9E00;background:rgba(193,240,0,.3)}
.vb-richard{color:#444;background:rgba(0,0,0,.07)}
.vb-cgl{color:#2278A0;background:rgba(126,200,227,.25)}
.vname{flex:1;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  color:#1A1A1A;font-weight:500}
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

/* TABS */
.view-tabs{display:flex;gap:2px;background:#E5E5E5;border-radius:8px;padding:3px}
.tab-btn{font-family:'Inter',sans-serif;font-size:12px;font-weight:600;padding:6px 16px;border:none;border-radius:6px;cursor:pointer;background:none;color:#666;transition:all .15s}
.tab-btn.active{background:#fff;color:#111;box-shadow:0 1px 4px rgba(0,0,0,.1)}

/* PIPELINE */
.pipeline-wrap{padding:16px 24px 60px}
.pipeline-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
@media(max-width:1000px){.pipeline-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.pipeline-grid{grid-template-columns:1fr}}
.p-col{background:#EBEBEB;border-radius:10px;padding:12px;min-height:200px}
.p-col-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.p-col-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#555}
.p-col-count{background:#D8D8D8;color:#555;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;min-width:24px;text-align:center}
.p-col-inprog .p-col-title{color:#2278A0}
.p-col-ready .p-col-title{color:#6A9E00}
.p-card{background:#fff;border-radius:8px;padding:10px 12px;margin-bottom:6px;border:1px solid #E5E5E5;transition:box-shadow .15s}
.p-card:hover{box-shadow:0 2px 10px rgba(0,0,0,.07)}
.p-card-risk{border-left:3px solid #F59E0B}
.p-card-overdue{border-left:3px solid #EF4444}
.p-card-top{display:flex;align-items:center;gap:5px;margin-bottom:5px;flex-wrap:wrap}
.p-date{font-size:10px;color:#999;font-weight:600;margin-left:auto}
.tag-risk{font-size:9px;font-weight:700;text-transform:uppercase;background:rgba(245,158,11,.15);color:#D97706;padding:2px 5px;border-radius:3px}
.tag-overdue{font-size:9px;font-weight:700;text-transform:uppercase;background:rgba(239,68,68,.12);color:#DC2626;padding:2px 5px;border-radius:3px}
.p-name{font-size:13px;font-weight:600;color:#111;margin-bottom:7px;line-height:1.3}
.p-card-bottom{display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}
.p-links{display:flex;gap:8px;align-items:center}
.p-link{font-size:11px;font-weight:700;color:#6A9E00;text-decoration:none}
.p-link:hover{text-decoration:underline}
.p-link-fin{color:#2278A0}
.p-metrics{font-size:11px;color:#999}
.p-action-btn{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;padding:5px 12px;background:#C1F000;color:#111;border:none;border-radius:5px;cursor:pointer;white-space:nowrap}
.p-action-btn:hover{background:#d4ff00}
.p-empty{font-size:12px;color:#bbb;text-align:center;padding:24px 0}
.p-loading{font-size:12px;color:#bbb;text-align:center;padding:24px 0}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav">
  <div class="nav-left">
    <div class="logo">Ric<span>Fit</span></div>
    <div class="view-tabs">
      <button class="tab-btn active" id="tab-cal" onclick="switchTab('calendar')">Calendar</button>
      <button class="tab-btn" id="tab-pipe" onclick="switchTab('pipeline')">Pipeline</button>
    </div>
    <div class="month-nav" id="monthNav">
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

<div id="calendar-view">
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
              <div class="vcard {{ 'posted' if v.posted else '' }} {{ 'editor-done-card' if v.editor_done else '' }}"
                   onclick="event.stopPropagation(); openModal({{ v.id }})">
                <span class="vbadge vb-{{ v.editor }}">{{ v.editor[:3] }}</span>
                <span class="vname">{{ v.name }}</span>
                {% if v.editor_done %}<span title="Editor done" style="font-size:10px;color:#6A9E00;flex-shrink:0">✓</span>{% endif %}
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

</div><!-- /main -->
</div><!-- /calendar-view -->

<!-- PIPELINE VIEW -->
<div id="pipeline-view" style="display:none">
  <div class="pipeline-wrap">
    <div class="pipeline-grid">
      <div class="p-col" id="pColQueued">
        <div class="p-col-hdr"><span class="p-col-title">Queued</span><span class="p-col-count" id="pCntQ">—</span></div>
        <div class="p-loading">Loading…</div>
      </div>
      <div class="p-col p-col-inprog" id="pColInprog">
        <div class="p-col-hdr"><span class="p-col-title">In Progress</span><span class="p-col-count" id="pCntI">—</span></div>
        <div class="p-loading">Loading…</div>
      </div>
      <div class="p-col p-col-ready" id="pColReady">
        <div class="p-col-hdr"><span class="p-col-title">Ready to Post</span><span class="p-col-count" id="pCntR">—</span></div>
        <div class="p-loading">Loading…</div>
      </div>
      <div class="p-col" id="pColPosted">
        <div class="p-col-hdr"><span class="p-col-title">Posted</span><span class="p-col-count" id="pCntP">—</span></div>
        <div class="p-loading">Loading…</div>
      </div>
    </div>
  </div>
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
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:16px;flex-wrap:wrap">
      <a class="drive-btn" id="mDrive" href="#" target="_blank" style="margin-bottom:0">▶ Raw Footage</a>
      <a class="drive-btn" id="mFinishedDrive" href="#" target="_blank" style="margin-bottom:0;display:none;background:rgba(193,240,0,.3)">✓ Finished Edit</a>
    </div>

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
  document.getElementById('mTitle').textContent     = v.name;
  document.getElementById('mMeta').textContent      = `${v.editor.charAt(0).toUpperCase()+v.editor.slice(1)}  ·  ${v.post_date}`;
  document.getElementById('mDrive').href            = v.drive_link;
  document.getElementById('mPostedChk').checked     = !!v.posted;
  document.getElementById('mPostedLbl').textContent = v.posted ? '✓ Posted' : 'Mark as posted';
  document.getElementById('mViews').value    = v.views    || '';
  document.getElementById('mLikes').value    = v.likes    || '';
  document.getElementById('mComments').value = v.comments || '';
  const finBtn = document.getElementById('mFinishedDrive');
  if (v.finished_link) {
    finBtn.href = v.finished_link; finBtn.style.display = 'inline-flex';
  } else { finBtn.style.display = 'none'; }
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
  if (r.ok) {
    if (VD[activeId]) { VD[activeId].views=views; VD[activeId].likes=likes; VD[activeId].comments=comments; }
    document.getElementById('mOverlay').classList.remove('open');
    activeId = null;
  }
}

async function deleteVideo() {
  if (!activeId) return;
  if (!confirm(`Delete "${VD[activeId]?.name}"?`)) return;
  const r = await fetch(`/api/videos/${activeId}`,{method:'DELETE'});
  if (r.ok) { document.getElementById('mOverlay').classList.remove('open'); location.reload(); }
}

// ── PIPELINE ──────────────────────────────────────────────────────────────
function switchTab(name) {
  const isCalendar = name === 'calendar';
  document.getElementById('calendar-view').style.display  = isCalendar ? '' : 'none';
  document.getElementById('pipeline-view').style.display  = isCalendar ? 'none' : '';
  document.getElementById('monthNav').style.display       = isCalendar ? '' : 'none';
  document.getElementById('tab-cal').className  = 'tab-btn' + (isCalendar ? ' active' : '');
  document.getElementById('tab-pipe').className = 'tab-btn' + (isCalendar ? '' : ' active');
  if (!isCalendar) loadPipeline();
}

async function loadPipeline() {
  ['pColQueued','pColInprog','pColReady','pColPosted'].forEach(id => {
    const col = document.getElementById(id);
    while (col.children.length > 1) col.removeChild(col.lastChild);
    col.insertAdjacentHTML('beforeend', '<div class="p-loading">Loading…</div>');
  });
  const r = await fetch('/api/pipeline');
  if (!r.ok) return;
  const d = await r.json();
  renderPCol('pColQueued', 'pCntQ', d.queued,      'queued');
  renderPCol('pColInprog', 'pCntI', d.in_progress, 'inprog');
  renderPCol('pColReady',  'pCntR', d.ready,        'ready');
  renderPCol('pColPosted', 'pCntP', d.posted,       'posted');
}

function renderPCol(colId, cntId, videos, colType) {
  const col = document.getElementById(colId);
  while (col.children.length > 1) col.removeChild(col.lastChild);
  document.getElementById(cntId).textContent = videos.length;
  if (!videos.length) { col.insertAdjacentHTML('beforeend', '<div class="p-empty">Nothing here</div>'); return; }
  videos.forEach(v => col.insertAdjacentHTML('beforeend', buildPCard(v, colType)));
}

function buildPCard(v, colType) {
  const todayMs = new Date(new Date().toISOString().slice(0,10) + 'T00:00:00').getTime();
  const postMs  = new Date(v.post_date + 'T00:00:00').getTime();
  const diff    = Math.ceil((postMs - todayMs) / 86400000);
  let riskTag = '', riskCls = '';
  if (!v.posted && !v.editor_done) {
    if (diff < 0)      { riskTag = '<span class="tag-overdue">OVERDUE</span>';  riskCls = 'p-card-overdue'; }
    else if (diff <= 2){ riskTag = '<span class="tag-risk">⚠ Due Soon</span>'; riskCls = 'p-card-risk'; }
  }
  const badge  = `<span class="vbadge vb-${v.editor}">${v.editor.slice(0,3)}</span>`;
  let links    = `<a class="p-link" href="${v.drive_link}" target="_blank">▶ Raw</a>`;
  if (v.finished_link) links += ` <a class="p-link p-link-fin" href="${v.finished_link}" target="_blank">✓ Edit</a>`;
  let action   = colType === 'ready'
    ? `<button class="p-action-btn" onclick="markPostedPipeline(${v.id})">Mark Posted</button>`
    : '';
  let metrics  = (colType === 'posted' && v.views)
    ? `<div class="p-metrics">${Number(v.views).toLocaleString()} views</div>`
    : '';
  return `<div class="p-card ${riskCls}" id="pcard-${v.id}">
    <div class="p-card-top">${badge}${riskTag}<span class="p-date">${v.post_date}</span></div>
    <div class="p-name">${v.name.replace(/</g,'&lt;')}</div>
    <div class="p-card-bottom"><div class="p-links">${links}</div>${metrics}${action}</div>
  </div>`;
}

async function markPostedPipeline(id) {
  const r = await fetch(`/api/videos/${id}/toggle`, {method:'POST'});
  if (!r.ok) return;
  const data = await r.json();
  if (!data.posted) return;
  if (VD[id]) VD[id].posted = 1;
  // move card from Ready → Posted
  const card = document.getElementById(`pcard-${id}`);
  if (card) {
    card.querySelector('.p-action-btn')?.remove();
    const postedCol = document.getElementById('pColPosted');
    const empty = postedCol.querySelector('.p-empty');
    if (empty) empty.remove();
    postedCol.insertAdjacentElement('beforeend', card);
    const rCnt = document.getElementById('pCntR'), pCnt = document.getElementById('pCntP');
    rCnt.textContent = Math.max(0, parseInt(rCnt.textContent) - 1);
    pCnt.textContent = parseInt(pCnt.textContent) + 1;
  }
  // sync calendar checkbox
  const calCard = document.querySelector(`.vcard[onclick*="openModal(${id})"]`);
  if (calCard) { calCard.classList.add('posted'); const cb = calCard.querySelector('.vcheck'); if(cb) cb.checked=true; }
}
// ──────────────────────────────────────────────────────────────────────────

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
body{font-family:'Inter',sans-serif;background:#F2F2F2;color:#111;min-height:100vh}
:root{--accent:{{ color }};--border:#E2E2E2}
.nav{background:#fff;border-bottom:1px solid var(--border);padding:0 20px;
  display:flex;align-items:center;height:56px;gap:12px}
.logo{font-size:18px;font-weight:800}.logo span{color:var(--accent)}
.sep{color:#DDD}
.editor-tag{font-size:14px;font-weight:700;color:#111}
.wrap{padding:20px 20px 80px}
.kanban{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
@media(max-width:700px){.kanban{grid-template-columns:1fr}}
.kcol{background:#EBEBEB;border-radius:10px;padding:12px;min-height:160px}
.kcol-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.kcol-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#555}
.kcol-inprog .kcol-title{color:#2278A0}
.kcol-done .kcol-title{color:#6A9E00}
.kcol-count{background:#D8D8D8;color:#555;font-size:11px;font-weight:700;
  padding:2px 8px;border-radius:20px;min-width:22px;text-align:center}
.ec{background:#fff;border:1px solid var(--border);border-radius:8px;
  padding:12px 13px;margin-bottom:6px;transition:box-shadow .15s}
.ec:hover{box-shadow:0 2px 10px rgba(0,0,0,.07)}
.ec.inprog-card{border-left:3px solid #2278A0}
.ec.done-card{border-left:3px solid var(--accent)}
.ec-top{display:flex;align-items:center;gap:6px;margin-bottom:5px;flex-wrap:wrap}
.ec-date{font-size:10px;color:#999;font-weight:600;margin-left:auto}
.ec-name{font-size:13px;font-weight:600;color:#111;margin-bottom:7px;line-height:1.3}
.ec-links{display:flex;gap:8px;margin-bottom:7px}
.raw-lnk{font-size:11px;font-weight:700;color:#6A9E00;text-decoration:none}
.raw-lnk:hover{text-decoration:underline}
.fin-lnk{font-size:11px;font-weight:700;color:#2278A0;text-decoration:none}
.fin-lnk:hover{text-decoration:underline}
.tag-risk{font-size:9px;font-weight:700;text-transform:uppercase;
  background:rgba(245,158,11,.15);color:#D97706;padding:2px 5px;border-radius:3px}
.tag-overdue{font-size:9px;font-weight:700;text-transform:uppercase;
  background:rgba(239,68,68,.12);color:#DC2626;padding:2px 5px;border-radius:3px}
.ec-actions{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.btn-start{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
  padding:5px 12px;background:#E8F4FF;color:#2278A0;border:1px solid #BDE0F7;
  border-radius:6px;cursor:pointer}
.btn-start:hover{background:#D0E8FA}
.btn-done-e{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
  padding:5px 12px;background:rgba(193,240,0,.2);color:#5A8A00;
  border:1px solid rgba(193,240,0,.4);border-radius:6px;cursor:pointer}
.btn-done-e:hover{background:rgba(193,240,0,.35)}
.link-inp{font-family:'Inter',sans-serif;font-size:11px;padding:5px 9px;
  border:1px solid var(--border);border-radius:6px;color:#111;
  outline:none;background:#F8F8F8;flex:1;min-width:0}
.link-inp:focus{border-color:var(--accent)}
.link-inp.saved{border-color:#6A9E00}
.btn-save-lnk{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
  padding:5px 10px;background:#111;color:#fff;border:none;border-radius:6px;cursor:pointer;white-space:nowrap}
.btn-save-lnk:hover{background:#333}
.link-row{display:flex;gap:5px;align-items:center;margin-top:6px}
.kcol-empty{font-size:12px;color:#bbb;text-align:center;padding:24px 0}
.kcol-loading{font-size:12px;color:#bbb;text-align:center;padding:24px 0}
</style>
</head>
<body>
<nav class="nav">
  <div class="logo">Ric<span>Fit</span></div>
  <div class="sep">|</div>
  <div class="editor-tag">{{ editor }}</div>
</nav>
<div class="wrap">
  <div class="kanban">
    <div class="kcol" id="kColToEdit">
      <div class="kcol-hdr"><span class="kcol-title">To Edit</span><span class="kcol-count" id="kCntA">—</span></div>
      <div class="kcol-loading">Loading…</div>
    </div>
    <div class="kcol kcol-inprog" id="kColInprog">
      <div class="kcol-hdr"><span class="kcol-title">In Progress</span><span class="kcol-count" id="kCntB">—</span></div>
      <div class="kcol-loading">Loading…</div>
    </div>
    <div class="kcol kcol-done" id="kColDone">
      <div class="kcol-hdr"><span class="kcol-title">Done</span><span class="kcol-count" id="kCntC">—</span></div>
      <div class="kcol-loading">Loading…</div>
    </div>
  </div>
</div>
<script>
const ENAME = '{{ editor.lower() }}';
const TODAY = new Date(new Date().toISOString().slice(0,10)+'T00:00:00').getTime();

async function loadPipeline() {
  const r = await fetch(`/api/editor-pipeline/${ENAME}`);
  if (!r.ok) return;
  const d = await r.json();
  renderKCol('kColToEdit','kCntA', d.to_edit,     'toedit');
  renderKCol('kColInprog','kCntB', d.in_progress, 'inprog');
  renderKCol('kColDone',  'kCntC', d.done,        'done');
}

function renderKCol(colId, cntId, videos, colType) {
  const col = document.getElementById(colId);
  while (col.children.length > 1) col.removeChild(col.lastChild);
  document.getElementById(cntId).textContent = videos.length;
  if (!videos.length) { col.insertAdjacentHTML('beforeend','<div class="kcol-empty">Nothing here</div>'); return; }
  videos.forEach(v => col.insertAdjacentHTML('beforeend', buildCard(v, colType)));
}

function riskTag(v) {
  if (v.editor_done) return '';
  const diff = Math.ceil((new Date(v.post_date+'T00:00:00').getTime() - TODAY) / 86400000);
  if (diff < 0)      return '<span class="tag-overdue">OVERDUE</span>';
  if (diff <= 2)     return '<span class="tag-risk">⚠ Due Soon</span>';
  return '';
}

function buildCard(v, colType) {
  const tag    = riskTag(v);
  const cls    = colType==='inprog' ? 'inprog-card' : colType==='done' ? 'done-card' : '';
  const flink  = v.finished_link ? `<a class="fin-lnk" href="${v.finished_link}" target="_blank" id="fl-${v.id}">✓ Finished Edit</a>` : `<span id="fl-${v.id}"></span>`;
  let actions  = '';
  if (colType === 'toedit') {
    actions = `<button class="btn-start" onclick="startEdit(${v.id})">Start Editing</button>`;
  } else if (colType === 'inprog') {
    actions = `
      <button class="btn-done-e" onclick="markDone(${v.id})">✓ Mark Done</button>
      <div class="link-row" style="width:100%">
        <input class="link-inp" id="li-${v.id}" type="url" placeholder="Paste finished footage link…" value="${v.finished_link||''}" onkeydown="if(event.key==='Enter')saveLink(${v.id})">
        <button class="btn-save-lnk" onclick="saveLink(${v.id})">Save</button>
      </div>`;
  }
  return `<div class="ec ${cls}" id="ec-${v.id}">
    <div class="ec-top"><span style="font-size:10px;font-weight:700;color:#999">${v.post_date}</span>${tag}</div>
    <div class="ec-name">${v.name.replace(/</g,'&lt;')}</div>
    <div class="ec-links"><a class="raw-lnk" href="${v.drive_link}" target="_blank">▶ Raw Footage</a>${flink}</div>
    <div class="ec-actions">${actions}</div>
  </div>`;
}

async function startEdit(id) {
  const r = await fetch(`/api/videos/${id}/start`,{method:'POST'});
  if (!r.ok) return;
  moveCard(id,'kColToEdit','kCntA','kColInprog','kCntB','inprog');
}

async function markDone(id) {
  const r = await fetch(`/api/videos/${id}/editor-done`,{method:'POST'});
  if (!r.ok) return;
  const data = await r.json();
  if (data.done) moveCard(id,'kColInprog','kCntB','kColDone','kCntC','done');
}

async function saveLink(id) {
  const inp  = document.getElementById(`li-${id}`);
  const link = inp?.value.trim() || '';
  const r = await fetch(`/api/videos/${id}/finished-link`,{
    method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({link})
  });
  if (r.ok) {
    if (inp) inp.classList.add('saved');
    const el = document.getElementById(`fl-${id}`);
    if (el && link) el.outerHTML = `<a class="fin-lnk" href="${link}" target="_blank" id="fl-${id}">✓ Finished Edit</a>`;
  }
}

function moveCard(id, fromColId, fromCntId, toColId, toCntId, newColType) {
  const card    = document.getElementById(`ec-${id}`);
  const fromCol = document.getElementById(fromColId);
  const toCol   = document.getElementById(toColId);
  if (!card || !fromCol || !toCol) return;
  card.remove();
  // update from count
  const fCnt = document.getElementById(fromCntId);
  fCnt.textContent = Math.max(0, parseInt(fCnt.textContent)-1);
  if (parseInt(fCnt.textContent) === 0 && !fromCol.querySelector('.ec')) {
    fromCol.insertAdjacentHTML('beforeend','<div class="kcol-empty">Nothing here</div>');
  }
  // remove empty state from target
  const empty = toCol.querySelector('.kcol-empty');
  if (empty) empty.remove();
  // rebuild card for new column type
  toCol.insertAdjacentHTML('beforeend', buildCard(
    {id, name: card.querySelector('.ec-name').textContent,
     drive_link: card.querySelector('.raw-lnk')?.href || '#',
     finished_link: card.querySelector('.fin-lnk')?.href || null,
     post_date: card.querySelector('.ec-top span')?.textContent || '',
     editor_done: newColType==='done'?1:0},
    newColType
  ));
  const tCnt = document.getElementById(toCntId);
  tCnt.textContent = parseInt(tCnt.textContent)+1;
}

loadPipeline();
</script>
</body>
</html>'''

if __name__ == '__main__':
    app.run(debug=True)
