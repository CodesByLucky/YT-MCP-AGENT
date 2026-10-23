"""MCP server exposing YouTube transcript and task-instruction tools.

Run over stdio by the agent in main.py. Keeping tools here, outside the
agent, means new capabilities can be added without changing agent code.
"""
import logging
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi

# Keep MCP INFO logs out of the chat output
logging.getLogger("mcp").setLevel(logging.WARNING)

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
AVAILABLE_INSTRUCTIONS = ("write_blog_post", "write_social_post", "write_video_chapters")
VIDEO_ID_PATTERN = re.compile(r"(?:v=|/)([0-9A-Za-z_-]{11})")

mcp = FastMCP("yt-mcp")


def extract_video_id(url: str) -> str:
    """Return the 11-character video ID from watch, youtu.be, shorts or embed URLs."""
    match = VIDEO_ID_PATTERN.search(url)
    if not match:
        raise ValueError(f"Could not find a YouTube video ID in: {url}")
    return match.group(1)


def format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


@mcp.prompt()
def system_prompt() -> str:
    """Instructions for the YouTube video agent."""
    return (PROMPTS_DIR / "system_instructions.md").read_text(encoding="utf-8")


@mcp.tool()
def fetch_video_transcript(url: str) -> str:
    """
    Fetch the transcript of a YouTube video with timestamps.

    Args:
        url: YouTube video URL (watch, youtu.be, shorts or embed link)

    Returns:
        The canonical video URL on the first line, then one transcript entry per
        line as "[MM:SS] text" (or "[H:MM:SS] text" for long videos). To link to a
        moment, append "&t=<seconds>s" to the video URL.
    """
    video_id = extract_video_id(url)
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
    except Exception as exc:
        raise RuntimeError(f"Could not fetch a transcript for video {video_id}: {exc}") from exc

    lines = [f"Video URL: https://www.youtube.com/watch?v={video_id}"]
    lines += [f"[{format_timestamp(entry.start)}] {entry.text}" for entry in transcript]
    return "\n".join(lines)


@mcp.tool()
def fetch_instructions(prompt_name: str) -> str:
    """
    Fetch step-by-step instructions for a content task.

    Args:
        prompt_name: One of write_blog_post, write_social_post, write_video_chapters

    Returns:
        The instructions for that task, in markdown.
    """
    if prompt_name not in AVAILABLE_INSTRUCTIONS:
        raise ValueError(
            f"Unknown prompt '{prompt_name}'. Use one of: {', '.join(AVAILABLE_INSTRUCTIONS)}"
        )
    return (PROMPTS_DIR / f"{prompt_name}.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run(transport="stdio")
