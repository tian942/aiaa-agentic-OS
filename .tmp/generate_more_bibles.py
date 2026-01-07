#!/usr/bin/env python3
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

def generate_bible(topic, sources, output):
    combined = ""
    base = Path("/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/.tmp/sturtevant_transcripts/parsed")
    for s in sources:
        path = base / s
        if path.exists():
            combined += f"\n\n=== {s} ===\n" + path.read_text()
    
    combined = combined[:100000]
    
    prompt = f"""Create the DEFINITIVE skill bible on {topic} from Max Sturtevant's teachings ($40M+ ecommerce email).

SOURCE:
{combined}

Create an 8,000+ word skill bible:

# SKILL BIBLE: {topic.upper()}
## Max Sturtevant's $40M+ Email Marketing Methodology

### Executive Summary
[Comprehensive overview - 3-4 paragraphs]

### Source Attribution
- Expert: Max Sturtevant (@maxwellcopy)
- Credentials: $40M+ generated in ecommerce email
- Channel: YouTube @maxwellcopy

---

## PART 1: CORE FRAMEWORK
[Complete methodology - be exhaustive]

## PART 2: STEP-BY-STEP PROCESS
[Detailed implementation with numbered steps]

## PART 3: EMAIL TEMPLATES
[Actual copy examples - include full emails]

## PART 4: SUBJECT LINE SWIPE FILE
[25+ subject line examples with context]

## PART 5: DESIGN GUIDELINES
[Visual specifications, layouts, mobile]

## PART 6: METRICS & BENCHMARKS
[KPIs, targets, what good looks like]

## PART 7: COMMON MISTAKES
[What to avoid - be specific]

## PART 8: ADVANCED TACTICS
[Pro-level strategies]

## PART 9: IMPLEMENTATION CHECKLIST
[Complete pre-launch checklist]

## PART 10: AI IMPLEMENTATION NOTES
[How AI agents should apply this knowledge]

## QUICK REFERENCE CARD
[Key takeaways in bullet form]

REQUIREMENTS:
- MINIMUM 8,000 words
- Include SPECIFIC numbers, percentages, timings
- Include ACTUAL email copy examples
- Include REAL subject lines
- Be ACTIONABLE"""

    print(f"   Generating {topic}...")
    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10000,
        temperature=0.4
    )
    
    result = response.choices[0].message.content
    output_path = Path(f"/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/skills/{output}")
    output_path.write_text(result)
    print(f"   ✓ {output} ({len(result.split())} words)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        idx = int(sys.argv[1])
        bibles = [
            ("Email Copywriting & Campaign Creation", 
             ["21_mrbeast_emails.txt", "22_write_design_live.txt", "24_255k_boring.txt", "02_40m_advice.txt"],
             "SKILL_BIBLE_sturtevant_copywriting.md"),
            ("Klaviyo Setup & Optimization", 
             ["25_klaviyo_full.txt", "09_flows_2025.txt", "08_flows_tutorial.txt"],
             "SKILL_BIBLE_sturtevant_klaviyo.md"),
            ("Ecommerce Funnels & Revenue Systems", 
             ["23_100m_funnel.txt", "16_500k_strategy.txt", "03_40m_made.txt", "04_40m_strategy.txt"],
             "SKILL_BIBLE_sturtevant_revenue_systems.md"),
        ]
        generate_bible(*bibles[idx])
