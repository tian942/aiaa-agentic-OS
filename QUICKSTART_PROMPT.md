# AIAA Agentic OS - Single Prompt Setup Guide

Copy and paste this entire prompt into Claude Code to set up and learn the system.

---

## THE PROMPT

```
I just cloned the AIAA Agentic OS repository. Help me set it up and learn how to use it.

## What This System Is

AIAA Agentic OS is an AI-powered agency operating system that automates marketing workflows. It has:
- 118 workflow directives (SOPs)
- 126 Python execution scripts
- 264 skill bibles (domain expertise)
- Agency context system for brand voice
- Client profile system for per-client rules

## Architecture

The system uses a DOE (Directive-Orchestration-Execution) pattern:
1. DIRECTIVES (directives/*.md) - Natural language SOPs that define WHAT to do
2. ORCHESTRATION (You, Claude Code) - Decision making, routing, error handling
3. EXECUTION (execution/*.py) - Deterministic Python scripts that DO the work

## Setup Steps

### Step 1: Install Dependencies
Run the installer which checks Python version, installs packages, and creates directories:
```bash
python3 install.py
```

### Step 2: Run the Setup Wizard
The interactive wizard walks through API key configuration and agency profile setup:
```bash
python3 wizard.py
```

The wizard will:
1. Configure API Keys (OpenRouter required, plus optional Perplexity, Apify, Slack, etc.)
2. Create your Agency Profile (name, services, target market, brand voice)
3. Add Client Profiles (per-client context with rules and preferences)
4. Teach you the system with an interactive tutorial
5. Run your first workflow

### Step 3: Use the System
After setup, use the main interface:
```bash
python3 run.py
```

This gives you an interactive menu with:
- Content Creation (LinkedIn posts, blogs, YouTube scripts, newsletters)
- Sales Copy (VSL scripts, sales pages, email sequences, cold emails)
- Research (company research, competitor analysis, market research)
- Lead Generation (Google Maps scraping, LinkedIn scraping, email validation)
- Client Work (monthly reports, case studies, content calendars)

## Key Workflows I Can Run

### VSL Funnel (Complete)
```bash
python3 execution/generate_complete_vsl_funnel.py \
  --company "Client Name" \
  --website "https://example.com" \
  --offer "Their Main Offer"
```
Creates: Market research + VSL script (2500+ words) + Sales page + Email sequence

### Company Research
```bash
python3 execution/research_company_offer.py \
  --company "Company Name" \
  --website "https://company.com"
```

### Cold Emails
```bash
python3 execution/write_cold_emails.py \
  --sender "Your Name" \
  --company "Your Agency" \
  --offer "Your Service" \
  --target "Target Audience"
```

### Blog Post
```bash
python3 execution/generate_blog_post.py \
  --topic "Your Topic" \
  --length 1500
```

### LinkedIn Post
```bash
python3 execution/generate_linkedin_post.py \
  --topic "Your Topic" \
  --style "story"
```

## Required API Keys

At minimum, you need:
- OPENROUTER_API_KEY (required) - Powers all AI generation. Get free at https://openrouter.ai/keys

Recommended:
- PERPLEXITY_API_KEY - For deep research (https://perplexity.ai)
- SLACK_WEBHOOK_URL - For notifications
- APIFY_API_TOKEN - For lead scraping (https://apify.com)

## Key Files to Know

- CLAUDE.md - Complete agent instructions (read this for full capabilities)
- context/agency.md - Your agency's brand voice and positioning
- context/services.md - Your service offerings
- clients/{name}/ - Per-client profiles with rules and preferences
- skills/SKILL_BIBLE_*.md - Domain expertise files (264 total)
- directives/*.md - Workflow SOPs (118 total)
- execution/*.py - Python scripts (126 total)

## Please Help Me:

1. First, run `python3 install.py` to set up dependencies
2. Then run `python3 wizard.py` to configure my API keys and agency profile
3. Show me how to run my first workflow
4. Explain the DOE architecture as we go
5. Point out key files I should read to understand the system

I want to fully understand how this system works so I can use it daily for my agency.
```

---

## What Happens When You Paste This

Claude Code will:

1. **Run the installer** - Checks Python 3.10+, installs packages from requirements.txt, creates directories

2. **Launch the wizard** which walks you through:
   - OpenRouter API key setup (required - takes 2 minutes)
   - Optional API keys (Perplexity, Apify, HubSpot, Slack, etc.)
   - Your agency profile (name, services, target market, brand voice)
   - Client profiles (can add multiple clients with rules/preferences)
   - Interactive tutorial showing you the system
   - Your first workflow execution

3. **Explain the architecture** as it goes:
   - DOE pattern (Directive-Orchestration-Execution)
   - How directives define workflows
   - How skill bibles provide domain expertise
   - How execution scripts do the actual work

4. **Run your first workflow** - Typically a VSL funnel, research report, or content piece

## After Setup

Use these commands daily:

```bash
# Interactive menu
python3 run.py

# Direct workflow execution
python3 execution/generate_complete_vsl_funnel.py --company "X" --website "Y" --offer "Z"
python3 execution/research_company_offer.py --company "X" --website "Y"
python3 execution/write_cold_emails.py --sender "Name" --product "Service"

# List all available workflows
python3 run.py --list
```

## System Stats

| Resource | Count | Location |
|----------|-------|----------|
| Directives | 118 | `directives/` |
| Execution Scripts | 126 | `execution/` |
| Skill Bibles | 264 | `skills/` |
| Agency Context Files | 4 | `context/` |

## Tips

1. **Always load context first** - Before generating content, ensure CLAUDE.md is loaded
2. **Check for existing tools** - Run `ls directives/ | grep keyword` before creating new workflows
3. **Use skill bibles** - They contain domain expertise that improves output quality
4. **Self-anneal** - When things break, fix and update the system for next time
