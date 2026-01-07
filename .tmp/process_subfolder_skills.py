#!/usr/bin/env python3
"""
Process subfolder skills into full skill bibles or merge into existing ones.
"""
import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

SKILLS_DIR = Path("/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/skills")

def process_skill_file(skill_path: str, output_path: str):
    """Process a skill file into a full skill bible."""
    with open(skill_path, "r") as f:
        content = f.read()
    
    filename = Path(skill_path).stem
    folder = Path(skill_path).parent.name
    
    prompt = f"""Transform this skill/SOP document into a comprehensive SKILL BIBLE format.

SOURCE FILE: {folder}/{filename}.md
CONTENT:
{content[:40000]}

Create a SKILL BIBLE with these sections:

# SKILL BIBLE: [DESCRIPTIVE TITLE]

## Executive Summary
[2-3 paragraph overview of what this skill teaches]

## Source
- **Type:** Internal SOP/Skill Document
- **Category:** {folder}
- **Original File:** {filename}.md

## Core Principles
[5-8 key principles extracted from the content]

## Step-by-Step Process
[Detailed process breakdown with numbered steps]

## Frameworks & Templates
[Any frameworks, templates, or formulas mentioned]

## Best Practices
[Key best practices and pro tips]

## Common Mistakes to Avoid
[What NOT to do]

## Tools & Resources
[Tools, software, or resources mentioned]

## Quality Checklist
[Checklist for validating work]

## AI Implementation Notes
[How an AI agent should use this knowledge]

Make it comprehensive (4,000-8,000 words), actionable, and well-structured.
Preserve all specific tactical details, numbers, and examples from the original."""

    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=[
            {"role": "system", "content": "You are an expert at transforming SOPs and skill documents into comprehensive skill bibles. Preserve all tactical details while adding structure and context."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=6000,
        temperature=0.5
    )
    
    result = response.choices[0].message.content
    
    with open(output_path, "w") as f:
        f.write(result)
    
    print(f"✓ Created: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_subfolder_skills.py <input_path> <output_path>")
        sys.exit(1)
    
    process_skill_file(sys.argv[1], sys.argv[2])
