# AIAA Agentic OS

An AI-powered agency operating system that runs inside Claude Code. Just paste prompts and Claude handles everything - from VSL funnels to cold emails to market research. Includes a beautiful web dashboard for monitoring workflows and managing your system.

**Version:** 2.3 | **139 Workflows** | **Last Updated:** January 2026

---

## Quick Start

**Open Claude Code and paste this entire prompt to get started:**

```
I want to set up AIAA Agentic OS v2.3. Please help me through the entire process interactively, asking me ONE question at a time and waiting for my response before moving on.

## Step 1: Clone & Install

Run these commands to download and install the system:

git clone https://github.com/stopmoclay/AIAA-Agentic-OS.git
cd AIAA-Agentic-OS
pip install -r requirements.txt

Execute these commands and confirm they complete successfully before moving on.

## Step 2: Configure API Keys (.env file)

Create my .env file with API keys. Ask me for each one individually:

**Required Keys:**
- OPENROUTER_API_KEY (required for all AI features)
  - Get free at: https://openrouter.ai/keys

**Recommended Keys (ask if I want each):**
- PERPLEXITY_API_KEY - Deep research (https://perplexity.ai/settings/api)
- ANTHROPIC_API_KEY - Direct Claude access (https://console.anthropic.com)
- APIFY_API_TOKEN - Lead scraping (https://console.apify.com/account/integrations)
- FAL_KEY - AI image generation (https://fal.ai/dashboard/keys)
- SLACK_WEBHOOK_URL - Notifications (https://api.slack.com/messaging/webhooks)

## Step 3: Agency Profile Setup

Ask me questions one at a time to create my agency profile:
1. Agency name?
2. Website URL?
3. Services offered?
4. Target audience?
5. What makes you different?
6. Brand voice?

Save to: context/agency.md, context/brand_voice.md, context/services.md

## Step 4: Deploy AIAA Dashboard to Railway (AUTOMATE THIS)

Deploy my monitoring dashboard. Handle as much as possible automatically:

### 4a: Check Prerequisites
- Check: railway --version (if missing: npm install -g @railway/cli)
- Check: railway whoami (if not logged in: railway login)

### 4b: Get My Credentials
Ask me: "What username for your dashboard?" and "What password?"
Then YOU generate the password hash using heredoc (avoids escape issues with special chars):
python3 << 'PYHASH'
import hashlib
password = "MY_PASSWORD"
print(hashlib.sha256(password.encode()).hexdigest())
PYHASH

### 4c: Deploy
cd railway_apps/aiaa_dashboard
railway init
railway up

### 4d: Set Environment Variables
railway variables set DASHBOARD_USERNAME="[my_username]"
railway variables set DASHBOARD_PASSWORD_HASH="[hash_you_generated]"
railway variables set FLASK_SECRET_KEY="[generate with: python3 -c 'import secrets; print(secrets.token_hex(32))']"

### 4e: Generate Domain & Verify
railway domain
curl https://[domain]/health

### 4f: Give Me My Login Details
- Dashboard URL
- Username
- Password

## Step 5: Test the System

Run a test workflow based on my agency type.

## Step 6: Show What's Available

Tour of 139 workflows: Content, Sales, Research, Lead Gen, Ads, Client Management.

## Important Instructions

- Ask ONE question at a time
- For Railway deployment, DO AS MUCH AUTOMATICALLY AS POSSIBLE
- Generate hashes, secrets, and run commands for me
- Only ask for input when absolutely needed

Let's start! Begin with Step 1.
```

---

## What This Does

When you paste this prompt, Claude Code becomes your personal setup assistant:

1. **Downloads & installs** - Clones repo and installs dependencies
2. **Configures API keys** - One-by-one walkthrough with instructions
3. **Creates agency profile** - Your brand voice and services
4. **Deploys dashboard to Railway** - **Fully automated:**
   - Creates Railway project
   - Deploys dashboard code
   - Sets all environment variables (generates hashes/secrets for you)
   - Generates public domain
   - Verifies deployment
   - Provides login credentials
5. **Tests the system** - Verifies everything works
6. **Shows capabilities** - Tour of all 139 workflows

**Time to complete:** 15-20 minutes

---

## What You Can Do

Once set up, just tell Claude what you need. Here are example prompts:

### Sales Copy

**VSL Funnel:**
```
Create a complete VSL funnel for [COMPANY NAME]. Their website is [WEBSITE] and they sell [PRODUCT/SERVICE] to [TARGET AUDIENCE].
```

**Sales Page:**
```
Write a long-form sales page for [PRODUCT]. Price point is [PRICE]. Target audience is [AUDIENCE]. Focus on [MAIN BENEFIT].
```

**Cold Emails:**
```
Write a cold email sequence for my [SERVICE] targeting [INDUSTRY]. I'm [YOUR NAME] from [YOUR COMPANY]. Focus on [PAIN POINT].
```

### Content Creation

**Blog Post:**
```
Write a 1500-word blog post about [TOPIC] for [TARGET AUDIENCE]. Tone should be [PROFESSIONAL/CASUAL/etc].
```

**LinkedIn Post:**
```
Write a LinkedIn post about [TOPIC]. Style: [STORY/EDUCATIONAL/LISTICLE]. Make it engaging and end with a call to action.
```

**YouTube Script:**
```
Write a YouTube script about [TOPIC]. Target length: [X] minutes. Style: [EDUCATIONAL/TUTORIAL/STORY].
```

### Research

**Company Research:**
```
Research [COMPANY NAME]. Their website is [WEBSITE]. I need to understand their business model, target audience, competitors, and positioning.
```

**Market Research:**
```
Research the [INDUSTRY] market. I need to understand key players, trends, opportunities, and challenges.
```

### Ad Creatives

**Meta Ads Campaign (with AI images):**
```
Generate a Meta ads campaign for [PRODUCT] targeting [AUDIENCE]. Generate images for the ads.
```

**Static Ad Creatives:**
```
Create static ad creatives for [PRODUCT] on [PLATFORM]. Generate the actual images.
```

### Lead Generation

**Google Maps Leads:**
```
Find [BUSINESS TYPE] in [LOCATION]. I need their name, address, phone, website, and reviews.
```

**LinkedIn Scraping:**
```
Find [JOB TITLES] at companies in [INDUSTRY] located in [LOCATION].
```

### Landing Pages

**AI Landing Page:**
```
Generate a landing page for [PRODUCT] targeting [AUDIENCE]. Style: [modern-gradient/neo-noir/editorial-luxury]. Deploy to Cloudflare.
```

### Client Work

**Add a New Client:**
```
Help me add a new client: [CLIENT NAME]. Their website is [WEBSITE]. They're in the [INDUSTRY] industry and sell [PRODUCTS/SERVICES] to [AUDIENCE].
```

**Monthly Report:**
```
Create a monthly report for [CLIENT NAME]. Key metrics: [LIST METRICS]. Highlights: [ACHIEVEMENTS].
```

---

## System Overview

| What | Count |
|------|-------|
| Workflow Templates | 139 |
| Execution Scripts | 130+ |
| Skill Bibles (AI Knowledge) | 280+ |

The system uses a **DOE** architecture:
- **Directives** - Natural language SOPs that define what to do
- **Orchestration** - Claude Code reads directives and makes decisions
- **Execution** - Python scripts handle API calls and data processing

---

## AIAA Dashboard (v2.3)

A beautiful web dashboard for monitoring and managing your AIAA system. Deploy to Railway in minutes.

### Dashboard Features

- **139 Documented Workflows** - Full descriptions, prerequisites, how-to-run instructions
- **Light/Dark Mode** - Toggle with localStorage persistence
- **Environment Variables** - View and set API keys from the UI
- **Webhook Monitoring** - Track incoming webhooks and events
- **Real-time Logs** - See all workflow executions
- **Mobile Responsive** - Works on phones and tablets
- **Password Protected** - Secure login system

### Deploy to Railway

**Prerequisites:**
- Railway account (https://railway.app)
- Railway CLI installed: `npm install -g @railway/cli`

**Step 1: Login to Railway**
```bash
railway login
```

**Step 2: Navigate to dashboard folder**
```bash
cd railway_apps/aiaa_dashboard
```

**Step 3: Initialize Railway project**
```bash
railway init
```
Select "Empty Project" when prompted.

**Step 4: Deploy**
```bash
railway up
```

**Step 5: Configure environment variables**

In Railway's dashboard (https://railway.app), add these variables:

| Variable | Description |
|----------|-------------|
| `DASHBOARD_USERNAME` | Login username (default: admin) |
| `DASHBOARD_PASSWORD_HASH` | SHA-256 hash of your password |
| `FLASK_SECRET_KEY` | Random secret for sessions (optional) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `PERPLEXITY_API_KEY` | Your Perplexity API key |
| `SLACK_WEBHOOK_URL` | Slack notifications (optional) |

**Generate password hash (use heredoc to avoid escape issues with special characters like ! or \):**
```bash
python3 << 'PYHASH'
import hashlib
password = "YOUR_PASSWORD_HERE"
print(hashlib.sha256(password.encode()).hexdigest())
PYHASH
```

**Step 6: Generate domain**

In Railway dashboard, go to Settings → Generate Domain to get your public URL.

Your dashboard will be available at: `https://your-app.up.railway.app`

### Dashboard Screenshots

Once deployed, your dashboard includes:
- **Overview** - Stats, recent events, quick workflow access
- **Workflows** - Browse all 139 workflows with search
- **Workflow Details** - Full documentation with code examples
- **Environment** - Manage API keys
- **Webhooks** - Available endpoints
- **Logs** - Event history

---

## Required API Keys

| Key | What It's For | Get It At |
|-----|---------------|-----------|
| OPENROUTER_API_KEY | Powers all AI generation (required) | https://openrouter.ai/keys |
| PERPLEXITY_API_KEY | Deep research capabilities | https://perplexity.ai/settings/api |
| FAL_API_KEY | AI image generation (Nano Banana Pro) | https://fal.ai/dashboard/keys |
| SLACK_WEBHOOK_URL | Notifications | https://api.slack.com/apps |
| APIFY_API_TOKEN | Lead scraping | https://console.apify.com |

---

## Context System

### Your Agency (`context/` folder)
- `agency.md` - Your agency name, positioning, mission
- `brand_voice.md` - Your tone and style guidelines
- `services.md` - What you offer

### Your Clients (`clients/{name}/` folders)
- `profile.md` - Client business info
- `rules.md` - Content rules for this client
- `preferences.md` - Their style preferences

---

## New Features (v2.3 - January 2026)

### AIAA Dashboard
Beautiful web dashboard deployed to Railway with:
- 139 fully documented workflows
- Light/dark mode toggle
- Environment variable management
- Webhook monitoring & logs
- Mobile-responsive design

### AI Ad Creative Generation
All ad workflows now generate actual images using **fal.ai Nano Banana Pro**:
- `generate_meta_ads_campaign.py --generate-images`
- `generate_ad_creative.py --generate-images`
- `generate_static_ad.py --generate-images`

### Calendly Meeting Prep Automation
Automatic research when meetings are booked:
- Instant Slack alerts
- Company & prospect research via Perplexity
- AI-generated talking points via Claude
- Formatted Google Docs with meeting briefs

### Landing Page Generator with PROPS Formula
Generate high-converting landing pages with the PROPS funnel structure:
- Problem amplification (3-layer deep)
- Result demonstration (Triple R formula)
- Proof pyramid (testimonials)
- Objection handling (FAQ)
- Simple next step (offer stack)

### 139 Workflow Categories
- **Content Creation** (25+): Blogs, social posts, YouTube scripts, newsletters
- **Sales & Funnels** (30+): VSL scripts, sales pages, webinar funnels, email sequences
- **Research** (20+): Company research, competitor monitoring, niche validation
- **Lead Generation** (15+): Google Maps, LinkedIn, email enrichment
- **Paid Advertising** (15+): Meta ads, Google Ads, ad creative generation
- **Client Management** (20+): Onboarding, QBRs, churn alerts, invoices

---

## Content Standards

| Content Type | Target Length |
|--------------|---------------|
| VSL Script | 2,500-3,000 words (16-20 min video) |
| Sales Page | 1,500-3,000 words |
| Blog Post | 1,500-2,500 words |
| Email | 300-500 words each |

---

## License

Private repository - Client Ascension internal use.
