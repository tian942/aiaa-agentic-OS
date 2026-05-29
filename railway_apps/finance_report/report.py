#!/usr/bin/env python3
"""
Daily Finance Report — Railway Cron Job
Runs at 5am UTC (7am CEST / 6am CET) daily.
Reads all tabs: FINANCIAL, D100, COLD OUTREACH, COLD CALLS, LEADS.
"""

import os
import sys
import base64
import pickle
import tempfile
import requests
import anthropic
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import gspread
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID = "1MSiJlArpy_zXchd_B5-IxLy9zGb5KOj6terF3nPKdR4"
SENDER_EMAIL = "tmarsel26@gmail.com"
REPORT_EMAIL = "tian@kairoscales.com"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.send",
]


def get_google_creds():
    token_b64 = os.getenv("GOOGLE_TOKEN_B64")
    creds_b64 = os.getenv("GOOGLE_CREDS_B64")

    if not token_b64:
        print("Error: GOOGLE_TOKEN_B64 env var not set")
        sys.exit(1)

    # Decode token into a temp file
    token_data = base64.b64decode(token_b64)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pickle")
    tmp.write(token_data)
    tmp.close()

    with open(tmp.name, "rb") as f:
        creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Re-encode refreshed token back to env (log it so you can update Railway if needed)
        refreshed = base64.b64encode(pickle.dumps(creds)).decode()
        print(f"Token refreshed. Update GOOGLE_TOKEN_B64 on Railway if needed (first 50 chars): {refreshed[:50]}...")

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
            print(f"   Read tab '{ws.title}': {len(lines)} rows")

    return "\n\n".join(sections), tab_names


def read_notes(creds):
    """Read the DAILY NOTES tab if it exists — returns last 14 rows as context string."""
    try:
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet("DAILY NOTES")
        rows = ws.get_all_values()
        if not rows:
            return ""
        lines = []
        for row in rows[1:]:  # skip header row
            cleaned = [str(c).strip() for c in row]
            if any(cleaned):
                lines.append(" | ".join(cleaned))
        return "\n".join(lines[-14:])  # last 14 rows (roughly 7 days of entries)
    except Exception:
        return ""  # tab doesn't exist yet — silent fail


def generate_report(sheet_data: str, tab_names: list, notes_context: str = "") -> str:
    today = datetime.now().strftime("%B %d, %Y")

    known_tab_descriptions = {
        "FINANCIAL": "Revenue, expenses, client MRR, cash collected, EBIT, payroll",
        "D100": "Dream 100 prospect list — names, stages, last touch, next action, channel",
        "COLD OUTREACH": "Manual cold outreach log — DMs sent, manual email activity, responses",
        "COLD CALLS": "Call activity log — dials, connects, conversations, bookings",
        "LEADS": "Open pipeline — prospects in sales process, status, close probability, value",
        "PLUSVIBE STATS": "Automated cold email campaigns. Columns: Date, Campaign, Status, Total Leads, Sent, Contacted, Opened, Open Rate %, Replied, Reply Rate %, Positive Replies, Bounced, Unsubscribed, Completed. Each row = one campaign snapshot.",
        "CLIENT FEEDBACK": "Client satisfaction responses — flag any negative sentiment immediately",
        "SCORESHEET": "Performance scoring across key business metrics",
        "Daily Briefings": "Daily logged metrics — calls booked, emails sent, replies, MRR, new clients",
        "DAILY NOTES": "Tian's own daily notes, responses to yesterday's report, observations, priorities, concerns. Use this as critical context — it reflects what Tian is thinking and feeling about the business right now.",
    }

    tab_guide_lines = []
    for tab in tab_names:
        if tab in known_tab_descriptions:
            tab_guide_lines.append(f"- {tab}: {known_tab_descriptions[tab]}")
        else:
            tab_guide_lines.append(f"- {tab}: (NEW TAB — auto-detected. Interpret based on column headers and data patterns. Include a full dedicated section in the report. Do not skip or summarise — treat it as important as any other tab.)")

    tab_guide = "\n".join(tab_guide_lines)

    notes_section = ""
    if notes_context.strip():
        notes_section = f"""
---

## 📝 TIAN'S NOTES / CONTEXT FROM YESTERDAY
{notes_context}

IMPORTANT: Read these notes carefully before writing today's report. Reference them directly where relevant. If Tian flagged a concern yesterday, check today's data and report back on it. If he set a priority, confirm whether it was acted on. Make the report feel like a conversation, not a one-way broadcast.

---
"""

    prompt = f"""You are an elite business advisor, financial analyst, and growth strategist for Kairo Enterprises (formerly Win Marketing) — a marketing agency run by Tian (CEO). Tagline: "Weird Is Normal."

You have deep mastery of Alex Hormozi, Dan Martell, Leila Hormozi, and Sharran Srivatsaa frameworks. You apply them precisely — not as decoration, but as the actual analytical lens. You are Tian's most valuable advisor: the one who never forgets a number, always speaks the truth, and makes every report actionable.

Today is {today}.

---

## ANALYTICAL FRAMEWORKS — APPLY THESE TO EVERY SECTION

### LTGP:CAC — THE ENGINE OF EVERYTHING (Hormozi)
The business that makes more money per customer than its competitors can outspend them in every channel. The ratio is not a metric — it is the moat.

**How to calculate:**
- CAC = total acquisition spend ÷ new customers acquired
- Gross margin = (price - cost to deliver) ÷ price
- LTGP = lifetime revenue per customer × gross margin
- Ratio = LTGP ÷ CAC

**Minimum viable ratios by automation level:**
- All 3 automated (lead gen + sales + delivery): 3:1 minimum
- 2 of 3 automated: 6:1 minimum
- 1 of 3 automated: 9:1 minimum
- All manual (most agencies): 12:1 minimum

**Warning:** A higher CAC business can be the better business if LTGP is proportionally higher. Optimise the ratio, not just the CAC.

**30-day payback rule:** Recover CAC within 30 days. Beyond 30 days = you need outside capital or the flywheel slows. This is the cash flow constraint.

### 7 LEVERS TO INCREASE LTGP
1. Raise price (same service, higher charge)
2. Decrease COGS (negotiate delivery costs down)
3. Upsell (sell higher-tier version)
4. Downsell (capture buyers who'd walk — different product, not same product cheaper)
5. Cross-sell (sell something different to same client)
6. Financing (pull cash forward — payment plans)
7. Change collection terms (frontload cash — prepay quarterly/annual)

### 4 LEVERS TO DECREASE CAC
1. Improve offer (more compelling → higher conversion)
2. Better ad creative (volume + hook testing)
3. CRO (split test pages, scripts, follow-up sequences)
4. Cheaper CPMs (platforms with lower cost per eyeball)

### CHURN COHORT MODEL (Hormozi)
- Month 1-3: highest churn window (20%+ expected) — any churn here is most dangerous
- Day 90: first major drop. Clients who survive past day 90 churn at ~10%
- Month 6+: churn drops to ~2% — these are long-term clients
- Key insight: reducing churn from 20% to 10% DOUBLES customer LTV

### AC/DC DASHBOARD (Matt Gray / Hormozi)
Every business problem lives in one of four buckets:
- **Attract** — are enough people finding you?
- **Convert** — are enough people becoming clients?
- **Deliver** — are clients getting results?
- **Collect** — is the cash actually coming in?

The constraint is always in ONE bucket. Fixing the wrong bucket = wasted effort.

### MRR HEALTH FORMULA (Hormozi)
- MRR grows when: new > churn
- MRR flat when: new = churn
- MRR declining when: churn > new
- Logo Retention = # clients retained ÷ # clients last month
- Net Revenue Retention = this month MRR ÷ last month MRR × 100 (>100% = expansion)

### GOLDILOCKS ZONE (Simon Squibb / Martell)
- Stasis Zone: flat, comfortable, no growth pressure = slow death
- Goldilocks Zone: challenging but manageable = healthy growth
- Trauma Zone: growth so fast delivery breaks = dangerous

---
{notes_section}

## TODAY'S DATA

TABS IN SHEET:
{tab_guide}

SHEET DATA:
{sheet_data}

---

Produce a full daily business briefing. Every number from the data. No invented figures. No filler. Apply the frameworks above to every section — not as decoration, as the actual lens.

---

# Kairo Enterprises — Daily Report ({today})

---

## 💰 FINANCIAL SNAPSHOT
- MTD cash collected, total expenses, EBIT, net margin — exact numbers
- MoM change in revenue AND margin (% not just $)
- MRR status: apply the Hormozi formula — new vs churn, direction of travel
- Blended CAC this month: total acquisition spend ÷ new clients added
- Apply the 30-day payback rule: for each new client, how many days to recover CAC? Flag any beyond 30 days.
- Effective hourly rate: monthly net ÷ 160 working hours. Is Tian's time priced correctly? What should be delegated?
- AC/DC diagnosis: is the constraint in Attract, Convert, Deliver, or Collect this month?
- Flag: if expenses are growing faster than revenue — this is a constraint problem, not a cost problem

---

## 👥 CLIENT HEALTH DASHBOARD
The most important section. Churn is the silent killer (Hormozi).

For EVERY active client:
| Client | MRR | Est. LTGP | LTGP:CAC | vs Min (12:1) | Churn Cohort | Health |
|--------|-----|-----------|----------|---------------|--------------|--------|

Then:
- **Logo Retention**: X of Y clients from last month still active
- **Net Revenue Retention**: (this month MRR ÷ last month MRR) × 100. Flag if below 100%.
- **Expansion revenue**: any client paying more than last month? This is the leading indicator of a healthy business.
- **Churn cohort check**: name every client in Month 1-3 (20%+ churn window). What retention action is in place for each?
- **Day 90 clients**: anyone approaching or past 90 days? Survival past day 90 drops churn to ~10% — what's the trigger to get them there?
- 🟢 Green / 🟡 Yellow / 🔴 Red for every client with specific reason

---

## 📊 UNIT ECONOMICS — CLIENT BY CLIENT
| Client | Acq Channel | CAC | LTGP est. | LTGP:CAC | Min required | Verdict |
|--------|-------------|-----|-----------|----------|--------------|---------|

Apply the automation level test per client:
- Is this client's acquisition/sales/delivery manual or automated? → sets the minimum ratio
- Flag every client below their minimum ratio
- Apply the 7 LTGP levers: which lever could Tian pull for each underperforming client?
- Apply the 4 CAC levers: which channel is most improvable?
- Customer Avatar: which clients score 4/4 on (love to work with + highest LTV + highest margin + easiest delivery)? That's the ICP. Flag if Kairo is not acquiring more of them.

---

## 🧾 EXPENSE BREAKDOWN
Hormozi: every dollar either (a) buys back Tian's time or (b) directly generates revenue. Everything else is a vanity expense.

For each expense line:
| Item | Cost | Category | Verdict |
|------|------|----------|---------|
| ... | ... | TIME SAVER / REVENUE GENERATOR / UNCLEAR | ✅ Keep / ⚠️ Review / ❌ Cut |

- Automation ratio: tools vs people spend. Tools scale, people don't.
- Apply the LTGP lever check: any expense that could be restructured to increase LTGP (e.g. payment plans, upsells, prepay incentives)?
- Flag any subscription unused this week

---

## 📈 D100 (DREAM 100)
9-10 Touch Sequence: most responses come after touch 7-10. Most people quit at 3.
Multi-Channel Waterfall: LinkedIn DM → Email → WhatsApp → Phone.

- Status: Hot (responded <3 days), Warm (3-7 days), Cold (7+ days)
- Total pipeline MRR value if all active D100 prospects closed
- Top 3 prospects: stage, touch count, last action, ONE specific next action
- Anyone at touch 8-10: flag — they're at the decision point. One message away.
- LTGP:CAC projection for each prospect based on estimated contract value vs acquisition effort

---

## 📧 COLD EMAIL CAMPAIGNS (PlusVibe)
Rule of 100: 100 outbound touches per day is the floor.

For EACH campaign:
| Campaign | Sent | Open % | Reply % | Positive Replies | Bounced | % List Used | Status |
|----------|------|--------|---------|-----------------|---------|-------------|--------|

Analysis:
- Apply the 4 CAC levers: is the problem offer, creative, conversion, or CPM (list quality)?
- Reply rate below 3% = flag (messaging or deliverability — diagnose which)
- Bounce rate above 5% = list quality issue, domain reputation risk — flag
- List exhaustion: sent ÷ total_leads > 80% = urgent replenishment needed
- Volume trend day-over-day: growing, flat, stalled?
- Every positive reply = pipeline entry. Name them. These are the most valuable outputs of the entire system.
- LTGP:CAC check: what's the projected ratio on a typical cold email close? Is it above the 12:1 manual minimum?

---

## 📞 COLD CALLS
Phone qualifies, meeting closes (Martell).

- Dials → connects → conversations → bookings (% at each stage)
- Connect rate below 10% = wrong list or wrong time — flag
- Booking rate below 15% = script or positioning problem — flag
- Consistency check: any day with zero calls is a signal, not a data point — flag it

---

## 🔥 LEADS PIPELINE
CLOSER Framework per lead:
C — Clarify (why are they looking?) L — Label (name their problem) O — Overview (what you do) S — Sell the vacation (outcome) E — Explain the vehicle (your service) R — Reinforce (the decision)

| Lead | Est. MRR | CLOSER Stage | Days Since Touch | Next Action | Est. Close |
|------|----------|-------------|-----------------|-------------|------------|

- Total pipeline value
- Who is ONE action away from closing? Name it exactly.
- Apply the 30-day payback check: if this lead closes, when does CAC recover?
- Flag any lead untouched 5+ days — momentum is the only thing keeping a lead alive
- Price vs value check: any conversation drifting to price = wrong positioning, flag it

---

## 📐 BUSINESS HEALTH DIAGNOSIS

**AC/DC Constraint:** Which bucket is the bottleneck right now — Attract, Convert, Deliver, or Collect? Give one verdict with the data to back it.

**LTGP:CAC Portfolio Check:** What is today's blended ratio across all active clients? Is it above or below the 12:1 manual minimum? What's the single highest-leverage LTGP lever to pull this month?

**MRR Direction:** Is the business in expansion (new > churn), flat, or contraction? What is the exact churn number?

**Goldilocks Check:** Stasis (flat, comfortable, dangerous) / Goldilocks (challenging but manageable) / Trauma (delivery breaking under growth)?

**The ONE Priority:** What single thing — if true in 12 months — changes everything? Based on the data today, what is Tian's highest-leverage hour?

---

## ⚡ TOP 3 ACTIONS FOR TODAY
Domino Principle: what one action makes everything else easier or unnecessary?

Ranked by revenue impact. Format:
1. [PERSON + EXACT ACTION + BY WHEN + REVENUE IMPACT]
2. [PERSON + EXACT ACTION + BY WHEN + REVENUE IMPACT]
3. [PERSON + EXACT ACTION + BY WHEN + REVENUE IMPACT]

Bad: "Follow up with leads"
Good: "Message Sarah K by 10am — proposal sent 6 days ago, no response. One check-in at this stage has a ~60% response rate. Contract value: $2,500/month = $30K LTV. One message."

---

Rules:
- Every number from the data. If missing, say why and what to log.
- Never skip a tab. New tabs get full analysis, not a summary.
- Apply the frameworks to the data — don't just recite them.
- If Tian left notes in the DAILY NOTES tab, respond to them directly in the relevant sections.
- You are the advisor Tian pays $10,000/month for. Earn it."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text


def inline_format(text: str) -> str:
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code style="background:#f4f4f4;padding:1px 4px;border-radius:3px">\1</code>', text)
    return text


def to_html(markdown: str) -> str:
    import re
    lines = markdown.split("\n")
    html = ["<html><body style='font-family:Arial,sans-serif;max-width:680px;margin:auto;padding:24px;color:#1a1a1a;line-height:1.6;'>"]
    i = 0
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("# ") and not stripped.startswith("## "):
            close_list()
            html.append(f"<h1 style='color:#1a1a2e;font-size:22px;margin-bottom:4px'>{inline_format(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            close_list()
            html.append(f"<h2 style='color:#111;font-size:18px;border-bottom:2px solid #e0e0e0;padding-bottom:8px;margin-top:28px'>{inline_format(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            close_list()
            html.append(f"<h3 style='color:#333;font-size:15px;margin-top:20px;margin-bottom:6px'>{inline_format(stripped[4:])}</h3>")
        elif stripped == "---":
            close_list()
            html.append("<hr style='border:none;border-top:1px solid #eee;margin:16px 0'>")
        elif stripped.startswith("> "):
            close_list()
            html.append(f"<blockquote style='border-left:3px solid #e0e0e0;margin:8px 0;padding:6px 12px;color:#555;font-style:italic'>{inline_format(stripped[2:])}</blockquote>")
        elif stripped.startswith("|"):
            close_list()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            html.append("<table style='border-collapse:collapse;width:100%;margin:12px 0;font-size:14px'>")
            first_data_row = True
            for tl in table_lines:
                if re.match(r'^\|[\s\-:|]+\|', tl):
                    continue
                cells = [c.strip() for c in tl.strip("|").split("|")]
                if first_data_row:
                    html.append("<thead><tr>")
                    for cell in cells:
                        html.append(f"<th style='background:#1a1a2e;color:#fff;padding:8px 12px;text-align:left;font-size:13px'>{inline_format(cell)}</th>")
                    html.append("</tr></thead><tbody>")
                    first_data_row = False
                else:
                    html.append("<tr style='border-bottom:1px solid #eee'>")
                    for cell in cells:
                        html.append(f"<td style='padding:7px 12px;color:#333'>{inline_format(cell)}</td>")
                    html.append("</tr>")
            html.append("</tbody></table>")
            continue
        elif stripped.startswith("- "):
            if not in_list:
                html.append("<ul style='margin:6px 0;padding-left:20px'>")
                in_list = True
            html.append(f"<li style='margin:4px 0;color:#333'>{inline_format(stripped[2:])}</li>")
        elif stripped == "":
            close_list()
            html.append("<div style='margin:6px 0'></div>")
        else:
            close_list()
            html.append(f"<p style='margin:5px 0;color:#333'>{inline_format(stripped)}</p>")
        i += 1

    close_list()
    html.append("</body></html>")
    return "\n".join(html)


def send_via_gmail_api(creds, subject: str, body_text: str, body_html: str):
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
    print(f"Sent: {SENDER_EMAIL} → {REPORT_EMAIL}")


def main():
    today = datetime.now().strftime("%a %b %d, %Y")
    print(f"\n📊 Daily Finance Report — {today}")
    print("=" * 50)

    print("1. Authorizing with Google...")
    creds = get_google_creds()

    print("2. Reading finance sheet...")
    sheet_data, tab_names = read_sheet(creds)
    print(f"   {len(sheet_data.split(chr(10)))} rows read across {len(tab_names)} tabs: {', '.join(tab_names)}")

    print("2b. Reading DAILY NOTES tab...")
    notes = read_notes(creds)
    if notes:
        print(f"   Found notes ({len(notes.split(chr(10)))} entries)")
    else:
        print("   No DAILY NOTES tab yet — skipping")

    print("3. Generating report with Claude...")
    report = generate_report(sheet_data, tab_names, notes)
    print("   Done.")

    print("4. Sending email...")
    subject = f"📊 Win Marketing — Daily Finance Report ({today})"
    send_via_gmail_api(creds, subject, report, to_html(report))

    print("\nDone.")


if __name__ == "__main__":
    main()
