"""
TikTok Profile, Videos & Comments Scraper
"""
import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, BrowserContext
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TikTokScraper")

def load_env_cookie() -> Optional[str]:
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TIKTOK_SESSION_ID="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return os.getenv("TIKTOK_SESSION_ID")

class TikTokScraper:
    def __init__(self, session_id: Optional[str] = None, headless: bool = True):
        self.session_id = session_id or load_env_cookie()
        self.headless = headless
        self.stealth = Stealth()

    async def _setup_context(self, p) -> tuple[Any, BrowserContext]:
        launch_args = {
            "headless": self.headless,
            "args": [
                "--headless=new",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-size=1280,800",
            ],
        }
        try:
            browser = await p.chromium.launch(channel="chrome", **launch_args)
        except Exception:
            browser = await p.chromium.launch(**launch_args)

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="es-ES",
        )
        return browser, context
