#!/usr/bin/env python3
import json, os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Test with very explicit paragraph requirements
research_file = ".tmp/vsl_funnel_peak_performance_agency_20260105_163539/01_research.json"

with open(research_file) as f:
    research_data = json.load(f)

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

prompt = f"""Write a COMPLETE VSL script (not an outline) for:

Company: {research_data['company']['name']}
Offer: {research_data['offer']['name']}

CRITICAL: Each section below requires MULTIPLE FULL PARAGRAPHS.
Total script must be 2500-3000 words MINIMUM.

Write these 10 sections in COMPLETE DETAIL:

## 1. HOOK (100-150 words - 2-3 paragraphs)
Write the complete opening hook with full paragraphs.

## 2. PROBLEM (300-400 words - 4-5 paragraphs)
Write FOUR full paragraphs agitating pain points.

## 3. CREDIBILITY (200-250 words - 3 paragraphs)
Write THREE paragraphs establishing authority.

## 4. SOLUTION (200-250 words - 3 paragraphs)
Write THREE paragraphs introducing the mechanism.

## 5. MECHANISM DEEP DIVE (600-800 words - 6-8 paragraphs)
Write SIX TO EIGHT full paragraphs explaining how it works step-by-step.

## 6. SOCIAL PROOF (400-500 words - 5-6 paragraphs)
Write FIVE paragraphs with case studies and results.

## 7. OFFER REVEAL (400-500 words - 5-6 paragraphs)
Write FIVE paragraphs breaking down what's included.

## 8. URGENCY (200-250 words - 3 paragraphs)
Write THREE paragraphs on scarcity.

## 9. GUARANTEE (150-200 words - 2-3 paragraphs)
Write THREE paragraphs on risk reversal.

## 10. CTA (200-250 words - 3 paragraphs)
Write THREE paragraphs closing and driving action.

PARAGRAPH LENGTH: Each paragraph should be 50-80 words (3-5 sentences).

DO NOT write one-sentence paragraphs.
DO NOT abbreviate sections.
Write COMPLETE, FULL-LENGTH paragraphs for EVERY section.
"""

print("Generating with explicit paragraph requirements...")
response = client.chat.completions.create(
    model="anthropic/claude-opus-4.5",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=16000,
    temperature=0.7
)

result = response.choices[0].message.content
words = len(result.split())

print(f"\n✅ Generated: {words} words")
print(f"Target: 2500+ words")
print(f"Status: {'✅✅✅ GOOD!' if words >= 2500 else f'❌ Still {2500-words} words short'}")

# Save test
with open(".tmp/test_vsl_explicit_paragraphs.md", "w") as f:
    f.write(result)

print(f"Saved to: .tmp/test_vsl_explicit_paragraphs.md")
