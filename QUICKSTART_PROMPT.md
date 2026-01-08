# AIAA Agentic OS - Setup Guide

**Paste this entire prompt into Claude Code. Claude will clone the system and walk you through setup.**

---

## The Prompt (Copy Everything Below)

```
I want to set up AIAA Agentic OS. Please help me through the entire process.

## Step 1: Clone the Repository

Run this command to download the system:
git clone https://github.com/stopmoclay/AIAA-Agentic-OS.git

Then change into that directory so we can work from there.

## Step 2: Install Dependencies

Run the installer to set up Python packages:
python3 install.py

## Step 3: Walk Me Through Setup

Now I need you to be my setup wizard. Walk me through configuring everything by asking me questions one at a time. Here's what we need to set up:

### 3a. API Keys (.env file)

Create or update my .env file with API keys. Ask me for each one:

**Required:**
- OPENROUTER_API_KEY (required for all AI features)
  - Get it free at: https://openrouter.ai/keys
  - Takes 2 minutes to sign up

**Recommended (ask if I want each one):**
- PERPLEXITY_API_KEY - For deep research (https://perplexity.ai/settings/api)
- APIFY_API_TOKEN - For lead scraping (https://console.apify.com/account/integrations)
- SLACK_WEBHOOK_URL - For notifications (https://api.slack.com/messaging/webhooks)

For each key I don't have, give me simple step-by-step instructions to get it.

### 3b. Agency Profile (context/ folder)

Ask me questions to create my agency profile. Save the answers to context/agency_profile.json:

- What's your agency name?
- What's your website?
- What services do you offer? (list them)
- Who is your target audience?
- What makes you different from competitors?
- What's your brand voice? (professional, casual, bold, friendly, etc.)

Also create these markdown files in context/:
- agency.md - Summary of my agency
- brand_voice.md - My tone and style guidelines
- services.md - My service offerings

### 3c. First Client (optional)

Ask if I want to add a client. If yes, create a folder in clients/{client_name}/ with:

- profile.md - Their company info, industry, target audience
- rules.md - Content rules and guidelines for this client
- preferences.md - Their style preferences

Ask me:
- Client/company name?
- Their website?
- Their industry?
- What do they sell?
- Who is their target audience?
- Any specific content rules or tone preferences?

## Step 4: Test the System

Once setup is complete, help me run a simple test workflow to make sure everything works. Suggest something based on what I told you about my agency.

## Step 5: Show Me What's Available

Give me a quick tour of what workflows I can now run:
- Content creation (blogs, social posts, scripts)
- Sales copy (VSL funnels, emails, landing pages)
- Research (company research, market analysis)
- Lead generation (if I set up Apify)

## Important Notes

- Ask me ONE question at a time - don't overwhelm me
- If I don't know an answer, help me figure it out or skip it
- Save everything to the appropriate files as we go
- Be encouraging and explain why each step matters
- After setup, remind me I can always run "python3 run.py" for the interactive menu

Let's start! Begin with Step 1.
```

---

## What This Does

When you paste this prompt, Claude Code becomes your personal setup assistant:

1. **Downloads the system** - Clones the GitHub repo
2. **Installs dependencies** - Runs the Python installer
3. **Configures API keys** - Walks you through getting each key, one at a time
4. **Creates your agency profile** - Asks questions and saves your brand info
5. **Sets up your first client** - Optional client profile creation
6. **Tests the system** - Runs a workflow to verify everything works
7. **Shows you around** - Explains what you can do next

The whole process takes about 10-15 minutes, and Claude explains everything as you go.
