# YouTube Knowledge Miner

## What This Workflow Is

An automated system that extracts best practices and how-to knowledge from top YouTube channels in any niche, converts video content into structured manuals, and generates comprehensive skill bibles for AI automation.

## What It Does

1. **Find Top Channels** - Search YouTube for authority channels in your niche
2. **Extract Best Videos** - Get highest-performing educational videos
3. **Transcribe Content** - Use Whisper or Gemini for accurate transcription
4. **Convert to Manuals** - Transform transcripts into structured how-to guides
5. **Filter Quality** - Rate and filter manuals worth keeping
6. **Generate Skill Bibles** - Synthesize multiple sources into comprehensive guides

## Prerequisites

**Required API Keys:**
- `OPENROUTER_API_KEY` - For Claude manual generation
- YouTube Data API enabled in Google Cloud Console

**Optional:**
- `OPENAI_API_KEY` - For Whisper transcription (fallback only)
- `GOOGLE_API_KEY` - For Gemini (cheaper alternative)

**Installation:**
```bash
pip install google-api-python-client google-auth google-auth-oauthlib youtube-transcript-api python-dotenv
```

**Note:** Primary transcript source is YouTube's built-in captions (free, fast). Falls back to Whisper transcription if captions unavailable.

**Rate Limiting:** YouTube may temporarily block transcript requests from your IP. Solutions:
1. Wait 5-10 minutes between large batch runs
2. Export cookies from your browser to `youtube_cookies.txt` in the project root
3. Use `--parallel 1` to process videos sequentially

## How to Run

```bash
# Basic usage - mine knowledge from a niche
python3 execution/youtube_knowledge_miner.py \
  --niche "meta ads" "facebook advertising" \
  --max-channels 10 \
  --videos-per-channel 5

# Use Gemini for cheaper processing
python3 execution/youtube_knowledge_miner.py \
  --niche "cold email" "lead generation" \
  --use-gemini \
  --max-channels 5

# Full options
python3 execution/youtube_knowledge_miner.py \
  --niche "landing page copywriting" \
  --max-channels 15 \
  --videos-per-channel 10 \
  --min-subscribers 10000 \
  --min-views 10000 \
  --min-skill-rating 8 \
  --output-dir .tmp/landing_page_knowledge \
  --parallel 5
```

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--niche` | list | Yes | - | Keywords to search (can provide multiple) |
| `--max-channels` | int | No | 10 | Maximum channels to analyze |
| `--videos-per-channel` | int | No | 5 | Videos to process per channel |
| `--min-subscribers` | int | No | 5000 | Minimum channel subscribers |
| `--min-views` | int | No | 5000 | Minimum video views |
| `--min-skill-rating` | int | No | 7 | Minimum quality rating (1-10) |
| `--use-gemini` | flag | No | False | Use Gemini Flash (cheaper) |
| `--output-dir` | string | No | .tmp/knowledge_mine | Output directory |
| `--parallel` | int | No | 3 | Parallel video processing |

## Process

### Step 1: Channel Discovery
- Search YouTube Data API for channels matching keywords
- Filter by subscriber count and video count
- Rank by authority metrics

### Step 2: Video Selection
- Get uploads playlist for each channel
- Filter by view count and duration
- Select top-performing educational content

### Step 3: Audio Extraction
- Download audio using yt-dlp
- Optimize for transcription quality

### Step 4: Transcription
- Use Whisper (OpenAI) for accurate transcription
- Alternative: Gemini Flash for cost savings
- Handle long videos with chunking

### Step 5: Manual Generation
- Send transcript to Claude/Gemini
- Generate structured how-to format:
  - Executive Summary
  - Key Concepts
  - Step-by-Step Process
  - Best Practices
  - Common Mistakes
  - Actionable Takeaways
  - Skill Rating

### Step 6: Quality Filtering
- AI rates each manual 1-10
- Filter by minimum rating
- Rank by potential automation value

### Step 7: Skill Bible Synthesis
- Combine multiple high-quality manuals
- Generate comprehensive skill bible
- Save to skills/ directory

## Outputs

```
.tmp/knowledge_mine/
├── channels.json           # Found channels
├── videos.json            # Selected videos
├── manuals/               # Individual how-to manuals
│   ├── video_title_1.md
│   └── video_title_2.md
├── manuals_index.json     # Manual metadata
├── SKILL_BIBLE_*.md       # Generated skill bible
└── audio/                 # Temporary (cleaned up)
```

## Quality Gates

- [ ] Found at least 3 qualifying channels
- [ ] Processed at least 5 videos successfully
- [ ] At least 3 manuals rated 7+ 
- [ ] Skill bible generated and saved

## Cost Estimates

| Component | Cost per Video |
|-----------|---------------|
| YouTube API | Free (10K quota/day) |
| Whisper transcription | ~$0.006/min |
| Claude manual generation | ~$0.03/video |
| Gemini (alternative) | ~$0.001/video |

**Typical run (10 channels, 5 videos each):**
- 50 videos x 15 min avg = 750 minutes
- Whisper: ~$4.50
- Claude: ~$1.50
- **Total: ~$6.00**

## Related Workflows

- `youtube_channel_finder.md` - Just find channels
- `full_campaign_pipeline.md` - Use skill bibles in campaigns
- `youtube_to_campaign_pipeline.md` - Complete automation
