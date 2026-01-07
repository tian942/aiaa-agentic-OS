#!/usr/bin/env python3
"""
Complete E-commerce Email Flow Generator
Generates all 7 email flows using $40M methodology.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CONTENT_CHANNEL_ID = os.getenv("SLACK_CONTENT_CHANNEL_ID")

FLOWS = [
    {"name": "Welcome Flow", "emails": 8, "key": "welcome"},
    {"name": "Cart Abandon Flow", "emails": 6, "key": "cart_abandon"},
    {"name": "Checkout Abandon Flow", "emails": 6, "key": "checkout_abandon"},
    {"name": "Browse Abandon Flow", "emails": 4, "key": "browse_abandon"},
    {"name": "Post-Purchase Flow", "emails": 4, "key": "post_purchase"},
    {"name": "Site Abandon Flow", "emails": 1, "key": "site_abandon"},
    {"name": "Win-Back Flow", "emails": 3, "key": "winback"},
]

def research_brand(brand_name: str, website: str, niche: str) -> str:
    """Research brand using Perplexity."""
    print("   Researching brand...")
    
    prompt = f"""Research this e-commerce brand for email marketing:

BRAND: {brand_name}
WEBSITE: {website}
NICHE: {niche}

Provide comprehensive research on:

1. BRAND FOUNDATION
- Company background and founding story
- Mission, values, and positioning
- Unique selling propositions
- Brand voice and tone

2. PRODUCT PORTFOLIO
- Main product categories
- Best-sellers and hero products
- Price points and positioning
- Key ingredients/features

3. TARGET AUDIENCE
- Primary demographics
- Psychographics and lifestyle
- Pain points and desires
- Purchase motivations

4. COMPETITIVE LANDSCAPE
- Key competitors
- Differentiation factors
- Market positioning

5. EMAIL MARKETING INSIGHTS
- What messaging would resonate
- Key benefits to highlight
- Objections to address
- Emotional triggers to use"""

    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {"role": "system", "content": "You are a brand research expert. Provide actionable insights for email marketing."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            },
            timeout=60
        )
        
        if resp.ok:
            result = resp.json()
            research = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print("   ✓ Brand research complete")
            return research
        else:
            print(f"   ⚠️ Research error: {resp.status_code}")
            return ""
    except Exception as e:
        print(f"   ⚠️ Research error: {e}")
        return ""


def generate_flow(flow_config: dict, brand_name: str, website: str, niche: str, brand_research: str) -> str:
    """Generate a single email flow."""
    
    client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
    
    flow_prompts = {
        "welcome": """Create a master-level 8-email Welcome Flow that:
- Achieves 10%+ conversion rates
- Builds brand relationship from first touch
- Educates without being salesy
- Creates dopamine-triggering engagement

EMAIL SEQUENCE:
1. Welcome + Brand Story (immediate)
2. Founder's Note + Mission (Day 1)
3. Product Education + Benefits (Day 2)
4. Social Proof + Reviews (Day 3)
5. Best-Sellers Showcase (Day 4)
6. Usage Tips + Value Add (Day 5)
7. Exclusive Offer (Day 6)
8. Soft Close + Community (Day 7)""",

        "cart_abandon": """Create a 6-email Cart Abandonment Flow that:
- Recovers 25-50% of abandoned carts
- Creates urgency without desperation
- Addresses common objections
- Uses psychology-driven copy

EMAIL SEQUENCE:
1. Gentle Reminder (1 hour)
2. Product Benefits Recap (4 hours)
3. Social Proof + Reviews (24 hours)
4. Objection Handler (48 hours)
5. Scarcity/Stock Warning (72 hours)
6. Final Offer + Urgency (96 hours)""",

        "checkout_abandon": """Create a 6-email Checkout Abandonment Flow that:
- Recovers 40-60% of checkout abandoners (highest intent)
- Addresses payment/trust concerns
- Creates immediate urgency
- Uses shortest, punchiest copy

EMAIL SEQUENCE:
1. Quick Recovery (30 min)
2. Trust Builder (2 hours)
3. Support Offer (12 hours)
4. Benefits Reminder (24 hours)
5. Limited Time Save (48 hours)
6. Last Chance (72 hours)""",

        "browse_abandon": """Create a 4-email Browse Abandonment Flow that:
- Converts 15-25% of browsers to buyers
- Re-engages product interest
- Provides additional value
- Gentle product recommendations

EMAIL SEQUENCE:
1. "Still Thinking?" (4 hours)
2. Product Deep-Dive (24 hours)
3. Customer Stories (48 hours)
4. Curated Picks (72 hours)""",

        "post_purchase": """Create a 4-email Post-Purchase Flow that:
- Maximizes 27% higher repurchase window
- Builds brand loyalty
- Generates reviews/UGC
- Creates repeat customers

EMAIL SEQUENCE:
1. Order Confirmation + Excitement (immediate)
2. Shipping + Usage Tips (shipping day)
3. Check-In + Review Request (5 days post-delivery)
4. Replenishment/Cross-Sell (14 days)""",

        "site_abandon": """Create a 1-email Site Abandonment Flow that:
- Converts 2%+ of site abandoners
- Re-engages earliest-stage visitors
- Showcases brand value prop
- Drives to product discovery

Single powerful email sent 2 hours after site exit.""",

        "winback": """Create a 3-email Win-Back Flow that:
- Re-engages 5-15% of dormant customers
- Rebuilds purchasing relationship
- Uses nostalgia and exclusivity
- Provides compelling reason to return

EMAIL SEQUENCE:
1. "We Miss You" (60 days inactive)
2. Exclusive Comeback Offer (67 days)
3. Final Farewell + Best Offer (74 days)"""
    }
    
    system_prompt = """You are a master e-commerce email designer and copywriter using Max Sturtevant's $100M methodology.

REFERENCE: SKILL_BIBLE_sturtevant_high_converting_email_design.md - The 10 Commandments of High-Converting Design

You create DESIGNED HTML EMAILS - not plaintext. Each email is a visual blueprint with:
- Specific sections (HERO, BODY, PRODUCT GRID, FOOTER)
- Image placeholders with exact descriptions
- Button specifications (color, size, text)
- Typography hierarchy (headlines, subheads, body)
- Mobile-responsive layout instructions

DESIGN STRUCTURE (Every Email):
1. HEADER BAR: Logo centered or left, optional nav links
2. HERO SECTION: Full-width image OR color banner with headline overlay
3. BODY SECTION: Short copy block (50-75 words max), CTA button
4. PRODUCT/CONTENT SECTION: 2-column grid on desktop, stacked on mobile
5. SOCIAL PROOF SECTION: Star ratings, testimonial quote, customer photo
6. FOOTER: Category buttons, social icons, unsubscribe

COPYWRITING FRAMEWORK (SCE):
- Skimmable: 3-5 second reading time
- Clear & Concise: Under 75 words body copy
- Engaging: Dopamine-triggering, curiosity-driven

BUTTON SPECIFICATIONS:
- Primary CTA: Brand color, 48px height, full-width on mobile, rounded corners
- Secondary CTA: Outlined/ghost style, same dimensions
- Product CTAs: Smaller (40px), individual per product

IMAGE SPECIFICATIONS:
- Hero images: 600x400px, lifestyle shots showing product in use
- Product images: 300x300px, clean white background
- Testimonial images: 60x60px circular avatar

TYPOGRAPHY:
- Headlines: 28-32px, bold, brand font
- Subheadlines: 18-22px, medium weight
- Body: 16px, regular, high readability
- Button text: 14-16px, bold, ALL CAPS or Title Case

COLOR PSYCHOLOGY:
- Red/Orange CTAs for urgency and action
- Brand colors for headers and accents
- White/light backgrounds for readability
- Dark text (#333333) for body copy

THE 10 COMMANDMENTS (from Max Sturtevant's $100M methodology):
1. BIG BUTTONS = HIGHER CLICKS (48px+ height, high contrast)
2. BUTTON + OFFER AT TOP (visible in first 300-400px)
3. NO NAVIGATION AT TOP (only in footer)
4. INDIVIDUAL PRODUCTS NEED SHOP BUTTONS
5. END WITH GENERAL SHOP BUTTON
6. FOOTER CATEGORY BUTTONS ARE MANDATORY
7. MAKE EMAILS IMMERSIVE (gradients, overlapping elements, depth)
8. MATCH YOUR BRAND VIBE
9. HERO IMAGE REPRESENTS YOUR CUSTOMER
10. FULL IMAGE EMAILS ARE FINE ($10M+/month proven)"""

    user_prompt = f"""{flow_prompts[flow_config['key']]}

BRAND INTELLIGENCE:
- Brand Name: {brand_name}
- Website: {website}
- Niche: {niche}
- Brand Research: {brand_research[:3000]}

FOR EACH EMAIL, USE THIS EXACT KLAVIYO-READY FORMAT:

---

## Email [X]: [Name]

**Timing:** [When to send]

### KLAVIYO USE

| Field | Value |
|-------|-------|
| **Campaign Name** | [Flow Name] Email [X] |
| **Subject Line** | [2-5 words, curiosity-driven] |
| **Preview Text** | [40-90 chars, complements subject] |

---

### HERO SECTION

| Element | Content |
|---------|---------|
| **Company Logo** | [Brand Name] logo centered |
| **Headline** | [Main headline - 5-8 words, punchy] |
| **Subheadline** | [Supporting copy - benefit-driven, include discount code if applicable] |
| **Product Image** | [Detailed description: lifestyle photo of product in use, or product on clean background] |
| **Call To Action** | [Button text - action verb + benefit, e.g., "SHOP 15% OFF"] |

---

### BRIDGE SECTION

| Element | Content |
|---------|---------|
| **Content** | [Body copy - 50-100 words max, punchy, benefit-driven, skimmable. Use line breaks for readability.] |
| **CTA** | [Optional secondary button] |

---

### TESTIMONIAL SECTION (OPTIONAL)

| Element | Content |
|---------|---------|
| **Star Rating** | ⭐⭐⭐⭐⭐ |
| **Quote** | "[Customer testimonial - 1-2 sentences]" |
| **Customer** | — [Name], Verified Customer |

---

### PRODUCT SECTION

| Element | Content |
|---------|---------|
| **Content** | [Section headline, e.g., "Shop Our Bestsellers" or "You May Also Like"] |
| **Products** | [List 3-4 products with names and brief descriptions] |
| **CTA** | [General shop button, e.g., "SHOP ALL BESTSELLERS"] |

---

### FOOTER

| Element | Content |
|---------|---------|
| **Icons** | 🚚 Fast Shipping | 🛡️ 60-Day Guarantee | 💬 Real Support |
| **Content** | [LOGO] + Category buttons: [Shop All] | [Best Sellers] | [New Arrivals] |

---

### TEMPLATE REFERENCE
[Brief note on which template style to use: lifestyle hero, product focus, testimonial-led, urgency-driven, etc.]

---

Create all {flow_config['emails']} emails for this flow in this EXACT Klaviyo-ready format."""

    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=8000
    )
    
    return response.choices[0].message.content


def upload_to_drive(content: str, filename: str, folder_id: str = None) -> dict:
    """Upload markdown as formatted Google Doc."""
    try:
        # Use centralized formatted doc creator
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "execution"))
        from create_formatted_google_doc import create_formatted_doc
        
        result = create_formatted_doc(
            title=filename,
            content=content,
            folder_id=folder_id,
            notify_slack=False
        )
        
        if result.get("status") == "created":
            return {"id": result.get("documentId"), "url": result.get("documentUrl")}
        return None
    except ImportError:
        # Fallback to basic method
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            creds = Credentials.from_authorized_user_file('token_docs.json')
            service = build('docs', 'v1', credentials=creds)
            drive_service = build('drive', 'v3', credentials=creds)
            
            doc = service.documents().create(body={'title': filename}).execute()
            doc_id = doc.get('documentId')
            
            service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': [{'insertText': {'location': {'index': 1}, 'text': content}}]}
            ).execute()
            
            if folder_id:
                drive_service.files().update(fileId=doc_id, addParents=folder_id, removeParents='root', fields='id').execute()
            
            return {"id": doc_id, "url": f"https://docs.google.com/document/d/{doc_id}"}
        except Exception as e:
            print(f"   ⚠️ Drive upload error: {e}")
            return None
    except Exception as e:
        print(f"   ⚠️ Drive upload error: {e}")
        return None


def send_slack_notification(brand_name: str, flow_docs: list):
    """Send Slack notification with all flow links."""
    if not SLACK_BOT_TOKEN or not SLACK_CONTENT_CHANNEL_ID:
        return
    
    flow_links = "\n".join([f"• <{doc['url']}|{doc['name']}>" for doc in flow_docs if doc.get('url')])
    
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "📧 E-commerce Email Flows Complete", "emoji": True}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Brand:*\n{brand_name}"},
            {"type": "mrkdwn", "text": f"*Flows:*\n7 complete flows"}
        ]},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*📄 Flow Documents:*\n{flow_links}"}}
    ]
    
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"},
        json={"channel": SLACK_CONTENT_CHANNEL_ID, "text": f"Email flows complete for {brand_name}", "blocks": blocks},
        timeout=30
    )


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", "-b", required=True)
    parser.add_argument("--website", "-w", required=True)
    parser.add_argument("--niche", "-n", default="E-commerce")
    parser.add_argument("--output", "-o", default=".tmp/email_flows")
    args = parser.parse_args()
    
    print(f"\n📧 E-commerce Email Flow Generator")
    print(f"   Brand: {args.brand}")
    print(f"   Website: {args.website}")
    print(f"   Generating 7 flows...\n")
    
    output_dir = Path(args.output) / args.brand.replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Research brand
    print("1️⃣ Researching brand...")
    brand_research = research_brand(args.brand, args.website, args.niche)
    
    # Save research
    research_path = output_dir / "00_brand_research.md"
    research_path.write_text(f"# Brand Research: {args.brand}\n\n{brand_research}", encoding="utf-8")
    
    # Step 2: Generate all flows
    print("\n2️⃣ Generating email flows...")
    flow_docs = []
    
    for i, flow in enumerate(FLOWS, 1):
        print(f"   [{i}/7] {flow['name']}...")
        
        try:
            content = generate_flow(flow, args.brand, args.website, args.niche, brand_research)
            
            # Save locally
            filename = f"{i:02d}_{flow['key']}_flow.md"
            filepath = output_dir / filename
            
            full_content = f"""# {flow['name']} - {args.brand}

**Brand:** {args.brand}
**Website:** {args.website}
**Flow Type:** {flow['name']}
**Emails:** {flow['emails']}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

{content}
"""
            filepath.write_text(full_content, encoding="utf-8")
            print(f"   ✓ {flow['name']} complete ({flow['emails']} emails)")
            
            # Upload to Drive
            doc_result = upload_to_drive(full_content, f"{args.brand} - {flow['name']}")
            flow_docs.append({
                "name": flow['name'],
                "local": str(filepath),
                "url": doc_result.get("url") if doc_result else None
            })
            
        except Exception as e:
            print(f"   ⚠️ Error generating {flow['name']}: {e}")
            flow_docs.append({"name": flow['name'], "local": None, "url": None})
    
    # Step 3: Send Slack notification
    print("\n3️⃣ Sending Slack notification...")
    send_slack_notification(args.brand, flow_docs)
    print("   ✓ Notification sent")
    
    # Summary
    print(f"\n✅ All flows complete!")
    print(f"   📁 Output folder: {output_dir}")
    print(f"   📄 Files generated: {len([f for f in flow_docs if f.get('local')])}")
    
    for doc in flow_docs:
        if doc.get('url'):
            print(f"   🔗 {doc['name']}: {doc['url']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
