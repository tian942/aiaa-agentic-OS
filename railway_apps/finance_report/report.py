#!/usr/bin/env python3
"""
Daily Finance Report — Railway Cron Job
Runs at 5am UTC (7am CEST / 6am CET) daily.
Reads all tabs: FINANCIAL, D100, COLD OUTREACH, COLD CALLS, LEADS, PLUSVIBE STATS, etc.

Auth: Service Account for Google Sheets (never expires).
Email: Gmail SMTP + App Password (no OAuth, no token refresh issues).
"""

import os
import sys
import json
import smtplib
import anthropic
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1MSiJlArpy_zXchd_B5-IxLy9zGb5KOj6terF3nPKdR4"
SENDER_EMAIL = "tmarsel26@gmail.com"
REPORT_EMAIL = "tian@kairoscales.com"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_sheets_client():
    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON env var not set")
        sys.exit(1)

    try:
        info = json.loads(sa_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {e}")
        sys.exit(1)

    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.Client(auth=creds)


def read_sheet(gc):
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


def generate_report(sheet_data: str, tab_names: list) -> str:
    today = datetime.now().strftime("%B %d, %Y")

    known_tab_descriptions = {
        "FINANCIAL": "Revenue, expenses, client MRR, cash collected, EBIT",
        "D100": "Dream 100 prospect list — names, stages, last touch, next action",
        "COLD OUTREACH": "Manual cold outreach log — calls made, DMs sent, manual email activity",
        "COLD CALLS": "Call activity log — dials, connects, conversations, bookings",
        "LEADS": "Open pipeline — prospects in sales process, status, close probability",
        "PLUSVIBE STATS": "Automated cold email campaigns. Columns: Date, Campaign, Status, Total Leads, Sent, Contacted, Opened, Open Rate %, Replied, Reply Rate %, Positive Replies, Bounced, Unsubscribed, Completed. Each row = one campaign snapshot.",
        "CLIENT FEEDBACK": "Client satisfaction responses — flag any negative sentiment immediately",
        "SCORESHEET": "Performance scoring across key business metrics",
        "Daily Briefings": "Daily logged metrics — calls booked, emails sent, replies, MRR, new clients",
    }

    tab_guide_lines = []
    for tab in tab_names:
        if tab in known_tab_descriptions:
            tab_guide_lines.append(f"- {tab}: {known_tab_descriptions[tab]}")
        else:
            tab_guide_lines.append(f"- {tab}: (new tab — interpret based on column headers and data, include in your analysis)")

    tab_guide = "\n".join(tab_guide_lines)

    prompt = f"""You are an elite business advisor, financial analyst, and growth strategist for Win Marketing — a marketing agency run by Tian (CEO). Tagline: "Weird Is Normal."

You think like Alex Hormozi, Dan Martell, Leila Hormozi, and Sharran Srivatsaa combined. You apply their exact frameworks to every section of this report. You are direct, specific, and ruthless about what matters.

Today is {today}. Below is raw data from EVERY tab of Tian's master sheet. Analyze ALL tabs — do not skip any.

TABS FOUND IN SHEET TODAY:
{tab_guide}

SHEET DATA:
{sheet_data}

Produce a daily business briefing. Use exact numbers only. No fluff. No filler. Say something real in every line.

---

# Win Marketing — Daily Report ({today})

---

## 💰 FINANCIAL SNAPSHOT
Apply Hormozi's MRR formula: revenue grows when new > churn, flat when equal, declining when churn > new.
- MTD cash collected, expenses, EBIT, net margin
- MoM change (% not just dollar)
- Is profit margin expanding or contracting? Why?
- Apply the Time Arbitrage Framework: at current revenue, what is Tian's effective hourly rate? What does that mean for delegation decisions?
- Flag: if expenses are growing faster than revenue this is a constraint, not a cost problem

---

## 👥 CLIENT HEALTH DASHBOARD
This is the most important section. Churn is the silent killer (Hormozi).
Apply the Triangle of Trust to each client: Emotional Connection + Credibility + Reliability.
Apply the Review Flywheel: Results → Reviews → Referrals → Revenue.

For EVERY active client produce a one-line health score:
| Client | MRR | vs Last Month | Retention Signal | Results Signal | Churn Risk |
|--------|-----|---------------|-----------------|----------------|------------|

Then answer:
- **Logo Retention**: X of Y clients from last month still active
- **Revenue Retention**: of last month's total, what % is recurring this month? (>100% = expansion, <100% = contraction — flag immediately)
- **Expansion Revenue**: any client paying more than last month? That's the best signal of success
- **Churn Cohorts**: flag any client in Month 1-3 (highest churn risk window per Hormozi)
- Who is 🟢 Green (healthy + growing), 🟡 Yellow (flat, watch), 🔴 Red (at risk, act today)?

---

## 📊 CLIENT REVENUE BREAKDOWN
- Each client: amount, service, MoM change
- Apply the Customer Avatar Mapping: which clients are (1) loved to work with, (2) highest spend, (3) highest margin, (4) easiest to deliver? Flag the overlap — that's the ideal client to clone
- Flag every client who paid less than last month
- Flag every client from last month missing from this month's data

---

## 🧾 EXPENSE BREAKDOWN
Apply Hormozi's Productivity Leverage Model: every expense should either (a) return hours back to Tian or (b) directly generate revenue.
- Categorized line items with ROI verdict per category
- Flag any expense with no clear revenue link
- Flag unclassified entries — these indicate operational gaps
- Flag any subscription not actively used this week

---

## 📈 D100 (DREAM 100)
Apply the 9-10 Touch Follow-Up Sequence: most responses come after touch 7-10.
Apply the Multi-Channel Waterfall: LinkedIn → Email → WhatsApp → Phone.
- Who's hot (responded in last 3 days), warm (7 days), cold (7+ days, needs re-touch)
- DM activity, replies, meetings booked this week
- For top 3 prospects: what stage are they at, what's the ONE next action to move them forward?
- Pipeline value: estimated MRR if top 3 D100 prospects closed

---

## 📧 COLD OUTREACH (PlusVibe Campaigns)
The PLUSVIBE STATS tab contains daily rows per campaign. Columns: Date, Campaign, Status, Total Leads, Sent, Contacted, Opened, Open Rate %, Replied, Reply Rate %, Positive Replies, Bounced, Unsubscribed, Completed.
Apply Hormozi's Rule of 100: 100 touches per day is the baseline.
Apply Dan Martell's Speed-to-First-Response metric.

For EACH active campaign produce a one-line summary:
| Campaign | Sent | Open Rate | Reply Rate | Positive Replies | Bounced | Status |
|----------|------|-----------|------------|-----------------|---------|--------|

Then answer:
- Total emails sent across all campaigns combined today
- Which campaign has the highest reply rate? Lowest? Why might that be?
- Are reply rates above or below 3%? Below = deliverability or messaging problem — flag it
- Bounce rate above 5% on any campaign = list quality issue — flag it
- Day-over-day trend: compare today's row vs yesterday's row per campaign — is sent count growing, flat, or stalled?
- Which campaign is closest to exhausting its lead list (sent_count / total_leads > 80%)? Flag as needing replenishment
- Positive replies: these are pipeline leads — flag every campaign with positive_reply_count > 0 as a priority follow-up
- Infrastructure note: if bounce rate is climbing, flag domain health risk before it hits spam

---

## 📞 COLD CALLS
Apply the Phone-First Qualification Model (Martell): phone qualifies, meeting closes.
- Calls made → connects → conversations → bookings (conversion % at each stage)
- Best converting time of day or niche if pattern is visible
- If connect rate < 10%, likely wrong list or wrong time — flag it

---

## 🔥 LEADS PIPELINE
Apply the CLOSER Framework for every open lead: where are they in Clarify → Label → Overview → Sell → Explain → Reinforce?
Apply the Value-Based Pricing Framework: are we selling value or price?
- Every open lead: status, last touch, next action, estimated close date
- Pipeline value (total potential MRR if all leads close)
- Who is closest to close — name ONE specific action to move them today
- Flag any lead that hasn't been touched in 5+ days — momentum dies fast

---

## 📐 BUSINESS HEALTH DIAGNOSIS
Apply Hormozi's Constraint-Based Problem Solving: at this stage of the business, is the constraint Product, Marketing, or Fulfillment?
Apply The One Strategic Priority Framework: what is the single thing that if true in 12 months changes everything?
Apply The Leverage Bet Model: Tian has ~20-30% bandwidth beyond daily work — is it being bet on the right thing?

Answer in 3 bullets:
1. What is the current bottleneck constraining growth?
2. Is the business in the Goldilocks Zone (challenging but doable growth) or either stasis or trauma zone?
3. What would Hormozi/Martell say to focus on this week based on the data?

---

## ⚡ TOP 3 ACTIONS FOR TODAY
Ranked by revenue impact. Each action must be hyper-specific — no vague tasks.
Apply the Domino Principle: the one action that makes everything else easier or unnecessary.

Format:
1. [WHO + WHAT + WHEN + WHY IT MATTERS]
2. [WHO + WHAT + WHEN + WHY IT MATTERS]
3. [WHO + WHAT + WHEN + WHY IT MATTERS]

Example of bad action: "Follow up with leads"
Example of good action: "Text Brian Jenney before 11am — his retainer dropped $147 last month, confirm if intentional or a billing issue before it becomes a churn"

---

Rules:
- Every number must come from the data. If it's missing say why.
- Client Health Dashboard is non-negotiable — skip nothing
- Flag every anomaly, drop, or gap no matter how small
- Be the advisor Tian would pay $10,000/month to have on call"""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
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


def send_email(subject: str, body_text: str, body_html: str):
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if not app_password:
        print("ERROR: GMAIL_APP_PASSWORD env var not set")
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = REPORT_EMAIL
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, app_password)
        server.send_message(msg)

    print(f"Sent: {SENDER_EMAIL} → {REPORT_EMAIL}")


def main():
    today = datetime.now().strftime("%a %b %d, %Y")
    print(f"\n📊 Daily Finance Report — {today}")
    print("=" * 50)

    print("1. Connecting to Google Sheets (service account)...")
    gc = get_sheets_client()

    print("2. Reading finance sheet...")
    sheet_data, tab_names = read_sheet(gc)
    print(f"   {len(sheet_data.split(chr(10)))} rows read across {len(tab_names)} tabs: {', '.join(tab_names)}")

    print("3. Generating report with Claude...")
    report = generate_report(sheet_data, tab_names)
    print("   Done.")

    print("4. Sending email via Gmail SMTP...")
    subject = f"📊 Win Marketing — Daily Finance Report ({today})"
    send_email(subject, report, to_html(report))

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
