# AIAA Agentic OS - Interactive Setup Guide

**Version 2.3** | **139 Workflows** | **Complete Agency Operating System**

Paste this entire prompt into Claude Code to get a fully interactive setup experience. Claude will clone the system, configure your APIs, set up your agency profile, **deploy your dashboard to Railway automatically**, and walk you through everything step by step.

---

## The Prompt (Copy Everything Below)

```
I want to set up AIAA Agentic OS v2.3. Please help me through the entire process interactively, asking me ONE question at a time and waiting for my response before moving on.

## Step 1: Clone & Install

Run these commands to download and install the system:

git clone https://github.com/stopmoclay/AIAA-Agentic-OS.git
cd AIAA-Agentic-OS
pip install -r requirements.txt

Execute these commands and confirm they complete successfully before moving on.

## Step 2: Configure API Keys (.env file)

Create my .env file with API keys. Ask me for each one individually, and walk me through getting each key with detailed instructions:

---

### OPENROUTER_API_KEY (REQUIRED - Powers all AI features)

**What it does:** Routes requests to Claude, GPT-4, and other AI models. This is the only required key.

**How to get it:**
1. Go to https://openrouter.ai
2. Click "Sign Up" (top right) - use Google or email
3. Once logged in, click your profile icon → "Keys"
4. Click "Create Key"
5. Name it "AIAA" and click "Create"
6. Copy the key (starts with `sk-or-`)

**Cost:** Pay-as-you-go. Most workflows cost $0.01-0.10. Add $5-10 credits to start.

---

### PERPLEXITY_API_KEY (Recommended - Deep research & prospect intel)

**What it does:** Powers all research workflows - company research, market analysis, prospect intelligence, competitor monitoring.

**How to get it:**
1. Go to https://perplexity.ai
2. Sign up or log in
3. Click your profile icon (bottom left) → "Settings"
4. Click "API" in the left sidebar
5. Click "Generate" to create a new API key
6. Copy the key (starts with `pplx-`)

**Cost:** $5/month for 1000 requests, or pay-as-you-go at ~$0.005 per request.

---

### SLACK_WEBHOOK_URL (Recommended - Notifications & alerts)

**What it does:** Sends notifications when workflows complete, meetings are booked, leads are found, etc.

**How to get it:**
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "AIAA Notifications" and select your workspace
4. Click "Create App"
5. In the left sidebar, click "Incoming Webhooks"
6. Toggle "Activate Incoming Webhooks" to ON
7. Click "Add New Webhook to Workspace"
8. Select the channel for notifications (e.g., #aiaa-alerts)
9. Click "Allow"
10. Copy the Webhook URL (starts with `https://hooks.slack.com/services/`)

**Cost:** Free

---

### ANTHROPIC_API_KEY (Optional - Direct Claude access, faster)

**What it does:** Direct access to Claude without going through OpenRouter. Slightly faster responses.

**How to get it:**
1. Go to https://console.anthropic.com
2. Sign up with email
3. Verify your email and complete setup
4. Click "Get API Keys" in the dashboard
5. Click "Create Key"
6. Name it "AIAA" and copy the key (starts with `sk-ant-`)

**Cost:** Pay-as-you-go, similar pricing to OpenRouter.

---

### FAL_KEY (Optional - AI image generation)

**What it does:** Generates ad creatives, thumbnails, and marketing images using Nano Banana Pro model.

**How to get it:**
1. Go to https://fal.ai
2. Click "Sign Up" → use Google or GitHub
3. Once logged in, click your profile → "Dashboard"
4. Click "Keys" in the left sidebar
5. Click "Create Key"
6. Copy the key

**Cost:** Pay-as-you-go. ~$0.02-0.05 per image.

---

### APIFY_API_TOKEN (Optional - Lead scraping)

**What it does:** Scrapes Google Maps for local businesses, LinkedIn for prospects, and other lead generation tasks.

**How to get it:**
1. Go to https://console.apify.com
2. Sign up with email or Google
3. Once logged in, click "Settings" (gear icon, bottom left)
4. Click "Integrations" in the left sidebar
5. Your API token is displayed - click to copy

**Cost:** Free tier includes $5/month credits. Most scraping tasks cost $0.25-2.00.

---

For each key, ask me: "Do you have [KEY_NAME]? If yes, paste it. If no, I'll help you get it."

## Step 3: Google Drive, Docs & Sheets Setup (Recommended)

This enables automatic document creation, lead exports to Sheets, and file management. Walk me through the complete setup:

---

### Why This Matters

Google integration powers these workflows:
- **Auto-create Google Docs** from generated content (VSL scripts, sales pages, emails)
- **Export leads to Sheets** from scraping workflows
- **Meeting prep documents** created automatically from Calendly webhooks
- **Client deliverables** formatted and shared via Google Drive

---

### Step 3a: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click the project dropdown (top left, next to "Google Cloud")
3. Click "NEW PROJECT" (top right of popup)
4. Name it "AIAA Agentic OS" 
5. Click "CREATE"
6. Wait for project creation (takes 10-30 seconds)
7. Make sure the new project is selected in the dropdown

---

### Step 3b: Enable Required APIs

1. In the left sidebar, click "APIs & Services" → "Library"
2. Search for and enable EACH of these APIs (click each one, then click "ENABLE"):

**Required APIs:**
- **Google Docs API** - For creating/editing documents
- **Google Sheets API** - For spreadsheet exports
- **Google Drive API** - For file management and sharing

For each API:
1. Search the name in the API Library
2. Click on the API
3. Click the blue "ENABLE" button
4. Wait for it to enable, then go back and enable the next one

---

### Step 3c: Create OAuth 2.0 Credentials

1. In the left sidebar, click "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" (top of page)
3. Select "OAuth client ID"

**If you see "Configure Consent Screen" warning:**
1. Click "CONFIGURE CONSENT SCREEN"
2. Select "External" (unless you have Google Workspace, then "Internal")
3. Click "CREATE"
4. Fill in required fields:
   - App name: "AIAA Agentic OS"
   - User support email: Your email
   - Developer contact: Your email
5. Click "SAVE AND CONTINUE"
6. On Scopes page, click "SAVE AND CONTINUE" (no changes needed)
7. On Test Users page, click "ADD USERS"
8. Add your Gmail address
9. Click "SAVE AND CONTINUE"
10. Click "BACK TO DASHBOARD"
11. Go back to Credentials and create OAuth client ID again

**Create the OAuth Client:**
1. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
2. Application type: Select "Desktop app"
3. Name: "AIAA Desktop Client"
4. Click "CREATE"

---

### Step 3d: Download and Place Credentials

1. After creating, you'll see a popup with your Client ID
2. Click "DOWNLOAD JSON" button
3. Rename the downloaded file to exactly: `credentials.json`
4. Move it to your AIAA project root folder:
   ```
   AIAA-Agentic-OS/
   ├── credentials.json    ← Place it here
   ├── directives/
   ├── execution/
   └── ...
   ```

---

### Step 3e: Test the Integration

Run this command to test Google authentication:
```bash
python3 execution/create_google_doc.py --test
```

**What happens:**
1. A browser window opens asking you to sign in to Google
2. Select your Google account
3. You may see "Google hasn't verified this app" - click "Continue" (it's your own app)
4. Grant permissions for Docs, Sheets, and Drive
5. You'll see "The authentication flow has completed"
6. A `token.pickle` file is created (saves your auth for future use)

**Success looks like:**
```
Authentication successful!
Token saved to token.pickle
Test document created: https://docs.google.com/document/d/...
```

---

### Troubleshooting Google Setup

**"credentials.json not found"**
- Make sure the file is named exactly `credentials.json` (not `credentials (1).json`)
- Make sure it's in the project root, not a subfolder

**"Access blocked" or "App not verified"**
- Click "Advanced" → "Go to AIAA Agentic OS (unsafe)"
- This is safe - it's your own app

**"Token has been expired or revoked"**
- Delete `token.pickle` and `token_docs.json` files
- Run the test command again to re-authenticate

**"API not enabled"**
- Go back to Google Cloud Console → APIs & Services → Library
- Make sure all 3 APIs are enabled (Docs, Sheets, Drive)

---

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

## Step 6: Deploy AIAA Dashboard to Railway (IMPORTANT - AUTOMATE THIS)

This is the key step. Deploy my monitoring dashboard to Railway. Handle as much as possible automatically.

### Step 6a: Check Prerequisites
First, check if Railway CLI is installed:
```bash
railway --version
```

If not installed, tell me to run:
```bash
npm install -g @railway/cli
```

Then check if I'm logged in:
```bash
railway whoami
```

If not logged in, tell me to run `railway login` and complete the browser authentication.

### Step 6b: Ask for Dashboard Credentials
Ask me TWO questions:
1. "What username do you want for your dashboard? (default: admin)"
2. "What password do you want for your dashboard?"

Then YOU (Claude) generate the password hash automatically using a heredoc to avoid escape sequence issues with special characters:
```bash
python3 << 'PYHASH'
import hashlib
password = "THE_PASSWORD_I_GAVE_YOU"
print(hashlib.sha256(password.encode()).hexdigest())
PYHASH
```

IMPORTANT: Use this heredoc method instead of `python3 -c` to avoid escape sequence issues with special characters like `!`, `\`, etc. in passwords.

Save the hash - you'll need it for environment variables.

### Step 6c: Create Railway Project and Deploy
Navigate to the dashboard folder and deploy:

```bash
cd railway_apps/aiaa_dashboard
railway init
```

When prompted, select "Empty Project" and give it a name like "aiaa-dashboard".

Then deploy:
```bash
railway up
```

Wait for the deployment to complete. This uploads the dashboard code to Railway.

### Step 6d: Set Environment Variables
After deployment, set the environment variables using Railway CLI:

```bash
railway variables set DASHBOARD_USERNAME="[USERNAME_I_CHOSE]"
railway variables set DASHBOARD_PASSWORD_HASH="[THE_HASH_YOU_GENERATED]"
railway variables set FLASK_SECRET_KEY="[GENERATE_A_RANDOM_32_CHAR_STRING]"
```

Generate the FLASK_SECRET_KEY with:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

If I provided API keys in Step 2, also set them:
```bash
railway variables set OPENROUTER_API_KEY="[MY_KEY]"
railway variables set PERPLEXITY_API_KEY="[MY_KEY]"
railway variables set SLACK_WEBHOOK_URL="[MY_WEBHOOK]"
```

### Step 6e: Generate Public Domain
Generate a public URL for the dashboard:

```bash
railway domain
```

This creates a URL like: https://aiaa-dashboard-production.up.railway.app

### Step 6f: Verify Deployment
Test that the dashboard is running:

```bash
curl -s "https://[GENERATED_DOMAIN]/health"
```

Should return: {"status": "ok", "version": "2.3.0", "workflows": 139}

### Step 6g: Provide Login Details
Once everything is deployed, give me:
- Dashboard URL
- Username
- Password (the one I chose)
- Remind me to bookmark it!

Tell me: "Your AIAA Dashboard is now live! You can monitor all 139 workflows, manage environment variables, and track webhook events."

## Step 7: Test the System

Run a simple test based on my agency type:
- If marketing agency: Generate a cold email sequence
- If content agency: Create a blog post or social content
- If design agency: Generate an ad creative concept
- General: Run company research on a sample company

Verify output and show me the result.

## Step 8: Show What's Available

Give me a quick tour of the 139 workflows:

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

## Important Instructions for Claude

- Ask me ONE question at a time
- Wait for my response before continuing
- If I don't know something, help me or skip it
- Save files as we complete each section
- Be encouraging and explain why each step matters
- If errors occur, help me debug them
- For the Railway deployment, DO AS MUCH AUTOMATICALLY AS POSSIBLE
- Generate hashes, secrets, and run commands for me
- Only ask me for input when you absolutely need it (username, password, API keys)

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
6. **Deploys dashboard to Railway** - **Fully automated deployment**
   - Creates Railway project
   - Deploys dashboard code
   - Sets all environment variables
   - Generates public domain
   - Verifies deployment
   - Provides login credentials
7. **Tests the system** - Verifies everything works
8. **Shows capabilities** - Tour of all 139 workflows

**Time to complete:** 15-30 minutes depending on options chosen

---

## Dashboard Features (v2.3)

Once deployed, your dashboard includes:

| Feature | Description |
|---------|-------------|
| **139 Workflows** | Full documentation with prerequisites, how-to-run, and process steps |
| **Light/Dark Mode** | Toggle with localStorage persistence |
| **Environment Variables** | View and set API keys from the UI |
| **Webhook Monitoring** | Track incoming webhooks and events |
| **Real-time Logs** | See all workflow executions |
| **Mobile Responsive** | Works on phones and tablets |
| **Password Protected** | Secure SHA-256 hashed login |

---

## Manual Dashboard Deployment (Alternative)

If you prefer to deploy manually instead of using the interactive prompt:

### Prerequisites
```bash
npm install -g @railway/cli
railway login
```

### Deploy
```bash
cd railway_apps/aiaa_dashboard
railway init
railway up
```

### Configure
```bash
# Generate password hash (use heredoc to avoid escape sequence issues)
python3 << 'PYHASH'
import hashlib
password = "your-password"
print(hashlib.sha256(password.encode()).hexdigest())
PYHASH

# Set variables
railway variables set DASHBOARD_USERNAME="admin"
railway variables set DASHBOARD_PASSWORD_HASH="your-hash-here"
railway variables set FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

# Generate domain
railway domain
```

### Verify
```bash
curl https://your-domain.up.railway.app/health
```

---

## Troubleshooting

### "railway: command not found"
```bash
npm install -g @railway/cli
```

### "Not logged in"
```bash
railway login
```
Complete browser authentication.

### "No project linked"
```bash
railway init
```
Select "Empty Project" when prompted.

### Dashboard shows "Invalid credentials"
Regenerate password hash using heredoc (avoids escape sequence issues with special characters):
```bash
python3 << 'PYHASH'
import hashlib
password = "your-password"
print(hashlib.sha256(password.encode()).hexdigest())
PYHASH

railway variables set DASHBOARD_PASSWORD_HASH="new-hash"
```

### Health check fails
Wait 1-2 minutes for deployment to complete, then retry:
```bash
railway logs
```

---

## Support

- **GitHub Issues:** https://github.com/stopmoclay/AIAA-Agentic-OS/issues
- **Documentation:** See `CLAUDE.md` for full system documentation
- **Workflows:** Browse all 139 in your deployed dashboard
