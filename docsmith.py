#!/usr/bin/env python3
# Compatibility script - redirects to main.py
import sys
from main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:]))