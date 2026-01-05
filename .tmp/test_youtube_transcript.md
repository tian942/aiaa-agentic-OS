# YouTube Transcript MCP Test

## Installation Status
✅ **MCP Server Installed Successfully**
- **Server Name**: youtube-transcript-enhanced
- **Package**: @kimtaeyoon83/mcp-server-youtube-transcript
- **Status**: Connected
- **Type**: stdio

## Available Features
The MCP server provides the `get_transcript` tool with:

### Parameters
- **url** (required): YouTube video URL, Shorts URL, or video ID
- **lang** (optional, default: "en"): Language code with automatic fallback
- **include_timestamps** (optional, default: false): Add time codes like "[0:05]"
- **strip_ads** (optional, default: true): Remove sponsorship/ad content

### Key Capabilities
- Multiple URL format support (full URLs, shorts, video IDs)
- Language-specific retrieval with automatic fallback
- Optional timestamp insertion
- Built-in ad/sponsorship filtering based on chapters
- No external API dependencies

## Configuration Locations

### 1. Claude Desktop
Location: `/Users/lucasnolan/Library/Application Support/Claude/claude_desktop_config.json`
```json
"youtube-transcript-enhanced": {
  "command": "npx",
  "args": ["-y", "@kimtaeyoon83/mcp-server-youtube-transcript"]
}
```

### 2. Claude Code CLI
Location: `/Users/lucasnolan/.claude.json`
Status: ✓ Connected

## Next Steps
To use the MCP server:
1. Restart Claude Desktop to enable the server there
2. In Claude Code CLI, the server is already active and ready to use
3. Simply reference YouTube URLs in your requests and the transcript functionality will be available

## Test Ready
The MCP server is now ready to fetch transcripts from any YouTube video!
