# AIAA Agentic OS

An AI-powered agency operating system that runs inside Claude Code. Just paste prompts and Claude handles everything - from VSL funnels to cold emails to market research.

**Version:** 5.0 | **Last Updated:** January 2026

---

## Quick Start

**Open Claude Code and paste this prompt to get started:**

```
I want to set up AIAA Agentic OS. Please help me through the entire process.

## Step 1: Clone the Repository
Run: git clone https://github.com/stopmoclay/AIAA-Agentic-OS.git
Then change into that directory.

## Step 2: Install Dependencies
Run: pip install -r requirements.txt

## Step 3: Walk Me Through Setup
Be my setup wizard. Ask me questions ONE AT A TIME to configure:

1. API Keys (.env file)
   - OPENROUTER_API_KEY (required) - https://openrouter.ai/keys
   - PERPLEXITY_API_KEY (optional) - for deep research
   - SLACK_WEBHOOK_URL (optional) - for notifications

2. Agency Profile (context/ folder)
   Ask me: agency name, website, services, target audience, brand voice

3. First Client (optional)
   Ask me: company name, industry, what they sell, their audience

## Step 4: Test the System
Run a simple workflow to verify everything works.

Be encouraging, explain why each step matters, and save files as we go. Start now!
```

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

**Competitor Analysis:**
```
Analyze [COMPETITOR NAME] as a competitor. Their website is [WEBSITE]. Compare them to [YOUR COMPANY/PRODUCT].
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
| Workflow Templates | 118 |
| Execution Scripts | 126 |
| Skill Bibles (AI Knowledge) | 264 |

The system uses a **DOE** architecture:
- **Directives** - Natural language SOPs that define what to do
- **Orchestration** - Claude Code reads directives and makes decisions
- **Execution** - Python scripts handle API calls and data processing

---

## Required API Keys

| Key | What It's For | Get It At |
|-----|---------------|-----------|
| OPENROUTER_API_KEY | Powers all AI generation (required) | https://openrouter.ai/keys |
| PERPLEXITY_API_KEY | Deep research capabilities | https://perplexity.ai/settings/api |
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
