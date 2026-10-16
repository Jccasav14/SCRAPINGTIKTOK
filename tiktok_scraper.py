"""
TikTok Profile, Videos & Comments Scraper
"""
import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TikTokScraper")
