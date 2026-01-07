#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

def create_skill_bible(transcript_path: str, output_path: str):
    """Create a skill bible from a transcript."""
    with open(transcript_path, "r") as f:
        transcript = f.read()
    
    title = Path(transcript_path).stem
    
    prompt = f"""Create a comprehensive SKILL BIBLE from this Alex Hormozi transcript.

VIDEO: {title}

TRANSCRIPT:
{transcript[:50000]}

Create a detailed skill bible with these sections:

# SKILL BIBLE: [TOPIC TITLE]

## Executive Summary
[2-3 paragraph overview of the core teachings]

## Source
- **Creator:** Alex Hormozi
- **Video:** {title}
- **Channel:** Alex Hormozi (@AlexHormozi)
- **Expertise:** $100M+ entrepreneur, author of $100M Offers and $100M Leads

## Core Principles
[5-10 key principles with explanations]

## Frameworks & Models
[Any frameworks, models, or systems mentioned - with step-by-step breakdowns]

## Tactical Implementation
[Specific actionable tactics with examples]

## Common Mistakes to Avoid
[What NOT to do]

## Key Quotes
[5-10 powerful quotes from the video]

## Action Items
[Specific next steps the reader should take]

## AI Implementation Notes
[How an AI agent should use this knowledge]

Make it comprehensive (8,000-12,000 words), actionable, and deeply insightful."""

    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=[
            {"role": "system", "content": "You are an expert at creating comprehensive skill bibles from video transcripts. Extract maximum value and structure it for actionability."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=8000,
        temperature=0.7
    )
    
    content = response.choices[0].message.content
    
    with open(output_path, "w") as f:
        f.write(content)
    
    print(f"✓ Created: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_hormozi_skill_bible.py <transcript_path> <output_path>")
        sys.exit(1)
    
    create_skill_bible(sys.argv[1], sys.argv[2])
