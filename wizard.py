#!/usr/bin/env python3
"""
AIAA Agentic OS - Setup Wizard
Interactive onboarding that teaches you everything.

Usage:
    python3 wizard.py
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

BASE_DIR = Path(__file__).parent
CONTEXT_DIR = BASE_DIR / "context"
CLIENTS_DIR = BASE_DIR / "clients"
ENV_FILE = BASE_DIR / ".env"

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header(title, subtitle=""):
    clear_screen()
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║{Colors.END}                                                              {Colors.CYAN}║
║           {Colors.BOLD}{Colors.END}{title.center(44)}{Colors.CYAN}             ║
║{Colors.END}                                                              {Colors.CYAN}║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
""")
    if subtitle:
        print(f"  {Colors.DIM}{subtitle}{Colors.END}\n")

def print_step_indicator(current, total, steps):
    """Print progress bar showing all steps."""
    print(f"{Colors.DIM}─" * 62 + f"{Colors.END}")
    step_width = 62 // total
    
    for i, step in enumerate(steps):
        if i < current:
            marker = f"{Colors.GREEN}●{Colors.END}"
        elif i == current:
            marker = f"{Colors.CYAN}◉{Colors.END}"
        else:
            marker = f"{Colors.DIM}○{Colors.END}"
        
        if i == current:
            print(f"  {marker} {Colors.BOLD}{step}{Colors.END}")
        else:
            print(f"  {marker} {Colors.DIM}{step}{Colors.END}")
    
    print(f"{Colors.DIM}─" * 62 + f"{Colors.END}\n")

def prompt(question, default=None, required=True):
    """Get user input with optional default."""
    if default:
        prompt_text = f"  {Colors.CYAN}→{Colors.END} {question} {Colors.DIM}[{default}]{Colors.END}: "
    else:
        prompt_text = f"  {Colors.CYAN}→{Colors.END} {question}: "
    
    while True:
        response = input(prompt_text).strip()
        
        if not response and default:
            return default
        elif not response and required:
            print(f"    {Colors.RED}This field is required{Colors.END}")
            continue
        elif not response and not required:
            return ""
        else:
            return response

def prompt_choice(question, options, allow_skip=False):
    """Present numbered choices to user."""
    print(f"  {Colors.CYAN}→{Colors.END} {question}\n")
    
    for i, option in enumerate(options, 1):
        print(f"    {Colors.BOLD}{i}.{Colors.END} {option}")
    
    if allow_skip:
        print(f"    {Colors.DIM}0. Skip{Colors.END}")
    
    print()
    
    while True:
        try:
            choice = input(f"    Enter number: ").strip()
            if allow_skip and choice == "0":
                return None
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice - 1
            print(f"    {Colors.RED}Please enter a number 1-{len(options)}{Colors.END}")
        except ValueError:
            print(f"    {Colors.RED}Please enter a number{Colors.END}")

def prompt_yes_no(question, default=True):
    """Yes/no prompt."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"  {Colors.CYAN}→{Colors.END} {question} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    return response in ('y', 'yes')

def wait_for_enter(message="Press Enter to continue..."):
    input(f"\n  {Colors.DIM}{message}{Colors.END}")

def typing_effect(text, delay=0.02):
    """Print text with typing effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def save_to_env(key, value):
    """Save or update a key in .env file."""
    env_path = ENV_FILE
    
    if env_path.exists():
        content = env_path.read_text()
        lines = content.split('\n')
        
        # Update existing key or add new one
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                found = True
                break
        
        if not found:
            lines.append(f"{key}={value}")
        
        env_path.write_text('\n'.join(lines))
    else:
        env_path.write_text(f"{key}={value}\n")

def load_env():
    """Load environment variables from .env."""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().split('\n'):
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()


# ═══════════════════════════════════════════════════════════════
# STEP 1: API KEYS
# ═══════════════════════════════════════════════════════════════

# Complete API key registry with detailed hand-holding instructions
API_KEY_REGISTRY = {
    # === CORE (Required) ===
    "OPENROUTER_API_KEY": {
        "name": "OpenRouter",
        "category": "core",
        "required": True,
        "description": "Powers ALL AI generation in the system (Claude, GPT-4, Llama, etc.)",
        "url": "https://openrouter.ai/keys",
        "prefix": "sk-or-",
        "workflows": "All content generation, VSL scripts, email writing, research, etc.",
        "pricing": "Free tier available, then ~$0.001-0.03 per request depending on model",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://openrouter.ai{end}
  
  2. Click {bold}"Sign Up"{end} in the top right corner
     - Use "Continue with Google" for fastest setup
     - Or create account with email
  
  3. Once logged in, click your profile icon (top right)
     Then click {bold}"Keys"{end}
     Or go directly to: {cyan}https://openrouter.ai/keys{end}
  
  4. Click the {bold}"Create Key"{end} button
  
  5. Give your key a name (e.g., "AIAA Agentic OS")
  
  6. {bold}Copy the key{end} - it starts with "sk-or-"
     {yellow}Important: You can only see this once!{end}
  
  7. Paste it below when prompted
  
  {dim}Tip: Add $5-10 credits to start. Most requests cost $0.001-0.01{end}
"""
    },
    
    # === RESEARCH ===
    "PERPLEXITY_API_KEY": {
        "name": "Perplexity",
        "category": "research",
        "required": False,
        "description": "AI-powered research with real-time web access",
        "url": "https://www.perplexity.ai/settings/api",
        "prefix": "pplx-",
        "workflows": "Company research, market analysis, prospect research, competitive intel",
        "pricing": "Free tier: Limited requests. Pro: ~$0.005 per request",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://www.perplexity.ai{end}
  
  2. Click {bold}"Sign Up"{end} or {bold}"Log In"{end} (top right)
     - Google sign-in is fastest
     - Or use email
  
  3. Once logged in, click your profile icon (bottom left)
     Then click {bold}"Settings"{end}
  
  4. In the left sidebar, click {bold}"API"{end}
     Or go directly to: {cyan}https://www.perplexity.ai/settings/api{end}
  
  5. Click {bold}"Generate API Key"{end}
  
  6. {bold}Copy the key{end} - it starts with "pplx-"
  
  7. Paste it below when prompted
  
  {dim}Note: You may need to add a payment method for API access{end}
  {dim}The API is separate from Perplexity Pro subscription{end}
"""
    },
    
    # === LEAD GENERATION ===
    "APIFY_API_TOKEN": {
        "name": "Apify",
        "category": "leadgen",
        "required": False,
        "description": "Web scraping platform for Google Maps, LinkedIn, websites",
        "url": "https://console.apify.com/account/integrations",
        "prefix": None,
        "workflows": "Google Maps leads, LinkedIn scraping, website contact extraction",
        "pricing": "Free tier: $5/month credits. Paid plans from $49/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://apify.com{end}
  
  2. Click {bold}"Start for free"{end} or {bold}"Sign up"{end}
     - Google/GitHub sign-in available
     - Or use email
  
  3. Once logged in, click your profile icon (top right)
     Then click {bold}"Settings"{end}
  
  4. In the left sidebar, click {bold}"Integrations"{end}
     Or go directly to: {cyan}https://console.apify.com/account/integrations{end}
  
  5. You'll see {bold}"Personal API Tokens"{end} section
     Your default token is already created
  
  6. Click the {bold}copy icon{end} next to your API token
  
  7. Paste it below when prompted
  
  {dim}Free tier includes $5/month in credits - enough for ~500 Google Maps scrapes{end}
"""
    },
    "HUNTER_API_KEY": {
        "name": "Hunter.io",
        "category": "leadgen",
        "required": False,
        "description": "Find and verify professional email addresses",
        "url": "https://hunter.io/api_keys",
        "prefix": None,
        "workflows": "Email finding, lead enrichment, email verification",
        "pricing": "Free: 25 searches/month. Starter: $49/month for 500 searches",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://hunter.io{end}
  
  2. Click {bold}"Sign up"{end} (top right)
     - Google sign-in available
     - Or use email
  
  3. Once logged in, click your profile icon (top right)
     Then click {bold}"API"{end}
     Or go directly to: {cyan}https://hunter.io/api_keys{end}
  
  4. You'll see your {bold}"API key"{end} displayed
  
  5. Click {bold}"Copy"{end} to copy your API key
  
  6. Paste it below when prompted
  
  {dim}Free tier: 25 searches & 50 verifications per month{end}
  {dim}Great for validating leads before cold outreach{end}
"""
    },
    "APOLLO_API_KEY": {
        "name": "Apollo.io",
        "category": "leadgen",
        "required": False,
        "description": "B2B lead database with 270M+ contacts",
        "url": "https://app.apollo.io/#/settings/integrations/api",
        "prefix": None,
        "workflows": "Lead list building, contact enrichment, company data",
        "pricing": "Free: 10,000 credits/month. Basic: $49/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://apollo.io{end}
  
  2. Click {bold}"Sign Up Free"{end}
     - Google/Microsoft sign-in available
     - Or use work email (recommended)
  
  3. Complete the onboarding questions
  
  4. Once in the dashboard, click {bold}"Settings"{end} (gear icon, bottom left)
  
  5. Click {bold}"Integrations"{end} in the left sidebar
  
  6. Click {bold}"API Keys"{end} tab
     Or go directly to: {cyan}https://app.apollo.io/#/settings/integrations/api{end}
  
  7. Click {bold}"Create New Key"{end}
  
  8. Name it (e.g., "AIAA") and click {bold}"Create"{end}
  
  9. {bold}Copy the key{end} immediately
     {yellow}You won't be able to see it again!{end}
  
  {dim}Free tier is generous - 10,000 credits/month for lead lookup{end}
"""
    },
    
    # === CRM & EMAIL ===
    "HUBSPOT_API_KEY": {
        "name": "HubSpot",
        "category": "crm",
        "required": False,
        "description": "CRM integration for contacts, deals, and automation",
        "url": "https://app.hubspot.com/settings/integrations/private-apps",
        "prefix": "pat-",
        "workflows": "CRM sync, deal tracking, contact management, churn alerts",
        "pricing": "Free CRM available. API access included in all plans",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://app.hubspot.com{end}
  
  2. Log in to your HubSpot account
     (Create free account if you don't have one)
  
  3. Click the {bold}Settings gear icon{end} (top right)
  
  4. In the left sidebar, scroll down to {bold}"Integrations"{end}
     Then click {bold}"Private Apps"{end}
  
  5. Click {bold}"Create a private app"{end}
  
  6. Fill in the details:
     - Name: "AIAA Agentic OS"
     - Description: "AI agency automation"
  
  7. Click {bold}"Scopes"{end} tab and enable:
     - crm.objects.contacts (read/write)
     - crm.objects.deals (read/write)
     - crm.objects.companies (read/write)
  
  8. Click {bold}"Create app"{end} then {bold}"Continue creating"{end}
  
  9. {bold}Copy the access token{end} shown
     It starts with "pat-"
  
  {dim}The token gives access only to scopes you selected{end}
"""
    },
    "INSTANTLY_API_KEY": {
        "name": "Instantly",
        "category": "email",
        "required": False,
        "description": "Cold email platform with unlimited sending accounts",
        "url": "https://app.instantly.ai/settings/integrations/api",
        "prefix": None,
        "workflows": "Cold email campaigns, inbox management, email warmup",
        "pricing": "Growth: $37/month. Hypergrowth: $97/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://instantly.ai{end}
  
  2. Click {bold}"Login"{end} or {bold}"Start Free Trial"{end}
  
  3. Once logged in, click {bold}"Settings"{end} (gear icon, bottom left)
  
  4. Click {bold}"Integrations"{end} in the sidebar
  
  5. Click {bold}"API"{end} tab
     Or go directly to: {cyan}https://app.instantly.ai/settings/integrations/api{end}
  
  6. Click {bold}"Generate New API Key"{end}
  
  7. {bold}Copy the API key{end}
  
  8. Paste it below when prompted
  
  {dim}Note: You need an active Instantly subscription for API access{end}
"""
    },
    "SMARTLEAD_API_KEY": {
        "name": "SmartLead",
        "category": "email",
        "required": False,
        "description": "Cold email automation with AI personalization",
        "url": "https://app.smartlead.ai/settings/general",
        "prefix": None,
        "workflows": "Cold email campaigns, multi-inbox sending, AI warmup",
        "pricing": "Basic: $39/month. Pro: $94/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://smartlead.ai{end}
  
  2. Click {bold}"Login"{end} or {bold}"Start Free Trial"{end}
  
  3. Once logged in, click your {bold}profile icon{end} (top right)
  
  4. Click {bold}"Settings"{end}
  
  5. Scroll down to find {bold}"API Key"{end} section
  
  6. Click {bold}"Generate API Key"{end} if not already created
  
  7. {bold}Copy the API key{end}
  
  8. Paste it below when prompted
  
  {dim}Note: You need an active SmartLead subscription for API access{end}
"""
    },
    "SENDGRID_API_KEY": {
        "name": "SendGrid",
        "category": "email",
        "required": False,
        "description": "Transactional email delivery service",
        "url": "https://app.sendgrid.com/settings/api_keys",
        "prefix": "SG.",
        "workflows": "Email notifications, transactional emails, delivery reports",
        "pricing": "Free: 100 emails/day. Essentials: $19.95/month for 50K",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://sendgrid.com{end}
  
  2. Click {bold}"Start for Free"{end} or {bold}"Login"{end}
  
  3. Complete account setup (email verification required)
  
  4. Once in dashboard, click {bold}"Settings"{end} (left sidebar)
  
  5. Click {bold}"API Keys"{end}
     Or go to: {cyan}https://app.sendgrid.com/settings/api_keys{end}
  
  6. Click {bold}"Create API Key"{end}
  
  7. Give it a name: "AIAA Agentic OS"
  
  8. Select {bold}"Full Access"{end} or customize permissions
  
  9. Click {bold}"Create & View"{end}
  
  10. {bold}Copy the key{end} - it starts with "SG."
      {yellow}You can only see this once!{end}
  
  {dim}Free tier: 100 emails/day forever{end}
"""
    },
    "CONVERTKIT_API_KEY": {
        "name": "ConvertKit",
        "category": "email",
        "required": False,
        "description": "Email marketing for creators and newsletters",
        "url": "https://app.convertkit.com/account_settings/advanced_settings",
        "prefix": None,
        "workflows": "Newsletter sending, subscriber management, email sequences",
        "pricing": "Free: Up to 10,000 subscribers. Creator: $25/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://convertkit.com{end}
  
  2. Click {bold}"Sign up free"{end} or {bold}"Log in"{end}
  
  3. Once logged in, click your {bold}profile icon{end} (top right)
  
  4. Click {bold}"Settings"{end}
  
  5. Click {bold}"Advanced"{end} in the sidebar
     Or go to: {cyan}https://app.convertkit.com/account_settings/advanced_settings{end}
  
  6. Scroll to {bold}"API"{end} section
  
  7. You'll see your {bold}API Key{end} displayed
     Click to reveal and copy it
  
  8. Also note your {bold}API Secret{end} (may be needed)
  
  {dim}Great for newsletter automation and subscriber management{end}
"""
    },
    
    # === GOOGLE SERVICES ===
    "GOOGLE_APPLICATION_CREDENTIALS": {
        "name": "Google Service Account",
        "category": "google",
        "required": False,
        "description": "Google Docs, Sheets, Drive, and Gmail integration",
        "url": "https://console.cloud.google.com",
        "prefix": None,
        "workflows": "Google Docs creation, Sheets export, Drive storage, Gmail sending",
        "pricing": "Free for most use cases (generous quotas)",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  {yellow}This is more complex - takes about 5-10 minutes{end}
  
  1. Open your browser and go to:
     {cyan}https://console.cloud.google.com{end}
  
  2. Sign in with your Google account
  
  3. Click {bold}"Select a project"{end} (top bar) → {bold}"New Project"{end}
     - Name: "AIAA Agentic OS"
     - Click "Create"
  
  4. Wait for project creation, then select it
  
  5. {bold}Enable APIs:{end}
     - Go to "APIs & Services" → "Library"
     - Search and enable:
       • Google Docs API
       • Google Sheets API
       • Google Drive API
       • Gmail API (if needed)
  
  6. {bold}Create Service Account:{end}
     - Go to "IAM & Admin" → "Service Accounts"
     - Click "Create Service Account"
     - Name: "aiaa-service"
     - Click "Create and Continue"
     - Role: "Editor" (or "Owner" for full access)
     - Click "Done"
  
  7. {bold}Create Key:{end}
     - Click on the service account you just created
     - Go to "Keys" tab
     - Click "Add Key" → "Create new key"
     - Select "JSON"
     - Click "Create"
     - {bold}A JSON file will download{end}
  
  8. {bold}Move the JSON file{end} to this project folder:
     - Rename it to: aiaa-google-credentials.json
     - Move it to: {dim}[this folder]{end}
  
  9. For the prompt below, enter the {bold}file path{end}:
     Example: ./aiaa-google-credentials.json
  
  {dim}The JSON file contains your credentials - keep it secure!{end}
"""
    },
    
    # === SOCIAL MEDIA ===
    "TWITTER_API_KEY": {
        "name": "Twitter/X",
        "category": "social",
        "required": False,
        "description": "Twitter/X posting and analytics",
        "url": "https://developer.twitter.com/en/portal/dashboard",
        "prefix": None,
        "workflows": "Twitter thread posting, scheduled tweets, analytics",
        "pricing": "Free: Basic access. Basic: $100/month for more features",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  {yellow}Twitter API access requires developer account approval{end}
  
  1. Open your browser and go to:
     {cyan}https://developer.twitter.com{end}
  
  2. Click {bold}"Sign up"{end} (use your Twitter account)
  
  3. Apply for {bold}"Free"{end} access tier
     - Answer the use case questions
     - Describe your app usage
  
  4. Wait for approval (usually instant for Free tier)
  
  5. Once approved, go to {bold}"Dashboard"{end}
  
  6. Click {bold}"+ Create Project"{end}
     - Name: "AIAA Agentic OS"
     - Use case: "Making a bot"
  
  7. Create an {bold}"App"{end} within the project
  
  8. Go to {bold}"Keys and tokens"{end} tab
  
  9. Generate {bold}"API Key and Secret"{end}
     {yellow}Save both immediately!{end}
  
  10. Generate {bold}"Access Token and Secret"{end}
      {yellow}Save these too!{end}
  
  {dim}Note: You need all 4 values for full API access{end}
  {dim}Enter them as: API_KEY:API_SECRET:ACCESS_TOKEN:ACCESS_SECRET{end}
"""
    },
    "BUFFER_API_KEY": {
        "name": "Buffer",
        "category": "social",
        "required": False,
        "description": "Social media scheduling across platforms",
        "url": "https://buffer.com/developers/api",
        "prefix": None,
        "workflows": "Social media scheduling, cross-platform posting",
        "pricing": "Free: 3 channels. Essentials: $6/month per channel",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://buffer.com{end}
  
  2. Click {bold}"Get started now"{end} or {bold}"Log in"{end}
  
  3. Connect your social media accounts
  
  4. Go to: {cyan}https://buffer.com/developers/apps{end}
  
  5. Click {bold}"Create App"{end}
     - Name: "AIAA Agentic OS"
     - Description: "AI agency automation"
     - Website: Your website or placeholder
  
  6. Click {bold}"Create Application"{end}
  
  7. Copy your {bold}"Access Token"{end}
  
  8. Paste it below when prompted
  
  {dim}Buffer allows scheduling to LinkedIn, Twitter, Facebook, etc.{end}
"""
    },
    
    # === AI SERVICES ===
    "OPENAI_API_KEY": {
        "name": "OpenAI Direct",
        "category": "ai",
        "required": False,
        "description": "Direct OpenAI access for GPT-4, DALL-E, Whisper",
        "url": "https://platform.openai.com/api-keys",
        "prefix": "sk-",
        "workflows": "Image generation (DALL-E), embeddings, GPT-4 direct",
        "pricing": "Pay-as-you-go. GPT-4: ~$0.03/1K tokens. DALL-E: $0.04/image",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  {dim}Note: OpenRouter already provides access to OpenAI models.{end}
  {dim}This is only needed for DALL-E images or direct API access.{end}
  
  1. Open your browser and go to:
     {cyan}https://platform.openai.com{end}
  
  2. Click {bold}"Sign up"{end} or {bold}"Log in"{end}
  
  3. Click your profile icon (top right)
     Then click {bold}"View API keys"{end}
     Or go to: {cyan}https://platform.openai.com/api-keys{end}
  
  4. Click {bold}"Create new secret key"{end}
  
  5. Name it: "AIAA Agentic OS"
  
  6. {bold}Copy the key{end} - it starts with "sk-"
     {yellow}You can only see this once!{end}
  
  7. Add payment method in Billing section
  
  {dim}Start with $10 credit to test{end}
"""
    },
    "ANTHROPIC_API_KEY": {
        "name": "Anthropic Direct",
        "category": "ai",
        "required": False,
        "description": "Direct Claude access (Claude 3.5 Sonnet, Opus, Haiku)",
        "url": "https://console.anthropic.com/settings/keys",
        "prefix": "sk-ant-",
        "workflows": "Claude direct access (optional - OpenRouter covers this)",
        "pricing": "Pay-as-you-go. Claude 3.5 Sonnet: ~$3/M input, $15/M output",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  {dim}Note: OpenRouter already provides access to Claude models.{end}
  {dim}This is only needed for direct Anthropic API access.{end}
  
  1. Open your browser and go to:
     {cyan}https://console.anthropic.com{end}
  
  2. Click {bold}"Sign up"{end} or {bold}"Log in"{end}
  
  3. Complete account verification
  
  4. Click {bold}"Settings"{end} (left sidebar)
  
  5. Click {bold}"API Keys"{end}
     Or go to: {cyan}https://console.anthropic.com/settings/keys{end}
  
  6. Click {bold}"Create Key"{end}
  
  7. Name it: "AIAA Agentic OS"
  
  8. {bold}Copy the key{end} - it starts with "sk-ant-"
     {yellow}You can only see this once!{end}
  
  {dim}Add payment method in Billing for usage beyond free tier{end}
"""
    },
    "FAL_API_KEY": {
        "name": "Fal.ai",
        "category": "ai",
        "required": False,
        "description": "Fast image generation with Flux, SDXL, and more",
        "url": "https://fal.ai/dashboard/keys",
        "prefix": None,
        "workflows": "Product photoshoots, AI image generation, fast inference",
        "pricing": "Pay-as-you-go. Flux: ~$0.025/image. SDXL: ~$0.01/image",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://fal.ai{end}
  
  2. Click {bold}"Sign In"{end} (top right)
     - GitHub sign-in is fastest
     - Or use Google/email
  
  3. Once logged in, click {bold}"Dashboard"{end}
  
  4. Click {bold}"Keys"{end} in the sidebar
     Or go to: {cyan}https://fal.ai/dashboard/keys{end}
  
  5. Click {bold}"Create new key"{end}
  
  6. Name it: "AIAA Agentic OS"
  
  7. {bold}Copy the key{end}
  
  8. Paste it below when prompted
  
  {dim}Great for product photoshoots - faster than DALL-E{end}
  {dim}Add credits in Billing section{end}
"""
    },
    
    # === WEBHOOKS & NOTIFICATIONS ===
    "SLACK_WEBHOOK_URL": {
        "name": "Slack Webhook",
        "category": "notifications",
        "required": False,
        "description": "Send notifications and reports to Slack channels",
        "url": "https://api.slack.com/messaging/webhooks",
        "prefix": "https://hooks.slack.com/",
        "workflows": "Workflow notifications, alerts, report delivery, team updates",
        "pricing": "Free (part of Slack)",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://api.slack.com/apps{end}
  
  2. Click {bold}"Create New App"{end}
  
  3. Select {bold}"From scratch"{end}
  
  4. Fill in:
     - App Name: "AIAA Agentic OS"
     - Workspace: Select your Slack workspace
  
  5. Click {bold}"Create App"{end}
  
  6. In the left sidebar, click {bold}"Incoming Webhooks"{end}
  
  7. Toggle {bold}"Activate Incoming Webhooks"{end} to ON
  
  8. Click {bold}"Add New Webhook to Workspace"{end}
  
  9. Select the {bold}channel{end} where notifications should go
     (e.g., #ai-notifications or #general)
  
  10. Click {bold}"Allow"{end}
  
  11. {bold}Copy the Webhook URL{end}
      It looks like: https://hooks.slack.com/services/T.../B.../...
  
  12. Paste it below when prompted
  
  {dim}You can create multiple webhooks for different channels{end}
"""
    },
    
    # === ANALYTICS & SEO ===
    "SEMRUSH_API_KEY": {
        "name": "SEMrush",
        "category": "seo",
        "required": False,
        "description": "SEO, keyword research, and competitor analysis",
        "url": "https://www.semrush.com/api-documentation/",
        "prefix": None,
        "workflows": "SEO analysis, keyword research, competitor analysis, backlinks",
        "pricing": "API access requires paid plan. Pro: $129/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  {yellow}Note: SEMrush API requires a paid subscription{end}
  
  1. Open your browser and go to:
     {cyan}https://www.semrush.com{end}
  
  2. Log in to your SEMrush account
     (You need an active subscription)
  
  3. Click your profile icon (top right)
  
  4. Click {bold}"Subscription Info"{end}
  
  5. Click {bold}"API units"{end} or go to:
     {cyan}https://www.semrush.com/api-units/{end}
  
  6. Your {bold}API Key{end} is displayed at the top
  
  7. Copy the key
  
  8. Paste it below when prompted
  
  {dim}API calls consume "API units" from your subscription{end}
"""
    },
    "AHREFS_API_KEY": {
        "name": "Ahrefs",
        "category": "seo",
        "required": False,
        "description": "Backlink analysis and SEO toolkit",
        "url": "https://ahrefs.com/api",
        "prefix": None,
        "workflows": "Backlink analysis, SEO audits, competitor research",
        "pricing": "API access requires paid plan. Lite: $129/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  {yellow}Note: Ahrefs API requires a paid subscription{end}
  
  1. Open your browser and go to:
     {cyan}https://ahrefs.com{end}
  
  2. Log in to your Ahrefs account
     (You need an active subscription)
  
  3. Click your profile icon (top right)
  
  4. Click {bold}"API"{end}
     Or go to: {cyan}https://ahrefs.com/api{end}
  
  5. You'll see your {bold}API Token{end} displayed
  
  6. Click {bold}"Copy"{end}
  
  7. Paste it below when prompted
  
  {dim}Different endpoints have different row limits based on plan{end}
"""
    },
    
    # === PAYMENTS ===
    "STRIPE_API_KEY": {
        "name": "Stripe",
        "category": "payments",
        "required": False,
        "description": "Payment processing, subscriptions, and invoicing",
        "url": "https://dashboard.stripe.com/apikeys",
        "prefix": "sk_",
        "workflows": "Client onboarding, payment tracking, subscription management",
        "pricing": "2.9% + $0.30 per transaction",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://dashboard.stripe.com{end}
  
  2. Log in or create a Stripe account
  
  3. Complete account activation if needed
  
  4. Click {bold}"Developers"{end} (top right)
  
  5. Click {bold}"API keys"{end}
     Or go to: {cyan}https://dashboard.stripe.com/apikeys{end}
  
  6. You'll see:
     - Publishable key (pk_...) - for frontend
     - Secret key (sk_...) - {bold}this is what you need{end}
  
  7. Click {bold}"Reveal test key"{end} or {bold}"Reveal live key"{end}
     {yellow}Use TEST key for development!{end}
  
  8. Copy the {bold}Secret key{end} (starts with sk_test_ or sk_live_)
  
  9. Paste it below when prompted
  
  {dim}Start with TEST mode keys, switch to LIVE when ready{end}
"""
    },
    
    # === DATABASES ===
    "PINECONE_API_KEY": {
        "name": "Pinecone",
        "category": "database",
        "required": False,
        "description": "Vector database for AI embeddings and semantic search",
        "url": "https://app.pinecone.io",
        "prefix": None,
        "workflows": "RAG systems, semantic search, knowledge bases, AI memory",
        "pricing": "Free: 1 index, 100K vectors. Standard: $70/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://www.pinecone.io{end}
  
  2. Click {bold}"Start Free"{end} or {bold}"Sign In"{end}
  
  3. Complete account creation (Google sign-in available)
  
  4. Once in the console, look for {bold}"API Keys"{end}
     in the left sidebar
  
  5. Your default API key is already created
  
  6. Click {bold}"Copy"{end} next to the key
  
  7. Also note your {bold}Environment{end} (e.g., "us-east-1-aws")
  
  8. Paste the key below when prompted
  
  {dim}Free tier includes 1 index with 100K vectors{end}
  {dim}Great for building RAG systems and AI memory{end}
"""
    },
    "AIRTABLE_API_KEY": {
        "name": "Airtable",
        "category": "database",
        "required": False,
        "description": "Flexible database with spreadsheet interface",
        "url": "https://airtable.com/create/tokens",
        "prefix": "pat",
        "workflows": "Data storage, CRM alternatives, content calendars, project tracking",
        "pricing": "Free: Unlimited bases, 1,000 records/base. Plus: $12/user/month",
        "instructions": """
  {bold}Step-by-Step Instructions:{end}
  
  1. Open your browser and go to:
     {cyan}https://airtable.com{end}
  
  2. Click {bold}"Sign up for free"{end} or {bold}"Sign in"{end}
  
  3. Once logged in, go to:
     {cyan}https://airtable.com/create/tokens{end}
  
  4. Click {bold}"Create new token"{end}
  
  5. Fill in:
     - Name: "AIAA Agentic OS"
     - Scopes: Select the permissions you need:
       • data.records:read
       • data.records:write
       • schema.bases:read
     - Access: Select "All current and future bases" or specific ones
  
  6. Click {bold}"Create token"{end}
  
  7. {bold}Copy the token{end} - it starts with "pat"
     {yellow}You can only see this once!{end}
  
  8. Paste it below when prompted
  
  {dim}Airtable is great for managing leads, content calendars, etc.{end}
"""
    },
}

def format_instructions(instructions):
    """Format instructions string with color codes."""
    return instructions.format(
        bold=Colors.BOLD,
        end=Colors.END,
        cyan=Colors.CYAN,
        yellow=Colors.YELLOW,
        green=Colors.GREEN,
        red=Colors.RED,
        dim=Colors.DIM
    )

def collect_api_key(key_id, key_config, steps):
    """Collect a single API key with detailed hand-holding instructions."""
    print_header(f"Step 1: API Keys", f"{key_config['name']} - {'Required' if key_config['required'] else 'Optional'}")
    print_step_indicator(0, len(steps), steps)
    
    required_badge = f"{Colors.BOLD}(Required){Colors.END}" if key_config['required'] else f"{Colors.DIM}(Optional){Colors.END}"
    
    # Format the detailed instructions with colors
    formatted_instructions = format_instructions(key_config['instructions'])
    
    # Get pricing info if available
    pricing_info = key_config.get('pricing', '')
    pricing_line = f"\n  {Colors.DIM}Pricing: {pricing_info}{Colors.END}" if pricing_info else ""
    
    print(f"""  {Colors.BOLD}{key_config['name']} API Key{Colors.END} {required_badge}
  
  {key_config['description']}
  
  {Colors.CYAN}Used for:{Colors.END} {key_config['workflows']}{pricing_line}
{formatted_instructions}
  {Colors.DIM}Direct URL: {key_config['url']}{Colors.END}
""")
    
    current_key = os.environ.get(key_id, '')
    if current_key:
        masked = current_key[:15] + "..." if len(current_key) > 15 else current_key
        print(f"  {Colors.GREEN}✓ Found existing key: {masked}{Colors.END}\n")
        if prompt_yes_no("Keep this key?", default=True):
            return True
    
    if not key_config['required']:
        if not prompt_yes_no(f"Add {key_config['name']} key?", default=False):
            print(f"\n  {Colors.DIM}Skipped - add later in .env: {key_id}=your_key{Colors.END}")
            return False
    
    while True:
        key = prompt(f"Paste your {key_config['name']} key")
        
        # Validate prefix if specified
        if key_config.get('prefix') and not key.startswith(key_config['prefix']):
            print(f"    {Colors.YELLOW}Warning: Expected key to start with '{key_config['prefix']}'{Colors.END}")
            if not prompt_yes_no("Save anyway?", default=False):
                continue
        
        save_to_env(key_id, key)
        os.environ[key_id] = key
        print(f"\n  {Colors.GREEN}✓ {key_config['name']} key saved!{Colors.END}")
        return True

def step_api_keys():
    """Configure API keys with comprehensive collection."""
    steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    print_header("AIAA Agentic OS - Setup Wizard", "Let's get your AI agency assistant configured!")
    print_step_indicator(0, len(steps), steps)
    
    print(f"""  {Colors.BOLD}About API Keys{Colors.END}
  
  This system uses various APIs to power different capabilities.
  We'll walk through each one and explain what it's for.
  
  {Colors.GREEN}REQUIRED:{Colors.END}
  • OpenRouter - Powers ALL AI generation (must have)
  
  {Colors.YELLOW}RECOMMENDED:{Colors.END}
  • Perplexity - Deep research capabilities
  • Apify - Lead generation & scraping
  • HubSpot - CRM integration
  • Slack Webhook - Notifications
  
  {Colors.DIM}OPTIONAL:{Colors.END}
  • 20+ additional integrations for specific workflows
  
  {Colors.CYAN}You can skip any optional key and add it later to .env{Colors.END}
""")
    
    wait_for_enter()
    
    # Define collection order by category
    collection_order = [
        # Core (required)
        "OPENROUTER_API_KEY",
        # Research
        "PERPLEXITY_API_KEY",
        # Lead Gen
        "APIFY_API_TOKEN",
        "HUNTER_API_KEY",
        "APOLLO_API_KEY",
        # CRM & Email
        "HUBSPOT_API_KEY",
        "INSTANTLY_API_KEY",
        "SENDGRID_API_KEY",
        # Notifications
        "SLACK_WEBHOOK_URL",
        # Google
        "GOOGLE_APPLICATION_CREDENTIALS",
    ]
    
    # Required key first
    openrouter_config = API_KEY_REGISTRY["OPENROUTER_API_KEY"]
    print_header("Step 1: API Keys", "OpenRouter - REQUIRED")
    print_step_indicator(0, len(steps), steps)
    
    print(f"""  {Colors.BOLD}{Colors.GREEN}OpenRouter API Key{Colors.END} {Colors.BOLD}(REQUIRED){Colors.END}
  
  This powers ALL AI generation in the system.
  {Colors.RED}You cannot proceed without this key.{Colors.END}
  
  {Colors.CYAN}How to get your key (takes 2 minutes):{Colors.END}
  1. Go to {Colors.BOLD}https://openrouter.ai{Colors.END}
  2. Click "Sign Up" (use Google for fastest setup)
  3. Go to {Colors.BOLD}https://openrouter.ai/keys{Colors.END}
  4. Click "Create Key"
  5. Copy and paste it below
  
  {Colors.DIM}Free tier available, then pay-as-you-go (~$0.001-0.02 per request){Colors.END}
""")
    
    current_key = os.environ.get('OPENROUTER_API_KEY', '')
    if current_key:
        print(f"  {Colors.GREEN}✓ Found existing key: {current_key[:20]}...{Colors.END}\n")
        if not prompt_yes_no("Keep this key?", default=True):
            current_key = ""
    
    if not current_key:
        while True:
            key = prompt("Paste your OpenRouter API key")
            if key.startswith('sk-or-'):
                save_to_env('OPENROUTER_API_KEY', key)
                os.environ['OPENROUTER_API_KEY'] = key
                print(f"\n  {Colors.GREEN}✓ OpenRouter API key saved!{Colors.END}")
                break
            else:
                print(f"    {Colors.RED}That doesn't look like an OpenRouter key (should start with sk-or-){Colors.END}")
    
    wait_for_enter()
    
    # Ask about setup depth
    print_header("Step 1: API Keys", "Setup Depth")
    print_step_indicator(0, len(steps), steps)
    
    print(f"""  {Colors.BOLD}How thorough do you want the setup to be?{Colors.END}
  
  The system has 50+ possible integrations. You can:
""")
    
    setup_options = [
        "Quick Setup - Just essentials (OpenRouter + 3-4 recommended)",
        "Standard Setup - Research + Lead Gen + CRM + Notifications",
        "Full Setup - Walk through ALL available integrations",
        "Skip for now - I'll add keys to .env manually"
    ]
    
    setup_choice = prompt_choice("Choose setup depth:", setup_options)
    
    if setup_choice == 3:  # Skip
        print(f"\n  {Colors.DIM}Skipped - edit .env file to add keys later{Colors.END}")
        print(f"  {Colors.DIM}See QUICKREF.md for full list of available keys{Colors.END}")
        wait_for_enter()
        return
    
    # Define keys to collect based on choice
    if setup_choice == 0:  # Quick
        keys_to_collect = ["PERPLEXITY_API_KEY", "APIFY_API_TOKEN", "SLACK_WEBHOOK_URL"]
    elif setup_choice == 1:  # Standard
        keys_to_collect = [
            "PERPLEXITY_API_KEY", "APIFY_API_TOKEN", "HUNTER_API_KEY",
            "HUBSPOT_API_KEY", "INSTANTLY_API_KEY", "SLACK_WEBHOOK_URL",
            "GOOGLE_APPLICATION_CREDENTIALS"
        ]
    else:  # Full
        keys_to_collect = [k for k in collection_order if k != "OPENROUTER_API_KEY"]
        # Add remaining keys not in collection_order
        for key_id in API_KEY_REGISTRY:
            if key_id not in keys_to_collect and key_id != "OPENROUTER_API_KEY":
                keys_to_collect.append(key_id)
    
    # Collect each key
    configured_count = 1  # OpenRouter already done
    for key_id in keys_to_collect:
        if key_id in API_KEY_REGISTRY:
            if collect_api_key(key_id, API_KEY_REGISTRY[key_id], steps):
                configured_count += 1
            wait_for_enter()
    
    # Summary
    print_header("Step 1: API Keys", "Summary")
    print_step_indicator(0, len(steps), steps)
    
    print(f"  {Colors.GREEN}{'═' * 56}{Colors.END}")
    print(f"  {Colors.GREEN}✓ API Keys configured: {configured_count}{Colors.END}")
    print(f"  {Colors.GREEN}{'═' * 56}{Colors.END}\n")
    
    print(f"  {Colors.BOLD}Configured keys:{Colors.END}\n")
    
    for key_id in ["OPENROUTER_API_KEY"] + keys_to_collect:
        if os.environ.get(key_id):
            name = API_KEY_REGISTRY.get(key_id, {}).get('name', key_id)
            print(f"  {Colors.GREEN}✓{Colors.END} {name}")
    
    print(f"\n  {Colors.DIM}You can add more keys later by editing .env{Colors.END}")
    print(f"  {Colors.DIM}Full list of supported keys in QUICKREF.md{Colors.END}")
    
    wait_for_enter()


# ═══════════════════════════════════════════════════════════════
# STEP 2: AGENCY PROFILE
# ═══════════════════════════════════════════════════════════════

def step_agency_profile():
    """Create agency profile."""
    steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    print_header("Step 2: Your Agency Profile", "Tell us about your agency so the AI can personalize outputs")
    print_step_indicator(1, len(steps), steps)
    
    print(f"""  The AI will use this information to:
  • Write content in your voice
  • Reference your services correctly
  • Understand your target market
""")
    
    wait_for_enter()
    
    print_header("Step 2: Your Agency Profile", "Basic Information")
    print_step_indicator(1, len(steps), steps)
    
    agency = {}
    
    agency['name'] = prompt("What's your agency name?")
    agency['website'] = prompt("What's your website?", required=False)
    agency['tagline'] = prompt("One-sentence description of what you do")
    
    print()
    
    # Services
    print(f"  {Colors.BOLD}What services do you offer?{Colors.END}")
    print(f"  {Colors.DIM}(Enter each service, press Enter twice when done){Colors.END}\n")
    
    services = []
    while True:
        service = prompt(f"Service {len(services) + 1}", required=False)
        if not service:
            break
        services.append(service)
    
    agency['services'] = services
    
    wait_for_enter()
    
    print_header("Step 2: Your Agency Profile", "Target Market")
    print_step_indicator(1, len(steps), steps)
    
    agency['target_audience'] = prompt("Who is your ideal client? (e.g., 'B2B SaaS companies')")
    agency['target_industries'] = prompt("What industries do you serve? (comma-separated)", required=False)
    agency['unique_value'] = prompt("What makes you different from competitors?", required=False)
    
    wait_for_enter()
    
    print_header("Step 2: Your Agency Profile", "Social Profiles")
    print_step_indicator(1, len(steps), steps)
    
    print(f"  {Colors.DIM}These help the AI match your brand voice. Press Enter to skip any.{Colors.END}\n")
    
    agency['social'] = {
        'linkedin': prompt("LinkedIn URL", required=False),
        'twitter': prompt("Twitter/X URL", required=False),
        'youtube': prompt("YouTube URL", required=False),
        'instagram': prompt("Instagram URL", required=False),
    }
    
    # Save agency profile
    agency['created_at'] = datetime.now().isoformat()
    
    CONTEXT_DIR.mkdir(exist_ok=True)
    profile_path = CONTEXT_DIR / "agency_profile.json"
    profile_path.write_text(json.dumps(agency, indent=2))
    
    print(f"\n  {Colors.GREEN}{'═' * 56}{Colors.END}")
    print(f"  {Colors.GREEN}✓ Agency profile saved!{Colors.END}")
    print(f"  {Colors.DIM}  Location: {profile_path}{Colors.END}")
    print(f"  {Colors.GREEN}{'═' * 56}{Colors.END}")
    
    wait_for_enter()
    
    return agency


# ═══════════════════════════════════════════════════════════════
# STEP 3: ADD CLIENTS
# ═══════════════════════════════════════════════════════════════

def create_client_profile_md(client_data):
    """Generate profile.md content for a client."""
    return f"""# {client_data['name']} - Client Profile

## Company Overview
- **Company Name:** {client_data['name']}
- **Website:** {client_data.get('website', 'N/A')}
- **Industry:** {client_data.get('industry', 'N/A')}
- **Description:** {client_data.get('description', 'N/A')}

## Business Details
- **Business Model:** {client_data.get('business_model', 'N/A')}
- **Main Products/Services:** {client_data.get('products_services', 'N/A')}
- **Price Range:** {client_data.get('price_range', 'N/A')}
- **Founded:** {client_data.get('founded', 'N/A')}
- **Company Size:** {client_data.get('company_size', 'N/A')}

## Target Audience
- **Primary Audience:** {client_data.get('target_audience', 'N/A')}
- **Customer Avatar:** {client_data.get('customer_avatar', 'N/A')}
- **Pain Points:** {client_data.get('pain_points', 'N/A')}

## Market Position
- **Unique Value Proposition:** {client_data.get('uvp', 'N/A')}
- **Main Competitors:** {client_data.get('competitors', 'N/A')}
- **Differentiators:** {client_data.get('differentiators', 'N/A')}

## Contact Information
- **Primary Contact:** {client_data.get('contact_name', 'N/A')}
- **Email:** {client_data.get('contact_email', 'N/A')}
- **Phone:** {client_data.get('contact_phone', 'N/A')}

## Social Profiles
- **LinkedIn:** {client_data.get('social', {}).get('linkedin', 'N/A')}
- **Twitter/X:** {client_data.get('social', {}).get('twitter', 'N/A')}
- **Instagram:** {client_data.get('social', {}).get('instagram', 'N/A')}
- **YouTube:** {client_data.get('social', {}).get('youtube', 'N/A')}
- **Facebook:** {client_data.get('social', {}).get('facebook', 'N/A')}

## Goals & Objectives
{client_data.get('goals', 'To be defined')}

## Notes
{client_data.get('notes', 'No additional notes')}

---
*Profile created: {client_data.get('created_at', 'Unknown')}*
"""

def create_client_rules_md(client_data):
    """Generate rules.md content for a client."""
    return f"""# {client_data['name']} - Content Rules

## Brand Guidelines

### Voice & Tone
{client_data.get('voice_tone', '- Professional yet approachable\n- Confident but not arrogant\n- Educational and helpful')}

### Words to USE
{client_data.get('words_to_use', '- [Add preferred terminology]\n- [Industry-specific terms]\n- [Brand keywords]')}

### Words to AVOID
{client_data.get('words_to_avoid', '- [Competitor names]\n- [Negative terms]\n- [Off-brand language]')}

## Content Requirements

### Required Elements
{client_data.get('required_elements', '- Always include CTA\n- Use approved brand colors\n- Include social proof when possible')}

### Approval Process
{client_data.get('approval_process', 'All content requires client review before publishing')}

### Compliance Notes
{client_data.get('compliance_notes', 'N/A - Add any regulatory or legal requirements')}

## Formatting Standards
{client_data.get('formatting_standards', '- Use sentence case for headlines\n- Keep paragraphs short (2-3 sentences)\n- Include bullet points for readability')}

## DO's
{client_data.get('dos', '- Highlight customer success stories\n- Emphasize ROI and results\n- Use data and statistics')}

## DON'Ts
{client_data.get('donts', "- Don't make unsubstantiated claims\n- Don't disparage competitors\n- Don't use jargon without explanation")}

---
*Rules last updated: {client_data.get('created_at', 'Unknown')}*
"""

def create_client_preferences_md(client_data):
    """Generate preferences.md content for a client."""
    return f"""# {client_data['name']} - Style Preferences

## Communication Style
- **Formality Level:** {client_data.get('formality', 'Professional')}
- **Emoji Usage:** {client_data.get('emoji_usage', 'Minimal/None')}
- **Humor Level:** {client_data.get('humor_level', 'Light/Professional')}

## Content Preferences

### Preferred Content Types
{client_data.get('preferred_content', '- Educational blog posts\n- Case studies\n- Social proof content')}

### Content Length Preferences
{client_data.get('content_length', '- Social posts: 150-300 words\n- Blog posts: 1500-2500 words\n- Emails: 200-400 words')}

### Visual Style
{client_data.get('visual_style', '- Clean and modern\n- Brand color palette\n- Professional imagery')}

## Platform-Specific Preferences

### LinkedIn
{client_data.get('linkedin_style', '- Thought leadership focus\n- Industry insights\n- Professional tone')}

### Email Marketing
{client_data.get('email_style', '- Personal, from founder\n- Value-first approach\n- Clear CTAs')}

### Website/Blog
{client_data.get('website_style', '- SEO-optimized\n- Educational content\n- Clear navigation')}

## Scheduling Preferences
{client_data.get('scheduling', '- Best posting times: Business hours\n- Content calendar: Weekly review\n- Approval timeline: 48 hours')}

---
*Preferences last updated: {client_data.get('created_at', 'Unknown')}*
"""

def create_client_history_md(client_data):
    """Generate history.md content for a client."""
    return f"""# {client_data['name']} - Project History

## Engagement Summary
- **Client Since:** {client_data.get('created_at', 'Unknown')[:10]}
- **Current Status:** Active
- **Engagement Type:** {client_data.get('engagement_type', 'Ongoing Retainer')}

## Services Provided
{client_data.get('services_provided', '- [List services you provide to this client]')}

## Completed Projects

### Project 1: Initial Setup
- **Date:** {client_data.get('created_at', 'Unknown')[:10]}
- **Deliverables:** Client profile setup
- **Outcome:** Client onboarded successfully

<!-- Add more projects as you complete them -->

## Performance Metrics
- **Content Pieces Created:** 0
- **Campaigns Launched:** 0
- **Results Achieved:** Pending first project

## What's Working
- [Add insights as you learn what works for this client]

## What to Avoid
- [Add learnings about what doesn't work]

## Key Learnings
- [Document important discoveries about this client]

## Upcoming Projects
- [List planned work]

---
*History last updated: {client_data.get('created_at', 'Unknown')}*
"""

def add_single_client(client_num=1, steps=None, show_header=True):
    """Add a single client with comprehensive profile creation."""
    if steps is None:
        steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    if show_header:
        print_header(f"Add Client #{client_num}", "Let's create a comprehensive client profile")
        print_step_indicator(2, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Client Profile Setup{Colors.END}
  
  We'll collect information in 4 categories:
  1. {Colors.CYAN}Basic Info{Colors.END} - Company name, industry, website
  2. {Colors.CYAN}Business Details{Colors.END} - Products, audience, competitors
  3. {Colors.CYAN}Contact & Social{Colors.END} - Who to reach, social profiles
  4. {Colors.CYAN}Style Preferences{Colors.END} - Tone, voice, content rules
  
  {Colors.DIM}Press Enter to skip any field you don't know yet.{Colors.END}
""")
    
    wait_for_enter("Press Enter to start...")
    
    client = {}
    
    # === SECTION 1: BASIC INFO ===
    if show_header:
        print_header(f"Client #{client_num}: Basic Information", "Essential details about the company")
        print_step_indicator(2, len(steps), steps)
    
    print(f"  {Colors.BOLD}{Colors.CYAN}Section 1: Basic Information{Colors.END}\n")
    
    client['name'] = prompt("Company/Client name")
    client['website'] = prompt("Website URL", required=False)
    client['industry'] = prompt("Industry (e.g., SaaS, E-commerce, Agency)")
    client['description'] = prompt("One-sentence description of what they do")
    
    wait_for_enter()
    
    # === SECTION 2: BUSINESS DETAILS ===
    if show_header:
        print_header(f"Client #{client_num}: Business Details", "Understanding their business model")
        print_step_indicator(2, len(steps), steps)
    
    print(f"  {Colors.BOLD}{Colors.CYAN}Section 2: Business Details{Colors.END}\n")
    
    client['business_model'] = prompt("Business model (B2B, B2C, D2C, SaaS)", required=False)
    client['products_services'] = prompt("Main products or services", required=False)
    client['price_range'] = prompt("Price range (e.g., $500-5000, Premium, Budget)", required=False)
    client['company_size'] = prompt("Company size (employees or revenue range)", required=False)
    
    print()
    print(f"  {Colors.DIM}Target Market:{Colors.END}\n")
    
    client['target_audience'] = prompt("Who is their target audience?", required=False)
    client['customer_avatar'] = prompt("Ideal customer avatar (job title, demographics)", required=False)
    client['pain_points'] = prompt("Main customer pain points (comma-separated)", required=False)
    
    print()
    print(f"  {Colors.DIM}Market Position:{Colors.END}\n")
    
    client['uvp'] = prompt("Unique value proposition (what makes them different)", required=False)
    client['competitors'] = prompt("Main competitors (comma-separated)", required=False)
    client['differentiators'] = prompt("Key differentiators from competitors", required=False)
    
    wait_for_enter()
    
    # === SECTION 3: CONTACT & SOCIAL ===
    if show_header:
        print_header(f"Client #{client_num}: Contact & Social", "How to reach them and their online presence")
        print_step_indicator(2, len(steps), steps)
    
    print(f"  {Colors.BOLD}{Colors.CYAN}Section 3: Contact Information{Colors.END}\n")
    
    client['contact_name'] = prompt("Primary contact name", required=False)
    client['contact_email'] = prompt("Contact email", required=False)
    client['contact_phone'] = prompt("Contact phone", required=False)
    
    print()
    print(f"  {Colors.DIM}Social Profiles (press Enter to skip):{Colors.END}\n")
    
    client['social'] = {
        'linkedin': prompt("LinkedIn company page URL", required=False),
        'twitter': prompt("Twitter/X URL", required=False),
        'instagram': prompt("Instagram URL", required=False),
        'youtube': prompt("YouTube channel URL", required=False),
        'facebook': prompt("Facebook page URL", required=False),
    }
    
    wait_for_enter()
    
    # === SECTION 4: STYLE PREFERENCES ===
    if show_header:
        print_header(f"Client #{client_num}: Style Preferences", "How they want content to sound")
        print_step_indicator(2, len(steps), steps)
    
    print(f"  {Colors.BOLD}{Colors.CYAN}Section 4: Content Style{Colors.END}\n")
    
    print(f"  {Colors.DIM}What tone should we use for their content?{Colors.END}\n")
    
    tone_options = [
        "Professional & Formal",
        "Professional & Friendly",
        "Casual & Conversational",
        "Bold & Confident",
        "Educational & Helpful",
        "Custom (specify)"
    ]
    
    tone_choice = prompt_choice("Select their preferred tone:", tone_options, allow_skip=True)
    if tone_choice is not None:
        if tone_choice == 5:  # Custom
            client['voice_tone'] = prompt("Describe their preferred tone")
        else:
            client['voice_tone'] = tone_options[tone_choice]
    
    print()
    client['formality'] = prompt("Formality level (Formal/Semi-formal/Casual)", required=False) or "Professional"
    client['emoji_usage'] = prompt("Use emojis? (Yes/Minimal/No)", required=False) or "Minimal"
    
    print()
    print(f"  {Colors.DIM}Content rules (optional):{Colors.END}\n")
    
    client['words_to_use'] = prompt("Keywords or phrases to emphasize", required=False)
    client['words_to_avoid'] = prompt("Words or phrases to avoid", required=False)
    
    wait_for_enter()
    
    # === SECTION 5: GOALS & NOTES ===
    if show_header:
        print_header(f"Client #{client_num}: Goals & Notes", "What are we trying to achieve?")
        print_step_indicator(2, len(steps), steps)
    
    print(f"  {Colors.BOLD}{Colors.CYAN}Section 5: Goals & Additional Notes{Colors.END}\n")
    
    client['goals'] = prompt("What are their main goals? (e.g., More leads, Brand awareness)", required=False)
    client['engagement_type'] = prompt("Engagement type (Retainer/Project/Consultation)", required=False)
    client['services_provided'] = prompt("What services are you providing?", required=False)
    client['notes'] = prompt("Any other important notes?", required=False)
    
    # === CREATE CLIENT FOLDER & FILES ===
    client_slug = client['name'].lower().replace(' ', '_').replace('-', '_')
    client_slug = ''.join(c for c in client_slug if c.isalnum() or c == '_')
    
    client_dir = CLIENTS_DIR / client_slug
    client_dir.mkdir(parents=True, exist_ok=True)
    (client_dir / "outputs").mkdir(exist_ok=True)
    
    client['created_at'] = datetime.now().isoformat()
    client['folder'] = str(client_dir)
    client['slug'] = client_slug
    
    # Create all the markdown files
    (client_dir / "profile.md").write_text(create_client_profile_md(client))
    (client_dir / "rules.md").write_text(create_client_rules_md(client))
    (client_dir / "preferences.md").write_text(create_client_preferences_md(client))
    (client_dir / "history.md").write_text(create_client_history_md(client))
    
    # Also save as JSON for programmatic access
    (client_dir / "context.json").write_text(json.dumps(client, indent=2))
    
    print(f"\n  {Colors.GREEN}{'═' * 56}{Colors.END}")
    print(f"  {Colors.GREEN}✓ Client '{client['name']}' created successfully!{Colors.END}")
    print(f"  {Colors.GREEN}{'═' * 56}{Colors.END}")
    print()
    print(f"  {Colors.BOLD}Created files:{Colors.END}")
    print(f"  {Colors.DIM}clients/{client_slug}/{Colors.END}")
    print(f"  {Colors.DIM}  ├── profile.md      {Colors.END}{Colors.CYAN}← Business info & overview{Colors.END}")
    print(f"  {Colors.DIM}  ├── rules.md        {Colors.END}{Colors.CYAN}← Content rules & guidelines{Colors.END}")
    print(f"  {Colors.DIM}  ├── preferences.md  {Colors.END}{Colors.CYAN}← Style & tone preferences{Colors.END}")
    print(f"  {Colors.DIM}  ├── history.md      {Colors.END}{Colors.CYAN}← Project history & learnings{Colors.END}")
    print(f"  {Colors.DIM}  ├── context.json    {Colors.END}{Colors.CYAN}← Machine-readable data{Colors.END}")
    print(f"  {Colors.DIM}  └── outputs/        {Colors.END}{Colors.CYAN}← Generated content goes here{Colors.END}")
    
    print(f"""
  {Colors.BOLD}What's next:{Colors.END}
  • The AI will automatically load this client's context
  • Say "create content for {client['name']}" and it knows everything
  • Edit the .md files anytime to update client info
  • Generated content saves to clients/{client_slug}/outputs/
""")
    
    return client

def step_add_clients():
    """Add client profiles with comprehensive setup."""
    steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    print_header("Step 3: Add Your Clients", "Create comprehensive profiles for each client")
    print_step_indicator(2, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Why add clients?{Colors.END}
  
  Each client gets their own folder with 4 key files:
  
  📄 {Colors.CYAN}profile.md{Colors.END}      - Who they are, their business, audience
  📄 {Colors.CYAN}rules.md{Colors.END}        - Content rules, words to use/avoid
  📄 {Colors.CYAN}preferences.md{Colors.END}  - Tone, style, platform preferences
  📄 {Colors.CYAN}history.md{Colors.END}      - Past projects, what works, learnings
  
  {Colors.BOLD}Benefits:{Colors.END}
  • AI automatically knows each client's business
  • Content matches their voice and style
  • Never repeat past mistakes
  • All outputs organized by client
  
  {Colors.DIM}Example: "Write a LinkedIn post for Acme Corp" - the AI loads
  all their context files and writes in their voice.{Colors.END}
""")
    
    if not prompt_yes_no("Add clients now?", default=True):
        print(f"\n  {Colors.DIM}Skipped - you can add clients anytime with:{Colors.END}")
        print(f"  {Colors.CYAN}python3 wizard.py --add-client{Colors.END}")
        print(f"  {Colors.DIM}or{Colors.END}")
        print(f"  {Colors.CYAN}python3 run.py --add-client{Colors.END}")
        wait_for_enter()
        return []
    
    clients = []
    
    while True:
        client_num = len(clients) + 1
        client = add_single_client(client_num, steps, show_header=True)
        clients.append(client)
        
        wait_for_enter()
        
        if not prompt_yes_no("Add another client?", default=False):
            break
    
    print(f"\n  {Colors.GREEN}{'═' * 56}{Colors.END}")
    print(f"  {Colors.GREEN}✓ {len(clients)} client(s) added successfully!{Colors.END}")
    print(f"  {Colors.GREEN}{'═' * 56}{Colors.END}")
    
    if clients:
        print(f"\n  {Colors.BOLD}Your clients:{Colors.END}")
        for c in clients:
            print(f"  • {c['name']} → clients/{c['slug']}/")
    
    wait_for_enter()
    
    return clients


# ═══════════════════════════════════════════════════════════════
# STEP 4: LEARN THE SYSTEM
# ═══════════════════════════════════════════════════════════════

def step_learn_system():
    """Explain system capabilities."""
    steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    # Count resources
    directives_count = len(list((BASE_DIR / "directives").glob("*.md")))
    scripts_count = len(list((BASE_DIR / "execution").glob("*.py")))
    skills_count = len(list((BASE_DIR / "skills").glob("*.md")))
    
    print_header("Step 4: Your System Capabilities", "Here's what you can do now")
    print_step_indicator(3, len(steps), steps)
    
    print(f"""  {Colors.BOLD}System Overview{Colors.END}
  
  Your AI agency assistant is now configured with:
  
  • {Colors.CYAN}{directives_count}{Colors.END} Workflow Directives (step-by-step SOPs)
  • {Colors.CYAN}{scripts_count}{Colors.END} Execution Scripts (automated tasks)
  • {Colors.CYAN}{skills_count}{Colors.END} Skill Bibles (expert knowledge)
  
  Think of it like having a team of specialists:
  • A copywriter who knows VSLs, emails, and landing pages
  • A researcher who can analyze any company or market
  • A lead gen specialist who can scrape and qualify leads
  • A content creator for social media and blogs
""")
    
    wait_for_enter()
    
    # Content Creation
    print_header("Step 4: Capabilities", "📝 Content Creation")
    print_step_indicator(3, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Content You Can Create:{Colors.END}
  
  {Colors.GREEN}Sales Copy{Colors.END}
  • VSL scripts (video sales letters)
  • Sales pages and landing pages
  • Email sequences (welcome, nurture, sales)
  • Case studies and testimonials
  
  {Colors.GREEN}Social Media{Colors.END}
  • LinkedIn posts and carousels
  • Twitter/X threads
  • Instagram reel scripts
  • YouTube scripts
  
  {Colors.GREEN}Long-Form{Colors.END}
  • Blog posts (SEO-optimized)
  • Newsletters
  • Press releases
  • Whitepapers
  
  {Colors.DIM}All content uses the Skill Bibles - expert knowledge from
  top copywriters, marketers, and sales professionals.{Colors.END}
""")
    
    wait_for_enter()
    
    # Research
    print_header("Step 4: Capabilities", "🔍 Research")
    print_step_indicator(3, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Research Capabilities:{Colors.END}
  
  {Colors.GREEN}Company Research{Colors.END}
  • Full company analysis (positioning, offers, pricing)
  • Competitor breakdowns
  • Market opportunity analysis
  
  {Colors.GREEN}Prospect Research{Colors.END}
  • Deep-dive on potential clients
  • LinkedIn profile analysis
  • Company pain points identification
  
  {Colors.GREEN}Market Research{Colors.END}
  • Industry trends and analysis
  • Target audience insights
  • Pricing research
  
  {Colors.DIM}Research uses Perplexity AI for real-time web data
  (if you added that API key).{Colors.END}
""")
    
    wait_for_enter()
    
    # Lead Generation
    print_header("Step 4: Capabilities", "📊 Lead Generation")
    print_step_indicator(3, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Lead Generation:{Colors.END}
  
  {Colors.GREEN}Scraping Sources{Colors.END}
  • Google Maps (local businesses)
  • LinkedIn (profiles and companies)
  • Google Search results
  • Yelp reviews
  • Job boards
  
  {Colors.GREEN}Enrichment{Colors.END}
  • Email finding and verification
  • Company data enrichment
  • Contact information extraction
  
  {Colors.GREEN}Processing{Colors.END}
  • Lead scoring with AI
  • Deduplication
  • Export to CSV/Google Sheets
  
  {Colors.DIM}Lead gen requires Apify API token
  (if you added that during setup).{Colors.END}
""")
    
    wait_for_enter()
    
    # Client Deliverables
    print_header("Step 4: Capabilities", "📈 Client Deliverables")
    print_step_indicator(3, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Client Work:{Colors.END}
  
  {Colors.GREEN}Reports{Colors.END}
  • Monthly performance reports
  • Quarterly business reviews (QBRs)
  • Campaign analysis reports
  
  {Colors.GREEN}Strategy{Colors.END}
  • Funnel strategies and outlines
  • Content calendars
  • A/B test analysis
  
  {Colors.GREEN}Onboarding{Colors.END}
  • Client welcome sequences
  • Kickoff documentation
  • Proposal generation
  
  {Colors.DIM}All outputs can be saved directly to Google Docs
  (if you connect Google Drive).{Colors.END}
""")
    
    wait_for_enter()


# ═══════════════════════════════════════════════════════════════
# STEP 5: FIRST WORKFLOW
# ═══════════════════════════════════════════════════════════════

def step_first_workflow(agency):
    """Run first workflow with hand-holding."""
    steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    print_header("Step 5: Run Your First Workflow", "Let's create something together!")
    print_step_indicator(4, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Time to see it in action!{Colors.END}
  
  We'll run a simple workflow together so you can see how it works.
  This will take about 30 seconds.
  
  {Colors.CYAN}Choose what to create:{Colors.END}
""")
    
    options = [
        "LinkedIn Post - Quick win, great for testing",
        "Blog Post Outline - See the research capabilities",
        "Cold Email Sequence - If you do outreach",
    ]
    
    choice = prompt_choice("What would you like to create?", options)
    
    if choice == 0:  # LinkedIn Post
        print_header("Step 5: Creating LinkedIn Post", "Follow along...")
        print_step_indicator(4, len(steps), steps)
        
        topic = prompt("What topic should the post be about?")
        
        print(f"\n  {Colors.CYAN}⏳ Generating your LinkedIn post...{Colors.END}")
        print(f"  {Colors.DIM}   (The AI is writing using expert copywriting knowledge){Colors.END}\n")
        
        try:
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "execution" / "generate_linkedin_post.py"),
                 "--topic", topic,
                 "--output", str(BASE_DIR / ".tmp" / "first_workflow_output.md")],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            output_file = BASE_DIR / ".tmp" / "linkedin_post.md"
            if output_file.exists():
                content = output_file.read_text()
                
                print(f"  {Colors.GREEN}✓ Done! Here's your post:{Colors.END}\n")
                print(f"  {Colors.DIM}{'─' * 56}{Colors.END}")
                
                # Show first 500 chars
                preview = content[:800] + "..." if len(content) > 800 else content
                for line in preview.split('\n'):
                    print(f"  {line}")
                
                print(f"  {Colors.DIM}{'─' * 56}{Colors.END}")
                
                print(f"\n  {Colors.GREEN}Full post saved to: .tmp/linkedin_post.md{Colors.END}")
            else:
                print(f"  {Colors.YELLOW}Generated but output file not found. Check .tmp/ folder.{Colors.END}")
                
        except subprocess.TimeoutExpired:
            print(f"  {Colors.YELLOW}Taking longer than expected. The system is working!{Colors.END}")
        except Exception as e:
            print(f"  {Colors.RED}Error: {e}{Colors.END}")
            print(f"  {Colors.DIM}Don't worry - this might be an API key issue. You can try again later.{Colors.END}")
    
    elif choice == 1:  # Blog Post
        print_header("Step 5: Creating Blog Outline", "Follow along...")
        print_step_indicator(4, len(steps), steps)
        
        topic = prompt("What topic should the blog post cover?")
        
        print(f"\n  {Colors.CYAN}⏳ Generating your blog post...{Colors.END}")
        print(f"  {Colors.DIM}   (The AI is researching and writing){Colors.END}\n")
        
        try:
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "execution" / "generate_blog_post.py"),
                 "--topic", topic,
                 "--length", "800",
                 "--output", str(BASE_DIR / ".tmp" / "first_blog.md")],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            output_file = BASE_DIR / ".tmp" / "first_blog.md"
            if output_file.exists():
                content = output_file.read_text()
                
                print(f"  {Colors.GREEN}✓ Done! Here's your blog post:{Colors.END}\n")
                print(f"  {Colors.DIM}{'─' * 56}{Colors.END}")
                
                preview = content[:1000] + "..." if len(content) > 1000 else content
                for line in preview.split('\n')[:20]:
                    print(f"  {line}")
                
                print(f"  {Colors.DIM}{'─' * 56}{Colors.END}")
                
                print(f"\n  {Colors.GREEN}Full post saved to: .tmp/first_blog.md{Colors.END}")
            else:
                print(f"  {Colors.YELLOW}Generated but output file not found. Check .tmp/ folder.{Colors.END}")
                
        except Exception as e:
            print(f"  {Colors.RED}Error: {e}{Colors.END}")
    
    elif choice == 2:  # Cold Email
        print_header("Step 5: Creating Cold Emails", "Follow along...")
        print_step_indicator(4, len(steps), steps)
        
        print(f"  {Colors.DIM}Cold emails need a leads file. Let's create a sample one.{Colors.END}\n")
        
        # Create sample lead
        sample_leads = [
            {
                "name": "John Smith",
                "company": "TechCorp",
                "title": "CEO",
                "email": "john@techcorp.com"
            }
        ]
        
        leads_file = BASE_DIR / ".tmp" / "sample_leads.json"
        leads_file.write_text(json.dumps(sample_leads, indent=2))
        
        product = prompt("What product/service are you selling?")
        
        print(f"\n  {Colors.CYAN}⏳ Generating cold email sequence...{Colors.END}\n")
        
        try:
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "execution" / "write_cold_emails.py"),
                 "--leads", str(leads_file),
                 "--sender_name", agency.get('name', 'Your Agency'),
                 "--product", product,
                 "--output", str(BASE_DIR / ".tmp" / "first_emails.md"),
                 "--limit", "1",
                 "--skip_research"],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            output_file = BASE_DIR / ".tmp" / "first_emails.md"
            if output_file.exists():
                content = output_file.read_text()
                
                print(f"  {Colors.GREEN}✓ Done! Here's your email sequence:{Colors.END}\n")
                print(f"  {Colors.DIM}{'─' * 56}{Colors.END}")
                
                preview = content[:1200] + "..." if len(content) > 1200 else content
                for line in preview.split('\n')[:25]:
                    print(f"  {line}")
                
                print(f"  {Colors.DIM}{'─' * 56}{Colors.END}")
                
                print(f"\n  {Colors.GREEN}Full sequence saved to: .tmp/first_emails.md{Colors.END}")
            else:
                print(f"  {Colors.YELLOW}Check .tmp/ folder for output.{Colors.END}")
                
        except Exception as e:
            print(f"  {Colors.RED}Error: {e}{Colors.END}")
    
    print(f"""
  {Colors.GREEN}{'═' * 56}{Colors.END}
  {Colors.GREEN}🎉 You just ran your first workflow!{Colors.END}
  {Colors.GREEN}{'═' * 56}{Colors.END}
  
  {Colors.BOLD}What just happened:{Colors.END}
  1. Your command was interpreted
  2. The right script was selected
  3. Skill Bibles were loaded (expert knowledge)
  4. AI generated the content
  5. Output was saved to a file
  
  This same process works for all {scripts_count} workflows!
""")
    
    wait_for_enter()


# ═══════════════════════════════════════════════════════════════
# STEP 6: CREATE WORKFLOWS
# ═══════════════════════════════════════════════════════════════

def step_create_workflows():
    """Teach how to create custom workflows."""
    steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    print_header("Step 6: Creating Your Own Workflows", "Become a power user")
    print_step_indicator(5, len(steps), steps)
    
    print(f"""  {Colors.BOLD}The DOE Architecture{Colors.END}
  
  Every workflow in this system follows a simple pattern:
  
  {Colors.CYAN}D{Colors.END} - {Colors.BOLD}Directive{Colors.END}    (What to do - plain English instructions)
  {Colors.CYAN}O{Colors.END} - {Colors.BOLD}Orchestration{Colors.END} (You or AI deciding what runs)
  {Colors.CYAN}E{Colors.END} - {Colors.BOLD}Execution{Colors.END}    (Python script that does the work)
  
  {Colors.DIM}Directives are in: directives/*.md
  Scripts are in: execution/*.py
  Knowledge is in: skills/*.md{Colors.END}
""")
    
    wait_for_enter()
    
    print_header("Step 6: Creating Workflows", "Understanding Directives")
    print_step_indicator(5, len(steps), steps)
    
    print(f"""  {Colors.BOLD}What's a Directive?{Colors.END}
  
  A directive is a markdown file that describes a workflow.
  Think of it as an SOP (Standard Operating Procedure).
  
  {Colors.CYAN}Example: directives/linkedin_post_generator.md{Colors.END}
  
  {Colors.DIM}┌────────────────────────────────────────────────────────┐
  │ # LinkedIn Post Generator                               │
  │                                                         │
  │ ## What This Workflow Does                              │
  │ Creates engaging LinkedIn posts on any topic.           │
  │                                                         │
  │ ## Inputs                                               │
  │ - topic: The subject of the post                        │
  │ - style: story, educational, or listicle                │
  │                                                         │
  │ ## Process                                              │
  │ 1. Load SKILL_BIBLE_linkedin_copywriting.md            │
  │ 2. Generate hook options                                │
  │ 3. Write full post with CTA                             │
  │                                                         │
  │ ## How to Run                                           │
  │ python3 execution/generate_linkedin_post.py --topic X   │
  └────────────────────────────────────────────────────────┘{Colors.END}
""")
    
    wait_for_enter()
    
    print_header("Step 6: Creating Workflows", "Creating a New Workflow")
    print_step_indicator(5, len(steps), steps)
    
    print(f"""  {Colors.BOLD}To Create a New Workflow:{Colors.END}
  
  {Colors.CYAN}Step 1: Create the Directive{Colors.END}
  
  Create a new file in directives/ folder:
  
    {Colors.GREEN}directives/my_custom_workflow.md{Colors.END}
  
  Use this template:
  
  {Colors.DIM}# My Custom Workflow
  
  ## What This Workflow Does
  [Describe in plain English]
  
  ## Inputs
  | Field | Required | Description |
  |-------|----------|-------------|
  | input1 | Yes | What this input is for |
  
  ## Process
  1. First step
  2. Second step
  3. Third step
  
  ## How to Run
  python3 execution/my_script.py --input1 "value"{Colors.END}
""")
    
    wait_for_enter()
    
    print_header("Step 6: Creating Workflows", "Creating the Script")
    print_step_indicator(5, len(steps), steps)
    
    print(f"""  {Colors.CYAN}Step 2: Create the Execution Script{Colors.END}
  
  Create a new Python file in execution/ folder:
  
    {Colors.GREEN}execution/my_custom_workflow.py{Colors.END}
  
  Use this template:
  
  {Colors.DIM}#!/usr/bin/env python3
  \"\"\"
  My Custom Workflow - [Description]
  \"\"\"
  
  import argparse
  import os
  from openai import OpenAI
  from dotenv import load_dotenv
  
  load_dotenv()
  
  def main():
      parser = argparse.ArgumentParser()
      parser.add_argument("--input1", required=True)
      parser.add_argument("--output", default=".tmp/output.md")
      args = parser.parse_args()
      
      # Your logic here
      client = OpenAI(
          api_key=os.getenv("OPENROUTER_API_KEY"),
          base_url="https://openrouter.ai/api/v1"
      )
      
      # Generate with AI...
      # Save to output file...
      
  if __name__ == "__main__":
      main(){Colors.END}
""")
    
    wait_for_enter()
    
    print_header("Step 6: Creating Workflows", "Using Skill Bibles")
    print_step_indicator(5, len(steps), steps)
    
    print(f"""  {Colors.CYAN}Step 3: Leverage Skill Bibles{Colors.END}
  
  Skill Bibles contain expert knowledge. Load them in your prompt:
  
  {Colors.DIM}# In your script:
  skill_bible = open("skills/SKILL_BIBLE_copywriting.md").read()
  
  prompt = f\"\"\"
  You are an expert copywriter.
  
  Use this knowledge base:
  {{skill_bible}}
  
  Now write [whatever you need]...
  \"\"\"{Colors.END}
  
  {Colors.BOLD}Available Skill Bibles:{Colors.END}
  
  • {Colors.GREEN}SKILL_BIBLE_vsl_writing_production.md{Colors.END} - VSL scripts
  • {Colors.GREEN}SKILL_BIBLE_cold_email_mastery.md{Colors.END} - Cold outreach
  • {Colors.GREEN}SKILL_BIBLE_funnel_copywriting.md{Colors.END} - Funnel copy
  • {Colors.GREEN}SKILL_BIBLE_agency_sales_system.md{Colors.END} - Sales
  • ... and 130+ more!
  
  {Colors.DIM}Run: ls skills/ to see all available Skill Bibles{Colors.END}
""")
    
    wait_for_enter()
    
    print_header("Step 6: Creating Workflows", "Quick Reference")
    print_step_indicator(5, len(steps), steps)
    
    print(f"""  {Colors.BOLD}Workflow Creation Cheat Sheet:{Colors.END}
  
  {Colors.CYAN}1. Plan your workflow{Colors.END}
     What inputs? What outputs? What steps?
  
  {Colors.CYAN}2. Create directive{Colors.END}
     directives/my_workflow.md
  
  {Colors.CYAN}3. Create script{Colors.END}
     execution/my_workflow.py
  
  {Colors.CYAN}4. Test it{Colors.END}
     python3 execution/my_workflow.py --help
     python3 execution/my_workflow.py --input "test"
  
  {Colors.CYAN}5. Use it!{Colors.END}
     Now it's part of your system forever
  
  
  {Colors.BOLD}Pro Tips:{Colors.END}
  
  • Look at existing scripts for patterns
  • Always add --help support (use argparse)
  • Save outputs to .tmp/ or client folders
  • Load relevant Skill Bibles for better results
""")
    
    wait_for_enter()


# ═══════════════════════════════════════════════════════════════
# STEP 7: COMPLETION
# ═══════════════════════════════════════════════════════════════

def step_complete():
    """Show completion and next steps."""
    steps = ["API Keys", "Agency Profile", "Add Clients", "Learn the System", "First Workflow", "Create Workflows", "Complete!"]
    
    print_header("🎉 Setup Complete!", "You're ready to go!")
    print_step_indicator(6, len(steps), steps)
    
    directives_count = len(list((BASE_DIR / "directives").glob("*.md")))
    scripts_count = len(list((BASE_DIR / "execution").glob("*.py")))
    skills_count = len(list((BASE_DIR / "skills").glob("*.md")))
    clients_count = len(list(CLIENTS_DIR.iterdir())) if CLIENTS_DIR.exists() else 0
    
    print(f"""  {Colors.GREEN}{'═' * 56}{Colors.END}
  {Colors.GREEN}  Congratulations! Your AI Agency OS is ready.{Colors.END}
  {Colors.GREEN}{'═' * 56}{Colors.END}
  
  {Colors.BOLD}Your System:{Colors.END}
  • {directives_count} workflows available
  • {scripts_count} execution scripts  
  • {skills_count} skill bibles (expert knowledge)
  • {clients_count} clients configured
  
  
  {Colors.BOLD}Quick Commands:{Colors.END}
  
  {Colors.CYAN}python3 run.py{Colors.END}
      Launch the main interface (start here!)
  
  {Colors.CYAN}python3 run.py --help{Colors.END}
      See all available commands
  
  {Colors.CYAN}python3 execution/[script].py --help{Colors.END}
      Get help for any specific workflow
  
  
  {Colors.BOLD}Useful Files:{Colors.END}
  
  • {Colors.DIM}.env{Colors.END} - Your API keys (edit to add more)
  • {Colors.DIM}context/agency_profile.json{Colors.END} - Your agency info
  • {Colors.DIM}clients/{Colors.END} - Client folders and outputs
  • {Colors.DIM}.tmp/{Colors.END} - Temporary outputs
  
  
  {Colors.BOLD}Get Help:{Colors.END}
  
  • Read {Colors.CYAN}QUICKSTART.md{Colors.END} for common workflows
  • Check {Colors.CYAN}directives/{Colors.END} folder for all available SOPs
  • Look at {Colors.CYAN}skills/{Colors.END} for expert knowledge you can use
""")
    
    print(f"\n  {Colors.BOLD}Ready to start?{Colors.END}")
    print(f"  Run: {Colors.CYAN}python3 run.py{Colors.END}\n")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Run the complete setup wizard."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AIAA Agentic OS - Setup Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 wizard.py              Run the full setup wizard
  python3 wizard.py --add-client Add a new client interactively
  python3 wizard.py --api-keys   Configure API keys only
  python3 wizard.py --agency     Update agency profile only
        """
    )
    parser.add_argument('--add-client', action='store_true', 
                        help='Add a new client interactively')
    parser.add_argument('--api-keys', action='store_true',
                        help='Configure API keys only')
    parser.add_argument('--agency', action='store_true',
                        help='Update agency profile only')
    parser.add_argument('--version', action='version', version='AIAA Agentic OS Wizard v2.0')
    
    args = parser.parse_args()
    
    load_env()
    
    # Handle specific commands
    if args.add_client:
        print_header("Add New Client", "Create a comprehensive client profile")
        
        # Count existing clients
        existing_clients = list(CLIENTS_DIR.iterdir()) if CLIENTS_DIR.exists() else []
        client_num = len(existing_clients) + 1
        
        client = add_single_client(client_num, show_header=False)
        
        print(f"\n  {Colors.GREEN}Client '{client['name']}' added successfully!{Colors.END}")
        print(f"  {Colors.DIM}Folder: clients/{client['slug']}/{Colors.END}\n")
        return
    
    if args.api_keys:
        step_api_keys()
        return
    
    if args.agency:
        step_agency_profile()
        return
    
    # Default: Full wizard flow
    # Check if already set up
    agency_profile = CONTEXT_DIR / "agency_profile.json"
    if agency_profile.exists():
        print_header("AIAA Agentic OS", "Setup Wizard")
        print(f"  {Colors.YELLOW}It looks like you've already run the setup wizard.{Colors.END}\n")
        
        choice = prompt_choice("What would you like to do?", [
            "Run full setup again (overwrites existing)",
            "Just update API keys",
            "Add more clients",
            "Exit"
        ])
        
        if choice == 3:
            print(f"\n  {Colors.DIM}Goodbye! Run 'python3 run.py' to use the system.{Colors.END}\n")
            return
        elif choice == 1:
            step_api_keys()
            return
        elif choice == 2:
            step_add_clients()
            return
        # choice == 0 continues with full setup
    
    # Run full wizard
    step_api_keys()
    agency = step_agency_profile()
    step_add_clients()
    step_learn_system()
    step_first_workflow(agency)
    step_create_workflows()
    step_complete()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.YELLOW}Setup cancelled. Run 'python3 wizard.py' to continue later.{Colors.END}\n")
        sys.exit(0)
