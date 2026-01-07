#!/usr/bin/env python3
"""
AIAA Agentic OS - Installer
Run this once to set up your system.

Usage:
    python3 install.py
"""

import subprocess
import sys
import os
from pathlib import Path

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

def print_header():
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           {Colors.BOLD}AIAA Agentic OS - Installer{Colors.END}{Colors.CYAN}                      ║
║                                                              ║
║           Your AI-Powered Agency Operating System            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
""")

def print_step(step_num, total, message):
    print(f"\n{Colors.BLUE}[{step_num}/{total}]{Colors.END} {Colors.BOLD}{message}{Colors.END}")

def print_success(message):
    print(f"  {Colors.GREEN}✓{Colors.END} {message}")

def print_error(message):
    print(f"  {Colors.RED}✗{Colors.END} {message}")

def print_info(message):
    print(f"  {Colors.CYAN}→{Colors.END} {message}")

def check_python_version():
    """Ensure Python 3.10+ is installed."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required. You have {version.major}.{version.minor}")
        print_info("Download from: https://python.org/downloads")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required Python packages."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False
    
    print_info("Installing packages (this may take a minute)...")
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print_success("All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install packages")
        print_info(f"Try manually: pip install -r {requirements_file}")
        return False

def create_directories():
    """Create required directory structure."""
    base = Path(__file__).parent
    
    directories = [
        base / "context",
        base / "clients",
        base / ".tmp",
    ]
    
    for dir_path in directories:
        dir_path.mkdir(exist_ok=True)
    
    print_success("Directory structure created")
    return True

def check_env_file():
    """Check if .env exists, create template if not."""
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if env_file.exists():
        print_success(".env file found")
        return True
    
    # Create .env template
    template = """# AIAA Agentic OS - API Keys
# Fill these in during the setup wizard, or manually here

# Required: Powers the AI (get free key at https://openrouter.ai/keys)
OPENROUTER_API_KEY=

# Optional: For market research (https://perplexity.ai)
PERPLEXITY_API_KEY=

# Optional: For Google Docs integration
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# Optional: For Slack notifications
SLACK_WEBHOOK_URL=

# Optional: For lead scraping (https://apify.com)
APIFY_API_TOKEN=
"""
    
    env_file.write_text(template)
    print_success(".env template created")
    print_info("You'll add your API keys in the setup wizard")
    return True

def verify_core_files():
    """Verify that core system files exist."""
    base = Path(__file__).parent
    
    required = {
        "directives": "Workflow definitions (SOPs)",
        "execution": "Python scripts",
        "skills": "Skill Bibles (AI knowledge)",
    }
    
    all_present = True
    for folder, description in required.items():
        path = base / folder
        if path.exists() and any(path.iterdir()):
            count = len(list(path.glob("*")))
            print_success(f"{folder}/ - {count} {description}")
        else:
            print_error(f"{folder}/ missing or empty")
            all_present = False
    
    return all_present

def main():
    print_header()
    
    print(f"{Colors.YELLOW}This installer will:{Colors.END}")
    print("  • Check your Python version")
    print("  • Install required packages")
    print("  • Create necessary folders")
    print("  • Prepare configuration files")
    print()
    
    input(f"Press {Colors.BOLD}Enter{Colors.END} to continue (or Ctrl+C to cancel)...")
    
    total_steps = 5
    success = True
    
    # Step 1: Check Python
    print_step(1, total_steps, "Checking Python version")
    if not check_python_version():
        success = False
    
    # Step 2: Install dependencies
    print_step(2, total_steps, "Installing dependencies")
    if not install_dependencies():
        success = False
    
    # Step 3: Create directories
    print_step(3, total_steps, "Creating directories")
    if not create_directories():
        success = False
    
    # Step 4: Setup .env
    print_step(4, total_steps, "Preparing configuration")
    if not check_env_file():
        success = False
    
    # Step 5: Verify core files
    print_step(5, total_steps, "Verifying system files")
    if not verify_core_files():
        success = False
    
    # Final summary
    print()
    if success:
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}  ✓ Installation complete!{Colors.END}")
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        print()
        print(f"  {Colors.BOLD}Next step:{Colors.END} Run the setup wizard to configure your agency:")
        print()
        print(f"    {Colors.CYAN}python3 wizard.py{Colors.END}")
        print()
    else:
        print(f"{Colors.RED}{'═' * 60}{Colors.END}")
        print(f"{Colors.RED}  ✗ Installation had errors. Please fix them and try again.{Colors.END}")
        print(f"{Colors.RED}{'═' * 60}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Installation cancelled.{Colors.END}")
        sys.exit(0)
