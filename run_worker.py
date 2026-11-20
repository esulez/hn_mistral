#!/usr/bin/env python3
"""Entry point for Mistral workflows worker."""

import asyncio
from workflow import HackerNewsTechDigestWorkflow
from mistralai.workflows import run_worker


async def main():
    # Run the worker with the specific workflow class
    await run_worker([HackerNewsTechDigestWorkflow])


if __name__ == "__main__":
    asyncio.run(main())
