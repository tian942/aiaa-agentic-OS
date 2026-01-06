from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

print("Testing Claude Opus 4.5 output length...")

response = client.chat.completions.create(
    model="anthropic/claude-opus-4.5",
    messages=[
        {
            "role": "system",
            "content": "You are a VSL scriptwriter who writes VERY LONG, DETAILED scripts with full paragraphs and extensive development of each point."
        },
        {
            "role": "user",
            "content": """Write a 400-word problem agitation section about agency owners struggling with inconsistent lead flow.

REQUIREMENTS:
- MINIMUM 400 WORDS (this is critical)
- Full paragraphs with vivid details
- Specific scenarios and pain points
- Conversational tone

DO NOT abbreviate or summarize - write the COMPLETE section as it would appear in the final script."""
        }
    ],
    max_tokens=3000,
    temperature=0.7
)

result = response.choices[0].message.content
word_count = len(result.split())

print(f"\nGenerated: {word_count} words")
print(f"Target: 400 words")
print(f"Status: {'✅ Good' if word_count >= 400 else '❌ Too short'}")
print(f"\nContent:\n{result}")
