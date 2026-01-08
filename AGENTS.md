# AIAA Agentic OS - Complete Agent Instructions

> **Version:** 3.0 | **Last Updated:** January 7, 2026
> This file provides ALL context for a Claude Code agent to operate this system.

---

## Quick Reference

| Resource | Count | Location |
|----------|-------|----------|
| Directives (SOPs) | 110+ | `directives/*.md` |
| Execution Scripts | 120+ | `execution/*.py` |
| Skill Bibles | 260+ | `skills/SKILL_BIBLE_*.md` |
| Agency Context | - | `context/` |
| Client Profiles | - | `clients/{client_name}/` |
| Deployed Apps | Modal AI | `execution/modal_apps/` |

**Environment Variables Required:**
```
OPENROUTER_API_KEY     # Primary LLM access (Claude, GPT via OpenRouter)
OPENAI_API_KEY         # OpenAI direct (optional)
PERPLEXITY_API_KEY     # Market research
GOOGLE_APPLICATION_CREDENTIALS  # Google Docs/Sheets
SLACK_WEBHOOK_URL      # Notifications
```

---

## System Architecture (DOE Pattern)

This system uses a **Directive-Orchestration-Execution (DOE)** architecture that separates concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REQUEST                                  │
│              "Create a VSL funnel for Acme Corp"                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: DIRECTIVE (What to do)                                │
│  ─────────────────────────────────                              │
│  • Location: directives/*.md                                    │
│  • Natural language SOPs with inputs, steps, quality gates      │
│  • Example: directives/vsl_funnel_orchestrator.md               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: ORCHESTRATION (Decision making)                       │
│  ─────────────────────────────────────────                      │
│  • THIS IS YOU - The Claude Code Agent                          │
│  • Read directives, load skill bibles, call scripts in order    │
│  • Handle errors, make routing decisions, self-anneal           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: EXECUTION (Doing the work)                            │
│  ───────────────────────────────────                            │
│  • Location: execution/*.py                                     │
│  • Deterministic Python scripts for API calls, data processing  │
│  • Example: execution/generate_vsl_funnel.py                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT                                      │
│  • Local files: .tmp/*.md                                       │
│  • Google Docs: Formatted, shareable                            │
│  • Slack: Notification with links                               │
└─────────────────────────────────────────────────────────────────┘
```

**Why DOE Works:** LLMs are probabilistic (90% accuracy = 59% over 5 steps). Push deterministic work into Python scripts. You focus on decision-making.

---

## Directory Structure

```
Agentic Workflows/
├── .env                    # API keys (NEVER commit)
├── .tmp/                   # Intermediate outputs (gitignored)
├── credentials.json        # Google OAuth credentials
├── token.pickle           # Google OAuth token
│
├── context/               # AGENCY CONTEXT - Who you are
│   ├── agency.md          # Agency info, services, positioning
│   ├── owner.md           # Owner profile, background, expertise
│   ├── brand_voice.md     # Tone, style, communication preferences
│   └── services.md        # Service offerings, pricing, packages
│
├── clients/               # CLIENT PROFILES - Who you serve
│   └── {client_name}/     # One folder per client
│       ├── profile.md     # Client info, business, goals
│       ├── rules.md       # Specific rules for this client
│       ├── preferences.md # Style, tone, do's and don'ts
│       └── history.md     # Past work, context, outcomes
│
├── directives/            # SOPs - What to do (110+ files)
│   ├── vsl_funnel_orchestrator.md
│   ├── company_market_research.md
│   ├── deploy_to_modal.md
│   └── ...
│
├── execution/             # Python scripts - Doing (120+ files)
│   ├── deploy_to_modal.py
│   ├── generate_vsl_funnel.py
│   ├── create_google_doc.py
│   ├── modal_apps/             # Generated Modal deployments
│   └── ...
│
├── skills/                # Domain expertise (260+ skill bibles)
│   ├── SKILL_BIBLE_*.md
│   └── ...
│
├── AGENTS.md              # THIS FILE - Agent instructions
├── CLAUDE.md              # Mirrored instructions for Claude
├── install.py             # First-time setup
├── run.py                 # Main interface
└── wizard.py              # Interactive onboarding
```

---

## Agency Context & Client Profiles

### Agency Context (`context/`)
This folder contains information about YOU and YOUR AGENCY. Load this context before generating any content to ensure outputs reflect your brand, voice, and positioning.

**Required Files:**

| File | Purpose | Example Content |
|------|---------|-----------------|
| `agency.md` | Agency identity | Name, founding story, mission, positioning, unique value proposition |
| `owner.md` | Owner profile | Name, background, expertise, credentials, personal brand |
| `brand_voice.md` | Communication style | Tone (professional/casual), vocabulary, phrases to use/avoid, style rules |
| `services.md` | Service offerings | Services, pricing tiers, packages, deliverables, timelines |

**When to Load Agency Context:**
- Content creation (blogs, emails, social posts)
- Client proposals and pitches
- Sales scripts and cold outreach
- Any branded deliverables

### Client Profiles (`clients/{client_name}/`)
Each client gets their own folder with specific context. Load these files when doing work FOR a specific client.

**Client Folder Structure:**
```
clients/
├── acme_corp/
│   ├── profile.md      # Business info, industry, goals, target audience
│   ├── rules.md        # MUST-FOLLOW rules for this client
│   ├── preferences.md  # Style preferences, tone, formatting
│   └── history.md      # Past projects, outcomes, learnings
│
├── startup_xyz/
│   ├── profile.md
│   ├── rules.md
│   └── ...
```

**Client Profile Fields (`profile.md`):**
- Company name and description
- Industry and niche
- Target audience
- Business goals
- Key products/services
- Competitors
- Unique selling points

**Client Rules (`rules.md`):**
- Content guidelines (words to use/avoid)
- Brand voice requirements
- Approval processes
- Compliance requirements
- Formatting standards

**When to Load Client Context:**
- Any deliverable FOR that client
- Client-specific campaigns
- Personalized content
- Before any client meeting prep

### Loading Context in Practice

```python
# Before generating content, always:
1. Check if context/agency.md exists → Load it
2. Check if client is specified → Load clients/{client}/*.md
3. Apply context to all prompts and outputs
```

**Example: Writing cold emails for client "Acme Corp"**
```
Load: context/agency.md          # Your agency voice
Load: context/brand_voice.md     # Your style rules
Load: clients/acme_corp/profile.md    # Their business info
Load: clients/acme_corp/rules.md      # Their specific rules
Then: Execute cold_email_scriptwriter directive
```

---

## Execution Flow (7 Phases)

When you receive ANY request, follow this flow:

### Phase 1: Parse User Input
Extract intent and map to capability:
```
"Write a VSL for my coaching business" → vsl_funnel_orchestrator
"Deploy the newsletter workflow"       → deploy_to_modal
"Research this company"                → company_market_research
"Generate cold emails"                 → cold_email_scriptwriter
```

### Phase 2: Capability Check
Does a directive exist for this task?

| Condition | Action |
|-----------|--------|
| Directive exists | Load it and execute |
| No directive | Check if script exists in execution/ |
| Nothing exists | Create new directive + script (Leader Manufacturing) |

**Quick check:**
```bash
ls directives/ | grep -i "<keyword>"
ls execution/ | grep -i "<keyword>"
```

### Phase 3: Load Context
Before execution, load ALL required context:
```
1. Agency Context       → context/*.md (who YOU are)
2. Client Context       → clients/{client}/  (if client-specific work)
3. Primary Directive    → directives/<workflow>.md
4. Skill Bibles         → skills/SKILL_BIBLE_<topic>.md
5. Related Directives   → Check "Related Directives" section
6. Execution Scripts    → execution/<script>.py
```

**CRITICAL: Always Load Agency Context First**
Before generating ANY content, check `context/` for:
- `agency.md` - Your agency's name, positioning, services
- `owner.md` - Owner's name, background, expertise
- `brand_voice.md` - Tone, style guide, communication rules
- `services.md` - What you offer, pricing, packages

**For Client-Specific Work, Also Load:**
```
clients/{client_name}/
├── profile.md      # Who they are, their business, goals
├── rules.md        # MUST follow these rules for this client
├── preferences.md  # Their style preferences
└── history.md      # Past work, what worked, what didn't
```

**Example for client VSL funnel:**
```
context/agency.md                    # Your agency context
context/brand_voice.md               # Your voice/style
clients/acme_corp/profile.md         # Client info
clients/acme_corp/rules.md           # Client-specific rules
directives/vsl_funnel_orchestrator.md
├── skills/SKILL_BIBLE_vsl_writing_production.md
├── skills/SKILL_BIBLE_funnel_copywriting_mastery.md
└── execution/generate_vsl_funnel.py
```

### Phase 4: Execute Directive
Follow the directive SOP step-by-step:
1. Check prerequisites (API keys, inputs)
2. Run each workflow phase in order
3. Save checkpoints to `.tmp/`
4. Validate outputs at quality gates

### Phase 5: Quality Gates
Validate at each checkpoint. Common checks:
- Required fields present?
- Output format correct?
- Word count/length appropriate?
- No API errors?

### Phase 6: Delivery
Standard delivery pipeline:
```
1. Save locally     → .tmp/<project>/<filename>.md
2. Create Google Doc → execution/create_google_doc.py
3. Send Slack       → execution/send_slack_notification.py
```

### Phase 7: Self-Annealing
After EVERY task:
- Did errors occur? → Fix script, update directive
- Better approach found? → Update skill bible
- Edge case discovered? → Add to directive

---

## Common Workflows

### 1. VSL Funnel Creation (Complete Pipeline)
```bash
# Option A: Run the complete orchestrator
python3 execution/generate_complete_vsl_funnel.py \
  --company "Acme Corp" \
  --website "https://acmecorp.com" \
  --offer "B2B Lead Generation"

# Option B: Run individual steps
python3 execution/research_company_offer.py --company "Acme Corp" --website "https://acmecorp.com"
python3 execution/generate_vsl_script.py --research-file ".tmp/research.json"
python3 execution/generate_sales_page.py --vsl-file ".tmp/vsl_script.md"
python3 execution/generate_email_sequence.py --research-file ".tmp/research.json"
```

**Outputs:**
- `.tmp/vsl_funnel_<company>/01_research.md`
- `.tmp/vsl_funnel_<company>/02_vsl_script.md`
- `.tmp/vsl_funnel_<company>/03_sales_page.md`
- `.tmp/vsl_funnel_<company>/04_email_sequence.md`

### 2. Cold Email Campaign
```bash
python3 execution/write_cold_emails.py \
  --sender "John Smith" \
  --company "Acme Corp" \
  --offer "Lead generation service" \
  --target "Marketing agencies"
```

### 3. Market Research
```bash
python3 execution/research_company_offer.py \
  --company "Target Company" \
  --website "https://targetcompany.com" \
  --offer "Their main product"
```

### 4. Content Generation
```bash
# Blog post
python3 execution/generate_blog_post.py --topic "AI in marketing" --length 1500

# LinkedIn post
python3 execution/generate_linkedin_post.py --topic "Agency growth tips"

# Newsletter
python3 execution/generate_newsletter.py --theme "Weekly AI updates"
```

---

## Cloud Deployment (Modal AI)

Deploy any workflow as a cloud webhook:

### Deploy a Workflow
```bash
# List all deployable workflows
python3 execution/deploy_to_modal.py --list

# Check what a workflow needs
python3 execution/deploy_to_modal.py --info vsl_funnel_writer

# Deploy to Modal
python3 execution/deploy_to_modal.py --directive vsl_funnel_writer

# Dry run (generate without deploying)
python3 execution/deploy_to_modal.py --directive vsl_funnel_writer --dry-run
```

### Setup Modal Secrets
```bash
# Auto-create secrets from .env
python3 execution/deploy_to_modal.py --setup-secrets

# Or manually via Modal CLI
modal secret create anthropic-secret ANTHROPIC_API_KEY=<key>
modal secret create openrouter-secret OPENROUTER_API_KEY=<key>
modal secret create slack-webhook SLACK_WEBHOOK_URL=<url>
```

### Deployed Endpoints
Each deployed app gets 3 endpoints:
```
POST https://<workspace>--<app>-webhook.modal.run  # Execute workflow
GET  https://<workspace>--<app>-health.modal.run   # Health check
GET  https://<workspace>--<app>-info.modal.run     # Workflow info
```

**Example:**
```bash
curl -X POST "https://lucas-37998--vsl-funnel-writer-webhook.modal.run" \
  -H "Content-Type: application/json" \
  -d '{"data": {"product": "AI Course", "price": "$997", "audience": "Marketers"}}'
```

---

## Key Execution Scripts

### Content & Copy
| Script | Purpose |
|--------|---------|
| `generate_vsl_funnel.py` | Complete VSL + landing page + emails |
| `generate_vsl_script.py` | VSL script only |
| `generate_sales_page.py` | Sales page copy |
| `generate_email_sequence.py` | Email nurture sequence |
| `generate_blog_post.py` | Long-form blog content |
| `generate_linkedin_post.py` | LinkedIn content |
| `write_cold_emails.py` | Cold email sequences |

### Research & Data
| Script | Purpose |
|--------|---------|
| `research_company_offer.py` | Deep company research via Perplexity |
| `research_market_deep.py` | Market/industry research |
| `research_prospect_deep.py` | Individual prospect research |
| `scrape_linkedin_apify.py` | LinkedIn profile scraping |

### Delivery & Integration
| Script | Purpose |
|--------|---------|
| `create_google_doc.py` | Upload to Google Docs |
| `send_slack_notification.py` | Send Slack messages |
| `deploy_to_modal.py` | Deploy workflows to Modal AI |

### Utilities
| Script | Purpose |
|--------|---------|
| `convert_n8n_to_directive.py` | Convert N8N JSON to directive |
| `parse_vtt_transcript.py` | Extract text from VTT files |
| `validate_emails.py` | Email validation |

---

## Skill Bibles

Skill bibles provide deep domain expertise. Load relevant ones before execution.

### Finding Skill Bibles
```bash
# List all skill bibles
ls skills/SKILL_BIBLE_*.md

# Search by topic
ls skills/ | grep -i "vsl\|funnel\|email\|sales"
```

### Key Skill Bibles by Category

**VSL & Funnels:**
- `SKILL_BIBLE_vsl_writing_production.md`
- `SKILL_BIBLE_vsl_script_mastery_fazio.md`
- `SKILL_BIBLE_funnel_copywriting_mastery.md`
- `SKILL_BIBLE_agency_funnel_building.md`

**Cold Email & Outreach:**
- `SKILL_BIBLE_cold_email_mastery.md`
- `SKILL_BIBLE_cold_dm_email_conversion.md`
- `SKILL_BIBLE_email_deliverability.md`

**Agency & Sales:**
- `SKILL_BIBLE_agency_sales_system.md`
- `SKILL_BIBLE_agency_scaling_roadmap.md`
- `SKILL_BIBLE_offer_positioning.md`

**AI & Automation:**
- `SKILL_BIBLE_ai_automation_agency.md`
- `SKILL_BIBLE_monetizable_agentic_workflows.md`
- `SKILL_BIBLE_ai_prompting_workflows.md`

---

## Creating New Capabilities (Leader Manufacturing)

When a capability doesn't exist:

### Step 1: Check If It Really Doesn't Exist
```bash
ls directives/ | grep -i "<keyword>"
ls execution/ | grep -i "<keyword>"
ls skills/ | grep -i "<keyword>"
```

### Step 2: Create New Directive
```markdown
# directives/new_workflow.md

## What This Workflow Is
[One paragraph description]

## What It Does
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Prerequisites
- Required API keys
- Required skill bibles
- Installation commands

## How to Run
```bash
python3 execution/new_workflow.py --arg1 "value"
```

## Inputs
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| arg1 | string | Yes | Description |

## Process
### Step 1: [Name]
[Details]

### Step 2: [Name]
[Details]

## Quality Gates
- [ ] Check 1
- [ ] Check 2

## Edge Cases
- Edge case 1 → Solution
- Edge case 2 → Solution
```

### Step 3: Create Execution Script
```python
#!/usr/bin/env python3
"""
New Workflow - [Description]

Usage:
    python3 execution/new_workflow.py --arg1 "value"
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arg1", required=True)
    args = parser.parse_args()
    
    # Implementation
    print(f"Running with {args.arg1}")
    
if __name__ == "__main__":
    main()
```

### Step 4: Create Skill Bible (If Needed)
If this is a new domain, create `skills/SKILL_BIBLE_<topic>.md` with:
- Executive Summary
- Core Principles
- Techniques & Tactics
- Common Mistakes
- Quality Checklist

---

## Self-Annealing Protocol

After EVERY task completion:

### 1. Check for Errors
Did anything fail? Fix it:
```
Error occurred → Read stack trace → Fix script → Test → Update directive
```

### 2. Update Directive
Add learnings:
- New edge cases discovered
- Better approaches found
- Quality gate refinements

### 3. Update Skill Bible
Add domain knowledge:
- New techniques that worked
- Mistakes to avoid
- Industry-specific insights

### 4. Commit Changes
Keep the system improving:
```bash
git add directives/ execution/ skills/
git commit -m "Self-anneal: [what was learned]"
```

---

## Error Handling Patterns

### API Failures
```python
for attempt in range(3):
    try:
        result = api_call()
        break
    except Exception as e:
        if attempt == 2:
            raise
        time.sleep(10 * (attempt + 1))  # Exponential backoff
```

### Missing Inputs
Fail fast with clear message:
```python
if not args.required_field:
    print("Error: --required_field is required")
    sys.exit(1)
```

### Partial Failures
Degrade gracefully:
```
Critical workflow fails → Stop and report
Non-critical fails → Continue with warning
Delivery fails → Save locally, continue
```

---

## Environment Setup

### First-Time Setup
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Setup Google OAuth (for Docs integration)
# Place credentials.json in project root
python3 execution/create_google_doc.py --test

# 4. Setup Modal AI (for cloud deployment)
pip install modal
python3 -m modal setup

# 5. Create Modal secrets
python3 execution/deploy_to_modal.py --setup-secrets
```

### Required API Keys
| Key | Purpose | Get From |
|-----|---------|----------|
| `OPENROUTER_API_KEY` | LLM access | openrouter.ai |
| `PERPLEXITY_API_KEY` | Research | perplexity.ai |
| `SLACK_WEBHOOK_URL` | Notifications | Slack app settings |
| `GOOGLE_APPLICATION_CREDENTIALS` | Docs/Sheets | Google Cloud Console |

---

## Debugging Tips

### Check Script Arguments
```bash
python3 execution/<script>.py --help
```

### Test with Minimal Input
```bash
python3 execution/generate_vsl_funnel.py \
  --product "Test Product" \
  --price "$99" \
  --audience "Test audience"
```

### Check API Connectivity
```bash
# Test OpenRouter
curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY"

# Test Perplexity
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.1-sonar-small-128k-online","messages":[{"role":"user","content":"test"}]}'
```

### View Execution Logs
```bash
# Modal logs
modal logs <app-name>

# Local execution
python3 execution/<script>.py 2>&1 | tee output.log
```

---

## Summary: Your Role as Orchestrator

You are the **brain** of this system. Your responsibilities:

1. **Parse Intent** → Understand what the user wants
2. **Load Agency Context** → Read `context/` to understand who you're representing
3. **Load Client Context** → If client-specific, read `clients/{client}/` for their rules
4. **Find Capability** → Locate directive + script + skill bible
5. **Execute** → Run scripts, follow SOPs, check quality gates
6. **Deliver** → Save locally, upload to Google Docs, notify via Slack
7. **Self-Anneal** → Learn from every execution, update the system

**Core Principles:**
- **ALWAYS load agency context before generating content**
- **ALWAYS load client context when doing client-specific work**
- Check for existing tools before creating new ones
- Load skill bibles for domain expertise
- Push deterministic work into Python scripts
- Self-anneal when things break
- Update directives as you learn

**Context Loading Priority:**
```
1. context/agency.md      → Always load first
2. context/brand_voice.md → For any content creation
3. clients/{name}/*.md    → For client-specific work
4. skills/SKILL_BIBLE_*   → For domain expertise
5. directives/*.md        → For workflow SOPs
```

**The bottleneck isn't ideas or execution. It's deciding what to build next.**

---

## Quick Commands Reference

```bash
# List all workflows
python3 execution/deploy_to_modal.py --list

# Get workflow info
python3 execution/deploy_to_modal.py --info <directive_name>

# Deploy to cloud
python3 execution/deploy_to_modal.py --directive <directive_name>

# Run VSL funnel
python3 execution/generate_complete_vsl_funnel.py --company "X" --website "Y" --offer "Z"

# Research a company
python3 execution/research_company_offer.py --company "X" --website "Y"

# Create Google Doc from markdown
python3 execution/create_google_doc.py --file ".tmp/output.md" --title "Doc Title"

# Send Slack notification
python3 execution/send_slack_notification.py --message "Task complete" --channel "#general"
```
