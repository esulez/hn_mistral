#!/usr/bin/env python3
import asyncio
from workflows import HackerNewsTechDigestWorkflow
from mistralai.workflows import run_worker

async def main():
    await run_worker([HackerNewsTechDigestWorkflow])

if __name__ == "__main__":
    asyncio.run(main())
