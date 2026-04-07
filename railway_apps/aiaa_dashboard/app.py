#!/usr/bin/env python3
"""
Kairo Marketing Automation Engine v1.0
Premium AI-Powered Marketing Package Generator

Features:
- Batch process up to 30 companies at once
- Generate 5 marketing assets per company (VSL, Landing Page, Emails, Creative Brief, Offer Deep Dive)
- Beautiful public landing pages for each company
- Real-time progress tracking
- Premium blue/gold/white design with animations
"""

import os
import json
import hashlib
import secrets
import re
import sqlite3
import threading
import time
import requests
from datetime import datetime
from functools import wraps
from collections import deque
from urllib.parse import urlparse

from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

# =============================================================================
# Configuration
# =============================================================================

DASHBOARD_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD_HASH = os.getenv("DASHBOARD_PASSWORD_HASH", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", "marketing_engine.db")

# =============================================================================
# Database Setup
# =============================================================================

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with all required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Batches table
    c.execute('''CREATE TABLE IF NOT EXISTS batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT UNIQUE NOT NULL,
        user_id TEXT,
        total_companies INTEGER DEFAULT 0,
        completed_companies INTEGER DEFAULT 0,
        failed_companies INTEGER DEFAULT 0,
        status TEXT DEFAULT 'processing',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Companies table
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT NOT NULL,
        company_name TEXT NOT NULL,
        website TEXT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        instagram TEXT,
        linkedin TEXT,
        about TEXT,
        status TEXT DEFAULT 'pending',
        current_step TEXT DEFAULT '',
        error_message TEXT,
        slug TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
    )''')

    # Research table
    c.execute('''CREATE TABLE IF NOT EXISTS research (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        website_content TEXT,
        company_history TEXT,
        market_analysis TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )''')

    # Analysis table (Niche Analysis)
    c.execute('''CREATE TABLE IF NOT EXISTS analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        target_market TEXT,
        pain_points TEXT,
        value_proposition TEXT,
        unique_benefits TEXT,
        sales_argument TEXT,
        why_chosen TEXT,
        confidence_scores TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )''')

    # Assets table (5 marketing assets)
    c.execute('''CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        vsl_script TEXT,
        landing_page_copy TEXT,
        email_sequence TEXT,
        creative_brief TEXT,
        offer_deep_dive TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )''')

    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# =============================================================================
# Authentication
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_password(password):
    if not DASHBOARD_PASSWORD_HASH:
        return password == "admin"
    return hashlib.sha256(password.encode()).hexdigest() == DASHBOARD_PASSWORD_HASH

# =============================================================================
# Data Parsing (Google Sheets format)
# =============================================================================

def parse_google_sheets_data(data):
    """Parse Google Sheets data - flexible column detection from copy-paste."""
    companies = []
    lines = data.strip().split('\n')

    print(f"[PARSE] Received {len(lines)} lines of data")
    print(f"[PARSE] First line preview: {lines[0][:100] if lines else 'empty'}...")

    # Skip empty data
    if not lines:
        print("[PARSE] No lines found")
        return companies

    # Check if first line is a header row (contains common header words)
    first_line_lower = lines[0].lower()
    header_keywords = ['company', 'website', 'name', 'email', 'first', 'last', 'instagram', 'linkedin', 'about']
    is_header = sum(1 for kw in header_keywords if kw in first_line_lower) >= 2

    start_idx = 1 if is_header else 0

    for line in lines[start_idx:]:
        if not line.strip():
            continue

        # Tab-separated (direct Google Sheets copy-paste)
        if '\t' in line:
            parts = [p.strip() for p in line.split('\t')]

            # Accept any number of columns (minimum 1)
            if len(parts) >= 1:
                company = {
                    'company_name': '',
                    'website': '',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'instagram': '',
                    'linkedin': '',
                    'about': ''
                }

                # Smart column detection based on content
                for i, part in enumerate(parts):
                    part_lower = part.lower()

                    # Detect by content pattern
                    if 'http' in part_lower and 'linkedin' in part_lower:
                        company['linkedin'] = part
                    elif 'http' in part_lower or '.com' in part_lower or '.co' in part_lower or '.io' in part_lower:
                        if not company['website']:
                            company['website'] = part if part.startswith('http') else f'https://{part}'
                    elif '@' in part and '.' in part and ' ' not in part:
                        company['email'] = part
                    elif part.startswith('@'):
                        company['instagram'] = part
                    elif len(part) > 50:  # Long text is likely "about"
                        company['about'] = part
                    elif i == 0 and not company['company_name']:
                        # First column is usually company name
                        company['company_name'] = part
                    elif not company['first_name'] and len(part.split()) == 1 and len(part) < 20:
                        company['first_name'] = part
                    elif company['first_name'] and not company['last_name'] and len(part.split()) == 1 and len(part) < 20:
                        company['last_name'] = part
                    elif not company['company_name']:
                        company['company_name'] = part
                    elif not company['about']:
                        company['about'] = part

                # Ensure we have at least a company name
                if company['company_name']:
                    companies.append(company)
                continue

        # Fallback: comma-separated or other formats
        if ',' in line:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                company = parse_parts_smart(parts)
                if company and company['company_name']:
                    companies.append(company)
                continue

        # Single column - just company name
        if line.strip() and not any(c in line for c in ['\t', ',']):
            companies.append({
                'company_name': line.strip(),
                'website': '',
                'first_name': '',
                'last_name': '',
                'email': '',
                'instagram': '',
                'linkedin': '',
                'about': ''
            })

    print(f"[PARSE] Parsed {len(companies)} companies")
    if companies:
        print(f"[PARSE] First company: {companies[0]}")
    return companies

def parse_parts_smart(parts):
    """Smart parsing of parts regardless of order."""
    company = {
        'company_name': '',
        'website': '',
        'first_name': '',
        'last_name': '',
        'email': '',
        'instagram': '',
        'linkedin': '',
        'about': ''
    }

    for part in parts:
        part = part.strip()
        part_lower = part.lower()

        if 'linkedin.com' in part_lower:
            company['linkedin'] = part
        elif 'http' in part_lower or '.com' in part_lower or '.co' in part_lower:
            if not company['website']:
                company['website'] = part if part.startswith('http') else f'https://{part}'
        elif '@' in part and '.' in part and ' ' not in part:
            company['email'] = part
        elif part.startswith('@'):
            company['instagram'] = part
        elif len(part) > 60:
            company['about'] = part
        elif not company['company_name']:
            company['company_name'] = part

    return company

def generate_slug(company_name):
    """Generate URL-safe slug from company name."""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', company_name.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return f"{slug}-{secrets.token_hex(4)}"

# =============================================================================
# AI Generation Functions
# =============================================================================

def call_ai(prompt, system_prompt="You are an expert marketing strategist and copywriter.", max_tokens=4000):
    """Call AI via OpenRouter or Anthropic."""

    # Try OpenRouter first
    if OPENROUTER_API_KEY:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens
                },
                timeout=300
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"[AI ERROR] OpenRouter: {e}")

    # Fallback to Anthropic
    if ANTHROPIC_API_KEY:
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=300
            )
            if response.status_code == 200:
                return response.json()['content'][0]['text']
        except Exception as e:
            print(f"[AI ERROR] Anthropic: {e}")

    return None

def scrape_website(url):
    """Simple website scraper to get content."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; MarketingBot/1.0)'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            # Basic HTML to text conversion
            text = re.sub(r'<script[^>]*>.*?</script>', '', response.text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            return text[:10000]  # Limit to 10k chars
    except Exception as e:
        print(f"[SCRAPE ERROR] {url}: {e}")
    return ""

# =============================================================================
# Processing Pipeline
# =============================================================================

def process_company(company_id):
    """Process a single company through the full pipeline."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        # Get company data
        c.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        company = dict(c.fetchone())

        print(f"[PROCESS] Starting: {company['company_name']}")

        # Step 1: Research
        update_company_status(conn, company_id, 'researching', 'Scraping website and researching company...')

        website_content = ""
        if company['website']:
            website_content = scrape_website(company['website'])

        research_prompt = f"""Research this company and provide a comprehensive analysis:

Company: {company['company_name']}
Website: {company['website']}
About: {company['about']}
Contact: {company['first_name']} {company['last_name']}
Website Content: {website_content[:5000]}

Provide:
1. Company Overview (what they do, their mission)
2. Products/Services offered
3. Target market they serve
4. Their unique positioning
5. Company history and background (if available)
6. Online presence assessment"""

        research_result = call_ai(research_prompt) or "Research data not available"

        c.execute("""INSERT INTO research (company_id, website_content, company_history, market_analysis)
                     VALUES (?, ?, ?, ?)""",
                  (company_id, website_content, research_result, ""))
        conn.commit()

        # Step 2: Niche Analysis
        update_company_status(conn, company_id, 'analyzing', 'Performing deep market analysis...')

        analysis_prompt = f"""You are an expert direct response copywriter and marketing strategist. Analyze this company and provide comprehensive insights:

Company: {company['company_name']}
Website: {company['website']}
About: {company['about']}
Research: {research_result[:3000]}

Provide the following with confidence scores (1-10) for each section:

## 1. TARGET MARKET ANALYSIS
Who is their ideal customer? Be specific about demographics, psychographics, and buying behavior.

## 2. PAIN POINTS & CONCERNS
What are the top 5-10 pain points their target market experiences? What questions and concerns do prospects have?

## 3. VALUE PROPOSITION
What is their core value proposition? How do they solve their customers' problems better than alternatives?

## 4. UNIQUE BENEFITS
What makes them different? What unique benefits do they offer that competitors don't?

## 5. SALES ARGUMENT
Create a compelling sales argument using Dan Kennedy's framework - why should someone buy from them?

## 6. WHY WE CHOSE THIS COMPANY (For Kairo's outreach)
Explain why Kairo (a marketing agency specializing in paid funnels with performance-based pricing) would be a perfect fit for this company. What specific opportunities do you see? How could Kairo help them scale?

Be specific, use reasoning, and provide confidence scores for each section."""

        analysis_result = call_ai(analysis_prompt, max_tokens=6000) or "Analysis not available"

        # Parse sections from analysis
        c.execute("""INSERT INTO analysis (company_id, target_market, pain_points, value_proposition,
                     unique_benefits, sales_argument, why_chosen, confidence_scores)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (company_id, analysis_result, "", "", "", "", "", ""))
        conn.commit()

        # Step 3: Generate 5 Marketing Assets
        update_company_status(conn, company_id, 'generating', 'Generating marketing assets...')

        context = f"""
Company: {company['company_name']}
Website: {company['website']}
Contact: {company['first_name']} {company['last_name']}
About: {company['about']}

Research & Analysis:
{analysis_result[:4000]}
"""

        # Generate all 5 assets
        print(f"[GEN] Generating VSL Script for {company['company_name']}...")
        vsl_script = generate_vsl_script(context)

        print(f"[GEN] Generating Landing Page for {company['company_name']}...")
        landing_page = generate_landing_page(context)

        print(f"[GEN] Generating Email Sequence for {company['company_name']}...")
        email_sequence = generate_email_sequence(context)

        print(f"[GEN] Generating Creative Brief for {company['company_name']}...")
        creative_brief = generate_creative_brief(context, analysis_result)

        print(f"[GEN] Generating Offer Deep Dive for {company['company_name']}...")
        offer_deep_dive = generate_offer_deep_dive(context, analysis_result)

        # Step 4: Save Assets
        update_company_status(conn, company_id, 'saving', 'Saving generated assets...')

        c.execute("""INSERT INTO assets (company_id, vsl_script, landing_page_copy, email_sequence,
                     creative_brief, offer_deep_dive)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (company_id, vsl_script, landing_page, email_sequence, creative_brief, offer_deep_dive))
        conn.commit()

        # Step 5: Mark Complete
        update_company_status(conn, company_id, 'completed', '')

        # Update batch progress
        c.execute("SELECT batch_id FROM companies WHERE id = ?", (company_id,))
        batch_id = c.fetchone()['batch_id']
        c.execute("""UPDATE batches SET completed_companies = completed_companies + 1,
                     updated_at = CURRENT_TIMESTAMP WHERE batch_id = ?""", (batch_id,))
        conn.commit()

        print(f"[PROCESS] Completed: {company['company_name']}")

    except Exception as e:
        print(f"[PROCESS ERROR] {e}")
        update_company_status(conn, company_id, 'failed', str(e))
        c.execute("SELECT batch_id FROM companies WHERE id = ?", (company_id,))
        result = c.fetchone()
        if result:
            batch_id = result['batch_id']
            c.execute("""UPDATE batches SET failed_companies = failed_companies + 1,
                         updated_at = CURRENT_TIMESTAMP WHERE batch_id = ?""", (batch_id,))
            conn.commit()
    finally:
        conn.close()

def update_company_status(conn, company_id, status, current_step):
    """Update company processing status."""
    c = conn.cursor()
    c.execute("""UPDATE companies SET status = ?, current_step = ?, updated_at = CURRENT_TIMESTAMP
                 WHERE id = ?""", (status, current_step, company_id))
    conn.commit()

# =============================================================================
# Asset Generation Functions
# =============================================================================

def generate_vsl_script(context):
    """Generate VSL script using the VSL prompt."""
    prompt = f"""You are creating a Video Sales Letter script for the following company. This VSL should be 4-6 minutes long (approximately 880-1320 words at 220 words per minute).

{context}

Create a compelling VSL script with the following structure:

1. OPENING HOOK (Pattern interrupt, create curiosity)
2. CREDIBILITY BRIDGE (Why they should listen)
3. PROBLEM AMPLIFICATION (Escalating waves of pain)
4. PARADIGM SHIFT (The key insight that changes everything)
5. SOLUTION REVELATION (Introduce the solution progressively)
6. PROOF CASCADE (Evidence in multiple forms)
7. BENEFIT TRANSFORMATION (Benefits as life transformation scenes)
8. OBJECTION DISSOLUTION (Preemptively handle concerns)
9. OFFER ARCHITECTURE (Present the offer as logical culmination)
10. RISK REVERSAL (Position guarantee as confidence)
11. URGENCY (Create legitimate urgency)
12. CALL TO ACTION (Book a call)
13. FUTURE PACING CLOSE

Write the complete script ready to record. Make it conversational, compelling, and focused on transformation."""

    return call_ai(prompt, max_tokens=4000) or "VSL Script generation failed"

def generate_landing_page(context):
    """Generate landing page copy."""
    prompt = f"""You are creating landing page copy for the following company. Determine if they are B2B or B2C and write accordingly.

{context}

Create complete landing page copy with:

1. PRE-HEADLINE (10-15 words of context/credibility)
2. MAIN HEADLINE (Focus on primary outcome/transformation)
3. SUBHEADLINE (Expand on mechanism/method)
4. PROBLEM AGITATION (3-5 paragraphs demonstrating deep understanding)
5. SOLUTION INTRODUCTION (2-3 paragraphs as bridge from problem to outcome)
6. AUTHORITY/CREDIBILITY BLOCK
7. BENEFITS SECTION (3-5 major benefits with headlines and explanations)
8. SOCIAL PROOF SECTION (Structure for case studies/testimonials)
9. PROCESS/METHOD OVERVIEW (3-5 steps of how it works)
10. OBJECTION HANDLING (Address top concerns)
11. OFFER STACK (Itemized list of everything included)
12. RISK REVERSAL (Guarantee that addresses biggest fear)
13. CTA (Book a strategy call)
14. FAQ SECTION (5-7 questions)
15. FINAL URGENCY BLOCK

Write compelling, conversion-focused copy."""

    return call_ai(prompt, max_tokens=5000) or "Landing page generation failed"

def generate_email_sequence(context):
    """Generate 12-day email sequence."""
    prompt = f"""Create a 12-day email nurture sequence for prospects who showed interest but haven't booked a call yet.

{context}

Write 12 emails following this structure:

DAYS 1-3: REENGAGEMENT & VALUE
- Email 1: Immediate value, soft CTA
- Email 2: Deep dive teaching
- Email 3: Case study/success story

DAYS 4-6: AUTHORITY & TRUST
- Email 4: Paradigm shift insight
- Email 5: Common mistakes to avoid
- Email 6: Behind-the-scenes/methodology

DAYS 7-9: DESIRE BUILDING
- Email 7: Transformation story
- Email 8: ROI/results breakdown
- Email 9: Future pacing (life after working together)

DAYS 10-12: CONVERSION PUSH
- Email 10: Direct sales email with full pitch
- Email 11: Objection handling & FAQ
- Email 12: Final invitation with urgency

For each email provide:
- Subject line (3 variations)
- Preview text
- Full email body
- CTA

Make them feel like a valuable conversation, not a sales barrage."""

    return call_ai(prompt, max_tokens=8000) or "Email sequence generation failed"

def generate_creative_brief(context, analysis):
    """Generate comprehensive creative brief."""
    prompt = f"""Create a comprehensive Creative Brief for marketing this company.

{context}

Analysis:
{analysis[:3000]}

Populate the following sections:

## WHO IS THE IDEAL CLIENT?
(Detailed avatar description)

## WHAT IS THE COST OF STAYING STUCK?
(Emotional and financial costs of inaction)

## 3-5 STEPS TO GET THEM TO THE FINISH LINE
(The transformation journey)

## SINGLE BEST COMPETITIVE ADVANTAGE

## EMOTIONAL BENEFITS CLIENTS EXPERIENCE

## WHAT DISTINGUISHES FROM COMPETITORS

## THE PROMISE
(Core promise that generates interest)

## THE PROBLEM
(In-depth problem description establishing preeminence)

## PROBLEM LIST
(25 specific problems the avatar experiences)

## DESIRED SITUATION
(Their ideal situation described vividly)

## JOURNAL ENTRY
(First-person perspective 6 months after transformation)

## THE GAP + HOW TO BRIDGE IT

## USP & USP DETAILS

## REASONS TO BELIEVE

## FEATURES AND BENEFITS
(List each feature with corresponding benefits)

## THE PRODUCT
(Conversational description as if telling a prospect)

## SALES ARGUMENT
(Compelling argument using straight-line selling)

## OBJECTIONS AND RESPONSES

## IDENTIFIER QUESTIONS (10)
(Questions to call out the audience)

## EMPATHY QUESTIONS (10)
(Questions showing understanding of their situation)

## OPPORTUNITY QUESTIONS (10)
(Questions highlighting benefits)"""

    return call_ai(prompt, max_tokens=8000) or "Creative brief generation failed"

def generate_offer_deep_dive(context, analysis):
    """Generate offer deep dive analysis."""
    prompt = f"""Create an Offer Deep Dive analysis for this company.

{context}

Analysis:
{analysis[:3000]}

Provide comprehensive analysis of:

## 1. CURRENT OFFER ASSESSMENT
- What are they currently selling?
- How is it positioned?
- What's the pricing structure?

## 2. OFFER VS SERVICE ANALYSIS
- Are they selling a service or an offer?
- What quantifiable results could they promise?
- What guarantee could they add?

## 3. VALUE PROPOSITION OPTIMIZATION
- Current value proposition
- Recommended enhanced value proposition
- Why this would convert better

## 4. CLAIM & GUARANTEE STRATEGY
- What specific results could they claim?
- What guarantee would reduce risk?
- Contract stipulations needed

## 5. COMPETITIVE POSITIONING
- Who are their main competitors?
- What makes them different (or could make them different)?
- Transfer of logistical intensity opportunities

## 6. PRICING STRATEGY
- Current pricing analysis
- Recommended pricing structure
- Performance-based options

## 7. OFFER STACK RECOMMENDATION
- Core offer
- Bonuses to add
- How to present the stack

## 8. URGENCY & SCARCITY
- Legitimate urgency factors
- Ethical scarcity elements

## 9. SOCIAL PROOF STRATEGY
- What proof do they need?
- Case study opportunities
- Authority building tactics

## 10. RECOMMENDED OFFER HEADLINE
- 3-5 headline variations for cold traffic
- Explanation of why each would work"""

    return call_ai(prompt, max_tokens=5000) or "Offer deep dive generation failed"

# =============================================================================
# Background Processing
# =============================================================================

def process_batch_async(batch_id, companies_data):
    """Process a batch of companies in background."""
    def run():
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Get all company IDs for this batch
        c.execute("SELECT id FROM companies WHERE batch_id = ? ORDER BY id", (batch_id,))
        company_ids = [row['id'] for row in c.fetchall()]
        conn.close()

        # Process each company sequentially
        for company_id in company_ids:
            process_company(company_id)
            time.sleep(1)  # Small delay between companies

        # Mark batch as complete
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("""UPDATE batches SET status = 'completed', updated_at = CURRENT_TIMESTAMP
                     WHERE batch_id = ?""", (batch_id,))
        conn.commit()
        conn.close()

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

# =============================================================================
# Premium UI Styles
# =============================================================================

PREMIUM_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');

    :root {
        --primary-blue: #1e3a5f;
        --primary-blue-light: #2d5a87;
        --primary-blue-dark: #0f1f33;
        --gold: #d4af37;
        --gold-light: #e8c547;
        --gold-dark: #b8942d;
        --white: #ffffff;
        --off-white: #f8f9fa;
        --gray-100: #f1f3f5;
        --gray-200: #e9ecef;
        --gray-300: #dee2e6;
        --gray-400: #ced4da;
        --gray-500: #adb5bd;
        --gray-600: #6c757d;
        --gray-700: #495057;
        --gray-800: #343a40;
        --gray-900: #212529;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --gradient-gold: linear-gradient(135deg, #d4af37 0%, #f4d03f 50%, #d4af37 100%);
        --gradient-blue: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        --shadow-gold: 0 4px 20px rgba(212, 175, 55, 0.3);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--off-white);
        color: var(--gray-800);
        line-height: 1.6;
        min-height: 100vh;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @keyframes goldGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(212, 175, 55, 0.3); }
        50% { box-shadow: 0 0 40px rgba(212, 175, 55, 0.5); }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .animate-fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }

    .animate-slide-in {
        animation: slideIn 0.5s ease-out forwards;
    }

    .animate-pulse {
        animation: pulse 2s infinite;
    }

    .animate-float {
        animation: float 3s ease-in-out infinite;
    }

    /* Navigation */
    .nav {
        background: var(--gradient-blue);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: var(--shadow-lg);
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
    }

    .nav-brand-icon {
        width: 40px;
        height: 40px;
        background: var(--gradient-gold);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: var(--primary-blue-dark);
        font-size: 1.2rem;
    }

    .nav-brand-text {
        color: var(--white);
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    .nav-brand-text span {
        color: var(--gold);
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .nav-link {
        color: var(--gray-300);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
        font-size: 0.95rem;
    }

    .nav-link:hover {
        color: var(--gold);
    }

    .nav-user {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--white);
        font-size: 0.9rem;
    }

    /* Container */
    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }

    /* Hero Section */
    .hero {
        background: var(--gradient-blue);
        padding: 4rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 50%);
        animation: float 10s ease-in-out infinite;
    }

    .hero-content {
        position: relative;
        z-index: 1;
    }

    .hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        color: var(--white);
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .hero h1 span {
        color: var(--gold);
    }

    .hero p {
        color: var(--gray-300);
        font-size: 1.2rem;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Cards */
    .card {
        background: var(--white);
        border-radius: 16px;
        box-shadow: var(--shadow-md);
        overflow: hidden;
        transition: transform 0.3s, box-shadow 0.3s;
    }

    .card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
    }

    .card-header {
        padding: 1.5rem;
        border-bottom: 1px solid var(--gray-200);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .card-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--gray-800);
    }

    .card-body {
        padding: 1.5rem;
    }

    /* Input Section */
    .input-section {
        background: var(--white);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: var(--shadow-lg);
        margin-bottom: 2rem;
        border: 1px solid var(--gray-200);
    }

    .input-section h2 {
        font-family: 'Playfair Display', serif;
        color: var(--primary-blue);
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
    }

    .input-section p {
        color: var(--gray-600);
        margin-bottom: 1.5rem;
    }

    textarea {
        width: 100%;
        min-height: 200px;
        padding: 1rem;
        border: 2px solid var(--gray-200);
        border-radius: 12px;
        font-family: 'Inter', monospace;
        font-size: 0.9rem;
        resize: vertical;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    textarea:focus {
        outline: none;
        border-color: var(--gold);
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.2);
    }

    .format-guide {
        background: linear-gradient(135deg, var(--gray-100) 0%, var(--white) 100%);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .sample-table {
        overflow-x: auto;
        border-radius: 8px;
        border: 1px solid var(--gray-200);
    }

    .sample-table table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
    }

    .sample-table th {
        background: var(--primary-blue);
        color: white;
        padding: 0.5rem 0.75rem;
        text-align: left;
        font-weight: 600;
        white-space: nowrap;
    }

    .sample-table td {
        background: white;
        padding: 0.5rem 0.75rem;
        border-top: 1px solid var(--gray-200);
        color: var(--gray-600);
        white-space: nowrap;
    }

    textarea::placeholder {
        color: var(--gray-400);
    }

    /* Buttons */
    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 0.875rem 1.75rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s;
        border: none;
        text-decoration: none;
    }

    .btn-primary {
        background: var(--gradient-gold);
        color: var(--primary-blue-dark);
        box-shadow: var(--shadow-gold);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(212, 175, 55, 0.4);
    }

    .btn-secondary {
        background: var(--primary-blue);
        color: var(--white);
    }

    .btn-secondary:hover {
        background: var(--primary-blue-light);
    }

    .btn-outline {
        background: transparent;
        border: 2px solid var(--gold);
        color: var(--gold);
    }

    .btn-outline:hover {
        background: var(--gold);
        color: var(--primary-blue-dark);
    }

    .btn-lg {
        padding: 1rem 2.5rem;
        font-size: 1.1rem;
    }

    /* Company Counter */
    .company-counter {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0;
        padding: 1rem;
        background: var(--gray-100);
        border-radius: 12px;
    }

    .counter-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-blue);
        font-family: 'Playfair Display', serif;
    }

    .counter-label {
        color: var(--gray-600);
    }

    /* Batch Cards */
    .batch-grid {
        display: grid;
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .batch-card {
        background: var(--white);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        animation: fadeIn 0.5s ease-out;
    }

    .batch-header {
        background: var(--gradient-blue);
        padding: 1.25rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .batch-id {
        color: var(--white);
        font-weight: 600;
        font-size: 1.1rem;
    }

    .batch-status {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .batch-status.processing {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
    }

    .batch-status.completed {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }

    .batch-progress {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid var(--gray-200);
    }

    .progress-bar-container {
        height: 8px;
        background: var(--gray-200);
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }

    .progress-bar {
        height: 100%;
        background: var(--gradient-gold);
        border-radius: 4px;
        transition: width 0.5s ease;
    }

    .progress-text {
        font-size: 0.85rem;
        color: var(--gray-600);
    }

    .batch-companies {
        padding: 1rem 1.5rem;
    }

    .company-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.875rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        background: var(--gray-100);
        transition: background 0.2s;
    }

    .company-item:hover {
        background: var(--gray-200);
    }

    .company-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .company-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .company-icon.pending {
        background: var(--gray-200);
        color: var(--gray-500);
    }

    .company-icon.processing {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        animation: pulse 1.5s infinite;
    }

    .company-icon.completed {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }

    .company-icon.failed {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }

    .company-name {
        font-weight: 500;
        color: var(--gray-800);
    }

    .company-status {
        font-size: 0.8rem;
        color: var(--gray-500);
    }

    .view-page-btn {
        padding: 0.5rem 1rem;
        background: var(--gradient-gold);
        color: var(--primary-blue-dark);
        border-radius: 8px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        transition: transform 0.2s;
    }

    .view-page-btn:hover {
        transform: scale(1.05);
    }

    /* Status Icons */
    .status-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
    }

    /* Login Page */
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--gradient-blue);
        padding: 2rem;
    }

    .login-box {
        background: var(--white);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: var(--shadow-xl);
        width: 100%;
        max-width: 400px;
        text-align: center;
    }

    .login-box h1 {
        font-family: 'Playfair Display', serif;
        color: var(--primary-blue);
        margin-bottom: 0.5rem;
    }

    .login-box h1 span {
        color: var(--gold);
    }

    .login-input {
        width: 100%;
        padding: 1rem;
        border: 2px solid var(--gray-200);
        border-radius: 10px;
        font-size: 1rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }

    .login-input:focus {
        outline: none;
        border-color: var(--gold);
    }

    /* Footer */
    .footer {
        background: var(--primary-blue-dark);
        color: var(--gray-400);
        padding: 2rem;
        text-align: center;
        margin-top: auto;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .nav {
            flex-direction: column;
            gap: 1rem;
        }

        .hero h1 {
            font-size: 2rem;
        }

        .container {
            padding: 1rem;
        }
    }
</style>
"""

# =============================================================================
# Public Page Styles (Premium Landing Page)
# =============================================================================

PUBLIC_PAGE_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');

    :root {
        --primary-blue: #1e3a5f;
        --primary-blue-light: #2d5a87;
        --primary-blue-dark: #0f1f33;
        --gold: #d4af37;
        --gold-light: #e8c547;
        --gold-dark: #b8942d;
        --white: #ffffff;
        --off-white: #f8f9fa;
        --gray-100: #f1f3f5;
        --gray-200: #e9ecef;
        --gray-300: #dee2e6;
        --gray-600: #6c757d;
        --gray-800: #343a40;
        --gradient-gold: linear-gradient(135deg, #d4af37 0%, #f4d03f 50%, #d4af37 100%);
        --gradient-blue: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        --shadow-gold: 0 4px 20px rgba(212, 175, 55, 0.3);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--off-white);
        color: var(--gray-800);
        line-height: 1.7;
    }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes goldShimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }

    .animate-fade-up {
        animation: fadeInUp 0.8s ease-out forwards;
    }

    .animate-delay-1 { animation-delay: 0.1s; opacity: 0; }
    .animate-delay-2 { animation-delay: 0.2s; opacity: 0; }
    .animate-delay-3 { animation-delay: 0.3s; opacity: 0; }
    .animate-delay-4 { animation-delay: 0.4s; opacity: 0; }
    .animate-delay-5 { animation-delay: 0.5s; opacity: 0; }

    /* Hero Section */
    .public-hero {
        background: var(--gradient-blue);
        padding: 6rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .public-hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(ellipse at top, rgba(212, 175, 55, 0.15) 0%, transparent 60%);
    }

    .public-hero::after {
        content: '';
        position: absolute;
        bottom: -50px;
        left: 0;
        right: 0;
        height: 100px;
        background: var(--off-white);
        transform: skewY(-2deg);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(212, 175, 55, 0.2);
        color: var(--gold);
        padding: 0.5rem 1.25rem;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.6s ease-out;
    }

    .public-hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        color: var(--white);
        margin-bottom: 1rem;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }

    .public-hero h1 .gold-text {
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .public-hero .tagline {
        color: var(--gray-300);
        font-size: 1.25rem;
        max-width: 700px;
        margin: 0 auto 2rem;
        position: relative;
        z-index: 1;
    }

    /* Why Chosen Section */
    .why-chosen {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.05) 0%, rgba(212, 175, 55, 0.05) 100%);
        padding: 4rem 2rem;
        margin: -2rem 0 2rem;
        position: relative;
        z-index: 2;
    }

    .why-chosen-card {
        max-width: 900px;
        margin: 0 auto;
        background: var(--white);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        border: 1px solid rgba(212, 175, 55, 0.2);
        position: relative;
    }

    .why-chosen-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: var(--gradient-gold);
        border-radius: 22px;
        z-index: -1;
        opacity: 0.5;
    }

    .why-chosen h2 {
        font-family: 'Playfair Display', serif;
        color: var(--primary-blue);
        font-size: 1.75rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .why-chosen h2 .icon {
        width: 40px;
        height: 40px;
        background: var(--gradient-gold);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Asset Sections */
    .assets-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem;
    }

    .asset-section {
        background: var(--white);
        border-radius: 20px;
        margin-bottom: 2rem;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid var(--gray-200);
        animation: scaleIn 0.6s ease-out forwards;
    }

    .asset-header {
        background: var(--gradient-blue);
        padding: 1.5rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        transition: background 0.3s;
    }

    .asset-header:hover {
        background: var(--primary-blue-light);
    }

    .asset-header-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .asset-icon {
        width: 50px;
        height: 50px;
        background: var(--gradient-gold);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    .asset-title {
        color: var(--white);
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 600;
    }

    .asset-subtitle {
        color: var(--gray-300);
        font-size: 0.9rem;
    }

    .expand-icon {
        color: var(--gold);
        font-size: 1.5rem;
        transition: transform 0.3s;
    }

    .asset-section.expanded .expand-icon {
        transform: rotate(180deg);
    }

    .asset-content {
        padding: 2rem;
        display: none;
        background: var(--white);
    }

    .asset-section.expanded .asset-content {
        display: block;
        animation: fadeInUp 0.4s ease-out;
    }

    .asset-content pre {
        background: var(--gray-100);
        padding: 1.5rem;
        border-radius: 12px;
        overflow-x: auto;
        font-size: 0.9rem;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* CTA Section */
    .cta-section {
        background: var(--gradient-blue);
        padding: 5rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .cta-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(ellipse at bottom, rgba(212, 175, 55, 0.2) 0%, transparent 60%);
    }

    .cta-content {
        position: relative;
        z-index: 1;
        max-width: 700px;
        margin: 0 auto;
    }

    .cta-section h2 {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        color: var(--white);
        margin-bottom: 1rem;
    }

    .cta-section p {
        color: var(--gray-300);
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .cta-btn {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: var(--gradient-gold);
        color: var(--primary-blue-dark);
        padding: 1.25rem 3rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 700;
        text-decoration: none;
        box-shadow: var(--shadow-gold);
        transition: transform 0.3s, box-shadow 0.3s;
        animation: goldShimmer 3s linear infinite;
        background-size: 200% auto;
    }

    .cta-btn:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 40px rgba(212, 175, 55, 0.5);
    }

    /* Footer */
    .public-footer {
        background: var(--primary-blue-dark);
        padding: 3rem 2rem;
        text-align: center;
    }

    .footer-brand {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: var(--white);
        margin-bottom: 0.5rem;
    }

    .footer-brand span {
        color: var(--gold);
    }

    .footer-text {
        color: var(--gray-600);
        font-size: 0.9rem;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .public-hero h1 {
            font-size: 2.25rem;
        }

        .asset-header {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }

        .asset-header-left {
            flex-direction: column;
        }
    }
</style>
"""

# =============================================================================
# Routes - Authentication
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == DASHBOARD_USERNAME and verify_password(password):
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")

    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# =============================================================================
# Routes - Dashboard
# =============================================================================

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    batches = db.execute("""
        SELECT b.*,
               (SELECT COUNT(*) FROM companies WHERE batch_id = b.batch_id) as total,
               (SELECT COUNT(*) FROM companies WHERE batch_id = b.batch_id AND status = 'completed') as done
        FROM batches b ORDER BY created_at DESC LIMIT 20
    """).fetchall()

    return render_template_string(DASHBOARD_TEMPLATE, batches=batches)

@app.route('/api/batches')
@login_required
def api_batches():
    db = get_db()
    batches = db.execute("""
        SELECT b.*,
               (SELECT COUNT(*) FROM companies WHERE batch_id = b.batch_id) as total,
               (SELECT COUNT(*) FROM companies WHERE batch_id = b.batch_id AND status = 'completed') as done
        FROM batches b ORDER BY created_at DESC LIMIT 20
    """).fetchall()

    result = []
    for batch in batches:
        companies = db.execute("""
            SELECT id, company_name, status, current_step, slug
            FROM companies WHERE batch_id = ? ORDER BY id
        """, (batch['batch_id'],)).fetchall()

        result.append({
            'batch_id': batch['batch_id'],
            'total': batch['total'],
            'done': batch['done'],
            'status': batch['status'],
            'created_at': batch['created_at'],
            'companies': [dict(c) for c in companies]
        })

    return jsonify(result)

@app.route('/api/process', methods=['POST'])
@login_required
def api_process():
    data = request.json.get('data', '')

    if not data.strip():
        return jsonify({'error': 'No data provided'}), 400

    companies = parse_google_sheets_data(data)

    if not companies:
        return jsonify({'error': 'Could not parse any companies from data'}), 400

    if len(companies) > 30:
        return jsonify({'error': 'Maximum 30 companies per batch'}), 400

    # Create batch
    batch_id = f"BATCH-{secrets.token_hex(4).upper()}"

    db = get_db()
    db.execute("""INSERT INTO batches (batch_id, total_companies, status)
                  VALUES (?, ?, 'processing')""", (batch_id, len(companies)))

    # Create company records
    for company in companies:
        slug = generate_slug(company['company_name'])
        db.execute("""INSERT INTO companies (batch_id, company_name, website, first_name,
                      last_name, email, instagram, linkedin, about, slug)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (batch_id, company['company_name'], company['website'],
                    company['first_name'], company['last_name'], '',
                    company['instagram'], company['linkedin'], company['about'], slug))

    db.commit()

    # Start background processing
    process_batch_async(batch_id, companies)

    return jsonify({
        'success': True,
        'batch_id': batch_id,
        'companies': len(companies)
    })

# =============================================================================
# Routes - Public Landing Pages
# =============================================================================

@app.route('/page/<slug>')
def public_page(slug):
    db = get_db()

    company = db.execute("SELECT * FROM companies WHERE slug = ?", (slug,)).fetchone()
    if not company:
        return "Company not found", 404

    analysis = db.execute("SELECT * FROM analysis WHERE company_id = ?", (company['id'],)).fetchone()
    assets = db.execute("SELECT * FROM assets WHERE company_id = ?", (company['id'],)).fetchone()

    if not assets:
        return render_template_string(PENDING_PAGE_TEMPLATE, company=company)

    return render_template_string(PUBLIC_PAGE_TEMPLATE,
                                  company=company,
                                  analysis=analysis,
                                  assets=assets)

# =============================================================================
# Routes - Health Check
# =============================================================================

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'service': 'kairo-marketing-engine',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

# =============================================================================
# Templates
# =============================================================================

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login | Kairo Marketing Engine</title>
    """ + PREMIUM_STYLES + """
</head>
<body>
    <div class="login-container">
        <div class="login-box animate-fade-in">
            <div class="nav-brand-icon" style="width: 60px; height: 60px; font-size: 1.5rem; margin: 0 auto 1.5rem;">K</div>
            <h1>Kairo <span>Engine</span></h1>
            <p style="color: var(--gray-600); margin-bottom: 2rem;">Marketing Automation Platform</p>

            {% if error %}
            <div style="background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;">
                {{ error }}
            </div>
            {% endif %}

            <form method="POST">
                <input type="text" name="username" class="login-input" placeholder="Username" required>
                <input type="password" name="password" class="login-input" placeholder="Password" required>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Sign In</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard | Kairo Marketing Engine</title>
    """ + PREMIUM_STYLES + """
</head>
<body>
    <nav class="nav">
        <a href="/" class="nav-brand">
            <div class="nav-brand-icon">K</div>
            <div class="nav-brand-text">Kairo <span>Engine</span></div>
        </a>
        <div class="nav-links">
            <a href="/" class="nav-link">Dashboard</a>
            <a href="/logout" class="nav-link">Logout</a>
        </div>
    </nav>

    <div class="hero">
        <div class="hero-content">
            <h1>Marketing <span>Automation</span> Engine</h1>
            <p>Generate complete marketing packages for multiple companies at once. VSL scripts, landing pages, email sequences, and more.</p>
        </div>
    </div>

    <div class="container">
        <div class="input-section animate-fade-in">
            <h2>Generate Marketing Packages</h2>
            <p>Paste company data from Google Sheets (up to 30 companies). Format: First Name, Last Name, Company, Website, Instagram, LinkedIn, About</p>

            <div class="format-guide">
                <h4 style="margin: 0 0 0.75rem 0; color: var(--primary-blue);">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 0.5rem;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    Copy & Paste from Google Sheets
                </h4>
                <p style="margin: 0 0 1rem 0; color: var(--gray-600); font-size: 0.9rem;">
                    Select your data in Google Sheets and paste directly. We auto-detect columns!
                </p>
                <div class="sample-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Company</th>
                                <th>Website</th>
                                <th>First Name</th>
                                <th>Email</th>
                                <th>About</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Acme Corp</td>
                                <td>acme.com</td>
                                <td>John</td>
                                <td>john@acme.com</td>
                                <td>B2B SaaS for...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p style="margin: 0.75rem 0 0 0; color: var(--gray-500); font-size: 0.8rem;">
                    ✓ Columns can be in any order &nbsp; ✓ Headers optional &nbsp; ✓ Max 30 companies
                </p>
            </div>

            <textarea id="companyData" placeholder="Paste your Google Sheets data here...

Acme Corp	https://acme.com	John	Doe	john@acme.com	B2B SaaS company helping teams...
Widget Inc	widgetinc.io	Sarah	Smith	sarah@widget.io	E-commerce platform for..."></textarea>

            <div class="company-counter">
                <div class="counter-number" id="companyCount">0</div>
                <div class="counter-label">
                    <div style="font-weight: 600;">Companies Detected</div>
                    <div style="font-size: 0.85rem;">Maximum 30 per batch</div>
                </div>
            </div>

            <button id="generateBtn" class="btn btn-primary btn-lg" onclick="startProcessing()">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
                Generate Marketing Assets
            </button>
        </div>

        <div id="batchesSection">
            <h2 style="font-family: 'Playfair Display', serif; color: var(--primary-blue); margin-bottom: 1rem;">Recent Batches</h2>
            <div id="batchesList" class="batch-grid">
                <!-- Batches loaded via JS -->
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>Kairo Marketing Engine v1.0 | Powered by AI</p>
    </footer>

    <script>
        const textarea = document.getElementById('companyData');
        const counter = document.getElementById('companyCount');

        textarea.addEventListener('input', function() {
            const lines = this.value.trim().split('\\n').filter(l => l.trim());
            counter.textContent = lines.length;
            counter.style.color = lines.length > 30 ? '#ef4444' : 'var(--primary-blue)';
        });

        function startProcessing() {
            const data = textarea.value.trim();
            if (!data) {
                alert('Please paste company data first');
                return;
            }

            const btn = document.getElementById('generateBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="animate-pulse">Processing...</span>';

            fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: data })
            })
            .then(r => r.json())
            .then(result => {
                if (result.error) {
                    alert(result.error);
                } else {
                    textarea.value = '';
                    counter.textContent = '0';
                    loadBatches();
                }
                btn.disabled = false;
                btn.innerHTML = '<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg> Generate Marketing Assets';
            })
            .catch(err => {
                alert('Error: ' + err.message);
                btn.disabled = false;
                btn.innerHTML = '<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg> Generate Marketing Assets';
            });
        }

        function loadBatches() {
            fetch('/api/batches')
            .then(r => r.json())
            .then(batches => {
                const container = document.getElementById('batchesList');
                if (batches.length === 0) {
                    container.innerHTML = '<p style="color: var(--gray-500); text-align: center; padding: 2rem;">No batches yet. Paste company data above to get started.</p>';
                    return;
                }

                container.innerHTML = batches.map(batch => `
                    <div class="batch-card">
                        <div class="batch-header">
                            <span class="batch-id">${batch.batch_id}</span>
                            <span class="batch-status ${batch.status}">${batch.status === 'completed' ? '✓ Completed' : '⏳ Processing'}</span>
                        </div>
                        <div class="batch-progress">
                            <div class="progress-bar-container">
                                <div class="progress-bar" style="width: ${batch.total > 0 ? (batch.done / batch.total * 100) : 0}%"></div>
                            </div>
                            <div class="progress-text">${batch.done} of ${batch.total} companies completed</div>
                        </div>
                        <div class="batch-companies">
                            ${batch.companies.map(c => `
                                <div class="company-item">
                                    <div class="company-info">
                                        <div class="company-icon ${c.status}">${getStatusIcon(c.status)}</div>
                                        <div>
                                            <div class="company-name">${c.company_name}</div>
                                            <div class="company-status">${c.current_step || c.status}</div>
                                        </div>
                                    </div>
                                    ${c.status === 'completed' ? `<a href="/page/${c.slug}" class="view-page-btn" target="_blank">View Page</a>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('');
            });
        }

        function getStatusIcon(status) {
            switch(status) {
                case 'completed': return '✓';
                case 'failed': return '✗';
                case 'pending': return '○';
                default: return '◉';
            }
        }

        // Load batches on page load and refresh every 5 seconds
        loadBatches();
        setInterval(loadBatches, 5000);
    </script>
</body>
</html>
"""

PUBLIC_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ company.company_name }} | Marketing Package by Kairo</title>
    """ + PUBLIC_PAGE_STYLES + """
</head>
<body>
    <header class="public-hero">
        <div class="hero-badge animate-fade-up">
            <span>✨</span> Custom Marketing Package
        </div>
        <h1 class="animate-fade-up animate-delay-1">
            <span class="gold-text">{{ company.company_name }}</span>
        </h1>
        <p class="tagline animate-fade-up animate-delay-2">
            A personalized marketing strategy crafted specifically for your business by Kairo
        </p>
    </header>

    {% if analysis and analysis.target_market %}
    <section class="why-chosen">
        <div class="why-chosen-card animate-fade-up animate-delay-3">
            <h2>
                <span class="icon">🎯</span>
                Why We Selected {{ company.company_name }}
            </h2>
            <div style="color: var(--gray-600); line-height: 1.8;">
                {{ analysis.target_market | safe }}
            </div>
        </div>
    </section>
    {% endif %}

    <div class="assets-container">
        <!-- VSL Script -->
        <div class="asset-section animate-fade-up animate-delay-1" onclick="toggleSection(this)">
            <div class="asset-header">
                <div class="asset-header-left">
                    <div class="asset-icon">📹</div>
                    <div>
                        <div class="asset-title">VSL Script</div>
                        <div class="asset-subtitle">4-6 minute video sales letter script</div>
                    </div>
                </div>
                <div class="expand-icon">▼</div>
            </div>
            <div class="asset-content">
                <pre>{{ assets.vsl_script }}</pre>
            </div>
        </div>

        <!-- Landing Page -->
        <div class="asset-section animate-fade-up animate-delay-2" onclick="toggleSection(this)">
            <div class="asset-header">
                <div class="asset-header-left">
                    <div class="asset-icon">🌐</div>
                    <div>
                        <div class="asset-title">Landing Page Copy</div>
                        <div class="asset-subtitle">High-converting sales page content</div>
                    </div>
                </div>
                <div class="expand-icon">▼</div>
            </div>
            <div class="asset-content">
                <pre>{{ assets.landing_page_copy }}</pre>
            </div>
        </div>

        <!-- Email Sequence -->
        <div class="asset-section animate-fade-up animate-delay-3" onclick="toggleSection(this)">
            <div class="asset-header">
                <div class="asset-header-left">
                    <div class="asset-icon">📧</div>
                    <div>
                        <div class="asset-title">12-Day Email Sequence</div>
                        <div class="asset-subtitle">Nurture sequence to convert prospects</div>
                    </div>
                </div>
                <div class="expand-icon">▼</div>
            </div>
            <div class="asset-content">
                <pre>{{ assets.email_sequence }}</pre>
            </div>
        </div>

        <!-- Creative Brief -->
        <div class="asset-section animate-fade-up animate-delay-4" onclick="toggleSection(this)">
            <div class="asset-header">
                <div class="asset-header-left">
                    <div class="asset-icon">🎨</div>
                    <div>
                        <div class="asset-title">Creative Brief</div>
                        <div class="asset-subtitle">Brand voice, messaging & design guidelines</div>
                    </div>
                </div>
                <div class="expand-icon">▼</div>
            </div>
            <div class="asset-content">
                <pre>{{ assets.creative_brief }}</pre>
            </div>
        </div>

        <!-- Offer Deep Dive -->
        <div class="asset-section animate-fade-up animate-delay-5" onclick="toggleSection(this)">
            <div class="asset-header">
                <div class="asset-header-left">
                    <div class="asset-icon">💎</div>
                    <div>
                        <div class="asset-title">Offer Deep Dive</div>
                        <div class="asset-subtitle">Strategic offer analysis & optimization</div>
                    </div>
                </div>
                <div class="expand-icon">▼</div>
            </div>
            <div class="asset-content">
                <pre>{{ assets.offer_deep_dive }}</pre>
            </div>
        </div>
    </div>

    <section class="cta-section">
        <div class="cta-content">
            <h2>Ready to Implement This Strategy?</h2>
            <p>Let's discuss how Kairo can build and run your entire marketing funnel on a performance basis — you only pay when you earn more.</p>
            <a href="https://kairo-scales.com/boostconversions" class="cta-btn" target="_blank">
                <span>📅</span> Book Your Strategy Call
            </a>
        </div>
    </section>

    <footer class="public-footer">
        <div class="footer-brand">Kairo <span>Marketing</span></div>
        <p class="footer-text">Performance-Based Marketing That Scales Your Business</p>
    </footer>

    <script>
        function toggleSection(section) {
            section.classList.toggle('expanded');
        }

        // Expand first section by default
        document.querySelector('.asset-section').classList.add('expanded');
    </script>
</body>
</html>
"""

PENDING_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ company.company_name }} | Processing...</title>
    """ + PUBLIC_PAGE_STYLES + """
    <style>
        .pending-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--gradient-blue);
            text-align: center;
            padding: 2rem;
        }
        .pending-content {
            background: var(--white);
            padding: 3rem;
            border-radius: 20px;
            max-width: 500px;
        }
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid var(--gray-200);
            border-top-color: var(--gold);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="pending-container">
        <div class="pending-content">
            <div class="spinner"></div>
            <h1 style="font-family: 'Playfair Display', serif; color: var(--primary-blue); margin-bottom: 0.5rem;">
                {{ company.company_name }}
            </h1>
            <p style="color: var(--gray-600); margin-bottom: 1rem;">
                Your marketing package is being generated...
            </p>
            <p style="color: var(--gray-500); font-size: 0.9rem;">
                Status: <strong>{{ company.current_step or company.status }}</strong>
            </p>
            <p style="color: var(--gray-400); font-size: 0.85rem; margin-top: 1rem;">
                This page will auto-refresh in 10 seconds
            </p>
        </div>
    </div>
    <script>
        setTimeout(() => location.reload(), 10000);
    </script>
</body>
</html>
"""

# =============================================================================
# Ron Breitenbach — Lead Capture + Email Sequence
# =============================================================================
#
# Required environment variables:
#   SENDGRID_API_KEY   — SendGrid API key for sending emails
#   FROM_EMAIL         — Sender address (e.g. ron@yourdomain.com)
#   FROM_NAME          — Sender display name (e.g. "Ron Breitenbach")
#   RON_GUIDE_URL      — Direct link to the PDF/page with the Investor ID Guide
#
# Google Sheets (master sheet, existing):
#   Sheet ID: 1yY2jqgokNDe-C0NLurARlxGTA--Hg9lUHLK219-Wywk
#   Tab name: "Ron Leads — Apr 2026"
# =============================================================================

import gspread
from google.oauth2.service_account import Credentials as ServiceCredentials

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL       = os.getenv("FROM_EMAIL", "ron@kairoscales.com")
FROM_NAME        = os.getenv("FROM_NAME", "Ron Breitenbach")
RON_GUIDE_URL    = os.getenv("RON_GUIDE_URL", "https://kairoscales.com/investor-id-guide")

MASTER_SHEET_ID  = "1yY2jqgokNDe-C0NLurARlxGTA--Hg9lUHLK219-Wywk"
RON_SHEET_TAB    = "Ron Leads — Apr 2026"

# ---------------------------------------------------------------------------
# DB tables for Ron's leads
# ---------------------------------------------------------------------------

def init_ron_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ron_leads (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name  TEXT,
        email      TEXT NOT NULL,
        phone      TEXT,
        source     TEXT DEFAULT 'landing_page',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ron_email_queue (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id     INTEGER NOT NULL,
        email_index INTEGER NOT NULL,
        send_at     TIMESTAMP NOT NULL,
        sent_at     TIMESTAMP,
        status      TEXT DEFAULT 'pending',
        FOREIGN KEY (lead_id) REFERENCES ron_leads(id)
    )''')
    conn.commit()
    conn.close()

init_ron_db()

# ---------------------------------------------------------------------------
# 8-email sequence copy
# ---------------------------------------------------------------------------

def get_ron_emails(first_name, guide_url):
    name = first_name or "there"
    return [
        # ── Email 0: Immediate ──────────────────────────────────────────────
        {
            "subject": "Your Free Investor ID Guide is here 📬",
            "html": f"""
<p>Hey {name},</p>
<p>Your <strong>Investor ID Guide</strong> is ready. Here's your link:</p>
<p style="text-align:center;margin:28px 0;">
  <a href="{guide_url}" style="background:#6F00FF;color:#fff;padding:14px 32px;border-radius:100px;text-decoration:none;font-weight:700;font-size:16px;">
    Download Your Free Guide →
  </a>
</p>
<p>Inside you'll find the 5 investor paths, the one question that tells you which fits you, and a 90-day action plan for your specific niche.</p>
<p>Read it tonight. Most people who download this and take the 90-day plan seriously see their first deal within the year.</p>
<p>— Ron</p>
<p style="font-size:12px;color:#888;">P.S. Over the next few weeks I'll send you a few more resources — real stories, numbers, and frameworks from 15 years of investing. You can unsubscribe anytime.</p>
"""
        },
        # ── Email 1: Day 1 ──────────────────────────────────────────────────
        {
            "subject": "Which of the 5 niches is actually yours?",
            "html": f"""
<p>Hey {name},</p>
<p>Yesterday I sent over the Investor ID Guide. Today I want to cut straight to the part most people skip.</p>
<p><strong>The 5 niches aren't equal for everyone.</strong></p>
<p>Fix &amp; flip sounds exciting — but if you work 50 hours a week and have $40K saved, that path will drain you before your first deal closes.</p>
<p>Wholesale sounds easy — but if you hate cold calling and pressure-heavy negotiations, you'll quit in month two.</p>
<p>The guide walks you through this, but here's the shortcut question:</p>
<blockquote style="border-left:4px solid #6F00FF;padding-left:16px;margin:20px 0;font-style:italic;color:#444;">
  "If I had 10 hours a week and $50K to deploy — what would let me sleep well AND build wealth?"
</blockquote>
<p>Your answer to that is your niche. Everything else is noise.</p>
<p>Reply to this email and tell me what you think your niche is. I read every reply.</p>
<p>— Ron</p>
"""
        },
        # ── Email 2: Day 3 ──────────────────────────────────────────────────
        {
            "subject": "From $200K/yr to $1M+ in real estate profits (real story)",
            "html": f"""
<p>Hey {name},</p>
<p>One of my students — I'll call him Marcus — came to me earning $200K a year as a software engineer. Solid income. Zero real estate experience.</p>
<p>His first question: <em>"Where do I start?"</em></p>
<p>We ran through the Investor ID framework. His profile: high income, limited time (maybe 6 hours/week), low appetite for active management. Classic <strong>rental/BRRRR</strong> investor.</p>
<p>Year one: One duplex in a B-class neighborhood. Small cash flow. Big learning curve.</p>
<p>Year three: 7 doors. Cash flow covering his car payment every month.</p>
<p>Year five: 22 doors. Passive income exceeding $1M in total real estate portfolio value. Refinanced into a 4-unit commercial property. Hasn't touched his 401k since.</p>
<p><strong>None of this required genius. It required identifying the right niche and not quitting.</strong></p>
<p>The guide gives you the framework Marcus used to identify his path. Your first step after reading it: pick ONE niche and spend 90 days learning only that niche.</p>
<p>— Ron</p>
"""
        },
        # ── Email 3: Day 5 ──────────────────────────────────────────────────
        {
            "subject": "The LLC mistake that cost this couple 14 homes",
            "html": f"""
<p>Hey {name},</p>
<p>I mentioned this in the guide but I want to hammer it home because I've seen it destroy investors personally.</p>
<p>A couple I know — bought their first rental property in their personal name. They thought they'd "set up the LLC later." Later never came.</p>
<p>A tenant slipped on their property. Sued. Won.</p>
<p>The judgment pierced their personal assets. They lost 14 properties over the following 18 months — not because of the lawsuit directly, but because lenders called notes and their credit collapsed.</p>
<p><strong>14 properties. Gone. Because they skipped one $500 step.</strong></p>
<p>Before you buy a single property:</p>
<ol style="margin:16px 0;padding-left:20px;line-height:2;">
  <li>Form an LLC (one per property cluster or one holding LLC minimum)</li>
  <li>Get landlord liability insurance</li>
  <li>Never buy in your personal name</li>
</ol>
<p>This is covered in the guide but I want you to take it seriously. The people who skip this are usually the ones who are "pretty sure it won't happen to them."</p>
<p>It happens.</p>
<p>— Ron</p>
"""
        },
        # ── Email 4: Day 7 ──────────────────────────────────────────────────
        {
            "subject": "Your 90-day action plan (let's make it real)",
            "html": f"""
<p>Hey {name},</p>
<p>You've had the guide for a week. By now you should have a sense of which niche fits you.</p>
<p>Here's what the next 90 days should look like, regardless of niche:</p>
<p><strong>Days 1–30: Education only.</strong> No deals. Read 2 books specific to your niche. Join 1 local real estate investor meetup. Find a mentor or community (we have one — 40,000 strong).</p>
<p><strong>Days 31–60: Analyze 30 deals.</strong> Don't buy. Just run the numbers on 30 real deals in your market using the criteria in the guide. Your eye for a good deal develops here.</p>
<p><strong>Days 61–90: Make your first offer.</strong> Not your first purchase — your first offer. You may not close. That's fine. The reps are what matter.</p>
<p>The investors who follow this sequence close their first deal within 12 months. The investors who skip straight to buying usually lose money and quit.</p>
<p>Which day are you on right now?</p>
<p>— Ron</p>
"""
        },
        # ── Email 5: Day 10 ─────────────────────────────────────────────────
        {
            "subject": "The question I get asked most (answered)",
            "html": f"""
<p>Hey {name},</p>
<p>The #1 question I get from people at my stage in their journey:</p>
<blockquote style="border-left:4px solid #6F00FF;padding-left:16px;margin:20px 0;font-style:italic;color:#444;">
  "Ron, I don't have enough money to start. What do I do?"
</blockquote>
<p>Here's the honest answer: <strong>capital is rarely the real barrier.</strong></p>
<p>Wholesale requires almost no capital — you're assigning contracts, not buying homes.</p>
<p>BRRRR requires capital initially, but after the refinance, that capital comes back — and you still own the asset.</p>
<p>Hard money lenders fund fix &amp; flips. Private money comes from your network. Partnerships split the equity.</p>
<p>The real barrier is <strong>knowledge and conviction.</strong> Most people use "I don't have money" as a reason not to learn. They wait until they have capital — and by the time they do, they still haven't learned anything.</p>
<p>Start learning now. The deals will find the capital. I've seen it happen dozens of times.</p>
<p>— Ron</p>
<p style="font-size:12px;color:#888;">P.S. If you want to talk through your specific situation, just reply to this email. I do read them.</p>
"""
        },
        # ── Email 6: Day 14 ─────────────────────────────────────────────────
        {
            "subject": "A real deal breakdown (numbers inside)",
            "html": f"""
<p>Hey {name},</p>
<p>Let me show you what a real deal looks like. This is a rental property I analyzed recently (numbers slightly adjusted):</p>
<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;">
  <tr style="background:#f3f0ff;"><td style="padding:10px;font-weight:700;">Purchase Price</td><td style="padding:10px;">$185,000</td></tr>
  <tr><td style="padding:10px;font-weight:700;">Down Payment (20%)</td><td style="padding:10px;">$37,000</td></tr>
  <tr style="background:#f3f0ff;"><td style="padding:10px;font-weight:700;">Monthly Rent</td><td style="padding:10px;">$1,850</td></tr>
  <tr><td style="padding:10px;font-weight:700;">PITI + Insurance</td><td style="padding:10px;">$1,240</td></tr>
  <tr style="background:#f3f0ff;"><td style="padding:10px;font-weight:700;">Vacancy (8%)</td><td style="padding:10px;">$148</td></tr>
  <tr><td style="padding:10px;font-weight:700;">Maintenance (5%)</td><td style="padding:10px;">$93</td></tr>
  <tr style="background:#f3f0ff;font-weight:700;color:#6F00FF;"><td style="padding:10px;">Monthly Cash Flow</td><td style="padding:10px;">$369/mo</td></tr>
  <tr><td style="padding:10px;font-weight:700;">Cash-on-Cash Return</td><td style="padding:10px;">11.96%</td></tr>
</table>
<p>That's $4,428/year on $37,000 invested. Not life-changing alone — but stack 10 of these and you're at $44K/year in passive income. Stack 20 and you've replaced a solid salary.</p>
<p>This is how wealth gets built in real estate. Not one big score. Systematic accumulation.</p>
<p>Run this analysis on 30 deals in your market. By deal 30 you'll know what a good deal looks like without a spreadsheet.</p>
<p>— Ron</p>
"""
        },
        # ── Email 7: Day 21 ─────────────────────────────────────────────────
        {
            "subject": "Ready to take the next step?",
            "html": f"""
<p>Hey {name},</p>
<p>Three weeks ago you downloaded the Investor ID Guide. I hope it's been useful.</p>
<p>I want to be direct with you:</p>
<p>The guide gives you the map. But maps don't build portfolios. <strong>Mentorship, community, and accountability do.</strong></p>
<p>I'm part of a nationwide investor education platform — 40,000 active investors, live trainings, deal reviews, and a community of people doing exactly what you're trying to do.</p>
<p>If you're serious about your first deal in the next 12 months, I'd like to get on a quick call with you. No pitch. Just a conversation about where you are, what niche fits you, and what your realistic next step looks like.</p>
<p>I pick up the phone. That's not a marketing line — it's just how I operate.</p>
<p style="text-align:center;margin:28px 0;">
  <a href="https://calendly.com/ronbreitenbach" style="background:#6F00FF;color:#fff;padding:14px 32px;border-radius:100px;text-decoration:none;font-weight:700;font-size:16px;">
    Book a Free 20-Minute Call →
  </a>
</p>
<p>If you're not ready yet, no problem — keep learning. I'll still be here.</p>
<p>— Ron</p>
<p style="font-size:12px;color:#888;">You've received this email because you downloaded the free Investor ID Guide. To unsubscribe, reply with "unsubscribe" in the subject line.</p>
"""
        },
    ]

# ---------------------------------------------------------------------------
# Email sender (SendGrid)
# ---------------------------------------------------------------------------

def send_email_sendgrid(to_email, to_name, subject, html_body):
    """Send a single email via SendGrid API."""
    if not SENDGRID_API_KEY:
        print(f"[EMAIL] No SENDGRID_API_KEY — skipping email to {to_email}")
        return False
    payload = {
        "personalizations": [{"to": [{"email": to_email, "name": to_name}]}],
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_body}],
    }
    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )
    if resp.status_code in (200, 202):
        print(f"[EMAIL] Sent '{subject}' to {to_email}")
        return True
    print(f"[EMAIL] SendGrid error {resp.status_code}: {resp.text}")
    return False

# ---------------------------------------------------------------------------
# Google Sheets helper
# ---------------------------------------------------------------------------

def append_ron_lead_to_sheet(first_name, last_name, email, phone):
    try:
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceCredentials.from_service_account_file(creds_path, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(MASTER_SHEET_ID)
        try:
            ws = sh.worksheet(RON_SHEET_TAB)
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title=RON_SHEET_TAB, rows=1000, cols=10)
            ws.append_row(["First Name", "Last Name", "Email", "Phone", "Source", "Created At"])
        ws.append_row([first_name, last_name, email, phone, "landing_page",
                       datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")])
        print(f"[SHEETS] Appended lead {email} to '{RON_SHEET_TAB}'")
    except Exception as e:
        print(f"[SHEETS] Error saving lead to sheet: {e}")

# ---------------------------------------------------------------------------
# Background email scheduler thread
# ---------------------------------------------------------------------------

def ron_email_scheduler():
    """Runs in background. Every 60s, checks for pending emails and sends them."""
    from datetime import timezone
    while True:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            rows = c.execute("""
                SELECT q.id, q.lead_id, q.email_index,
                       l.first_name, l.last_name, l.email
                FROM ron_email_queue q
                JOIN ron_leads l ON l.id = q.lead_id
                WHERE q.status = 'pending' AND q.send_at <= ?
                ORDER BY q.send_at ASC
                LIMIT 20
            """, (now_str,)).fetchall()

            for row in rows:
                emails = get_ron_emails(row["first_name"], RON_GUIDE_URL)
                idx = row["email_index"]
                if idx < len(emails):
                    email_data = emails[idx]
                    full_name = f"{row['first_name'] or ''} {row['last_name'] or ''}".strip()
                    ok = send_email_sendgrid(
                        to_email=row["email"],
                        to_name=full_name or row["email"],
                        subject=email_data["subject"],
                        html_body=email_data["html"],
                    )
                    status = "sent" if ok else "failed"
                    c.execute("""
                        UPDATE ron_email_queue
                        SET status=?, sent_at=?
                        WHERE id=?
                    """, (status, now_str, row["id"]))
                    conn.commit()
        except Exception as e:
            print(f"[SCHEDULER] Error: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
        time.sleep(60)

# Start the scheduler in a background thread
_scheduler_thread = threading.Thread(target=ron_email_scheduler, daemon=True)
_scheduler_thread.start()

# ---------------------------------------------------------------------------
# Email send delays (days after signup)
# ---------------------------------------------------------------------------
EMAIL_SEND_DELAYS_DAYS = [0, 1, 3, 5, 7, 10, 14, 21]

# ---------------------------------------------------------------------------
# Webhook endpoint: POST /webhook/ron-lead
# ---------------------------------------------------------------------------

@app.route("/webhook/ron-lead", methods=["POST", "OPTIONS"])
def ron_lead_webhook():
    # CORS preflight
    if request.method == "OPTIONS":
        resp = app.make_default_options_response()
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return resp

    data = request.get_json(silent=True) or {}
    first_name = (data.get("first_name") or "").strip()
    last_name  = (data.get("last_name")  or "").strip()
    email      = (data.get("email")      or "").strip().lower()
    phone      = (data.get("phone")      or "").strip()

    if not email:
        resp = jsonify({"error": "email is required"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp, 400

    # 1. Save lead to SQLite
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO ron_leads (first_name, last_name, email, phone)
        VALUES (?, ?, ?, ?)
    """, (first_name, last_name, email, phone))
    lead_id = c.lastrowid

    # 2. Schedule all 8 emails
    now = datetime.utcnow()
    for idx, delay_days in enumerate(EMAIL_SEND_DELAYS_DAYS):
        from datetime import timedelta
        send_at = now + timedelta(days=delay_days)
        # Email 0 sends in 10 seconds so it arrives quickly
        if delay_days == 0:
            from datetime import timedelta as td
            send_at = now + td(seconds=10)
        c.execute("""
            INSERT INTO ron_email_queue (lead_id, email_index, send_at)
            VALUES (?, ?, ?)
        """, (lead_id, idx, send_at.strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    # 3. Save to Google Sheet (non-blocking)
    sheet_thread = threading.Thread(
        target=append_ron_lead_to_sheet,
        args=(first_name, last_name, email, phone),
        daemon=True,
    )
    sheet_thread.start()

    resp = jsonify({"success": True, "message": "Lead captured and email sequence started."})
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp, 200


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
