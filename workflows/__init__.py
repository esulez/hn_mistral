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
        # Import activities and datetime with unsafe context
        with workflow.unsafe.imports_passed_through():
            from datetime import datetime
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

        # Don't access os.environ in workflow - activity will get it
        audio_data = await generate_audio(summary, None)
        result = await send_digest_email(summary, audio_data)

        # Get current time inside unsafe context
        with workflow.unsafe.imports_passed_through():
            from datetime import datetime
            completed_at = datetime.now().isoformat()

        return {
            **result,
            "tech_stories_count": len(tech_stories),
            "total_stories_fetched": len(stories),
            "completed_at": completed_at
        }
