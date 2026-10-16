"""
TikTok Scraper Module
Extracts profile info (nick, avatar, followers, following), lists of followers/following,
the last 10 videos with all interaction metrics (likes, comments, views, shares, saves),
and the actual comments for each video.
"""

import os
import re
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, BrowserContext, Page
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TikTokScraper")


def load_env_cookie() -> Optional[str]:
    """Lee TIKTOK_SESSION_ID desde archivo .env o variables de entorno."""
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TIKTOK_SESSION_ID="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return os.getenv("TIKTOK_SESSION_ID")


class TikTokScraper:
    def __init__(self, session_id: Optional[str] = None, headless: bool = True):
        """
        :param session_id: Optional TikTok 'sessionid' cookie value to bypass login walls.
                           Si no se especifica, se lee automáticamente desde el archivo .env
        :param headless: Run browser in headless mode.
        """
        self.session_id = session_id or load_env_cookie()
        self.headless = headless
        self.stealth = Stealth()

    async def _setup_context(self, p) -> tuple[Any, BrowserContext]:
        # Use real Chrome if installed for best stealth, fallback to chromium
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

        # Session cookies setup
        if self.session_id:
            await context.add_cookies([
                {"name": "sessionid", "value": self.session_id, "domain": ".tiktok.com", "path": "/"},
                {"name": "sessionid_ss", "value": self.session_id, "domain": ".tiktok.com", "path": "/"},
                {"name": "sid_tt", "value": self.session_id, "domain": ".tiktok.com", "path": "/"},
            ])

        return browser, context

    async def scrape(
        self,
        username: str,
        max_list_items: int = 30,
        max_videos: int = 10,
        max_comments_per_video: int = 20,
    ) -> Dict[str, Any]:
        """
        Scrapes a TikTok user profile given only their username/nick.
        
        :param username: TikTok handle (e.g. 'mrbeast' or '@mrbeast')
        :param max_list_items: Maximum items to collect for followers/following lists
        :param max_videos: Number of recent videos to extract (default: 10)
        :param max_comments_per_video: Maximum comments to extract per video
        :return: Dictionary containing complete profile data, lists, videos, and comments
        """
        clean_user = username.strip().lstrip("@")
        profile_url = f"https://www.tiktok.com/@{clean_user}"
        
        followers_list: List[Dict[str, Any]] = []
        following_list: List[Dict[str, Any]] = []
        
        async with self.stealth.use_async(async_playwright()) as p:
            browser, context = await self._setup_context(p)
            page = await context.new_page()

            following_private = False

            # Intercept follower/following list API calls
            async def intercept_user_list(response):
                nonlocal followers_list, following_list, following_private
                if "api/user/list" in response.url:
                    try:
                        data = await response.json()
                        st_code = data.get("statusCode", 0)
                        if st_code == 10222:
                            following_private = True
                        items = data.get("userList", [])
                        if not items:
                            return
                        parsed = []
                        for item in items:
                            u = item.get("user", {})
                            st = item.get("stats", {})
                            parsed.append({
                                "username": u.get("uniqueId"),
                                "nickname": u.get("nickname"),
                                "avatar_url": u.get("avatarThumb") or u.get("avatarMedium"),
                                "followers_count": st.get("followerCount", 0),
                                "following_count": st.get("followingCount", 0),
                                "verified": u.get("verified", False),
                                "sec_uid": u.get("secUid", ""),
                            })
                        
                        scene_match = re.search(r"[?&]scene=(\d+)", response.url)
                        scene = scene_match.group(1) if scene_match else ""

                        if scene == "67":
                            for p_user in parsed:
                                if not any(x["username"] == p_user["username"] for x in followers_list):
                                    followers_list.append(p_user)
                        elif scene == "21":
                            for p_user in parsed:
                                if not any(x["username"] == p_user["username"] for x in following_list):
                                    following_list.append(p_user)
                    except Exception:
                        pass

            page.on("response", intercept_user_list)

            logger.info(f"Navegando al perfil: {profile_url}")
            try:
                await page.goto(profile_url, wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(3)
            except Exception as e:
                await browser.close()
                return {
                    "success": False,
                    "error": f"Error cargando la página de TikTok: {str(e)}",
                    "username": clean_user
                }

            # Extract user data from rehydration script tag
            script_el = await page.query_selector("script#__UNIVERSAL_DATA_FOR_REHYDRATION__")
            if not script_el:
                await browser.close()
                return {
                    "success": False,
                    "error": f"No se pudo encontrar los datos del perfil de @{clean_user}. Podría no existir o estar bloqueado.",
                    "username": clean_user
                }

            content = await script_el.inner_text()
            try:
                raw_data = json.loads(content)
            except json.JSONDecodeError:
                await browser.close()
                return {
                    "success": False,
                    "error": "Error al parsear los datos internos de TikTok.",
                    "username": clean_user
                }

            user_detail = raw_data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {})
            status_code = user_detail.get("statusCode", 0)
            
            if status_code != 0:
                await browser.close()
                return {
                    "success": False,
                    "error": f"Usuario @{clean_user} no encontrado o cuenta no disponible (Status: {status_code}).",
                    "username": clean_user
                }

            user_info = user_detail.get("userInfo", {})
            user = user_info.get("user", {})
            stats = user_info.get("stats", {})
            stats_v2 = user_info.get("statsV2", {})

            def _parse_stat(key: str, default: int = 0) -> int:
                val = stats_v2.get(key)
                if val is not None:
                    try:
                        return int(val)
                    except (ValueError, TypeError):
                        pass
                num = stats.get(key, default)
                if isinstance(num, int) and num < 0:
                    return num + (1 << 32)
                try:
                    return int(num)
                except (ValueError, TypeError):
                    return default

