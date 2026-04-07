#!/usr/bin/env python3
"""
Ron Breitenbach — Lead Capture & Dashboard
"""

import os
import csv
import io
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, redirect, url_for, session, Response, render_template_string

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ronleads2026")

DB = "leads.db"
PIN = os.getenv("DASHBOARD_PIN", "kairo2026")

# ── DB ────────────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name  TEXT,
            email      TEXT NOT NULL,
            phone      TEXT,
            source     TEXT DEFAULT 'Unknown',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # Add source column if upgrading from old DB
    try:
        conn.execute("ALTER TABLE leads ADD COLUMN source TEXT DEFAULT 'Unknown'")
    except Exception:
        pass
    conn.commit()
    conn.close()

init_db()

def is_logged_in():
    return session.get("auth") == True

# ── Source badge colors ───────────────────────────────────────────────────────

SOURCE_COLORS = {
    "Investor ID Guide":  ("#1a1a2e", "#a78bfa", "#6F00FF44"),
    "90-Day Blueprint":   ("#0f1e1a", "#34d399", "#10b98133"),
}

def source_badge(source):
    s = source or "Unknown"
    bg, color, border = SOURCE_COLORS.get(s, ("#1a1a1a", "#888", "#33333388"))
    return f'<span style="background:{bg};color:{color};border:1px solid {border};border-radius:50px;padding:3px 10px;font-size:11px;font-weight:600;white-space:nowrap">{s}</span>'

# ── Webhook ───────────────────────────────────────────────────────────────────

@app.route("/webhook/ron-lead", methods=["POST", "OPTIONS"])
def webhook():
    if request.method == "OPTIONS":
        r = app.make_default_options_response()
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Access-Control-Allow-Headers"] = "Content-Type"
        r.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return r

    data  = request.get_json(silent=True) or request.form.to_dict()
    first  = (data.get("first_name") or "").strip()
    last   = (data.get("last_name")  or "").strip()
    email  = (data.get("email")      or "").strip().lower()
    phone  = (data.get("phone")      or "").strip()
    source = (data.get("source")     or "Unknown").strip()

    if not email:
        r = jsonify({"error": "email required"})
        r.headers["Access-Control-Allow-Origin"] = "*"
        return r, 400

    conn = get_db()
    conn.execute(
        "INSERT INTO leads (first_name, last_name, email, phone, source) VALUES (?,?,?,?,?)",
        (first, last, email, phone, source)
    )
    conn.commit()
    conn.close()
    print(f"[LEAD] {first} {last} <{email}> | {phone} | {source}")

    r = jsonify({"success": True})
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r, 200

# ── Login ─────────────────────────────────────────────────────────────────────

LOGIN_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ron Leads — Login</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Inter',sans-serif;background:#0f0f0f;display:flex;align-items:center;justify-content:center;min-height:100vh}
    .card{background:#141414;border:1px solid #2a2a2a;border-radius:16px;padding:40px 36px;width:100%;max-width:360px}
    .logo{font-size:22px;font-weight:700;color:#fff;margin-bottom:8px}.logo span{color:#6F00FF}
    .sub{color:#666;font-size:14px;margin-bottom:32px}
    label{display:block;font-size:13px;color:#888;margin-bottom:6px}
    input{width:100%;padding:12px 14px;background:#111;border:1px solid #333;border-radius:10px;color:#fff;font-size:15px;font-family:inherit;outline:none}
    input:focus{border-color:#6F00FF}
    button{width:100%;margin-top:16px;padding:13px;background:#6F00FF;color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;font-family:inherit}
    button:hover{background:#5a00cc}
    .err{color:#f87171;font-size:13px;margin-top:12px;text-align:center}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">RON <span>LEADS</span></div>
    <div class="sub">Enter your PIN to access the dashboard</div>
    <form method="post">
      <label>PIN</label>
      <input type="password" name="pin" placeholder="••••••••" autofocus>
      <button type="submit">Enter →</button>
      {% if error %}<div class="err">Wrong PIN. Try again.</div>{% endif %}
    </form>
  </div>
</body>
</html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        if request.form.get("pin") == PIN:
            session["auth"] = True
            return redirect(url_for("dashboard"))
        error = True
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Dashboard ─────────────────────────────────────────────────────────────────

DASHBOARD_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ron Leads</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Inter',sans-serif;background:#0f0f0f;color:#fff;min-height:100vh}
    .header{background:#141414;border-bottom:1px solid #222;padding:18px 32px;display:flex;align-items:center;justify-content:space-between}
    .logo{font-size:18px;font-weight:700}.logo span{color:#6F00FF}
    .header-right{display:flex;gap:12px;align-items:center}
    .badge{background:#1a1a2e;color:#a78bfa;border:1px solid #6F00FF44;border-radius:50px;padding:4px 14px;font-size:13px;font-weight:500}
    .btn{padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;text-decoration:none;font-family:inherit;border:none}
    .btn-outline{background:transparent;border:1px solid #333;color:#aaa}
    .btn-outline:hover{border-color:#555;color:#fff}
    .stats{padding:28px 32px 0;display:flex;gap:16px;flex-wrap:wrap}
    .stat-card{background:#141414;border:1px solid #222;border-radius:12px;padding:20px 24px;min-width:140px}
    .stat-label{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
    .stat-value{font-size:32px;font-weight:700;color:#fff}
    .stat-value.purple{color:#a78bfa}
    .table-wrap{padding:28px 32px}
    .table-title{font-size:16px;font-weight:600;color:#fff;margin-bottom:16px}
    table{width:100%;border-collapse:collapse;background:#141414;border-radius:12px;overflow:hidden;border:1px solid #222}
    thead tr{background:#1a1a1a}
    th{padding:13px 18px;text-align:left;font-size:11px;font-weight:600;color:#555;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #222}
    td{padding:13px 18px;font-size:14px;color:#ddd;border-bottom:1px solid #1e1e1e;vertical-align:middle}
    tr:last-child td{border-bottom:none}
    tr:hover td{background:#181818}
    .email-cell{color:#a78bfa}
    .phone-cell{color:#888;font-family:monospace;font-size:13px}
    .date-cell{color:#555;font-size:12px}
    .empty{text-align:center;padding:60px;color:#444;font-size:15px}
    .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;margin-right:8px}
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">RON <span>LEADS</span></div>
    <div class="header-right">
      <span class="badge"><span class="dot"></span>{{ total }} leads</span>
      <a href="/export.csv" class="btn btn-outline">Download CSV</a>
      <a href="/logout" class="btn btn-outline">Logout</a>
    </div>
  </div>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-label">Total Leads</div>
      <div class="stat-value purple">{{ total }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Today</div>
      <div class="stat-value">{{ today }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Investor ID Guide</div>
      <div class="stat-value">{{ src1 }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">90-Day Blueprint</div>
      <div class="stat-value">{{ src2 }}</div>
    </div>
  </div>

  <div class="table-wrap">
    <div class="table-title">All Leads</div>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Source</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {% if leads %}
          {% for l in leads %}
          <tr>
            <td style="color:#555">{{ loop.revindex }}</td>
            <td><strong>{{ l.first_name or '' }} {{ l.last_name or '' }}</strong></td>
            <td class="email-cell">{{ l.email }}</td>
            <td class="phone-cell">{{ l.phone or '—' }}</td>
            <td>{{ l.source_badge|safe }}</td>
            <td class="date-cell">{{ l.created_at[:16] }}</td>
          </tr>
          {% endfor %}
        {% else %}
          <tr><td colspan="6" class="empty">No leads yet — share your landing pages to start collecting.</td></tr>
        {% endif %}
      </tbody>
    </table>
  </div>
</body>
</html>"""

@app.route("/")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db()
    rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    leads = []
    for r in rows:
        d = dict(r)
        d["source_badge"] = source_badge(d.get("source"))
        leads.append(d)

    total  = len(leads)
    today  = sum(1 for l in leads if l["created_at"][:10] == today_str)
    src1   = sum(1 for l in leads if l.get("source") == "Investor ID Guide")
    src2   = sum(1 for l in leads if l.get("source") == "90-Day Blueprint")

    return render_template_string(DASHBOARD_HTML, leads=leads, total=total,
                                  today=today, src1=src1, src2=src2)

# ── CSV export ────────────────────────────────────────────────────────────────

@app.route("/export.csv")
def export_csv():
    if not is_logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    leads = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Date", "First Name", "Last Name", "Email", "Phone", "Source"])
    for l in leads:
        w.writerow([l["created_at"], l["first_name"], l["last_name"],
                    l["email"], l["phone"], l.get("source", "")])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=ron_leads.csv"})

# ── Health ────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
