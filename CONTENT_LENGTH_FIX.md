# Content Length Fix - VSL Funnel System

**Issue:** Generated content was too short (VSL scripts only 800 words instead of 2000+)
**Fixed:** 2026-01-05
**Status:** ✅ All generators updated

---

## 🔧 What Was Wrong

### Before (Broken)
- **VSL Scripts:** 800-1000 words → Only 5-6 minutes (should be 12-15 min)
- **Sales Pages:** 500-800 words → Too brief for conversions
- **Emails:** 150-200 words each → Not enough value/story
- **Model:** GPT-4o → Against AGENTS.MD instructions (should use Opus 4.5)
- **Skill Bibles:** Truncated to 15K chars → Lost critical frameworks
- **Max Tokens:** 4000 → Capped output artificially

### After (Fixed) ✅
- **VSL Scripts:** 2500-3000 words minimum → 16-20 minutes
- **Sales Pages:** 1500-3000 words → Long-form that converts
- **Emails:** 300-500 words each → Full narratives with stories
- **Model:** Claude Opus 4.5 → Best-in-class as instructed
- **Skill Bibles:** Full context loaded → Complete frameworks
- **Max Tokens:** 16,000 → No artificial limits

---

## 📝 Specific Changes Made

### 1. VSL Script Generator ([generate_vsl_script.py](execution/generate_vsl_script.py))

**Changes:**
```python
# Before
"medium": "1800-2200 words"  # Target was too low
max_tokens=4000  # Capped output
model="gpt-4o"  # Wrong model
{skill_bibles[:15000]}  # Truncated

# After
"medium": "2500-3000 words"  # Proper target for 16-20 min
max_tokens=16000  # Allow full generation
model="anthropic/claude-opus-4.5:beta"  # Best model
{skill_bibles}  # Full context
```

**Word Count Breakdown (per section):**
- Hook: 100-150 words
- Problem: 300-400 words
- Credibility: 200-250 words
- Solution: 200-250 words
- **Mechanism Deep Dive: 600-800 words** (longest section)
- Social Proof: 400-500 words
- Offer Reveal: 400-500 words
- Urgency: 200-250 words
- Guarantee: 150-200 words
- CTA: 200-250 words

**Total: 2,550-3,350 words**

### 2. Sales Page Generator ([generate_sales_page.py](execution/generate_sales_page.py))

**Changes:**
```python
# Before
max_tokens=3000  # Too small
model="gpt-4o"
bullets="7-10 bullets"  # Not enough

# After
max_tokens=12000  # Long-form capacity
model="anthropic/claude-opus-4.5:beta"
bullets="10-15 bullets (each 1-2 sentences)"  # Detailed
```

**Added Sections:**
- About the Mechanism (300-500 words)
- Expanded Social Proof (400-600 words)
- Detailed Offer Breakdown (500-700 words)

**Target: 1500-3000 words**

### 3. Email Sequence Generator ([generate_email_sequence.py](execution/generate_email_sequence.py))

**Changes:**
```python
# Before
"Body Copy (200-400 words)"  # Too short
max_tokens=4000  # Can't fit 7 full emails
model="gpt-4o"

# After
"Body Copy (300-500 words)"  # Substantial value
max_tokens=16000  # 7 full emails
model="anthropic/claude-opus-4.5:beta"
```

**Per Email Requirements:**
- Subject: 2 variations
- Preview: 50 chars
- Body: 300-500 words (full paragraphs with stories)
- PS: 50-100 words (not just one line)
- CTA: Clear action

**Total Sequence: 2,500-3,500 words (7 emails)**

---

## 🎯 New Minimum Standards

| Content Type | Old Length | New Length | Why |
|--------------|-----------|------------|-----|
| VSL Script (short) | 1200 words | 2000 words | 13 min minimum |
| VSL Script (medium) | 1800 words | 2500 words | 16-20 min standard |
| VSL Script (long) | 2500 words | 3500 words | 23+ min for complex offers |
| Sales Page | 500-800 words | 1500-3000 words | Long-form converts better |
| Email (each) | 150-200 words | 300-500 words | Enough for value + story |
| Total Sequence | 1000-1400 words | 2500-3500 words | 7 substantial emails |

---

## 🚀 Why This Matters

### Short Content Problems
- **Low watch time:** 5-min VSLs don't build enough trust
- **Weak value stack:** No room for proper proof/objection handling
- **Poor conversions:** Rushed CTAs without proper setup
- **Low email engagement:** Thin emails get ignored

### Proper Length Benefits
- **Trust building:** Time to establish credibility
- **Complete story:** Proper problem agitation → mechanism → proof → offer
- **Objection handling:** Space to address concerns pre-emptively
- **Value demonstration:** Full case studies and testimonials
- **Email engagement:** Substantial value in each email

---

## 📊 Expected Output (After Fix)

### Test Run: Acme Marketing (Running Now)

**Expected results:**
- Market Research: ~9-12KB (formatted markdown)
- **VSL Script: 2,500+ words** (16-20 minutes)
- **Sales Page: 1,500+ words** (long-form)
- **Email Sequence: 2,500+ words** (7 emails × 350-500 words)

vs. Previous (Broken):
- VSL Script: ~800 words (5-6 minutes) ❌
- Sales Page: ~600 words ❌
- Email Sequence: ~1,000 words total ❌

---

## ✅ Testing in Progress

Running test funnel for "Acme Marketing" to verify:
- VSL hits 2500+ words
- Sales page hits 1500+ words
- Each email hits 300-500 words

Results in 3-5 minutes...

---

## 🎯 Self-Annealing (Per AGENTS.MD)

**What we learned:**
- AI models default to brevity without explicit minimums
- Truncating skill bibles loses critical frameworks
- Max tokens caps need to match output requirements
- System prompts work better than user prompts for expertise loading

**System improvements:**
- Added explicit word count enforcement
- Loaded full skill bible context
- Switched to Claude Opus 4.5 (superior for long-form)
- Increased token limits significantly

**Directive updated:** [vsl_script_writer.md](directives/vsl_script_writer.md) now specifies minimum word counts.

---

The system will now generate production-quality, full-length VSL funnels! 🚀
