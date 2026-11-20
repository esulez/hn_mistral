"""
Activities for HackerNews Tech Digest Workflow
"""

import os
import base64
import json
from pathlib import Path
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
async def generate_audio(summary_text: str, api_key: str) -> bytes:
    """Generate audio summary using Mistral TTS."""
    lines = summary_text.split('\n')
    audio_text_parts = []

    in_stories = False
    for line in lines:
        if '## Top' in line:
            audio_text_parts.append(line.replace('#', '').replace('*', '').strip())
            in_stories = True
        elif in_stories and line.startswith('###'):
            story_text = line.replace('#', '').strip()
            if '][' in story_text:
                title_part = story_text.split('][')[1].split(']')[0]
                story_num = story_text.split('.')[0].split()[-1]
                audio_text_parts.append(f"Story {story_num}. {title_part}.")
        elif in_stories and line.startswith('- **Score'):
            pass

    audio_text = ' '.join(audio_text_parts)

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
