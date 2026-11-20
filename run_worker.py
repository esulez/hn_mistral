#!/usr/bin/env python3
"""Entry point for Mistral workflows worker."""

import asyncio
from mistralai.workflows import run_worker, discover_all_workflows_in_package


async def main():
    # Discover and run all workflows in the current package
    workflows = discover_all_workflows_in_package(".")
    await run_worker(workflows)


if __name__ == "__main__":
    asyncio.run(main())
