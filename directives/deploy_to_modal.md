# Deploy Workflow to Modal AI

## What This Workflow Is
Deploys any existing agentic workflow as a separate Modal AI app with auto-detected tools and webhook endpoint.

## What It Does
1. Parses the target directive to extract requirements
2. Identifies required execution scripts and integrations
3. Generates a dedicated Modal app for the workflow
4. Deploys to Modal cloud
5. Returns the webhook URL

## Prerequisites

### Required Setup
```bash
pip install modal
python3 -m modal setup
```

### Required Environment Variables (in .env)
```
ANTHROPIC_API_KEY=your_key
OPENROUTER_API_KEY=your_key  # Optional, for OpenRouter models
```

### Modal Secrets (configure in Modal dashboard)
- `anthropic-secret` - ANTHROPIC_API_KEY
- `env-vars` - Other environment variables
- `slack-webhook` - SLACK_WEBHOOK_URL (optional)
- `google-token` - GOOGLE_TOKEN_JSON (optional, for Google integrations)

## How to Run
```bash
# Deploy a specific workflow
python3 execution/deploy_to_modal.py --directive vsl_funnel_writer

# Deploy with custom app name
python3 execution/deploy_to_modal.py --directive vsl_funnel_writer --app-name my-vsl-app

# List all deployable directives
python3 execution/deploy_to_modal.py --list

# Dry run (generate without deploying)
python3 execution/deploy_to_modal.py --directive vsl_funnel_writer --dry-run
```

## Inputs
- **directive**: Name of the directive to deploy (without .md extension)
- **app-name**: Optional custom Modal app name (defaults to directive name)
- **dry-run**: Generate the Modal app file without deploying

## Auto-Detection Logic

The script parses directives to detect:

### 1. Execution Scripts
Looks for patterns like:
- `python3 execution/script_name.py`
- References to `execution/*.py` files
- "How to Run" sections

### 2. Integrations/Tools
Detects from "Integrations Required" section and content:
- `Slack` → slack_notify tool
- `Google Docs` → google_docs tool
- `Google Sheets` → read_sheet, update_sheet tools
- `Email/Gmail` → send_email tool
- `OpenRouter/Claude/GPT` → LLM calls

### 3. Input Schema
Parses "Inputs" section to build webhook payload schema

## Output
- Modal app file: `execution/modal_apps/{directive}_modal.py`
- Deployed webhook URL: `https://{workspace}--{app-name}-webhook.modal.run`

## Edge Cases
- Directive not found → Error with available directives list
- Missing Modal setup → Prompts to run `python3 -m modal setup`
- Missing secrets → Lists required secrets to configure

## Process Flow
1. Load and parse directive markdown
2. Extract execution scripts, tools, inputs
3. Generate Modal app from template
4. Save to `execution/modal_apps/`
5. Run `modal deploy`
6. Return webhook URL
