# PROJECT HANDOFF: Skill Bible Extraction System

## For Claude Code - Pick Up Exactly Where We Left Off

**Last Updated:** January 5, 2026
**Project Location:** `/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows`

---

## SECTION 1: WHAT WE'RE BUILDING

### The Vision

We're building an **Autonomous Idea Execution System** based on the PDF at:
`/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/Autonomous Idea Execution System.pdf`

The system uses a 3-layer architecture:
1. **Directives** (SOPs in `/directives/`) - What to do
2. **Orchestration** (AI agent) - Decision making
3. **Execution** (Python scripts in `/execution/`) - Deterministic tools

### The Skill Bible Component

**Skill Bibles** are comprehensive knowledge documents that give the AI agent deep domain expertise. They live in `/skills/SKILL_BIBLE_*.md`.

Each Skill Bible contains:
- Executive Summary
- Core Principles & Frameworks
- Techniques & Tactics
- Step-by-step implementation
- Case Studies
- Common Mistakes & Fixes
- AI Parsing Guide (for agent integration)

**Why this matters:** When the agent receives a task like "write a VSL," it loads the relevant Skill Bible(s) to have expert-level knowledge before execution.

---

## SECTION 2: WHAT HAS BEEN COMPLETED

### Phase 1: Original Skill Bibles (50 total, ~75,700 words)
Created 50 comprehensive Skill Bibles covering agency fundamentals:
- Cold email mastery
- Funnel copywriting
- Sales closing
- Offer creation
- And 46 more

### Phase 2: YouTube Transcript Extraction System

**Tools Built:**
- `yt-dlp` installed for downloading video metadata and subtitles
- `/execution/parse_vtt_transcript.py` - Converts VTT subtitle files to clean text

**Process:**
1. Use yt-dlp to download VTT subtitles from YouTube videos
2. Parse VTT files to clean readable text using the parser script
3. Read transcripts and create comprehensive Skill Bibles

### Phase 3: Jeremy Haynes Extraction (COMPLETE)
- **Source:** Jeremy Haynes YouTube channel (million-dollar-month agency owner)
- **Transcripts:** 30 downloaded, 29 parsed successfully
- **Skill Bibles Created:** 16 (~159,000 words)
- **Location:** `/skills/SKILL_BIBLE_*` (files with Jeremy Haynes attribution)

**Topics covered:**
- Call funnel mastery
- Show rate optimization
- Value-dense emails
- Webinar funnel launch
- Follow-up systems (CRM Dissertation)
- Cold ads mastery
- Sales mindset
- Challenge funnel mastery
- Case study creation
- Selling to rich people
- Low/high ticket strategies
- Exclusivity tactics
- Meta algorithm adaptation

### Phase 4: Matthew Larsen Extraction (COMPLETE)
- **Source:** Matthew Larsen YouTube channel (1000x Leads, agency scaling)
- **Transcripts:** 28 downloaded and parsed
- **Skill Bibles Created:** 23 (~175,000 words)
- **Location:** Various skill bibles with Larsen attribution
- **Video list:** `.tmp/matthew_larsen_videos.md`

**Topics covered:**
- Agency offer creation
- B2B lead generation
- Agency sales process
- Agency scaling roadmap
- Funnel building
- Hiring systems
- All lead gen methods
- Four ad funnel types
- Lead magnet funnels
- Digital product funnels
- Agency models (3 types)
- Webinar mastery
- And more

### Phase 5: Daniel Fazio Extraction (PARTIALLY COMPLETE - THIS IS WHERE YOU PICK UP)
- **Source:** Daniel Fazio YouTube channel (Client Ascension, ListKit - $500K-$1.1M+/month)
- **Transcripts Downloaded:** 40 VTT files
- **Transcripts Parsed:** 40 clean text files
- **Skill Bibles Created:** 32 (~260,000 words)
- **Transcript Location:** `.tmp/transcripts_fazio/parsed/`

---

## SECTION 3: DANIEL FAZIO - WHAT'S BEEN DONE

### Skill Bibles Already Created (32):

1. `SKILL_BIBLE_vsl_script_mastery_fazio.md` - $5M/$10M VSL methodology
2. `SKILL_BIBLE_self_liquidating_funnels.md` - $1.17M/month system
3. `SKILL_BIBLE_paid_ads_scaling_500k.md` - Complete ads scaling with qualification
4. `SKILL_BIBLE_value_proposition_fazio.md` - The "so that" framework
5. `SKILL_BIBLE_offer_formulation_fazio.md` - 4-component system
6. `SKILL_BIBLE_pricing_strategy_fazio.md` - Maximum profit pricing
7. `SKILL_BIBLE_social_proof_flywheel.md` - Case study machine methodology
8. `SKILL_BIBLE_30_business_lessons.md` - 30 lessons at $500K/month
9. `SKILL_BIBLE_twitter_masterclass_fazio.md` - 91K followers, $3M+ system
10. `SKILL_BIBLE_mathematical_client_signing.md` - Physics of sales
11. `SKILL_BIBLE_100k_in_24_months.md` - Complete roadmap from zero
12. `SKILL_BIBLE_8_steps_to_5_million.md` - $5.7M system documentation
13. `SKILL_BIBLE_roi_calculator_selling.md` - Logic-based closing
14. `SKILL_BIBLE_100k_from_scratch.md` - Zero to $100K with $500 budget
15. `SKILL_BIBLE_30_ways_to_sign_clients.md` - All 30 methods documented
16. `SKILL_BIBLE_stop_selling_poor_people.md` - Filtering and qualification
17. `SKILL_BIBLE_fastest_10_clients.md` - 3-pillar acceleration system
18. `SKILL_BIBLE_200k_organic_system.md` - Email-first content ecosystem
19. `SKILL_BIBLE_5_laws_of_selling.md` - Immutable selling principles
20. `SKILL_BIBLE_agency_checklist_az.md` - Complete A-Z to $50K/month
21. `SKILL_BIBLE_signing_clients_no_results.md` - Zero case study method
22. `SKILL_BIBLE_client_retention_ltv.md` - 4-step retention system
23. `SKILL_BIBLE_front_end_cold_traffic_offers.md` - Cold vs warm traffic
24. `SKILL_BIBLE_buying_customers.md` - $10.9M CAC/LTV method
25. `SKILL_BIBLE_0_to_7_million_story.md` - Daniel's complete journey
26. `SKILL_BIBLE_829k_month_breakdown.md` - Complete $829K month system
27. `SKILL_BIBLE_charging_more_money.md` - Three mechanisms to raise prices
28. `SKILL_BIBLE_8x_results_80_less_effort.md` - Efficiency and consistency

### Transcripts Already Processed (content used for above skill bibles):

```
✅ My $5 Million VSL Script [N_qAgrRfXpo].en.txt
✅ My $10M VSL Script - How to Use AI to Write Video Sales Letters [mehSj3hik8k].en.txt
✅ How to make $1,000,000⧸mo using self liquidating funnels (FREE COURSE) [By4MPc6yyFA].en.txt
✅ How to Scale an Agency to $500k⧸mo+ With Paid Ads [qK4vUCd4feA].en.txt
✅ How to Make a Value Proposition that Signs Clients [T__7hbEppcA].en.txt
✅ Offer Formulation： Getting Clients & Signing More Deals [opE6MRW9Ceg].en.txt
✅ How to price your services for maximum profit [EiTKmdNGzkM].en.txt
✅ Social Proof Flywheel： How To Use Social Proof To Sign More Clients [386ncFwz7B0].en.txt
✅ 30 Business Lessons I Learned Making $500,000⧸mo [BOQbr-9wu2U].en.txt
✅ Twitter Masterclass： Step-By-Step How To Grow Followers & Make Money [aSdn-lLZ-og].en.txt
✅ The Mathematical Process for Signing Clients [YxtH-9K8bCg].en.txt
✅ How to make $100,000⧸mo in 24 months [GXLj7Mjz4QY].en.txt
✅ These 8 steps made me $5,769,083 [musv0FW-6v4].en.txt
✅ The ROI Calculator： Sign More Clients Using Pure Logic [FepWs1qV3xg].en.txt
✅ Building a $100k⧸mo Online Business From Scratch [h3sLVFJsJc8].en.txt
✅ 30 Different Ways to Sign Clients for Your Business [vNDcpTtFuQ8].en.txt
✅ How to Stop Selling to Poor People & Sign Better Clients [9dRQ7lOAk2M].en.txt
✅ Fastest Way to Sign 10+ Clients in a Month [-ep4Rjl0qUM].en.txt
✅ The $200k⧸mo organic content system [eVdDY08Rs38].en.txt
✅ The 5 Laws of Selling & Marketing [XQ4VQWXvfKc].en.txt
✅ A Step-by-Step, A-Z Checklist for Building a Successful Agency [BZ5V6rrxInk].en.txt
✅ How To Sign Clients When You HAVE No Clients (Or Results) [2GaqJ-QQO3g].en.txt
✅ 4 Steps To Keep Your Clients Longer [_Wd5_JhfNGo].en.txt
✅ Why you need a front-end COLD TRAFFIC offer [sxjjIkIZ6Pg].en.txt
✅ How I BUY customers (I made $10.9M doing this) [6IOoVKyWvuk].en.txt
✅ How I Went From 0 to $7 Million by 26 [RRibtRvWAY4].en.txt
✅ I Made $829K Last Month, Here's Everything I Did [8L7DdL53FTY].en.txt
✅ How to Charge More Money and Still Sign Clients [bnEabDi_64E].en.txt
✅ How to get 8x more clients with 80% less effort [1h9mZTFWckg].en.txt
✅ Getting Clients, Guarantees, Scaling, Offers, Systems [G5bpHxz5QIQ].en.txt (PARTIALLY - very long)
```

---

## SECTION 4: DANIEL FAZIO - WHAT STILL NEEDS TO BE DONE

### Transcripts NOT Yet Processed Into Skill Bibles:

Check `.tmp/transcripts_fazio/parsed/` for these files:

```
❌ Creating Offers That Sell： Selling Asymmetric Opportunities [7JcS3TzRNnM].en.txt
❌ How To ACTUALLY Turn Cold DM's & Cold Emails Into Sales [a76Y8q5EBqY].en.txt
❌ How To Sell Any B2B Offer [pp0rGFgTGiU].en.txt
❌ How to create an offer that ACTUALLY sells [Qmu8t2fh_zM].en.txt
❌ How to get an Agency⧸B2B Business to $30k⧸mo+ as Fast as Possible [WqcTGkI7GOs].en.txt
❌ How to Scale a Marketing Agency to $100k⧸mo (FREE COURSE) [1T8CmTiA-Ks].en.txt
❌ How I Make $1,000,000 Per Month At 27 Years Old [lYUugyOKIcA].en.txt
❌ I made $10 million. Steal my Lead Generation Guide [hQXzKx2xWhc].en.txt
❌ If I Had to Reach $30,000⧸mo Again from Zero [jlA3f8SiE7Y].en.txt
❌ Offer Positioning： How to Get More Clients [4uai8ZqWMmc].en.txt
```

### How To Process Remaining Transcripts:

1. **Read the transcript:**
```
Read file: /Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/.tmp/transcripts_fazio/parsed/[FILENAME].en.txt
```

2. **Create comprehensive Skill Bible:**
- Follow the same format as existing skill bibles
- Include: Executive Summary, Core Concepts, Frameworks, Implementation Steps, AI Parsing Guide
- Minimum 2,000+ words with substantial depth
- Attribution to Daniel Fazio with video reference

3. **Save to skills directory:**
```
Create file: /Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/skills/SKILL_BIBLE_[topic_name].md
```

---

## SECTION 5: SKILL BIBLE FORMAT TEMPLATE

Use this format for consistency:

```markdown
# SKILL BIBLE: [Topic Name] (Daniel Fazio Method)

## Executive Summary

[2-3 paragraph summary of the core concept and why it matters]

**Key Quote:** "[Memorable quote from the video]"

---

## Section 1: [Core Concept]

### [Subsection]

[Content with tables, bullet points, code blocks as needed]

---

## Section 2: [Framework/Process]

### [Step-by-step breakdown]

[Include specific numbers, examples, formulas]

---

## Section 3: [Implementation]

### Checklist

- [ ] Step 1
- [ ] Step 2
- [ ] etc.

---

## Section N: AI Parsing Guide

### For Agentic Systems

**When to invoke this skill:**
- [Trigger condition 1]
- [Trigger condition 2]

**Required inputs:**
- [Input 1]
- [Input 2]

**Execution sequence:**
1. [Step 1]
2. [Step 2]

**Integration points:**
- `SKILL_BIBLE_related_skill.md` - [How it connects]

---

## Source Attribution

**Primary Source:** Daniel Fazio
- Co-founder: Client Ascension, ListKit
- Revenue: [relevant metric]

**Video Referenced:**
- "[Video Title]"

**Key Quote:** "[Another key quote]"
```

---

## SECTION 6: FILE LOCATIONS REFERENCE

### Key Directories

```
/Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows/
├── skills/                          # All Skill Bibles go here
│   └── SKILL_BIBLE_*.md            # 140+ files
├── directives/                      # SOP documents (102 total)
├── execution/                       # Python scripts
│   └── parse_vtt_transcript.py     # VTT parser tool
├── .tmp/                           # Temporary files (not committed)
│   ├── transcripts_fazio/          # Daniel Fazio transcripts
│   │   └── parsed/                 # Clean text files (40 files)
│   ├── transcripts_larsen/         # Matthew Larsen transcripts
│   │   └── parsed/                 # Clean text files
│   └── matthew_larsen_videos.md    # Video list
├── AGENTS.md                       # Agent instructions (mirrored)
├── CLAUDE.md                       # Agent instructions (mirrored)
└── Autonomous Idea Execution System.pdf  # The vision document
```

### Transcript Parsing (if needed for new channels)

```bash
# Download subtitles with yt-dlp
yt-dlp --write-auto-sub --sub-lang en --skip-download -o ".tmp/transcripts_[channel]/%(title)s [%(id)s]" "[VIDEO_URL]"

# Parse VTT to clean text
python3 execution/parse_vtt_transcript.py ".tmp/transcripts_[channel]/[filename].en.vtt"
```

---

## SECTION 7: CURRENT TOTALS

| Source | Skill Bibles | Estimated Words |
|--------|-------------|-----------------|
| Original 50 | 50 | ~75,700 |
| Jeremy Haynes | 16 | ~159,000 |
| Matthew Larsen | 23 | ~175,000 |
| Daniel Fazio | 32 | ~260,000 |
| **TOTAL** | **121** | **~670,000** |

---

## SECTION 8: IMMEDIATE NEXT STEPS

### Option A: Finish Daniel Fazio Extraction

1. List remaining unprocessed transcripts in `.tmp/transcripts_fazio/parsed/`
2. Read each transcript
3. Create skill bible following the template
4. Repeat until all 40 transcripts have corresponding skill bibles

### Option B: Expand to New YouTube Channels

**Potential channels to extract:**
- Alex Hormozi (offers, scaling)
- Cole Gordon (sales, appointment setting)
- Serge Gatari (agency scaling)
- Iman Gadzhi (agency fundamentals)

**Process:**
1. Use yt-dlp to download video list and subtitles
2. Parse VTT files to clean text
3. Create skill bibles from transcripts

### Option C: Build Missing System Components

Per the Autonomous Idea Execution System PDF:
- Quality gate validators (Python scripts)
- Pre/post execution hooks
- Auto-delivery pipeline (Google Docs + Slack)
- Self-annealing feedback loops

---

## SECTION 9: VERIFICATION COMMANDS

### Check Current Skill Bible Count
```bash
ls -la skills/SKILL_BIBLE_*.md | wc -l
```

### Check Fazio Transcript Count
```bash
ls -la .tmp/transcripts_fazio/parsed/*.txt | wc -l
```

### List All Skill Bibles
```bash
ls skills/SKILL_BIBLE_*.md
```

### Check for Specific Topic Coverage
```bash
grep -l "Daniel Fazio" skills/SKILL_BIBLE_*.md | wc -l
```

---

## SECTION 10: IMPORTANT CONTEXT

### About Daniel Fazio
- Co-founder of Client Ascension (coaching) and ListKit (software)
- Revenue: $500K-$1.1M+/month documented
- Focus: Cold email, VSLs, self-liquidating funnels, agency scaling
- Has worked with 1,000+ B2B clients
- Style: Very direct, practical, no-BS approach

### About the Skill Bible System
- Each skill bible should be comprehensive enough to make an AI agent an "expert"
- Include specific numbers, frameworks, and actionable steps
- The AI Parsing Guide section is crucial for agent integration
- Cross-reference related skill bibles for system coherence

### Model Preference
User prefers **Claude Opus 4** (or latest Opus) for quality content generation.

---

## SECTION 11: QUICK START FOR CLAUDE CODE

```
1. Navigate to: /Users/lucasnolan/Documents/Work/Client Ascension/AI Development/Agentic Workflows

2. Check remaining Fazio transcripts:
   ls .tmp/transcripts_fazio/parsed/

3. Compare against created skill bibles:
   ls skills/SKILL_BIBLE_*fazio*.md
   (Note: Not all have "fazio" in name - check content)

4. Read an unprocessed transcript:
   cat .tmp/transcripts_fazio/parsed/[filename].txt

5. Create skill bible:
   Create comprehensive markdown file following template above
   Save to skills/SKILL_BIBLE_[topic].md

6. Repeat until all valuable transcripts are processed
```

---

**END OF HANDOFF DOCUMENT**

*This document was created to enable seamless continuation of the Skill Bible extraction project. All file paths are absolute. All context is preserved.*
