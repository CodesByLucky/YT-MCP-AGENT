# YouTube MCP Agent

An AI-powered YouTube video assistant that extracts transcripts and generates content using [OpenRouter](https://openrouter.ai/) and the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

> Give it any YouTube link and it can summarize the video, write blog posts, create social media content, and generate chapter timestamps — all from the transcript.

---

## Features

| Feature | Description |
|---|---|
| **Transcript Extraction** | Fetches full timestamped transcripts from any YouTube video |
| **Blog Post Generation** | Creates structured blog posts from video content |
| **Social Media Posts** | Generates platform-specific posts (Twitter, LinkedIn, Instagram) |
| **Video Chapters** | Extracts chapter timestamps with clickable links |
| **Multi-Model Support** | Works with any model on OpenRouter (300+ models) |

## Tech Stack

- **Python 3.13+** with async/await
- **OpenAI Agents SDK** — agent orchestration with streaming
- **MCP Server** — tool definitions via Model Context Protocol
- **OpenRouter** — unified API for 300+ language models
- **youtube-transcript-api** — transcript extraction

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- [OpenRouter API key](https://openrouter.ai/settings/keys)

### Setup

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Configure your API key**
   
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=sk-or-v1-your-key-here
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct:free
   ```

   > **Note:** Free models require your OpenRouter [privacy settings](https://openrouter.ai/settings/privacy) to allow data sharing with providers.

3. **Run the agent**
   ```bash
   uv run main.py
   ```

### Usage

```
=== YouTube Agent ===
Model: meta-llama/llama-3.3-70b-instruct:free
Type 'exit' to quit

User: Summarize this: https://www.youtube.com/watch?v=dQw4w9WgXcQ

-- Fetching transcript...
-- Done.

Agent: Here's a summary of the video...
```

**Try these prompts:**
- `Summarize this: <youtube-url>`
- `Write a blog post about this video: <youtube-url>`
- `Generate chapter timestamps: <youtube-url>`
- `Write a LinkedIn post about: <youtube-url>`

## Project Structure

```
├── main.py                          # Agent entry point (OpenRouter + streaming)
├── mcp-server/
│   ├── yt-mcp.py                    # MCP server (tools + prompts)
│   └── prompts/
│       ├── system_instructions.md   # Agent system prompt
│       ├── write_blog_post.md       # Blog writing instructions
│       ├── write_social_post.md     # Social media instructions
│       └── write_video_chapters.md  # Chapter generation instructions
├── pyproject.toml                   # Dependencies
├── .env                             # API keys (not tracked)
└── .gitignore
```

## Changing Models

Edit the `OPENAI_MODEL` value in `.env` to use any OpenRouter model:

```env
# Free models with tool calling support
OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct:free
OPENAI_MODEL=mistralai/mistral-small-3.1-24b-instruct:free
OPENAI_MODEL=qwen/qwen3-235b-a22b:free

# Paid models (better reliability)
OPENAI_MODEL=openai/gpt-4o
OPENAI_MODEL=anthropic/claude-sonnet-4
```

Browse all models at [openrouter.ai/models](https://openrouter.ai/models).

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
