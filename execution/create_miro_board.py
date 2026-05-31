#!/usr/bin/env python3
"""
Miro Board Creator — The Scaler Method
Creates a full visual presentation board for Kairo Enterprises.
Perfect for client walkthroughs, YouTube videos, and team training.

Usage:
    python3 execution/create_miro_board.py
    python3 execution/create_miro_board.py --name "Smith HVAC — Scaler Plan"

Setup (one-time, 3 minutes):
    1. Go to https://miro.com/app/settings/user-profile/apps
    2. Click "Create new app" → name it "Kairo Boards"
    3. Under "Board content" → enable: boards:read, boards:write
    4. Click "Install app and get OAuth token"
    5. Copy the token → add to .env:  MIRO_ACCESS_TOKEN=your_token_here
    6. Run this script
"""

import argparse
import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────
DARK        = "#1A1A1A"
WHITE       = "#FFFFFF"
BRAND       = "#95D44A"    # Kairo yellow-green
BRAND_DARK  = "#2D6A4F"    # deep green
CRITICAL    = "#C53030"    # 🔴  critical
HIGH        = "#C05621"    # 🟠  high
MEDIUM      = "#975A16"    # 🟡  medium
GROWTH      = "#276749"    # 🟢  growth
BG_MAIN     = "#F0F2F5"
BG_DARK     = "#1A1A1A"
BG_CARD     = "#FFFFFF"
TEXT_MUTED  = "#718096"
GRAY_BORDER = "#CBD5E0"


# ─────────────────────────────────────────────────────────────
# MIRO API CLIENT
# ─────────────────────────────────────────────────────────────
class MiroBoard:
    BASE = "https://api.miro.com/v2"

    def __init__(self, token: str):
        self.token = token
        self.h = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.board_id = None
        self._n = 0  # call counter for throttle

    def _post(self, path: str, body: dict) -> dict:
        self._n += 1
        if self._n % 8 == 0:
            time.sleep(0.4)   # gentle throttle to avoid 429s
        r = requests.post(f"{self.BASE}{path}", headers=self.h, json=body)
        if r.status_code == 429:
            print("  ⏳ Rate limited — pausing 3s...")
            time.sleep(3)
            r = requests.post(f"{self.BASE}{path}", headers=self.h, json=body)
        if not r.ok:
            print(f"  ⚠  API {r.status_code}: {r.text[:120]}")
            return {}
        return r.json()

    # ── Board ─────────────────────────────────────────────────
    def create_board(self, name: str) -> str:
        """Create the board, return the share URL."""
        r = self._post("/v2/boards", {
            "name": name,
            "description": "The Scaler Method — Kairo Enterprises Local Service Marketing System"
        })
        self.board_id = r.get("id", "")
        return r.get("viewLink", ""), r.get("id", "")

    # ── Primitives ────────────────────────────────────────────
    def rect(self, x, y, w, h,
             text="", fill=WHITE, text_color=DARK,
             font_size=13, bold=False,
             border=None, border_w="1",
             shape="rectangle") -> dict:
        """Rectangle (or any shape) with centred text."""
        content = f"<strong>{text}</strong>" if bold else text
        return self._post(f"/v2/boards/{self.board_id}/shapes", {
            "data": {"shape": shape, "content": content},
            "style": {
                "fillColor": fill,
                "fontColor": text_color,
                "fontSize": str(font_size),
                "fontFamily": "opensans",
                "borderColor": border or fill,
                "borderWidth": border_w,
                "borderStyle": "normal",
                "textAlign": "center",
                "textAlignVertical": "middle"
            },
            "position": {"x": x, "y": y, "origin": "center"},
            "geometry": {"width": w, "height": h}
        })

    def txt(self, x, y, w, content,
            color=DARK, font_size=16, align="center") -> dict:
        """Free-floating text element."""
        return self._post(f"/v2/boards/{self.board_id}/texts", {
            "data": {"content": content},
            "style": {
                "color": color,
                "fontSize": str(font_size),
                "fontFamily": "opensans",
                "textAlign": align,
                "fillOpacity": "0"
            },
            "position": {"x": x, "y": y, "origin": "center"},
            "geometry": {"width": w}
        })

    def frame(self, x, y, w, h, title="", fill=BG_MAIN) -> dict:
        """Named frame (section container)."""
        return self._post(f"/v2/boards/{self.board_id}/frames", {
            "data": {"format": "custom", "type": "freeform", "title": title},
            "style": {"fillColor": fill},
            "position": {"x": x, "y": y, "origin": "center"},
            "geometry": {"width": w, "height": h}
        })

    def arrow(self, from_id: str, to_id: str, color=BRAND) -> dict:
        """Connector arrow between two item IDs."""
        return self._post(f"/v2/boards/{self.board_id}/connectors", {
            "startItem": {"id": from_id},
            "endItem":   {"id": to_id},
            "style": {
                "strokeColor": color,
                "strokeWidth": "2",
                "strokeStyle": "normal",
                "startStrokeCap": "none",
                "endStrokeCap":   "arrow"
            }
        })


# ─────────────────────────────────────────────────────────────
# BOARD BUILDER
# ─────────────────────────────────────────────────────────────
def build_board(b: MiroBoard, client_name: str = ""):

    label = f"— {client_name}" if client_name else ""

    # ════════════════════════════════════════════════════════
    # SLIDE 1 — HERO / TITLE
    # ════════════════════════════════════════════════════════
    print("  🎨 Slide 1: Hero")
    HERO_Y = -5200
    b.frame(-400, HERO_Y, 5200, 900, "THE SCALER METHOD — Overview", fill=BG_DARK)

    # Background dark rect
    b.rect(-400, HERO_Y, 5200, 900, fill=BG_DARK, border=BG_DARK)

    # Title
    b.txt(-400, HERO_Y - 260, 4000,
          "<strong>THE SCALER METHOD</strong>",
          color=BRAND, font_size=56, align="center")

    b.txt(-400, HERO_Y - 160, 3000,
          f"Kairo Enterprises {label}",
          color=WHITE, font_size=24, align="center")

    b.txt(-400, HERO_Y - 80, 3600,
          "Local Service Marketing OS — From first diagnosis to market dominance",
          color=TEXT_MUTED, font_size=16, align="center")

    # 5 Phase Pills
    phases = [
        ("01", "Website", "Fix the offer"),
        ("02", "Local SEO", "Own the map pack"),
        ("03", "AI Search", "Own ChatGPT too"),
        ("04", "Paid Ads", "Print money"),
        ("05", "Scale", "Compound it all"),
    ]
    pill_w, pill_h = 600, 90
    pill_gap = 40
    total_pill_w = len(phases) * pill_w + (len(phases) - 1) * pill_gap
    pill_x_start = -400 - total_pill_w / 2 + pill_w / 2
    for i, (num, title, sub) in enumerate(phases):
        px = pill_x_start + i * (pill_w + pill_gap)
        py = HERO_Y + 200
        b.rect(px, py, pill_w, pill_h,
               fill=BRAND_DARK, border=BRAND, border_w="2")
        b.txt(px, py - 14, pill_w - 20, f"<strong>{num} — {title}</strong>",
              color=BRAND, font_size=15, align="center")
        b.txt(px, py + 18, pill_w - 20, sub,
              color=WHITE, font_size=12, align="center")

    # ════════════════════════════════════════════════════════
    # SLIDE 2 — THE PROBLEM + THE METHOD SEQUENCE
    # ════════════════════════════════════════════════════════
    print("  🎨 Slide 2: The Problem + The Sequence")
    PROB_Y = -3000

    # LEFT — The Problem
    b.frame(-2800, PROB_Y, 2200, 2000, "THE PROBLEM — Why 97% of Local Businesses Plateau")
    b.txt(-2800, PROB_Y - 820, 2000,
          "<strong>Why 97% of Local Businesses Plateau</strong>",
          color=DARK, font_size=28, align="center")
    b.txt(-2800, PROB_Y - 740, 1900,
          "Not enough leads. Too expensive. Wrong order. Wrong metrics.",
          color=TEXT_MUTED, font_size=14, align="center")

    problems = [
        ("💸", "Invisible on Google", "Can't crack the map pack. $600/lead. Burning budget."),
        ("⏱", "Leads going cold", "No automation. 41% of jobs booked after hours. Missed calls = lost revenue."),
        ("📊", "Wrong metric", "Optimising for cheapest leads. Cheapest = worst customers."),
        ("🔧", "Wrong order", "Running ads into a 1% website. Website fix first — always."),
    ]
    for i, (icon, title, body) in enumerate(problems):
        py = PROB_Y - 520 + i * 330
        b.rect(-2800, py, 1900, 260,
               fill=WHITE, border=GRAY_BORDER, border_w="1")
        b.txt(-2800, py - 60, 1700,
              f"{icon}  <strong>{title}</strong>",
              color=CRITICAL, font_size=17, align="left")
        b.txt(-2800, py + 30, 1700, body,
              color=DARK, font_size=13, align="left")

    # RIGHT — The Sequence (non-negotiable order)
    b.frame(400, PROB_Y, 2000, 2000, "THE SEQUENCE — Non-Negotiable Order")
    b.txt(400, PROB_Y - 820, 1800,
          "<strong>The Non-Negotiable Order</strong>",
          color=DARK, font_size=28, align="center")
    b.txt(400, PROB_Y - 740, 1800,
          "Running ads before fixing the website = burning money. Sequence is law.",
          color=TEXT_MUTED, font_size=13, align="center")

    seq_steps = [
        (CRITICAL, "🔴", "1. Fix Website First",     "H1 outcome. Sticky CTA. Trust above fold. 1% → 5% = 5x leads."),
        (CRITICAL, "🔴", "2. Speed to Lead + Track",  "GHL automation. CallRail. Every lead gets a response in 60 seconds."),
        (CRITICAL, "🔴", "3. GBP + Review Velocity",  "DBA name match. 30+ reviews/month. Map pack position unlocked."),
        (HIGH,     "🟠", "4. LSA → PPC (LTV:CAC)",   "LSA first (30-45% close rate). PPC restructured by service tier."),
        (MEDIUM,   "🟡", "5. AI Search + Organic",    "Citations, press releases, Q&A pages. Own ChatGPT + Google."),
        (GROWTH,   "🟢", "6. Scale Everything Else",  "DB reactivation. Retargeting. Bing. Partnerships. Maintenance plans."),
    ]
    prev_id = None
    for i, (color, icon, title, desc) in enumerate(seq_steps):
        py = PROB_Y - 560 + i * 285
        r = b.rect(400, py, 1750, 230,
                   fill=color, text_color=WHITE)
        item_id = r.get("id", "")
        b.txt(400, py - 45, 1600,
              f"{icon}  <strong>{title}</strong>",
              color=WHITE, font_size=15, align="left")
        b.txt(400, py + 30, 1600, desc,
              color=WHITE, font_size=12, align="left")
        if prev_id:
            b.arrow(prev_id, item_id, color=BRAND)
        prev_id = item_id

    # ════════════════════════════════════════════════════════
    # SLIDE 3 — THE 21-MODULE DIAGNOSTIC GRID
    # ════════════════════════════════════════════════════════
    print("  🎨 Slide 3: 21-Module Diagnostic Grid")
    GRID_Y = 0
    GRID_FRAME_W = 5000
    GRID_FRAME_H = 2400

    b.frame(0, GRID_Y, GRID_FRAME_W, GRID_FRAME_H, "THE 21-MODULE DIAGNOSTIC — Kairo Scaler Method")

    b.txt(0, GRID_Y - 1100, 4600,
          "<strong>THE 21-MODULE DIAGNOSTIC</strong>",
          color=DARK, font_size=36, align="center")
    b.txt(0, GRID_Y - 1020, 4200,
          "Every module scored RED / YELLOW / GREEN. This is what we fix, in this order.",
          color=TEXT_MUTED, font_size=16, align="center")

    # Priority legend
    legend = [
        (CRITICAL, "🔴 CRITICAL — Fix immediately. Revenue bleeding."),
        (HIGH,     "🟠 HIGH — Month 1. Major leverage."),
        (MEDIUM,   "🟡 MEDIUM — Month 2-3. Strong multiplier."),
        (GROWTH,   "🟢 GROWTH — Month 4+. Compounds on the base."),
    ]
    for i, (color, label) in enumerate(legend):
        lx = -1800 + i * 940
        b.rect(lx, GRID_Y - 940, 880, 50, text=label,
               fill=color, text_color=WHITE, font_size=12)

    # Module cards by priority
    modules = {
        CRITICAL: [
            ("Website / Offer",        "H1 outcome? Sticky CTA?\n1% → 5% = 5x leads"),
            ("Speed to Lead",          "GHL automation. <60s\nresponse. 41% booked AH"),
            ("Call Tracking",          "CallRail. 60-sec calls.\nClosed-loop attribution"),
            ("GBP Optimization",       "DBA name match. Right\ncategory. Products tab."),
            ("Review Velocity",        "30+/month. In-person\nask. QR card. 3-touch"),
        ],
        HIGH: [
            ("Citation Building",      "80-120 dirs. NAP\nconsistency. AI signal"),
            ("Google LSA",             "Highest-intent leads.\n30-45% close rate"),
            ("Google Ads (LTV:CAC)",   "Tier by service. Kill\nwrong campaigns fast"),
            ("DB Reactivation",        "$40 ROI / $1. Past\ncustomers. Near zero CPL"),
            ("Financing",              "+11% close on $3K+\njobs. Lead with $/month"),
        ],
        MEDIUM: [
            ("AI Search System",       "Press releases, listicles,\nQ&A pages for ChatGPT"),
            ("Organic SEO",            "Service + location pages.\nInternal linking mesh"),
            ("Email + SMS",            "$40/$1 ROI. Seasonal\ncampaigns + reactivation"),
            ("Partnership Marketing",  "Realtors, builders,\nadjusters. Zero CPL"),
            ("Bing / Microsoft Ads",   "33-70% cheaper CPCs.\nImport from Google"),
            ("Retargeting",            "93% visitors leave.\n20% of budget here"),
            ("AI Chatbot",             "41% jobs after hours.\nGHL captures them all"),
        ],
        GROWTH: [
            ("Video Testimonials",     "34% conversion lift.\nVocal Video at job end"),
            ("Maintenance Plans",      "1,000 × $20/mo =\n$20K recurring MRR"),
            ("Nextdoor",               "Neighborhood Favorites.\n10x weight vs. paid"),
            ("TikTok / Short Video",   "Before/after content.\nBest organic reach 2025"),
        ],
    }

    CARD_W, CARD_H = 220, 110
    CARD_GAP = 18
    ROW_GAP = 24

    row_colors   = [CRITICAL, HIGH, MEDIUM, GROWTH]
    row_labels   = ["🔴 CRITICAL", "🟠 HIGH", "🟡 MEDIUM", "🟢 GROWTH"]
    row_y_starts = [-850, -580, -260, 80]

    for row_idx, (color, label) in enumerate(zip(row_colors, row_labels)):
        cards = modules[color]
        total_w = len(cards) * CARD_W + (len(cards) - 1) * CARD_GAP
        row_x_start = -total_w / 2 + CARD_W / 2
        row_y = GRID_Y + row_y_starts[row_idx]

        # Row label
        b.txt(0, row_y - CARD_H / 2 - 22, total_w + 100,
              f"<strong>{label}</strong>", color=color, font_size=14, align="left")

        for col_idx, (name, desc) in enumerate(cards):
            cx = row_x_start + col_idx * (CARD_W + CARD_GAP)
            # Card background (colored top strip + white body)
            b.rect(cx, row_y - 30, CARD_W, 50,
                   fill=color, border=color)
            b.txt(cx, row_y - 33, CARD_W - 12,
                  f"<strong>{name}</strong>", color=WHITE, font_size=11, align="center")
            b.rect(cx, row_y + 35, CARD_W, 70,
                   fill=WHITE, border=GRAY_BORDER, border_w="1")
            b.txt(cx, row_y + 35, CARD_W - 16,
                  desc, color=DARK, font_size=10, align="center")

    # ════════════════════════════════════════════════════════
    # SLIDE 4 — 90-DAY ROADMAP
    # ════════════════════════════════════════════════════════
    print("  🎨 Slide 4: 90-Day Roadmap")
    ROAD_Y = 1900
    b.frame(0, ROAD_Y, 5200, 1100, "THE 90-DAY ROADMAP")

    b.txt(0, ROAD_Y - 480, 4600,
          "<strong>THE 90-DAY ROADMAP</strong>",
          color=DARK, font_size=32, align="center")
    b.txt(0, ROAD_Y - 410, 4400,
          "This is the order. Every task in every phase builds on the one before it.",
          color=TEXT_MUTED, font_size=15, align="center")

    phases_road = [
        (CRITICAL, "WEEKS 1-2", "Stop the Bleeding",
         "GHL automation live\nCallRail installed\nGBP category fixed\nQR review cards out\nAd account audited"),
        (HIGH,     "WEEKS 3-4", "Build the Machine",
         "Citations: 80+ dirs\nService pages live\nLSA launched\nBing Ads imported\nDB reactivation sent"),
        (MEDIUM,   "MONTH 2", "Accelerate",
         "Press release #1\nListicle article\n5 Q&A pages\nRealtor outreach\nFinancing live"),
        (MEDIUM,   "MONTH 3", "Compound",
         "AI signals active\nGeographic expansion?\nDouble Tier-1 ad budget\nMaintenance plan live\nRetargeting live"),
        (GROWTH,   "MONTHS 4-6", "Scale",
         "Video testimonials\nNeighbor-effect ads\n2nd reactivation wave\nBing scaling\n$[X]/mo recurring"),
        (GROWTH,   "MONTHS 7-12", "Dominate",
         "AI citation ownership\nChatGPT recommends you\nMap pack: #1 position\n$[X]/mo in MRR\nNeighbour cities"),
    ]

    phase_w = 700
    phase_gap = 30
    total_phase_w = len(phases_road) * phase_w + (len(phases_road) - 1) * phase_gap
    ph_x_start = -total_phase_w / 2 + phase_w / 2

    prev_ph_id = None
    for i, (color, period, title, tasks) in enumerate(phases_road):
        px = ph_x_start + i * (phase_w + phase_gap)
        py = ROAD_Y + 80

        # Header
        header = b.rect(px, py - 170, phase_w, 70,
                        fill=color, text_color=WHITE, bold=True, font_size=14)
        h_id = header.get("id", "")
        b.txt(px, py - 185, phase_w - 16,
              f"<strong>{period}</strong>", color=WHITE, font_size=11, align="center")
        b.txt(px, py - 162, phase_w - 16,
              f"<strong>{title}</strong>", color=WHITE, font_size=13, align="center")

        # Task block
        b.rect(px, py + 40, phase_w, 340,
               fill=WHITE, border=color, border_w="2")
        b.txt(px, py + 40, phase_w - 20,
              tasks, color=DARK, font_size=12, align="left")

        if prev_ph_id:
            b.arrow(prev_ph_id, h_id, color=BRAND)
        prev_ph_id = h_id

    # ════════════════════════════════════════════════════════
    # SLIDE 5 — WEEK 1 EXECUTION PLAN
    # ════════════════════════════════════════════════════════
    print("  🎨 Slide 5: Week 1 Plan")
    WEEK_Y = 3400
    b.frame(0, WEEK_Y, 5200, 1000, "WEEK 1 — HOW WE BLOW THEM AWAY IN 7 DAYS")

    b.txt(0, WEEK_Y - 450, 4600,
          "<strong>WEEK 1 — HOW WE BLOW THEM AWAY IN 7 DAYS</strong>",
          color=DARK, font_size=30, align="center")
    b.txt(0, WEEK_Y - 380, 4000,
          "The goal: stop the bleeding and deliver a visible, measurable win before day 8.",
          color=TEXT_MUTED, font_size=15, align="center")

    days = [
        ("DAY 1", CRITICAL,
         "Stop the Bleeding",
         "✓ GHL missed-call text back LIVE\n✓ CallRail installed\n✓ Conversion tracking = 60s calls\n✓ GBP category corrected"),
        ("DAY 2", CRITICAL,
         "GBP Quick Wins",
         "✓ Service descriptions written\n✓ Products tab populated\n✓ DBA assessment completed\n✓ First GBP post scheduled"),
        ("DAY 3", CRITICAL,
         "Review Launch",
         "✓ QR code cards printed\n✓ Tech team briefed on script\n✓ 3-touch sequence in GHL\n✓ Tech incentive set"),
        ("DAY 4", HIGH,
         "Ad Triage",
         "✓ LTV:CAC test run per tier\n✓ Unprofitable campaigns killed\n✓ LSA response time checked\n✓ Bing import completed"),
        ("DAY 5", HIGH,
         "DB Reactivation",
         "✓ Past customer list exported\n✓ Segmented by service type\n✓ Email 1 + SMS 1 sent\n✓ Follow-up scheduled"),
        ("DAY 6", MEDIUM,
         "Lock It In",
         "✓ All automations tested live\n✓ Tracking verified working\n✓ QR cards confirmed with techs\n✓ Reactivation live"),
        ("DAY 7", GROWTH,
         "Show the Win",
         "✓ New review count vs. Day 1\n✓ GHL automation results\n✓ Ad waste eliminated\n✓ Brief client on Month 1"),
    ]

    day_w = 580
    day_gap = 22
    total_day_w = len(days) * day_w + (len(days) - 1) * day_gap
    day_x_start = -total_day_w / 2 + day_w / 2

    for i, (day_label, color, title, tasks) in enumerate(days):
        dx = day_x_start + i * (day_w + day_gap)
        dy = WEEK_Y + 80

        b.rect(dx, dy - 160, day_w, 60, fill=color, text_color=WHITE)
        b.txt(dx, dy - 172, day_w - 12, f"<strong>{day_label}</strong>",
              color=WHITE, font_size=12, align="center")
        b.txt(dx, dy - 153, day_w - 12, f"<strong>{title}</strong>",
              color=WHITE, font_size=13, align="center")
        b.rect(dx, dy + 40, day_w, 320, fill=WHITE, border=color, border_w="2")
        b.txt(dx, dy + 40, day_w - 20, tasks, color=DARK, font_size=12, align="left")

    # ════════════════════════════════════════════════════════
    # SLIDE 6 — THE REVENUE MATH
    # ════════════════════════════════════════════════════════
    print("  🎨 Slide 6: Revenue Math")
    MATH_Y = 5000
    b.frame(0, MATH_Y, 5200, 1000, "THE REVENUE MATH — LTV:CAC Framework")

    b.txt(0, MATH_Y - 450, 4600,
          "<strong>THE REVENUE MATH</strong>",
          color=DARK, font_size=32, align="center")
    b.txt(0, MATH_Y - 380, 4000,
          "CPL is a vanity metric. LTV:CAC is the only number that matters. Once the math works — you can outspend every competitor.",
          color=TEXT_MUTED, font_size=14, align="center")

    # Key principle cards
    principles = [
        (CRITICAL, "THE TRAP",
         "All services in one\ncampaign. Blended CPL\nlooks terrible. Kill\ncampaigns on wrong\nmetric. Money burned."),
        (HIGH, "THE FIX",
         "Segment by service tier.\nTier 1 = high ticket.\nTier 2 = repairs.\nTier 3 = maintenance.\nSeparate CPL targets."),
        (MEDIUM, "THE MATH",
         "Max CPL = LTV ÷ 5\n÷ close rate\n\n$15K system ÷ 5 = $3K\nMax CAC. At 30% close\n= $900 max CPL. Fine."),
        (GROWTH, "THE RESULT",
         "Once LTV:CAC works,\nno limit on spend.\nOutbid every competitor\non every click and\nstill print money."),
    ]

    card_w = 880
    total_math_w = len(principles) * card_w + (len(principles) - 1) * 30
    math_x_start = -total_math_w / 2 + card_w / 2

    for i, (color, title, body) in enumerate(principles):
        mx = math_x_start + i * (card_w + 30)
        my = MATH_Y + 80
        b.rect(mx, my - 140, card_w, 60, fill=color, text_color=WHITE)
        b.txt(mx, my - 148, card_w - 16, f"<strong>{title}</strong>",
              color=WHITE, font_size=15, align="center")
        b.rect(mx, my + 40, card_w, 320, fill=WHITE, border=color, border_w="2")
        b.txt(mx, my + 40, card_w - 24, body, color=DARK, font_size=13, align="center")

    # ════════════════════════════════════════════════════════
    # SLIDE 7 — HOW KAIRO WORKS WITH YOU
    # ════════════════════════════════════════════════════════
    print("  🎨 Slide 7: How Kairo Works")
    HOW_Y = 6500
    b.frame(0, HOW_Y, 5200, 800, "HOW KAIRO WORKS WITH YOU")

    b.txt(0, HOW_Y - 350, 4600,
          "<strong>HOW KAIRO WORKS WITH YOU</strong>",
          color=DARK, font_size=30, align="center")

    tiers = [
        (BRAND_DARK, "FOUNDATION", "$1,500–$2,500/mo",
         "Website fix + GBP + Citations\n+Review velocity + GHL automation\n+CallRail + Monthly press release\nBest for: $500K–$1.5M/yr"),
        (HIGH,       "AUTHORITY",  "$2,500–$4,500/mo",
         "Everything in Foundation +\nService + location page build\nListicle articles, Q&A pages\nPartnership outreach + retargeting\nBest for: $1.5M–$3M/yr"),
        (CRITICAL,   "DOMINATION", "$4,500–$8,000/mo",
         "Everything in Authority +\nGoogle LSA + PPC by service tier\nBing Ads management\nLTV:CAC monthly reporting\nBest for: $3M+/yr"),
    ]

    tier_w = 1400
    total_tier_w = len(tiers) * tier_w + 2 * 30
    tier_x_start = -total_tier_w / 2 + tier_w / 2

    for i, (color, name, price, features) in enumerate(tiers):
        tx = tier_x_start + i * (tier_w + 30)
        ty = HOW_Y + 60

        b.rect(tx, ty - 140, tier_w, 60, fill=color, text_color=WHITE)
        b.txt(tx, ty - 150, tier_w - 16,
              f"<strong>{name}</strong>", color=WHITE, font_size=16, align="center")
        b.txt(tx, ty - 130, tier_w - 16,
              price, color=WHITE, font_size=13, align="center")
        b.rect(tx, ty + 40, tier_w, 260, fill=WHITE, border=color, border_w="2")
        b.txt(tx, ty + 40, tier_w - 24, features, color=DARK, font_size=13, align="left")

    # Footer note
    b.txt(0, HOW_Y + 290, 4000,
          "🚀  Start with a Free Scaler Diagnostic — we show you exactly what's broken and what it's costing you.   kairo-scales.com",
          color=BRAND_DARK, font_size=15, align="center")

    print("  ✅ All slides built.")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Create The Scaler Method Miro board")
    parser.add_argument("--name", default="", help="Client or campaign name to append to title")
    args = parser.parse_args()

    token = os.getenv("MIRO_ACCESS_TOKEN")
    if not token:
        print("\n" + "="*60)
        print("  ⚠  MIRO_ACCESS_TOKEN not found in .env")
        print("="*60)
        print("""
  Setup takes ~3 minutes:

  1. Go to: https://miro.com/app/settings/user-profile/apps
  2. Click "Your apps" → "Build app"
  3. Name it: Kairo Boards
  4. Under Scopes → enable:
       ✓ boards:read
       ✓ boards:write
  5. Click "Install app and get OAuth token"
  6. Copy the token
  7. Add to your .env:

     MIRO_ACCESS_TOKEN=your_token_here

  8. Re-run this script.

  Free Miro account works — no upgrade needed.
""")
        print("="*60 + "\n")
        sys.exit(1)

    board_name = f"The Scaler Method — Kairo Enterprises"
    if args.name:
        board_name = f"{board_name} | {args.name}"

    print(f"\n🚀 Creating Miro board: {board_name}")
    print("   (This takes ~30-60 seconds)")
    print()

    b = MiroBoard(token)
    url, board_id = b.create_board(board_name)

    if not board_id:
        print("❌ Failed to create board. Check your MIRO_ACCESS_TOKEN.")
        sys.exit(1)

    print(f"  ✅ Board created: {url}")
    print()

    build_board(b, client_name=args.name)

    print()
    print("="*60)
    print("  ✅ MIRO BOARD COMPLETE")
    print(f"  🔗 {url}")
    print("="*60)
    print()
    print("  Slides created:")
    print("  1. Hero / Title")
    print("  2. The Problem + The Sequence")
    print("  3. The 21-Module Diagnostic Grid")
    print("  4. 90-Day Roadmap")
    print("  5. Week 1 Execution Plan")
    print("  6. The Revenue Math (LTV:CAC)")
    print("  7. How Kairo Works + Packages")
    print()


if __name__ == "__main__":
    main()
