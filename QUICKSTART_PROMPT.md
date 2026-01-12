# AIAA Agentic OS - Interactive Setup Guide

**Version 2.3** | **139 Workflows** | **Complete Agency Operating System**

Paste this entire prompt into Claude Code to get a fully interactive setup experience. Claude will clone the system, configure your APIs, set up your agency profile, deploy your dashboard, and walk you through everything step by step.

---

## The Prompt (Copy Everything Below)

```
I want to set up AIAA Agentic OS v2.3. Please help me through the entire process interactively, asking me ONE question at a time and waiting for my response before moving on.

## Step 1: Clone & Install

1. Clone the repository:
   git clone https://github.com/stopmoclay/AIAA-Agentic-OS.git
   
2. Change into the directory:
   cd AIAA-Agentic-OS
   
3. Install dependencies:
   pip install -r requirements.txt

Run these commands and confirm they complete successfully.

## Step 2: Configure API Keys (.env file)

Create my .env file with API keys. Ask me for each one individually:

**Required Keys:**
- OPENROUTER_API_KEY (required for all AI features)
  - Get free at: https://openrouter.ai/keys
  - Sign up takes 2 minutes

**Recommended Keys (ask if I want each):**
- PERPLEXITY_API_KEY - Deep research & prospect intel
  - Get at: https://perplexity.ai/settings/api
- ANTHROPIC_API_KEY - Direct Claude access (faster)
  - Get at: https://console.anthropic.com
- APIFY_API_TOKEN - Lead scraping (Google Maps, LinkedIn)
  - Get at: https://console.apify.com/account/integrations
- FAL_KEY - AI image generation (Nano Banana Pro)
  - Get at: https://fal.ai/dashboard/keys
- SLACK_WEBHOOK_URL - Notifications
  - Create at: https://api.slack.com/messaging/webhooks

For each missing key, provide simple instructions to get it.

## Step 3: Google OAuth Setup (Optional but Recommended)

Ask if I want Google Docs/Sheets integration. If yes:
1. Go to https://console.cloud.google.com
2. Create a project and enable Google Docs + Sheets APIs
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json to project root
5. Run: python3 execution/create_google_doc.py --test

This enables automatic document creation and lead exports.

## Step 4: Agency Profile Setup

Ask me questions one at a time and create my agency profile:

Questions to ask:
1. What's your agency name?
2. What's your website URL?
3. What services do you offer? (list them)
4. Who is your ideal client/target audience?
5. What makes you different from competitors?
6. Describe your brand voice (professional, casual, bold, friendly, authoritative, etc.)
7. Who is the owner/founder? (name and background)

Save to these files:
- context/agency.md - Agency overview
- context/brand_voice.md - Tone and style guide
- context/services.md - Service offerings
- context/owner.md - Founder info

## Step 5: First Client Profile (Optional)

Ask if I want to set up a client profile. If yes, create clients/{client_name}/ with:
- profile.md - Company info, industry, audience
- rules.md - Content guidelines
- preferences.md - Style preferences

Questions:
1. Client/company name?
2. Their website?
3. Industry?
4. What do they sell?
5. Target audience?
6. Content rules or tone preferences?

## Step 6: Deploy Dashboard to Railway

Ask if I want to deploy the monitoring dashboard. If yes:

1. Check Railway CLI: railway --version
2. If not installed: npm install -g @railway/cli
3. Login: railway login
4. Deploy dashboard:
   cd railway_apps/aiaa_dashboard
   railway init
   railway up

5. Set environment variables in Railway dashboard:
   - DASHBOARD_USERNAME (default: admin)
   - DASHBOARD_PASSWORD_HASH (generate with: python3 -c "import hashlib; print(hashlib.sha256(b'YOUR_PASSWORD').hexdigest())")
   - Copy API keys from .env

6. Get dashboard URL and provide credentials

The dashboard includes:
- 139 documented workflows
- Light/dark mode
- Environment variable management
- Webhook monitoring
- Mobile-responsive design

## Step 7: Test the System

Run a simple test based on my agency type:
- If marketing agency: Generate a cold email sequence
- If content agency: Create a blog post or social content
- If design agency: Generate an ad creative concept
- General: Run company research on a sample company

Verify output and show me the result.

## Step 8: Show What's Available

Give me a quick tour:

**Content Creation (25+ workflows):**
- Blog posts, LinkedIn posts, Twitter threads
- YouTube scripts, Instagram Reels
- Email newsletters, Content calendars

**Sales & Funnels (30+ workflows):**
- VSL scripts, Sales pages, Landing pages
- Cold email sequences, Follow-up automation
- Webinar funnels, Lead magnets

**Research & Intelligence (20+ workflows):**
- Company research, Competitor monitoring
- Prospect research, Market analysis
- Niche validation, Pricing strategy

**Lead Generation (15+ workflows):**
- Google Maps scraping, LinkedIn scraping
- Email enrichment, Lead scoring
- CRM automation, Prospecting pipelines

**Paid Advertising (15+ workflows):**
- Meta ad campaigns, Google Ads
- Ad creative generation, FB Ad Library analysis
- Video ad scripts, Static ad generation

**Client Management (20+ workflows):**
- Onboarding automation, QBR generation
- Churn risk alerts, Health scores
- Invoice generation, Testimonial requests

## Important Instructions

- Ask me ONE question at a time
- Wait for my response before continuing
- If I don't know something, help me or skip it
- Save files as we complete each section
- Be encouraging and explain why each step matters
- If errors occur, help me debug them

Let's start! Begin with Step 1: Clone & Install.
```

---

## What This Does

When you paste this prompt, Claude Code becomes your personal setup assistant:

1. **Downloads & installs** - Clones repo and installs dependencies
2. **Configures API keys** - One-by-one walkthrough with instructions
3. **Sets up Google OAuth** - Optional Docs/Sheets integration
4. **Creates agency profile** - Your brand voice and services
5. **Sets up clients** - Optional client profiles
6. **Deploys dashboard** - Railway deployment with 139 workflows
7. **Tests the system** - Verifies everything works
8. **Shows capabilities** - Tour of all 139 workflows

**Time to complete:** 15-30 minutes depending on options chosen

## Dashboard Features (v2.3)

Once deployed, your dashboard includes:
- **139 documented workflows** with full descriptions, prerequisites, and how-to-run instructions
- **Light/dark mode** with localStorage persistence
- **Environment variable management** - View and set API keys
- **Webhook endpoints** - Calendly prep, generic webhooks
- **Real-time event logs** - Track all workflow executions
- **Mobile-responsive** - Works on phones and tablets
- **Password protection** - Secure login system

Dashboard URL: `https://your-app.railway.app`
