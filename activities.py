"""
Activities for HackerNews Tech Digest Workflow
"""

import os
import re
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiohttp

from mistralai.client import Mistral
from mistralai.workflows import activity

# Configuration
GMAIL_TO = "esulez@gmail.com"
GMAIL_SUBJECT = "HackerNews Tech Digest"

# Tech news domains to filter by
TECH_DOMAINS = {
    "techcrunch.com",
    "theverge.com",
    "arstechnica.com",
    "wired.com",
    "bloomberg.com",
    "reuters.com",
    "cnet.com",
    "engadget.com",
    "zdnet.com",
    "techradar.com",
    "theinformation.com",
    "protocol.com",
    "venturebeat.com",
    "businessinsider.com",
    "forbes.com",
    "fortune.com",
    "cnbc.com",
    "wsj.com",
    "nytimes.com",
    "bbc.com",
    "theregister.com",
    "anandtech.com",
    "tomshardware.com",
    "pcworld.com",
    "macworld.com",
    "androidauthority.com",
    "xda-developers.com",
    "9to5mac.com",
    "9to5google.com",
}

# TTS Configuration
TTS_MODEL = "voxtral-mini-tts-3-0"
TTS_VOICE = "voice_478"
TTS_FORMAT = "mp3"


@activity()
async def fetch_hn_stories() -> List[Dict[str, Any]]:
    """Fetch top stories from HackerNews API using aiohttp."""
    # Test: return a simple hardcoded value first
    return [{"id": 1, "title": "Test Story", "url": "https://example.com", "score": 100, "descendants": 10}]


@activity()
async def filter_tech_stories(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter stories to only tech industry news."""
    def is_tech_news(story: Dict[str, Any]) -> bool:
        url = story.get("url", "").lower()
        if not url:
            return False
        return any(domain in url for domain in TECH_DOMAINS)

    return [story for story in stories if is_tech_news(story)]


@activity()
async def generate_summary(stories: List[Dict[str, Any]]) -> str:
    """Generate a markdown summary of tech stories."""
    if not stories:
        return "No tech industry news found on HackerNews front page."

    summary_parts = [
        f"# HackerNews Tech Digest\n",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"\n",
        f"## Top {len(stories)} Tech Industry Stories\n",
        f"\n",
    ]

    for i, story in enumerate(stories, 1):
        title = story.get("title", "Untitled")
        url = story.get("url", "")
        score = story.get("score", 0)
        comments = story.get("descendants", 0)

        summary_parts.append(f"### {i}. [{title}]({url})\n")
        summary_parts.append(f"- **Score:** {score} | **Comments:** {comments}\n")
        summary_parts.append(f"\n")

    return "".join(summary_parts)


@activity()
async def generate_audio(summary_text: str, api_key: Optional[str] = None) -> bytes:
    """Generate audio summary using Mistral TTS."""
    # Get API key from environment if not provided
    # Try both MISTRAL_API_KEY and my_api_key (from deployment secrets)
    if api_key is None:
        api_key = os.environ.get("MISTRAL_API_KEY") or os.environ.get("my_api_key")
    
    if not api_key:
        raise ValueError("MISTRAL_API_KEY or my_api_key environment variable not set")
    
    # Extract story titles and create a clean audio text
    # Split by lines and process markdown
    lines = summary_text.split('\n')
    audio_text_parts = []

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        # Remove markdown headers
        if line.startswith('#'):
            text = line.lstrip('#').strip()
            # Remove markdown links [text](url)
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
            audio_text_parts.append(text)
        # Skip score/comment lines
        elif line.startswith('- **Score') or line.startswith('- **Comments'):
            continue
        # For story lines with markdown links, extract the text
        elif '[[' in line or '][' in line:
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
            text = re.sub(r'[#*\-]', '', text).strip()
            if text:
                audio_text_parts.append(text)

    audio_text = ' '.join(audio_text_parts)
    
    # If audio_text is empty, use the full summary as fallback
    if not audio_text.strip():
        audio_text = summary_text

    client = Mistral(api_key=api_key)
    response = client.audio.speech.complete(
        model=TTS_MODEL,
        input=audio_text,
        voice_id=TTS_VOICE,
        response_format=TTS_FORMAT,
    )

    audio_data = base64.b64decode(response.audio_data)
    return audio_data


@activity()
async def send_digest_email(summary: str, audio_data: bytes) -> Dict[str, Any]:
    """Send email with digest and audio attachment."""
    return {
        "to": GMAIL_TO,
        "subject": GMAIL_SUBJECT,
        "summary": summary,
        "audio_size": len(audio_data),
        "status": "ready_to_send"
    }
