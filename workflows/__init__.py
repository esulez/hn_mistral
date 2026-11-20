"""
HackerNews Tech Digest Workflow

Mistral Workflow that fetches HN front page, filters tech news,
generates summary and audio, and sends to Gmail.
"""

from mistralai.workflows import workflow


@workflow.define(name="HackerNewsTechDigestWorkflow")
class HackerNewsTechDigestWorkflow:
    """Workflow that creates and sends a HackerNews tech digest."""

    @workflow.entrypoint
    async def run(self) -> dict:
        import os
        from datetime import datetime

        # Get API key from environment (this is in workflow sandbox, need to use unsafe)
        # But actually, let's move this to the activity
        # For now, just pass None and let the activity handle it
        
        # Import activities from top-level module
        from activities import (
            fetch_hn_stories,
            filter_tech_stories,
            generate_summary,
            generate_audio,
            send_digest_email,
        )

        stories = await fetch_hn_stories()
        tech_stories = await filter_tech_stories(stories)
        summary = await generate_summary(tech_stories)

        # Don't access os.environ in workflow - pass None and let activity get it
        audio_data = await generate_audio(summary, None)
        result = await send_digest_email(summary, audio_data)

        return {
            **result,
            "tech_stories_count": len(tech_stories),
            "total_stories_fetched": len(stories),
            "completed_at": datetime.now().isoformat()
        }
