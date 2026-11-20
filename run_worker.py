#!/usr/bin/env python3
"""Entry point for Mistral workflows worker."""

import asyncio
from mistralai.workflows import run_worker


async def main():
    # Import workflow here to avoid circular import issues
    from workflow import HackerNewsTechDigestWorkflow
    # Run the worker with the workflow
    await run_worker([HackerNewsTechDigestWorkflow])


if __name__ == "__main__":
    asyncio.run(main())
