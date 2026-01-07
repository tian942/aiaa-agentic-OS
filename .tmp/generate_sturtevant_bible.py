#!/usr/bin/env python3
"""
Generate hyper-detailed Max Sturtevant skill bibles from transcripts.
Target: 8000+ words per skill bible
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

def generate_skill_bible(topic: str, transcripts: list, output_path: str):
    """Generate a hyper-detailed skill bible from multiple transcripts."""
    
    # Combine transcripts
    combined_content = ""
    for t in transcripts:
        if os.path.exists(t):
            with open(t, "r") as f:
                content = f.read()
                combined_content += f"\n\n=== SOURCE: {Path(t).stem} ===\n{content}"
    
    if not combined_content:
        print(f"   ⚠️ No content found for {topic}")
        return
    
    # Truncate if too long
    combined_content = combined_content[:120000]
    
    prompt = f"""You are creating the DEFINITIVE skill bible on {topic} based on Max Sturtevant's teachings.

Max has generated over $40M+ in revenue through ecommerce email marketing. This skill bible must capture EVERY tactical detail, framework, and insight from his content.

SOURCE MATERIAL:
{combined_content}

Create a HYPER-DETAILED skill bible (8,000-12,000 words) with the following structure:

# SKILL BIBLE: {topic.upper()}
## The Definitive Guide Based on Max Sturtevant's $40M+ Methodology

### Executive Summary
[3-4 paragraphs summarizing the core principles and why this matters]

### Source Attribution
- **Expert:** Max Sturtevant (@maxwellcopy)
- **Credentials:** $40M+ generated in ecommerce email marketing
- **Content Type:** YouTube Educational Content

---

## PART 1: FOUNDATIONAL CONCEPTS

### Core Philosophy
[Max's fundamental beliefs about this topic]

### Key Principles (Number each one)
[List and explain 8-12 key principles with examples]

### The Framework Overview
[Visual/structural overview of how everything connects]

---

## PART 2: STRATEGIC FRAMEWORK

### Step-by-Step Process
[Detailed numbered steps with sub-bullets]

### Timing & Sequencing
[When to do what, exact delays, triggers]

### Segmentation Strategy
[Who gets what, how to segment]

---

## PART 3: TACTICAL EXECUTION

### Email Structure Templates
[Exact structures, layouts, components]

### Copywriting Formulas
[Specific formulas, hooks, frameworks]

### Subject Line Strategies
[Formulas, examples, testing approaches]

### Design Guidelines
[Visual elements, mobile optimization, CTAs]

---

## PART 4: OPTIMIZATION & TESTING

### Key Metrics to Track
[Exact KPIs, benchmarks, targets]

### A/B Testing Framework
[What to test, how to test, when to test]

### Optimization Tactics
[Specific improvements, quick wins]

---

## PART 5: ADVANCED STRATEGIES

### Psychology & Persuasion
[Mental triggers, urgency tactics, scarcity]

### Personalization Techniques
[Dynamic content, segmentation, behavioral triggers]

### Integration Points
[How this connects with other flows/campaigns]

---

## PART 6: COMMON MISTAKES & SOLUTIONS

### Critical Errors to Avoid
[Specific mistakes with consequences]

### Troubleshooting Guide
[Problem → Solution format]

---

## PART 7: IMPLEMENTATION CHECKLIST

### Pre-Launch Checklist
[Everything to verify before going live]

### Quality Assurance
[Testing protocols, approval process]

### Performance Monitoring
[What to watch, when to intervene]

---

## PART 8: TEMPLATES & EXAMPLES

### Email Templates
[Actual email copy examples]

### Subject Line Swipe File
[20+ subject line examples]

### Call-to-Action Examples
[CTA variations that convert]

---

## AI IMPLEMENTATION NOTES

### How to Use This as an AI Agent
[Instructions for AI to apply this knowledge]

### Prompt Engineering Tips
[How to prompt AI for best results]

### Quality Gates
[What to check before delivering]

---

## QUICK REFERENCE CARD

### The 5-Minute Summary
[Bullet points of the most critical takeaways]

### Key Numbers to Remember
[Specific metrics, timings, percentages]

### Red Flags to Watch
[Warning signs of problems]

---

REQUIREMENTS:
1. MINIMUM 8,000 words - be comprehensive
2. Include SPECIFIC numbers, percentages, and benchmarks from Max's content
3. Include EXACT email copy examples and templates
4. Include REAL subject lines that work
5. Be ACTIONABLE - someone should be able to implement immediately
6. Preserve Max's voice and specific terminology
7. Include both strategic overview AND tactical details

This should be the ONLY resource someone needs to master this topic."""

    print(f"   Generating {topic} skill bible...")
    
    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=[
            {"role": "system", "content": "You are an expert technical writer creating comprehensive educational documentation. Your output must be detailed, actionable, and preserve all specific tactical information from the source material."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=12000,
        temperature=0.4
    )
    
    result = response.choices[0].message.content
    
    # Save
    with open(output_path, "w") as f:
        f.write(result)
    
    word_count = len(result.split())
    print(f"   ✓ Created {output_path} ({word_count} words)")


if __name__ == "__main__":
    base_dir = Path("/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/.tmp/sturtevant_transcripts/parsed")
    skills_dir = Path("/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/skills")
    
    # Define skill bibles to create with their source transcripts
    bibles = [
        {
            "topic": "Ecommerce Email Marketing Master System",
            "sources": ["01_8hr_free_course.txt", "05_only_video_needed.txt", "02_40m_advice.txt"],
            "output": "SKILL_BIBLE_sturtevant_email_master_system.md"
        },
        {
            "topic": "Welcome Flow Mastery",
            "sources": ["06_welcome_flow.txt", "08_flows_tutorial.txt", "09_flows_2025.txt"],
            "output": "SKILL_BIBLE_sturtevant_welcome_flow.md"
        },
        {
            "topic": "Abandoned Cart & Checkout Recovery",
            "sources": ["07_abandoned_cart.txt", "08_flows_tutorial.txt", "10_browse_abandon.txt"],
            "output": "SKILL_BIBLE_sturtevant_cart_recovery.md"
        },
        {
            "topic": "Email Design & Conversion Optimization",
            "sources": ["12_email_design.txt", "13_high_converting_design.txt", "05_only_video_needed.txt"],
            "output": "SKILL_BIBLE_sturtevant_email_design.md"
        },
        {
            "topic": "Black Friday & Q4 Email Strategy",
            "sources": ["14_black_friday.txt", "11_best_campaigns_2025.txt", "16_500k_strategy.txt"],
            "output": "SKILL_BIBLE_sturtevant_black_friday.md"
        },
        {
            "topic": "Email Deliverability & List Health",
            "sources": ["19_deliverability.txt", "18_dead_list_goldmine.txt", "15_billion_emails.txt"],
            "output": "SKILL_BIBLE_sturtevant_deliverability.md"
        },
        {
            "topic": "Advanced Email Strategies & AI Integration",
            "sources": ["17_new_strategies_50m.txt", "20_ai_email.txt", "03_40m_made.txt", "04_40m_strategy.txt"],
            "output": "SKILL_BIBLE_sturtevant_advanced_strategies.md"
        }
    ]
    
    if len(sys.argv) > 1:
        # Run specific index
        idx = int(sys.argv[1])
        bible = bibles[idx]
        sources = [str(base_dir / s) for s in bible["sources"]]
        generate_skill_bible(bible["topic"], sources, str(skills_dir / bible["output"]))
    else:
        # Run all
        for bible in bibles:
            sources = [str(base_dir / s) for s in bible["sources"]]
            generate_skill_bible(bible["topic"], sources, str(skills_dir / bible["output"]))
