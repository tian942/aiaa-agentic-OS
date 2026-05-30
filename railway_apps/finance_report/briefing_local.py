#!/usr/bin/env python3
"""
Local daily briefing — run via /briefing Claude Code command.
Handles OAuth automatically (browser opens first time or if scopes wrong).
"""

import os
import sys
import pickle
import base64
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Load .env from project root
ROOT = Path(__file__).parent.parent.parent
ENV_PATH = ROOT / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import anthropic
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SHEET_ID = "1MSiJlArpy_zXchd_B5-IxLy9zGb5KOj6terF3nPKdR4"
SENDER_EMAIL = "tmarsel26@gmail.com"
REPORT_EMAIL = "tian@kairoscales.com"

REQUIRED_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

TOKEN_PATH = ROOT / "token.pickle"
CREDS_PATH = ROOT / "credentials.json"


def get_creds():
    creds = None

    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    # Check if scopes are correct
    def has_required_scopes(c):
        if not c or not getattr(c, "scopes", None):
            return False
        for s in REQUIRED_SCOPES:
            if s not in c.scopes:
                return False
        return True

    if creds and not has_required_scopes(creds):
        print("⚠️  Token has wrong scopes — re-authenticating (browser will open)...")
        creds = None

    if creds and creds.expired and creds.refresh_token:
        print("🔄 Refreshing token...")
        creds.refresh(Request())
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    if not creds or not creds.valid:
        if not CREDS_PATH.exists():
            print(f"ERROR: credentials.json not found at {CREDS_PATH}")
            print("Download it from console.cloud.google.com → APIs & Services → Credentials → OAuth 2.0 Client")
            sys.exit(1)
        print("🌐 Opening browser for Google login...")
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), REQUIRED_SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)
        print("✅ Token saved. Won't need to do this again.")

    return creds


def read_sheet(creds):
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    sections = []
    tab_names = []
    for ws in sh.worksheets():
        rows = ws.get_all_values()
        lines = []
        for row in rows:
            cleaned = [str(c).strip() for c in row]
            if any(cleaned):
                lines.append(" | ".join(cleaned))
        if lines:
            sections.append(f"=== TAB: {ws.title} ===\n" + "\n".join(lines))
            tab_names.append(ws.title)
            print(f"   ✓ {ws.title}: {len(lines)} rows")
    return "\n\n".join(sections), tab_names


def read_notes(creds):
    try:
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet("DAILY NOTES")
        rows = ws.get_all_values()
        if not rows:
            return ""
        lines = []
        for row in rows[1:]:
            cleaned = [str(c).strip() for c in row]
            if any(cleaned):
                lines.append(" | ".join(cleaned))
        return "\n".join(lines[-14:])
    except Exception:
        return ""


def generate_report(sheet_data, tab_names, notes_context=""):
    today = datetime.now().strftime("%B %d, %Y")

    known_tab_descriptions = {
        "FINANCIAL": "Revenue, expenses, client MRR, cash collected, EBIT, payroll",
        "D100": "Dream 100 prospect list — names, stages, last touch, next action, channel",
        "COLD OUTREACH": "Manual cold outreach log — DMs sent, manual email activity, responses",
        "COLD CALLS": "Call activity log — dials, connects, conversations, bookings",
        "LEADS": "Open pipeline — prospects in sales process, status, close probability, value",
        "PLUSVIBE STATS": "Automated cold email campaigns. Columns: Date, Campaign, Status, Total Leads, Sent, Contacted, Opened, Open Rate %, Replied, Reply Rate %, Positive Replies, Bounced, Unsubscribed, Completed.",
        "CLIENT FEEDBACK": "Client satisfaction responses — flag any negative sentiment immediately",
        "SCORESHEET": "Performance scoring across key business metrics",
        "Daily Briefings": "Daily logged metrics — calls booked, emails sent, replies, MRR, new clients",
        "DAILY NOTES": "Tian's own daily notes and responses to the previous report. Use as critical context.",
    }

    tab_guide = "\n".join(
        f"- {t}: {known_tab_descriptions.get(t, '(NEW TAB — auto-detected. Include full dedicated section. Do not skip.)')}"
        for t in tab_names
    )

    notes_section = ""
    if notes_context.strip():
        notes_section = f"""
---

## 📝 TIAN'S NOTES FROM YESTERDAY
{notes_context}

Read these carefully. Where Tian flagged a concern, check today's data and report back directly. Make the report feel like a conversation.

---
"""

    prompt = f"""You are an elite business advisor for Kairo Enterprises — a marketing agency run by Tian (CEO). Tagline: "Weird Is Normal."

You have deep mastery of Hormozi, Martell, Leila Hormozi, and Sharran frameworks. You apply them as the actual analytical lens — not decoration.

Today is {today}.

---

## FRAMEWORKS TO APPLY

**LTGP:CAC (Hormozi) — the engine of everything:**
- CAC = acquisition spend ÷ new customers
- LTGP = lifetime revenue × gross margin
- Minimum ratios: all automated = 3:1 | 2 automated = 6:1 | 1 automated = 9:1 | all manual = 12:1
- 30-day payback rule: recover CAC within 30 days or you need outside capital

**7 LTGP levers:** raise price | lower COGS | upsell | downsell (different product, not cheaper) | cross-sell | financing | frontload collection

**4 CAC levers:** better offer | better creative | CRO | cheaper CPMs

**Churn cohorts (Hormozi):**
- Month 1-3: highest risk (20%+) — most dangerous window
- Day 90: churn drops to ~10% if they survive
- Month 6+: drops to ~2% — these are long-term clients
- Cutting churn from 20% → 10% DOUBLES LTV

**MRR formula:** grows when new > churn | flat when equal | declining when churn > new

**AC/DC constraint (Hormozi/Matt Gray):** every problem is in one bucket — Attract / Convert / Deliver / Collect. Identify which ONE.

**Goldilocks Zone:** Stasis (flat, comfortable = slow death) | Goldilocks (challenging, manageable) | Trauma (growth breaking delivery)

---
{notes_section}

## TODAY'S DATA

TABS:
{tab_guide}

DATA:
{sheet_data}

---

# Kairo Enterprises — Daily Briefing ({today})

---

## 💰 FINANCIAL SNAPSHOT
- MTD cash collected, expenses, EBIT, net margin — exact numbers only
- MoM revenue AND margin change (% not just $)
- MRR direction: apply the Hormozi formula — new vs churn
- Blended CAC this month: acquisition spend ÷ new clients
- 30-day payback check for each new client — flag any over 30 days
- AC/DC diagnosis: which bucket is the constraint right now?

---

## 👥 CLIENT HEALTH DASHBOARD
Most important section. Every client, no exceptions.

| Client | MRR | LTGP est. | LTGP:CAC | Cohort (Month #) | 🟢🟡🔴 |
|--------|-----|-----------|----------|-----------------|--------|

- Logo Retention: X of Y from last month still active
- Net Revenue Retention: this month ÷ last month × 100 — flag if below 100%
- Expansion revenue: any client paying more? Name them.
- Month 1-3 clients: name every one, what retention action is in place?
- Who is one conversation away from churning?

---

## 📊 UNIT ECONOMICS
| Client | Channel | CAC | LTGP | Ratio | Min required | LTGP lever to pull |
|--------|---------|-----|------|-------|--------------|-------------------|

Flag every client below the minimum ratio for their automation level.

---

## 🧾 EXPENSES
| Item | Cost | Verdict |
|------|------|---------|
Every line: TIME SAVER / REVENUE GENERATOR / UNCLEAR / ❌ CUT

---

## 📈 D100
- Hot / Warm / Cold by prospect
- Touch count — flag anyone at 8-10 (decision point)
- Top 3: exact next action

---

## 📧 COLD EMAIL (PlusVibe)
| Campaign | Sent | Open% | Reply% | Positive | Bounced | List% Used |
|----------|------|-------|--------|----------|---------|------------|

- Below 3% reply = messaging or deliverability problem — diagnose which
- Above 5% bounce = domain at risk
- Any positive replies = pipeline — name the campaigns

---

## 📞 COLD CALLS
- Dials → connects → conversations → bookings (% each stage)
- Connect < 10% = wrong list or time
- Any day with zero calls — flag it

---

## 🔥 LEADS PIPELINE
| Lead | MRR | CLOSER Stage | Days Since Touch | Next Action |
|------|-----|-------------|-----------------|-------------|

- Total pipeline value
- Who closes this week? Name the exact action.
- Flag anything untouched 5+ days

---

## 📐 DIAGNOSIS
- **AC/DC Constraint:** which one bucket is limiting growth RIGHT NOW?
- **LTGP:CAC blended:** above or below 12:1 minimum? Which lever to pull?
- **MRR direction:** expanding / flat / contracting?
- **Goldilocks check:** stasis / goldilocks / trauma?
- **The ONE thing:** highest-leverage hour Tian could spend today

---

## ⚡ TOP 3 ACTIONS
1. [PERSON + EXACT ACTION + BY WHEN + $ IMPACT]
2. [PERSON + EXACT ACTION + BY WHEN + $ IMPACT]
3. [PERSON + EXACT ACTION + BY WHEN + $ IMPACT]

---

Rules: every number from the data. New tabs get full sections. If Tian left notes, respond to them directly. Be the $10K/month advisor."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text


def inline_format(text):
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text


def to_html(markdown):
    import re
    lines = markdown.split("\n")
    html = ["<html><body style='font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:24px;color:#1a1a1a;line-height:1.6;'>"]
    i = 0
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html.append("</ul>")
            in_list = False

    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("# ") and not s.startswith("## "):
            close_list()
            html.append(f"<h1 style='color:#1a1a2e;font-size:22px'>{inline_format(s[2:])}</h1>")
        elif s.startswith("## "):
            close_list()
            html.append(f"<h2 style='color:#111;font-size:18px;border-bottom:2px solid #e0e0e0;padding-bottom:8px;margin-top:28px'>{inline_format(s[3:])}</h2>")
        elif s.startswith("### "):
            close_list()
            html.append(f"<h3 style='color:#333;font-size:15px;margin-top:18px'>{inline_format(s[4:])}</h3>")
        elif s == "---":
            close_list()
            html.append("<hr style='border:none;border-top:1px solid #eee;margin:14px 0'>")
        elif s.startswith("|"):
            close_list()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            html.append("<table style='border-collapse:collapse;width:100%;margin:10px 0;font-size:13px'>")
            first = True
            for tl in table_lines:
                if re.match(r'^\|[\s\-:|]+\|', tl):
                    continue
                cells = [c.strip() for c in tl.strip("|").split("|")]
                if first:
                    html.append("<thead><tr>" + "".join(f"<th style='background:#1a1a2e;color:#fff;padding:7px 10px;text-align:left'>{inline_format(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                    first = False
                else:
                    html.append("<tr style='border-bottom:1px solid #eee'>" + "".join(f"<td style='padding:6px 10px'>{inline_format(c)}</td>" for c in cells) + "</tr>")
            html.append("</tbody></table>")
            continue
        elif s.startswith("- "):
            if not in_list:
                html.append("<ul style='margin:6px 0;padding-left:20px'>")
                in_list = True
            html.append(f"<li style='margin:3px 0'>{inline_format(s[2:])}</li>")
        elif s == "":
            close_list()
        else:
            close_list()
            html.append(f"<p style='margin:5px 0'>{inline_format(s)}</p>")
        i += 1

    close_list()
    html.append("</body></html>")
    return "\n".join(html)


def send_email(creds, subject, body_text, body_html):
    service = build("gmail", "v1", credentials=creds)
    import base64 as b64
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = REPORT_EMAIL
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))
    raw = b64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"✅ Sent to {REPORT_EMAIL}")


def main():
    today = datetime.now().strftime("%a %b %d, %Y")
    print(f"\n📊 Kairo Daily Briefing — {today}")
    print("=" * 50)

    print("1. Authenticating with Google...")
    creds = get_creds()

    print("2. Reading sheet...")
    sheet_data, tab_names = read_sheet(creds)

    print("3. Reading DAILY NOTES...")
    notes = read_notes(creds)
    if notes:
        print(f"   Found {len(notes.splitlines())} note entries")
    else:
        print("   No DAILY NOTES tab — skipping")

    print("4. Generating report with Claude...")
    report = generate_report(sheet_data, tab_names, notes)
    print("   Done.")

    print("5. Sending email...")
    subject = f"📊 Kairo Daily Briefing — {today}"
    send_email(creds, subject, report, to_html(report))

    print("\n✅ Briefing sent.")


if __name__ == "__main__":
    main()
