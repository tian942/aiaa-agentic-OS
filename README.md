# VSL Funnel Automation System + Trigger.dev Integration

**Status:** ✅ Production Ready
**Created:** 2026-01-05

---

## 🚀 Quick Start

### Generate Complete VSL Funnel (One Command)
```bash
python3 execution/generate_complete_vsl_funnel.py \
  --company "Client Name" \
  --website "https://clientsite.com" \
  --offer "Their Main Offer"
```

**Output (3-5 minutes):**
- Market Research Report (Google Doc)
- VSL Script (2500+ words, 16-20 min)
- Sales Page Copy (1500+ words)
- Email Sequence (7 emails, 300-500 words each)
- Slack notification with all links

---

## 📚 What's Included

### 1. VSL Funnel System (Complete & Working)
**7 Agentic Workflows:**
1. Company Market Research (Perplexity)
2. VSL Script Writer (Claude Opus 4.5 + Skill Bibles)
3. Sales Page Writer (Claude Opus 4.5)
4. Email Sequence Writer (Claude Opus 4.5)
5. Google Doc Creator (Standalone Utility)
6. Slack Notifier (Standalone Utility)
7. VSL Funnel Orchestrator (Master Coordinator)

**Key Features:**
- Follows AGENTS.MD 3-layer architecture
- Uses skill bibles for VSL frameworks
- Proper content length (2500+ word VSLs, 1500+ word sales pages)
- Formatted Google Docs (headers, bold, bullets)
- Complete automation (one command → complete funnel)

### 2. Trigger.dev Integration (Ready to Deploy)
- [trigger.config.ts](trigger.config.ts) configured
- [trigger/](trigger/) directory set up
- Conversion tools ready
- Dev server tested and working

---

## 📖 Documentation

### Start Here
- **[VSL_FUNNEL_COMPLETE.md](VSL_FUNNEL_COMPLETE.md)** - System overview
- **[QUICK_START_VSL_FUNNEL.md](QUICK_START_VSL_FUNNEL.md)** - Usage guide
- **[CONTENT_LENGTH_FIX.md](CONTENT_LENGTH_FIX.md)** - Recent improvements

### Trigger.dev
- **[TRIGGER_DEV_SETUP.md](TRIGGER_DEV_SETUP.md)** - Integration guide
- **[skills/SKILL_BIBLE_trigger_dev_automation.md](skills/SKILL_BIBLE_trigger_dev_automation.md)** - Comprehensive guide
- **[directives/upload_to_trigger_dev.md](directives/upload_to_trigger_dev.md)** - Conversion SOP

### Architecture
- **[AGENTS.MD](AGENTS.MD)** - System architecture
- **[CLAUDE.MD](CLAUDE.MD)** - Agent instructions

---

## 🔑 Configuration

### API Keys (all configured in .env)
- ✅ OPENAI_API_KEY
- ✅ OPENROUTER_API_KEY
- ✅ PERPLEXITY_API_KEY
- ✅ SLACK_WEBHOOK_URL

### Google OAuth
- ✅ client_secrets.json (OAuth client)
- ✅ token.pickle (auto-generated on first run)
- ✅ Folder ID: `1M_2lHBzVQuIv1fptf8BUfVcGJgL6jxf7`

---

## 📊 Content Standards (Enforced)

| Content Type | Minimum Words | Target Range | Duration |
|--------------|---------------|--------------|----------|
| VSL Script (short) | 2,000 | 2,000-2,500 | 13-17 min |
| VSL Script (medium) | 2,500 | 2,500-3,000 | 16-20 min |
| VSL Script (long) | 3,500 | 3,500-4,000 | 23-27 min |
| Sales Page | 1,500 | 1,500-3,000 | N/A |
| Email (each) | 300 | 300-500 | N/A |
| Total Sequence | 2,500 | 2,500-3,500 | 7 emails |

---

## 🏗️ Architecture

### 3-Layer System (Per AGENTS.MD)

**Layer 1: Directives** (What to do)
- 7 workflow SOPs in [directives/](directives/)
- Natural language instructions
- Quality gates and checklists

**Layer 2: Orchestration** (Decision making)
- Claude (intelligent routing)
- [generate_complete_vsl_funnel.py](execution/generate_complete_vsl_funnel.py:1) (pipeline coordinator)

**Layer 3: Execution** (Doing the work)
- 7 Python scripts in [execution/](execution/)
- Deterministic, testable, reliable
- Skill bible integration

---

## 🎯 Recent Improvements

### Content Length Fix (2026-01-05)
- VSL scripts now 2500+ words (was 800)
- Sales pages now 1500+ words (was 600)
- Emails now 300-500 words each (was 150-200)
- Using Claude Opus 4.5 (was GPT-4)
- Full skill bible context loaded (was truncated)

### Standalone Utilities
- Google Doc creator reusable by all workflows
- Slack notifier reusable by all workflows
- Proper markdown → Google Docs formatting

---

## 🚀 Next Steps

### Phase 1: Production Use (Ready Now!)
Generate VSL funnels for clients using Python scripts.

### Phase 2: Convert to Trigger.dev
- Convert workflows to TypeScript tasks
- Add webhook triggers
- Enable scheduled generation
- Full dashboard observability

### Phase 3: Expand
- Add more funnel types (webinar, challenge, etc.)
- Integrate with CRM
- A/B testing variants
- Performance tracking

---

## 📁 Project Structure

```
.
├── directives/              # 7 VSL funnel workflows + 60+ others
├── execution/               # Python scripts (deterministic layer)
├── skills/                  # 50+ skill bibles (75K+ words)
├── trigger/                 # Trigger.dev tasks (ready for deployment)
├── .tmp/                    # Generated funnels (gitignored)
├── AGENTS.MD                # System architecture
├── trigger.config.ts        # Trigger.dev configuration
└── README.md                # This file
```

---

## ✅ System Status

- ✅ VSL Funnel System: Operational
- ✅ Google Docs: Formatted correctly
- ✅ Slack Notifications: Working
- ✅ Content Length: Fixed (2500+ words)
- ✅ Model: Claude Opus 4.5
- ⏳ Trigger.dev: Ready for conversion

**The system can generate complete, professional VSL funnels in 3-5 minutes!** 🚀
