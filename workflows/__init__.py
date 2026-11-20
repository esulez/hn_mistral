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
        import importlib

        # Dynamically import activities to avoid sandbox restrictions
        activities_mod = importlib.import_module(".activities", package="workflows")
        fetch_hn_stories = activities_mod.fetch_hn_stories
        filter_tech_stories = activities_mod.filter_tech_stories
        generate_summary = activities_mod.generate_summary
        generate_audio = activities_mod.generate_audio
        send_digest_email = activities_mod.send_digest_email

        stories = await fetch_hn_stories()
        tech_stories = await filter_tech_stories(stories)
        summary = await generate_summary(tech_stories)

        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set")

        audio_data = await generate_audio(summary, api_key)
        result = await send_digest_email(summary, audio_data)

        return {
            **result,
            "tech_stories_count": len(tech_stories),
            "total_stories_fetched": len(stories),
            "completed_at": datetime.now().isoformat()
        }
