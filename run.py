#!/usr/bin/env python3
"""
AIAA Agentic OS - Main Interface
Your daily driver for running workflows.

Usage:
    python3 run.py              # Interactive menu
    python3 run.py --help       # See all options
    python3 run.py content      # Jump to content creation
    python3 run.py research     # Jump to research
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Colors
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
EXECUTION_DIR = BASE_DIR / "execution"
TMP_DIR = BASE_DIR / ".tmp"

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def load_env():
    """Load environment variables from .env."""
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().split('\n'):
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def load_agency():
    """Load agency profile."""
    profile = CONTEXT_DIR / "agency_profile.json"
    if profile.exists():
        return json.loads(profile.read_text())
    return None

def load_clients():
    """Load all client profiles."""
    clients = []
    if CLIENTS_DIR.exists():
        for client_dir in CLIENTS_DIR.iterdir():
            if client_dir.is_dir():
                context_file = client_dir / "context.json"
                if context_file.exists():
                    client = json.loads(context_file.read_text())
                    client['_folder'] = client_dir.name
                    clients.append(client)
    return clients

def print_header(agency_name=None):
    """Print main header."""
    clear_screen()
    name = agency_name or "Your Agency"
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║{Colors.END}                                                              {Colors.CYAN}║
║           {Colors.BOLD}AIAA Agentic OS{Colors.END}{Colors.CYAN}                                    ║
║           {Colors.END}{name[:44].center(44)}{Colors.CYAN}             ║
║{Colors.END}                                                              {Colors.CYAN}║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
""")

def prompt(question, default=None):
    """Get user input."""
    if default:
        response = input(f"  {Colors.CYAN}→{Colors.END} {question} [{default}]: ").strip()
        return response if response else default
    return input(f"  {Colors.CYAN}→{Colors.END} {question}: ").strip()

def prompt_choice(options, title=None, allow_back=True):
    """Present numbered menu."""
    if title:
        print(f"  {Colors.BOLD}{title}{Colors.END}\n")
    
    for i, option in enumerate(options, 1):
        print(f"    {Colors.BOLD}{i}.{Colors.END} {option}")
    
    if allow_back:
        print(f"    {Colors.DIM}0. Back{Colors.END}")
    
    print()
    
    while True:
        try:
            choice = input(f"  Enter choice: ").strip()
            if allow_back and choice == "0":
                return None
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice - 1
        except ValueError:
            pass
        print(f"    {Colors.RED}Please enter 1-{len(options)}{Colors.END}")

def run_script(script_name, args_dict, output_dir=None):
    """Run an execution script with given arguments."""
    script_path = EXECUTION_DIR / script_name
    
    if not script_path.exists():
        print(f"  {Colors.RED}Script not found: {script_name}{Colors.END}")
        return False
    
    # Build command
    cmd = [sys.executable, str(script_path)]
    
    for key, value in args_dict.items():
        if value:
            cmd.extend([f"--{key}", str(value)])
    
    # Set output directory if specified
    if output_dir:
        cmd.extend(["--output", str(output_dir)])
    
    print(f"\n  {Colors.CYAN}⏳ Running...{Colors.END}\n")
    
    try:
        result = subprocess.run(cmd, timeout=300)
        
        if result.returncode == 0:
            print(f"\n  {Colors.GREEN}✓ Complete!{Colors.END}")
            return True
        else:
            print(f"\n  {Colors.YELLOW}Finished with warnings{Colors.END}")
            return True
    except subprocess.TimeoutExpired:
        print(f"\n  {Colors.YELLOW}Still running... check .tmp/ for output{Colors.END}")
        return False
    except Exception as e:
        print(f"\n  {Colors.RED}Error: {e}{Colors.END}")
        return False


# ═══════════════════════════════════════════════════════════════
# CONTENT CREATION MENU
# ═══════════════════════════════════════════════════════════════

def menu_content(agency, clients):
    """Content creation submenu."""
    while True:
        print_header(agency.get('name') if agency else None)
        
        print(f"  {Colors.BOLD}📝 CONTENT CREATION{Colors.END}\n")
        
        options = [
            "LinkedIn Post",
            "Twitter/X Thread", 
            "Blog Post",
            "Instagram Reel Script",
            "YouTube Script",
            "Newsletter",
            "Press Release",
            "Carousel Post",
        ]
        
        choice = prompt_choice(options, "What would you like to create?")
        
        if choice is None:
            return
        
        print_header(agency.get('name') if agency else None)
        
        if choice == 0:  # LinkedIn
            print(f"  {Colors.BOLD}LinkedIn Post Generator{Colors.END}\n")
            topic = prompt("What topic?")
            style = prompt("Style (story/educational/listicle)", "story")
            
            run_script("generate_linkedin_post.py", {
                "topic": topic,
                "style": style,
            })
            
        elif choice == 1:  # Twitter
            print(f"  {Colors.BOLD}Twitter Thread Generator{Colors.END}\n")
            topic = prompt("What topic?")
            
            run_script("generate_twitter_thread.py", {
                "topic": topic,
            })
            
        elif choice == 2:  # Blog
            print(f"  {Colors.BOLD}Blog Post Generator{Colors.END}\n")
            topic = prompt("What topic?")
            length = prompt("Word count", "1500")
            
            run_script("generate_blog_post.py", {
                "topic": topic,
                "length": length,
            })
            
        elif choice == 3:  # Instagram
            print(f"  {Colors.BOLD}Instagram Reel Script{Colors.END}\n")
            topic = prompt("What topic?")
            
            run_script("generate_instagram_reel.py", {
                "topic": topic,
            })
            
        elif choice == 4:  # YouTube
            print(f"  {Colors.BOLD}YouTube Script Generator{Colors.END}\n")
            topic = prompt("Video topic?")
            video_type = prompt("Type (educational/story/tutorial)", "educational")
            
            run_script("generate_youtube_script.py", {
                "topic": topic,
                "type": video_type,
            })
            
        elif choice == 5:  # Newsletter
            print(f"  {Colors.BOLD}Newsletter Generator{Colors.END}\n")
            theme = prompt("Newsletter theme/topic?")
            
            run_script("generate_newsletter.py", {
                "theme": theme,
            })
            
        elif choice == 6:  # Press Release
            print(f"  {Colors.BOLD}Press Release Generator{Colors.END}\n")
            headline = prompt("What's the announcement?")
            company = prompt("Company name", agency.get('name', ''))
            
            run_script("generate_press_release.py", {
                "headline": headline,
                "company": company,
            })
            
        elif choice == 7:  # Carousel
            print(f"  {Colors.BOLD}Carousel Post Generator{Colors.END}\n")
            topic = prompt("What topic?")
            slides = prompt("Number of slides", "8")
            
            run_script("generate_carousel.py", {
                "topic": topic,
                "slides": slides,
            })
        
        input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# SALES COPY MENU
# ═══════════════════════════════════════════════════════════════

def menu_sales_copy(agency, clients):
    """Sales copy submenu."""
    while True:
        print_header(agency.get('name') if agency else None)
        
        print(f"  {Colors.BOLD}💰 SALES COPY{Colors.END}\n")
        
        options = [
            "VSL Script (Video Sales Letter)",
            "Sales Page / Landing Page",
            "Email Sequence",
            "Cold Email Campaign",
            "Case Study",
            "Ad Creative",
            "Complete VSL Funnel (all-in-one)",
        ]
        
        choice = prompt_choice(options, "What would you like to create?")
        
        if choice is None:
            return
        
        print_header(agency.get('name') if agency else None)
        
        if choice == 0:  # VSL
            print(f"  {Colors.BOLD}VSL Script Generator{Colors.END}\n")
            product = prompt("Product/service name?")
            audience = prompt("Target audience?")
            price = prompt("Price point?", "$997")
            
            run_script("generate_vsl_script.py", {
                "product": product,
                "audience": audience,
                "price": price,
            })
            
        elif choice == 1:  # Sales Page
            print(f"  {Colors.BOLD}Sales Page Generator{Colors.END}\n")
            product = prompt("Product/service?")
            audience = prompt("Target audience?")
            
            run_script("generate_sales_page.py", {
                "product": product,
                "audience": audience,
            })
            
        elif choice == 2:  # Email Sequence
            print(f"  {Colors.BOLD}Email Sequence Generator{Colors.END}\n")
            product = prompt("Product/service?")
            sequence_type = prompt("Type (welcome/nurture/sales)", "welcome")
            
            run_script("generate_email_sequence.py", {
                "product": product,
                "type": sequence_type,
            })
            
        elif choice == 3:  # Cold Email
            print(f"  {Colors.BOLD}Cold Email Generator{Colors.END}\n")
            print(f"  {Colors.DIM}Note: For personalized emails, you need a leads file.{Colors.END}\n")
            
            product = prompt("What are you selling?")
            sender = prompt("Your name?", agency.get('name', ''))
            
            # Create sample lead for demo
            sample_lead = [{"name": "John Smith", "company": "TechCorp", "email": "john@example.com"}]
            leads_file = TMP_DIR / "sample_lead.json"
            TMP_DIR.mkdir(exist_ok=True)
            leads_file.write_text(json.dumps(sample_lead))
            
            run_script("write_cold_emails.py", {
                "leads": str(leads_file),
                "sender_name": sender,
                "product": product,
                "skip_research": "",
            })
            
        elif choice == 4:  # Case Study
            print(f"  {Colors.BOLD}Case Study Generator{Colors.END}\n")
            client_name = prompt("Client name?")
            challenge = prompt("What challenge did they have?")
            solution = prompt("What solution did you provide?")
            results = prompt("What results did they get?")
            
            run_script("generate_case_study.py", {
                "client": client_name,
                "challenge": challenge,
                "solution": solution,
                "results": results,
            })
            
        elif choice == 5:  # Ad Creative
            print(f"  {Colors.BOLD}Ad Creative Generator{Colors.END}\n")
            product = prompt("Product/service?")
            platform = prompt("Platform (facebook/google/linkedin)", "facebook")
            audience = prompt("Target audience?")
            
            run_script("generate_ad_creative.py", {
                "product": product,
                "platform": platform,
                "audience": audience,
            })
            
        elif choice == 6:  # Complete Funnel
            print(f"  {Colors.BOLD}Complete VSL Funnel Generator{Colors.END}\n")
            print(f"  {Colors.DIM}This creates: VSL script + Sales page + Email sequence{Colors.END}\n")
            
            product = prompt("Product/service name?")
            audience = prompt("Target audience?")
            price = prompt("Price point?", "$997")
            
            run_script("generate_vsl_funnel.py", {
                "product": product,
                "audience": audience,
                "price": price,
            })
        
        input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# RESEARCH MENU  
# ═══════════════════════════════════════════════════════════════

def menu_research(agency, clients):
    """Research submenu."""
    while True:
        print_header(agency.get('name') if agency else None)
        
        print(f"  {Colors.BOLD}🔍 RESEARCH{Colors.END}\n")
        
        options = [
            "Company Research",
            "Competitor Analysis",
            "Prospect Deep-Dive",
            "Market Research",
        ]
        
        choice = prompt_choice(options, "What would you like to research?")
        
        if choice is None:
            return
        
        print_header(agency.get('name') if agency else None)
        
        if choice == 0:  # Company Research
            print(f"  {Colors.BOLD}Company Research{Colors.END}\n")
            company = prompt("Company name?")
            website = prompt("Website URL?")
            
            TMP_DIR.mkdir(exist_ok=True)
            output_file = TMP_DIR / f"research_{company.lower().replace(' ', '_')}.json"
            
            run_script("research_company_offer.py", {
                "company": company,
                "website": website,
                "offer": "their main product/service",
                "output": str(output_file),
            })
            
        elif choice == 1:  # Competitor
            print(f"  {Colors.BOLD}Competitor Analysis{Colors.END}\n")
            competitor = prompt("Competitor name?")
            website = prompt("Their website?")
            
            run_script("research_company_offer.py", {
                "company": competitor,
                "website": website,
                "offer": "their offering",
                "output": str(TMP_DIR / f"competitor_{competitor.lower().replace(' ', '_')}.json"),
            })
            
        elif choice == 2:  # Prospect
            print(f"  {Colors.BOLD}Prospect Deep-Dive{Colors.END}\n")
            name = prompt("Person's name?")
            company = prompt("Their company?")
            linkedin = prompt("LinkedIn URL?", required=False)
            
            run_script("research_prospect_deep.py", {
                "name": name,
                "company": company,
                "linkedin": linkedin,
            })
            
        elif choice == 3:  # Market
            print(f"  {Colors.BOLD}Market Research{Colors.END}\n")
            industry = prompt("Industry/market to research?")
            focus = prompt("Specific focus? (trends/competitors/opportunities)", "trends")
            
            run_script("research_market_deep.py", {
                "business": industry,
                "industry": industry,
                "audience": "businesses in this space",
            })
        
        input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# LEAD GENERATION MENU
# ═══════════════════════════════════════════════════════════════

def menu_leads(agency, clients):
    """Lead generation submenu."""
    while True:
        print_header(agency.get('name') if agency else None)
        
        print(f"  {Colors.BOLD}📊 LEAD GENERATION{Colors.END}\n")
        
        # Check if Apify is configured
        if not os.environ.get('APIFY_API_TOKEN'):
            print(f"  {Colors.YELLOW}⚠ Apify API token not configured{Colors.END}")
            print(f"  {Colors.DIM}Add APIFY_API_TOKEN to .env to enable lead scraping{Colors.END}\n")
        
        options = [
            "Google Maps Scraper (local businesses)",
            "LinkedIn Profile Scraper",
            "Google Search Scraper",
            "Deduplicate Leads",
            "Validate Emails",
        ]
        
        choice = prompt_choice(options, "What would you like to do?")
        
        if choice is None:
            return
        
        print_header(agency.get('name') if agency else None)
        
        if choice == 0:  # Google Maps
            print(f"  {Colors.BOLD}Google Maps Scraper{Colors.END}\n")
            search = prompt("Search query? (e.g., 'plumbers in Austin TX')")
            limit = prompt("How many results?", "25")
            
            run_script("scrape_google_maps.py", {
                "search": search,
                "limit": limit,
            })
            
        elif choice == 1:  # LinkedIn
            print(f"  {Colors.BOLD}LinkedIn Scraper{Colors.END}\n")
            titles = prompt("Job titles? (comma-separated, e.g., 'CEO,Founder')")
            locations = prompt("Locations?", "United States")
            limit = prompt("How many profiles?", "50")
            
            run_script("scrape_linkedin_apify.py", {
                "titles": titles,
                "locations": locations,
                "max_items": limit,
            })
            
        elif choice == 2:  # Google Search
            print(f"  {Colors.BOLD}Google Search Scraper{Colors.END}\n")
            query = prompt("Search query?")
            limit = prompt("How many results?", "20")
            
            run_script("scrape_serp.py", {
                "query": query,
                "limit": limit,
            })
            
        elif choice == 3:  # Dedupe
            print(f"  {Colors.BOLD}Deduplicate Leads{Colors.END}\n")
            input_file = prompt("Path to leads file (CSV or JSON)?")
            
            run_script("dedupe_leads.py", {
                "input": input_file,
            })
            
        elif choice == 4:  # Validate
            print(f"  {Colors.BOLD}Email Validator{Colors.END}\n")
            input_file = prompt("Path to file with emails?")
            
            run_script("validate_emails.py", {
                "input": input_file,
            })
        
        input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# CLIENT WORK MENU
# ═══════════════════════════════════════════════════════════════

def menu_client_work(agency, clients):
    """Client-specific work submenu."""
    while True:
        print_header(agency.get('name') if agency else None)
        
        print(f"  {Colors.BOLD}👥 CLIENT WORK{Colors.END}\n")
        
        if not clients:
            print(f"  {Colors.DIM}No clients configured yet.{Colors.END}")
            print(f"  {Colors.DIM}Ask Claude Code to help you add a client.{Colors.END}\n")
            input(f"  {Colors.DIM}Press Enter to go back...{Colors.END}")
            return
        
        # Show client selection
        client_options = [f"{c['name']} ({c.get('industry', 'N/A')})" for c in clients]
        client_options.append("General (no specific client)")
        
        client_choice = prompt_choice(client_options, "Select a client:")
        
        if client_choice is None:
            return
        
        if client_choice < len(clients):
            selected_client = clients[client_choice]
            output_dir = CLIENTS_DIR / selected_client['_folder'] / "outputs"
        else:
            selected_client = None
            output_dir = TMP_DIR
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Work type selection
        print_header(agency.get('name') if agency else None)
        
        client_name = selected_client['name'] if selected_client else "General"
        print(f"  {Colors.BOLD}Working on: {client_name}{Colors.END}\n")
        
        work_options = [
            "Monthly Report",
            "Quarterly Business Review (QBR)",
            "Case Study",
            "Content Calendar",
            "Campaign Report",
        ]
        
        work_choice = prompt_choice(work_options, "What do you need?")
        
        if work_choice is None:
            continue
        
        print_header(agency.get('name') if agency else None)
        
        if work_choice == 0:  # Monthly Report
            print(f"  {Colors.BOLD}Monthly Report for {client_name}{Colors.END}\n")
            metrics = prompt("Key metrics (JSON or describe)?", '{"leads": 100, "calls": 20}')
            
            run_script("generate_monthly_report.py", {
                "client": client_name,
                "metrics": metrics,
                "output": str(output_dir / "monthly_report.md"),
            })
            
        elif work_choice == 1:  # QBR
            print(f"  {Colors.BOLD}QBR for {client_name}{Colors.END}\n")
            metrics = prompt("Quarterly metrics?", '{"revenue": "$50k", "growth": "25%"}')
            
            run_script("generate_qbr.py", {
                "client": client_name,
                "metrics": metrics,
                "output": str(output_dir / "qbr.md"),
            })
            
        elif work_choice == 2:  # Case Study
            print(f"  {Colors.BOLD}Case Study for {client_name}{Colors.END}\n")
            challenge = prompt("What was their challenge?")
            solution = prompt("What solution did you provide?")
            results = prompt("What results did they achieve?")
            
            run_script("generate_case_study.py", {
                "client": client_name,
                "challenge": challenge,
                "solution": solution,
                "results": results,
                "output": str(output_dir / "case_study.md"),
            })
            
        elif work_choice == 3:  # Content Calendar
            print(f"  {Colors.BOLD}Content Calendar for {client_name}{Colors.END}\n")
            weeks = prompt("How many weeks?", "4")
            platforms = prompt("Platforms? (linkedin,twitter,blog)", "linkedin,twitter")
            
            run_script("generate_content_calendar.py", {
                "client": client_name,
                "weeks": weeks,
                "platforms": platforms,
                "output": str(output_dir / "content_calendar.md"),
            })
            
        elif work_choice == 4:  # Campaign Report
            print(f"  {Colors.BOLD}Campaign Report for {client_name}{Colors.END}\n")
            campaign = prompt("Campaign name?")
            metrics = prompt("Campaign metrics?", '{"sent": 1000, "opened": 250, "clicked": 50}')
            
            run_script("generate_campaign_report.py", {
                "client": client_name,
                "campaign": campaign,
                "metrics": metrics,
                "output": str(output_dir / "campaign_report.md"),
            })
        
        input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# ALL WORKFLOWS MENU
# ═══════════════════════════════════════════════════════════════

def menu_all_workflows():
    """List all available workflows."""
    print_header()
    
    print(f"  {Colors.BOLD}📋 ALL WORKFLOWS{Colors.END}\n")
    
    # List all scripts
    scripts = sorted(EXECUTION_DIR.glob("*.py"))
    
    print(f"  {Colors.DIM}Available execution scripts ({len(scripts)} total):{Colors.END}\n")
    
    # Group by prefix
    groups = {}
    for script in scripts:
        name = script.stem
        if name.startswith('generate_'):
            group = 'Generate'
        elif name.startswith('scrape_'):
            group = 'Scrape'
        elif name.startswith('research_'):
            group = 'Research'
        elif name.startswith('create_'):
            group = 'Create'
        else:
            group = 'Other'
        
        if group not in groups:
            groups[group] = []
        groups[group].append(name)
    
    for group, scripts_list in sorted(groups.items()):
        print(f"  {Colors.CYAN}{group}:{Colors.END}")
        for name in sorted(scripts_list)[:10]:
            print(f"    • {name}")
        if len(scripts_list) > 10:
            print(f"    {Colors.DIM}... and {len(scripts_list) - 10} more{Colors.END}")
        print()
    
    print(f"  {Colors.BOLD}To run any script:{Colors.END}")
    print(f"    python3 execution/<script>.py --help\n")
    
    input(f"  {Colors.DIM}Press Enter to go back...{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════════

def main_menu():
    """Main interactive menu."""
    load_env()
    agency = load_agency()
    clients = load_clients()
    
    # Check if setup has been run
    if not agency:
        print_header()
        print(f"  {Colors.YELLOW}Welcome! It looks like you need to set up your agency profile.{Colors.END}\n")
        print(f"  Ask Claude Code: {Colors.CYAN}\"Help me set up my agency profile\"{Colors.END}")
        print(f"  {Colors.DIM}Claude will create your context files and configure the system.{Colors.END}\n")
        return
    
    while True:
        print_header(agency.get('name'))
        
        # Quick stats
        print(f"  {Colors.DIM}Clients: {len(clients)} | Workflows: 115 | Skill Bibles: 138{Colors.END}\n")
        
        options = [
            f"{Colors.GREEN}📝{Colors.END} Content Creation (posts, blogs, scripts)",
            f"{Colors.GREEN}💰{Colors.END} Sales Copy (VSLs, emails, landing pages)",
            f"{Colors.GREEN}🔍{Colors.END} Research (companies, markets, prospects)",
            f"{Colors.GREEN}📊{Colors.END} Lead Generation (scrape & enrich)",
            f"{Colors.GREEN}👥{Colors.END} Client Work (reports, case studies)",
            f"{Colors.DIM}📋{Colors.END} All Workflows (see everything)",
        ]

        choice = prompt_choice(options, "What would you like to do?", allow_back=False)

        if choice is None:
            continue
        elif choice == 0:
            menu_content(agency, clients)
        elif choice == 1:
            menu_sales_copy(agency, clients)
        elif choice == 2:
            menu_research(agency, clients)
        elif choice == 3:
            menu_leads(agency, clients)
        elif choice == 4:
            menu_client_work(agency, clients)
        elif choice == 5:
            menu_all_workflows()


def main():
    """Entry point with argument handling."""
    parser = argparse.ArgumentParser(
        description="AIAA Agentic OS - Your AI Agency Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run.py              Launch interactive menu
  python3 run.py --add-client Add a new client
  python3 run.py --list       List all workflows
        """
    )
    
    parser.add_argument('--add-client', action='store_true', help='Add a new client')
    parser.add_argument('--list', action='store_true', help='List all workflows')
    parser.add_argument('--version', action='store_true', help='Show version')
    
    args = parser.parse_args()
    
    if args.version:
        print("AIAA Agentic OS v1.0.0")
        return
    
    if args.list:
        menu_all_workflows()
        return
    
    if args.add_client:
        print("To add a client, ask Claude Code: \"Help me add a new client\"")
        return
    
    # Default: run interactive menu
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.DIM}Goodbye!{Colors.END}\n")


if __name__ == "__main__":
    main()
