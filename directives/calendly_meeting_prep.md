# Calendly Meeting Prep Webhook

## What This Workflow Is
Automated meeting preparation that triggers when someone books a meeting on Calendly. Researches the prospect, creates a detailed prep document, and alerts you via Slack.

## What It Does
1. Receives Calendly webhook when meeting is booked
2. Fetches full event details (name, time) from Calendly API
3. Sends immediate Slack alert with prospect details and meeting time
4. Researches prospect and their company (via Perplexity Sonar)
5. Looks up LinkedIn profile information
6. Generates personalized talking points (via Claude)
7. Creates formatted Google Doc with full research (using service account)
8. Moves doc to shared Google Drive folder
9. Sends second Slack message with summary + doc link

## Prerequisites

### Required API Keys (in .env)
```
CALENDLY_API_KEY=your_calendly_token
OPENROUTER_API_KEY=your_openrouter_key
PERPLEXITY_API_KEY=your_perplexity_key
SLACK_WEBHOOK_URL=your_slack_webhook
```

### Required Modal Secrets
```bash
modal secret create calendly-secret CALENDLY_API_KEY="your_key"
modal secret create openrouter-secret OPENROUTER_API_KEY="your_key"
modal secret create perplexity-secret PERPLEXITY_API_KEY="your_key"
modal secret create slack-webhook SLACK_WEBHOOK_URL="your_url"
modal secret create google-service-account GOOGLE_SERVICE_ACCOUNT_JSON="$(cat service-account.json)"
```

### Google Service Account Setup
1. Create service account in Google Cloud Console
2. Enable Google Docs API and Google Drive API
3. Download JSON key file
4. Create Modal secret with the JSON
5. Share a Google Drive folder with the service account email

## How to Run

### Local Test
```bash
python3 execution/calendly_meeting_prep.py --test --email "prospect@company.com" --name "John Smith" --company "Acme Corp"
```

### Deploy to Modal
```bash
modal deploy execution/calendly_meeting_prep.py
```

### Register Webhook with Calendly
```python
import requests

resp = requests.post(
    'https://api.calendly.com/webhook_subscriptions',
    headers={'Authorization': f'Bearer {CALENDLY_API_KEY}'},
    json={
        'url': 'https://your-workspace--calendly-meeting-prep-webhook.modal.run',
        'events': ['invitee.created'],
        'organization': 'https://api.calendly.com/organizations/YOUR_ORG_ID',
        'user': 'https://api.calendly.com/users/YOUR_USER_ID',
        'scope': 'user'
    }
)
```

## Deployed Endpoints
- **Webhook:** `https://lucas-37998--calendly-meeting-prep-webhook.modal.run`
- **Health:** `https://lucas-37998--calendly-meeting-prep-health.modal.run`

## Webhook Payload (from Calendly)
```json
{
  "event": "invitee.created",
  "payload": {
    "name": "John Smith",
    "email": "john@acmecorp.com",
    "scheduled_event": "https://api.calendly.com/scheduled_events/EVENT_UUID",
    "event_type": "https://api.calendly.com/event_types/TYPE_UUID",
    "questions_and_answers": [
      {"question": "Company name", "answer": "Acme Corp"}
    ]
  }
}
```

## Output

### Slack Message 1 (Immediate)
- Meeting booked alert
- Prospect name and email
- Meeting type (fetched from Calendly API)
- Meeting time (fetched from Calendly API)
- "Researching now..." status

### Google Doc Contents
- Executive Summary (3-4 sentence overview)
- Company Research (products, size, funding, competitors)
- Prospect Research (role, background, content)
- LinkedIn Profile Summary
- Talking Points & Strategy
  - 5 personalized talking points
  - 3 questions to ask
  - Potential pain points
  - Connection points
  - Meeting goals

### Slack Message 2 (After Research)
- Quick summary (3-4 sentences)
- Button link to full Google Doc

## Configuration

### Shared Google Drive Folder
Docs are saved to: `1Xhgr63LTNqRI8ofFaVE-_zXYJLgjbBiF`

### Calendly Webhook Subscription
- ID: `7fef4d67-e65e-4230-aad9-a3d36016c4b5`
- Events: `invitee.created`
- Scope: `user`

## Quality Gates
- [x] Calendly API fetches event name and time
- [x] Slack messages send successfully
- [x] Company extracted from email domain or form questions
- [x] Perplexity research returns data (using Sonar model)
- [x] Claude generates talking points
- [x] Google Doc created with formatting
- [x] Doc moved to shared folder
- [x] Summary generated and sent with doc link

## Self-Annealing Notes

### 2026-01-09
- Fixed Perplexity model: changed from `llama-3.1-sonar-large-128k-online` to `sonar`
- Added Calendly API integration to fetch event details (name, start_time)
- Added Google service account for Modal deployment
- Added shared folder support for Google Docs
- Added detailed debug logging for troubleshooting
