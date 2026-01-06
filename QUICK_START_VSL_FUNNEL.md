# VSL Funnel System - Quick Start Guide

**Status:** ✅ All scripts built and ready to test!

---

## 🚀 Generate a Complete VSL Funnel (One Command!)

```bash
python3 execution/generate_complete_vsl_funnel.py \
  --company "Client Ascension" \
  --website "https://clientascension.com" \
  --offer "Agency Growth System"
```

**That's it!** This single command generates:
1. Market Research (Perplexity AI)
2. VSL Script (12-15 minutes, with hooks)
3. Sales Page Copy (headlines, bullets, CTA)
4. Email Sequence (7 emails)
5. Google Docs (optional, if credentials configured)
6. Slack Notification (optional, if webhook configured)

---

## 📋 What Gets Created

After 4-6 minutes, you'll have:

```
.tmp/vsl_funnel_client_ascension_20260105/
├── 01_research.json           # Comprehensive market research
├── 02_vsl_script.md            # Complete VSL script (1800+ words)
├── 02_vsl_hooks.md             # 3 hook options for A/B testing
├── 03_sales_page.md            # Landing page copy
├── 04_email_sequence.md        # 7-email nurture sequence
└── result.json                 # Execution metadata
```

---

## 🎯 Testing Individual Steps

### 1. Test Market Research Only
```bash
python3 execution/research_company_offer.py \
  --company "Test Company" \
  --website "https://example.com" \
  --offer "Test Offer" \
  --output .tmp/test_research.json
```
**Time:** ~30 seconds
**Output:** Comprehensive research dossier

### 2. Test VSL Script Generation
```bash
python3 execution/generate_vsl_script.py \
  --research .tmp/vsl_test/client_ascension_research.json \
  --length medium \
  --style education \
  --output .tmp/test_vsl_script.md \
  --hooks-output .tmp/test_hooks.md
```
**Time:** ~60 seconds
**Output:** VSL script + hook options

### 3. Test Sales Page Generation
```bash
python3 execution/generate_sales_page.py \
  --research .tmp/vsl_test/client_ascension_research.json \
  --vsl-script .tmp/test_vsl_script.md \
  --style full \
  --output .tmp/test_sales_page.md
```
**Time:** ~45 seconds
**Output:** Sales page copy

### 4. Test Email Sequence
```bash
python3 execution/generate_email_sequence.py \
  --research .tmp/vsl_test/client_ascension_research.json \
  --vsl-script .tmp/test_vsl_script.md \
  --sales-page .tmp/test_sales_page.md \
  --length 7 \
  --output .tmp/test_emails.md
```
**Time:** ~60 seconds
**Output:** 7-email sequence

---

## ⚙️ Configuration Options

### VSL Length
```bash
--vsl-length short    # 5-8 minutes (1200-1500 words)
--vsl-length medium   # 12-15 minutes (1800-2200 words) [DEFAULT]
--vsl-length long     # 20-25 minutes (2500-3000 words)
```

### VSL Style
```bash
--vsl-style education    # Teaching/mechanism focused [DEFAULT]
--vsl-style story        # Narrative-driven
--vsl-style case-study   # Social proof heavy
```

### Email Sequence Length
```bash
--email-count 5    # Shorter sequence
--email-count 7    # Full sequence [DEFAULT]
```

---

## 🔑 Required API Keys

### Already Configured ✅
- `OPENAI_API_KEY` or `OPENROUTER_API_KEY` - AI generation
- `PERPLEXITY_API_KEY` - Market research

### Optional (For Full Pipeline)
Add to [.env](.env):

```bash
# Google Docs (for document creation)
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# Slack (for notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Without these:** System still works! It just saves files locally instead.

---

## 📊 Example Output

### Input
```
Company: Client Ascension
Website: clientascension.com
Offer: Agency Growth System
```

### Output (4 minutes later)
- **Market Research:** 11KB JSON with pain points, audience, proof
- **VSL Script:** 2,200 words, 13-minute estimated length
- **Sales Page:** Headlines, bullets, testimonials, FAQ
- **Email Sequence:** 7 emails with subject lines, CTAs

---

## 🧪 Test Right Now!

Try it on any company:

```bash
# Example 1: Test on your own company
python3 execution/generate_complete_vsl_funnel.py \
  --company "Your Company" \
  --website "https://yoursite.com" \
  --offer "Your Main Offer"

# Example 2: Test on a competitor
python3 execution/generate_complete_vsl_funnel.py \
  --company "Competitor Name" \
  --website "https://competitor.com" \
  --offer "Their Product"

# Example 3: Generate for a client
python3 execution/generate_complete_vsl_funnel.py \
  --company "Client Name" \
  --website "https://clientsite.com" \
  --offer "Client's Service" \
  --industry "SaaS" \
  --price "$997/mo"
```

---

## 🐛 Troubleshooting

### "openai library not found"
```bash
pip install openai python-dotenv requests
```

### "google-api-python-client not found"
```bash
pip install google-api-python-client google-auth
```

### VSL generation fails
- Check API key is valid: `echo $OPENAI_API_KEY`
- Try using OpenRouter instead (already configured)
- Reduce VSL length: `--vsl-length short`

### Research returns empty data
- Verify Perplexity API key
- Check website URL is accessible
- Try adding `--industry` parameter

---

## 🎯 Next Steps After Testing

1. **Review generated content** - Check quality and relevance
2. **Configure Google Docs** - For automatic document creation
3. **Set up Slack webhook** - For completion notifications
4. **Convert to Trigger.dev** - For production deployment

---

## 📚 Full Documentation

- [VSL_FUNNEL_SYSTEM.md](VSL_FUNNEL_SYSTEM.md) - Complete system overview
- [directives/vsl_funnel_orchestrator.md](directives/vsl_funnel_orchestrator.md) - Detailed workflow
- [directives/company_market_research.md](directives/company_market_research.md) - Research process
- [directives/vsl_script_writer.md](directives/vsl_script_writer.md) - Script generation

---

## ✅ Scripts Created

All execution scripts are ready:

1. ✅ [execution/research_company_offer.py](execution/research_company_offer.py) - Market research
2. ✅ [execution/generate_vsl_script.py](execution/generate_vsl_script.py) - VSL script
3. ✅ [execution/generate_sales_page.py](execution/generate_sales_page.py) - Sales page
4. ✅ [execution/generate_email_sequence.py](execution/generate_email_sequence.py) - Email sequence
5. ✅ [execution/create_google_doc.py](execution/create_google_doc.py) - Google Docs
6. ✅ [execution/send_slack_notification.py](execution/send_slack_notification.py) - Slack
7. ✅ [execution/generate_complete_vsl_funnel.py](execution/generate_complete_vsl_funnel.py) - Orchestrator

---

**Ready to generate VSL funnels in minutes!** 🚀
