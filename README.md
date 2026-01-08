# AIAA Agentic OS

A production-ready agentic workflow system that turns Claude Code into an autonomous marketing agency operator. Built on the **DOE (Directive-Orchestration-Execution)** architecture pattern.

**Version:** 5.0 | **Last Updated:** January 2026

---

## Recommended Setup: Use Claude Code

**The easiest way to set up this system is with Claude Code.**

1. Clone this repository
2. Open the folder in Claude Code
3. Copy the prompt from [`QUICKSTART_PROMPT.md`](QUICKSTART_PROMPT.md) and paste it

Claude Code will:
- Run the installer (`python3 install.py`)
- Walk you through the setup wizard (`python3 wizard.py`)
- Configure your API keys and agency profile
- Teach you the system interactively
- Run your first workflow

**Or run setup manually:**
```bash
git clone https://github.com/stopmoclay/AIAA-Agentic-OS.git
cd AIAA-Agentic-OS
python3 install.py    # Install dependencies
python3 wizard.py     # Interactive setup wizard
python3 run.py        # Launch the system
```

---

## System Overview

| Resource | Count | Location |
|----------|-------|----------|
| Directives (SOPs) | 118 | `directives/` |
| Execution Scripts | 126 | `execution/` |
| Skill Bibles | 264 | `skills/` |
| Agency Context | 4 files | `context/` |
| Client Profiles | Template ready | `clients/` |
| Cloud Deployments | Modal AI | `execution/modal_apps/` |

---

## Architecture

The system uses a 3-layer **DOE** pattern that separates concerns for reliability:

```
USER REQUEST
     │
     ▼
┌─────────────────────────────────────────────────┐
│  DIRECTIVES (What to do)                        │
│  Natural language SOPs with quality gates       │
│  Location: directives/*.md                      │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  ORCHESTRATION (Decision making)                │
│  Claude Code agent reads directives,            │
│  loads skill bibles, routes to scripts          │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│  EXECUTION (Doing the work)                     │
│  Deterministic Python scripts for API calls     │
│  Location: execution/*.py                       │
└─────────────────────────────────────────────────┘
     │
     ▼
OUTPUT → Local files, Google Docs, Slack
```

**Why DOE works:** LLMs are probabilistic. Pushing deterministic work into Python scripts keeps reliability high across multi-step workflows.

---

## Quick Start

### Generate a Complete VSL Funnel
```bash
python3 execution/generate_complete_vsl_funnel.py \
  --company "Acme Corp" \
  --website "https://acmecorp.com" \
  --offer "B2B Lead Generation"
```

**Output (3-5 minutes):**
- Market Research Report
- VSL Script (2500+ words)
- Sales Page Copy (1500+ words)
- Email Sequence (7 emails)
- Google Docs + Slack notification

### Research a Company
```bash
python3 execution/research_company_offer.py \
  --company "Target Company" \
  --website "https://targetcompany.com"
```

### Write Cold Emails
```bash
python3 execution/write_cold_emails.py \
  --sender "John Smith" \
  --company "Acme Corp" \
  --offer "Lead generation" \
  --target "Marketing agencies"
```

---

## Project Structure

```
Agentic Workflows/
├── context/                 # Agency identity & brand voice
│   ├── agency.md           # Agency positioning & mission
│   ├── owner.md            # Owner background & expertise
│   ├── brand_voice.md      # Tone & style guidelines
│   └── services.md         # Service offerings & pricing
│
├── clients/                 # Per-client profiles & rules
│   └── _template/          # Template for new clients
│
├── directives/              # 118 workflow SOPs
│   ├── vsl_funnel_orchestrator.md
│   ├── company_market_research.md
│   ├── cold_email_scriptwriter.md
│   └── ...
│
├── execution/               # 126 Python scripts
│   ├── generate_complete_vsl_funnel.py
│   ├── research_company_offer.py
│   ├── create_google_doc.py
│   ├── deploy_to_modal.py
│   └── modal_apps/         # Cloud-deployed workflows
│
├── skills/                  # 264 skill bibles
│   ├── SKILL_BIBLE_vsl_writing_production.md
│   ├── SKILL_BIBLE_cold_email_mastery.md
│   ├── SKILL_BIBLE_funnel_copywriting_mastery.md
│   └── ...
│
├── CLAUDE.md               # Agent instructions (load this)
└── .env                    # API keys (never commit)
```

---

## Key Capabilities

### Content & Copy
| Capability | Directive | Script |
|------------|-----------|--------|
| VSL Funnels | `vsl_funnel_orchestrator.md` | `generate_complete_vsl_funnel.py` |
| Sales Pages | `sales_page_writer.md` | `generate_sales_page.py` |
| Cold Emails | `cold_email_scriptwriter.md` | `write_cold_emails.py` |
| Email Sequences | `email_sequence_writer.md` | `generate_email_sequence.py` |
| Blog Posts | `blog_post_writer.md` | `generate_blog_post.py` |

### Lead Generation
| Capability | Directive | Script |
|------------|-----------|--------|
| LinkedIn Scraping | `linkedin_lead_scraper.md` | `scrape_linkedin_apify.py` |
| Company Research | `company_market_research.md` | `research_company_offer.py` |
| Google Maps Scraping | `google_maps_scraper.md` | `scrape_google_maps.py` |
| Website Contact Scraping | `website_contact_scraper.md` | `scrape_website_contacts.py` |

### Operations
| Capability | Directive | Script |
|------------|-----------|--------|
| Client Onboarding | `ai_customer_onboarding_agent.md` | `onboard_new_client.py` |
| Google Doc Creation | `create_google_doc.md` | `create_google_doc.py` |
| Slack Notifications | `send_slack_notification.md` | `send_slack_notification.py` |
| Modal Deployment | `deploy_to_modal.md` | `deploy_to_modal.py` |

---

## Cloud Deployment (Modal AI)

Deploy any workflow as a cloud webhook:

```bash
# List deployable workflows
python3 execution/deploy_to_modal.py --list

# Deploy to Modal
python3 execution/deploy_to_modal.py --directive vsl_funnel_writer

# Setup secrets from .env
python3 execution/deploy_to_modal.py --setup-secrets
```

Each deployed app gets webhook, health, and info endpoints.

---

## Context System

### Agency Context (`context/`)
Load before generating any branded content:
- `agency.md` - Name, positioning, unique value
- `owner.md` - Background, expertise, credentials
- `brand_voice.md` - Tone, vocabulary, style rules
- `services.md` - Offerings, pricing, packages

### Client Profiles (`clients/{name}/`)
Load for client-specific work:
- `profile.md` - Business info, goals, audience
- `rules.md` - Must-follow guidelines
- `preferences.md` - Style preferences
- `history.md` - Past work, outcomes

---

## Configuration

### Required API Keys (.env)
```
OPENROUTER_API_KEY     # Primary LLM access
PERPLEXITY_API_KEY     # Market research
SLACK_WEBHOOK_URL      # Notifications
```

### Optional
```
OPENAI_API_KEY                    # Direct OpenAI access
GOOGLE_APPLICATION_CREDENTIALS    # Google Docs/Sheets
```

### First-Time Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Edit with your keys

# Google OAuth (for Docs)
python3 execution/create_google_doc.py --test

# Modal AI (for cloud deployment)
pip install modal
python3 -m modal setup
python3 execution/deploy_to_modal.py --setup-secrets
```

---

## Content Standards

| Content Type | Minimum | Target | Notes |
|--------------|---------|--------|-------|
| VSL Script | 2,000 | 2,500-3,000 | 16-20 min video |
| Sales Page | 1,500 | 1,500-3,000 | Long-form |
| Email (each) | 300 | 300-500 | 7-email sequences |

---

## How It Works

1. **Parse Intent** - Understand what's needed
2. **Load Context** - Agency context + client context + skill bibles
3. **Find Directive** - Locate the SOP for the task
4. **Execute** - Run Python scripts in sequence
5. **Quality Gate** - Validate outputs
6. **Deliver** - Google Docs + Slack notification
7. **Self-Anneal** - Learn and improve the system

---

## Recent Updates (V5)

- Context system for agency identity and client profiles
- 264 skill bibles covering marketing, sales, and operations
- Modal AI cloud deployment
- 118 workflow directives
- 126 execution scripts
- Improved VSL script frameworks with proper length enforcement

---

## License

Private repository - Client Ascension internal use.
