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
    """
    Lee de forma segura el archivo local '.env' en busca de la variable 'TIKTOK_SESSION_ID'.
    Si existe, retorna la cookie en texto plano para autenticar peticiones automáticamente.
    Si no existe el archivo, busca en las variables de entorno del sistema operativo.
    """
    script_dir = os.path.dirname(__file__)
    env_file = os.path.join(script_dir, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TIKTOK_SESSION_ID=") and not line.startswith("#"):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return os.getenv("TIKTOK_SESSION_ID")


class TikTokScraper:
    def __init__(self, session_id: Optional[str] = None, headless: bool = True):
        """
        Constructor de la clase: inicializa sesión, modo headless y camuflaje anti-bot.
        :param session_id: Cookie opcional de TikTok para saltar login wall.
        :param headless: Si es True, ejecuta en segundo plano.
        """
        self.session_id = session_id or load_env_cookie()
        self.headless = headless
        self.stealth = Stealth()

    async def _setup_context(self, p) -> tuple[Any, BrowserContext]:
        """Inicia Google Chrome con flags especiales que desactivan la detección automatizada."""
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

    # Extrae perfil, listas, videos y comentarios en un diccionario tipado
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
                        
                        # scene=67 corresponde a seguidores, scene=21 a seguidos en TikTok Web
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

            profile_data = {
                "success": True,
                "username": user.get("uniqueId", clean_user),
                "nickname": user.get("nickname", ""),
                "avatar_url": user.get("avatarLarger") or user.get("avatarMedium") or user.get("avatarThumb", ""),
                "followers_count": _parse_stat("followerCount"),
                "following_count": _parse_stat("followingCount"),
                "heart_count": _parse_stat("heartCount") or _parse_stat("heart"),
                "video_count": _parse_stat("videoCount"),
                "bio": user.get("signature", ""),
                "verified": user.get("verified", False),
                "private_account": user.get("privateAccount", False),
                "sec_uid": user.get("secUid", ""),
                "user_id": user.get("id", ""),
                "requires_login_for_lists": not bool(self.session_id),
                "following_list": [],
                "followers_list": [],
                "videos": [],
                "note": ""
            }

            # Extract followers & following lists if session cookie is present
            if self.session_id:
                # 1. SEGUIDORES
                try:
                    followers_btn = await page.query_selector('strong[data-e2e="followers-count"]')
                    if followers_btn:
                        await followers_btn.click(timeout=5000, force=True)
                        await asyncio.sleep(2.5)
                        for _ in range(min(3, max(0, (max_list_items - 30) // 10))):
                            await page.mouse.wheel(0, 800)
                            await asyncio.sleep(0.7)
                        await page.keyboard.press("Escape")
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Aviso al extraer seguidores: {e}")

                # 2. SEGUIDOS
                try:
                    following_btn = await page.query_selector('strong[data-e2e="following-count"]')
                    if following_btn:
                        await following_btn.click(timeout=5000, force=True)
                        await asyncio.sleep(2.5)
                        for _ in range(min(3, max(0, (max_list_items - 30) // 10))):
                            await page.mouse.wheel(0, 800)
                            await asyncio.sleep(0.7)
                        await page.keyboard.press("Escape")
                        await asyncio.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Aviso al extraer seguidos: {e}")
            else:
                profile_data["note"] = (
                    "TikTok requiere cookie 'sessionid' para listar usuarios individuales de seguidores/seguidos."
                )

            profile_data["following_list"] = following_list[:max_list_items]
            profile_data["followers_list"] = followers_list[:max_list_items]
            profile_data["following_list_private"] = following_private

            # Remove listener for user list
            page.remove_listener("response", intercept_user_list)

            if max_videos > 0:
                await page.close()

                logger.info(f"Buscando los últimos {max_videos} videos de @{clean_user}...")
                video_urls = await self._extract_video_urls(browser, clean_user, max_videos)
                logger.info(f"Se encontraron {len(video_urls)} URLs de videos más recientes.")

                videos_data = []
                for idx, v_url in enumerate(video_urls, 1):
                    logger.info(f"Extrayendo métricas y comentarios [{idx}/{len(video_urls)}]: {v_url}")
                    v_ctx = await browser.new_context(viewport={"width": 1280, "height": 800}, locale="es-ES")
                    if self.session_id:
                        await v_ctx.add_cookies([{"name": "sessionid", "value": self.session_id, "domain": ".tiktok.com", "path": "/"}])
                    
                    v_info = await self._extract_single_video_details(
                        context=v_ctx,
                        video_url=v_url,
                        max_comments=max_comments_per_video
                    )
                    await v_ctx.close()
                    videos_data.append(v_info)

                profile_data["videos"] = videos_data

            await browser.close()
            return profile_data

    async def _extract_video_urls(self, browser: Any, username: str, max_videos: int) -> List[str]:
        """
        Busca los videos del autor en TikTok mediante búsqueda oficial y scroll vertical.
        Luego ordena los enlaces de mayor a menor por su ID numérico (Snowflake: ID más alto = más reciente).
        Los videos se ordenan descendentemente por su ID (Snowflake: ID mayor = más reciente).
        """
        raw_urls: List[str] = []
        clean_user = username.strip().lstrip("@").lower()
        search_url = f"https://www.tiktok.com/search?q=%40{clean_user}"
        
        search_ctx = await browser.new_context(viewport={"width": 1280, "height": 800}, locale="es-ES")
        if self.session_id:
            await search_ctx.add_cookies([{"name": "sessionid", "value": self.session_id, "domain": ".tiktok.com", "path": "/"}])
        page = await search_ctx.new_page()

        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2.5)

            scroll_count = max(4, (max_videos + 2) // 3)
            for _ in range(scroll_count):
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(1.5)

            links = await page.evaluate(
                "() => Array.from(document.querySelectorAll('a')).map(a => a.href)"
            )
            for l in links:
                base = l.split("?")[0]
                es_video_del_usuario = f"/@{clean_user}/video/" in base.lower()
                no_esta_repetido = base not in raw_urls
                if es_video_del_usuario and no_esta_repetido:
                    raw_urls.append(base)
        except Exception as e:
            logger.warning(f"Aviso en búsqueda de videos: {e}")
        finally:
            try:
                await search_ctx.close()
            except Exception:
                pass

        def _get_vid_id(u: str) -> int:
            m = re.search(r"/video/(\d+)", u)
            return int(m.group(1)) if m else 0

        unique_urls = list(dict.fromkeys(raw_urls))
        sorted_urls = sorted(unique_urls, key=_get_vid_id, reverse=True)
        return sorted_urls[:max_videos]

    async def _extract_single_video_details(
        self,
        context: BrowserContext,
        video_url: str,
        max_comments: int = 20
    ) -> Dict[str, Any]:
        """Navega a un video específico en una pestaña limpia, extrae todas las métricas de interacción y los comentarios."""
        page = await context.new_page()
        captured_comments: List[Dict[str, Any]] = []

        # Interceptor de la API de comentarios de TikTok
        async def intercept_comments(response):
            nonlocal captured_comments
            if "comment/list" in response.url:
                try:
                    text = await response.text()
                    if not text:
                        return
                    d = json.loads(text)
                    raw_comments = d.get("comments", []) or []
                    logger.info(f"API de comentarios interceptada: {len(raw_comments)} comentarios obtenidos.")
                    for c in raw_comments:
                        u = c.get("user", {}) or {}
                        c_id = str(c.get("cid", ""))
                        if not any(x["comment_id"] == c_id for x in captured_comments):
                            created_ts = c.get("create_time", 0)
                            dt_str = ""
                            if created_ts:
                                try:
                                    dt_str = datetime.fromtimestamp(created_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                                except Exception:
                                    pass

                            captured_comments.append({
                                "comment_id": c_id,
                                "username": u.get("unique_id", "") or u.get("uniqueId", ""),
                                "nickname": u.get("nickname", ""),
                                "avatar_url": u.get("avatar_thumb", {}).get("url_list", [""])[0] if isinstance(u.get("avatar_thumb"), dict) else "",
                                "text": c.get("text", ""),
                                "likes_count": c.get("digg_count", 0),
                                "replies_count": c.get("reply_comment_total", 0),
                                "create_time": created_ts,
                                "date": dt_str
                            })
                except Exception as e:
                    logger.warning(f"Error parseando comentarios: {e}")

        page.on("response", intercept_comments)

        video_info: Dict[str, Any] = {
            "video_id": "",
            "video_url": video_url,
            "description": "",
            "create_time": 0,
            "date": "",
            "likes_count": 0,
            "comments_count": 0,
            "views_count": 0,
            "shares_count": 0,
            "bookmarks_count": 0,
            "music_title": "",
            "music_author": "",
            "comments": []
        }

        try:
            await page.goto(video_url, wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2.5)
        except Exception as e:
            logger.warning(f"Error navegando a video {video_url}: {e}")
            await page.close()
            return {
                "video_url": video_url,
                "error": str(e),
                "comments": []
            }

        # Extraer metadatos de rehidratación
        try:
            el = await page.wait_for_selector("script#__UNIVERSAL_DATA_FOR_REHYDRATION__", state="attached", timeout=12000)
            if el:
                txt = await el.text_content()
                d = json.loads(txt)
                detail = d.get("__DEFAULT_SCOPE__", {}).get("webapp.video-detail", {})
                item = detail.get("itemInfo", {}).get("itemStruct", {})
                stats = item.get("stats", {})

                def _to_int(val):
                    try:
                        return int(val)
                    except (ValueError, TypeError):
                        return 0

                c_time = _to_int(item.get("createTime", 0))
                dt_str = ""
                if c_time:
                    try:
                        dt_str = datetime.fromtimestamp(c_time, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    except Exception:
                        pass

                video_info["video_id"] = str(item.get("id", ""))
                video_info["description"] = item.get("desc", "")
                video_info["create_time"] = c_time
                video_info["date"] = dt_str
                video_info["likes_count"] = _to_int(stats.get("diggCount"))
                video_info["comments_count"] = _to_int(stats.get("commentCount"))
                video_info["views_count"] = _to_int(stats.get("playCount"))
                video_info["shares_count"] = _to_int(stats.get("shareCount"))
                video_info["bookmarks_count"] = _to_int(stats.get("collectCount"))
                video_info["music_title"] = item.get("music", {}).get("title", "")
                video_info["music_author"] = item.get("music", {}).get("authorName", "")
        except Exception as e:
            logger.warning(f"Error parseando universal data del video: {e}")

        if not video_info["video_id"]:
            m = re.search(r"/video/(\d+)", video_url)
            if m:
                video_info["video_id"] = m.group(1)

        # Esperar botón de comentarios y hacer clic nativo para activar la carga de api/comment/list
        try:
            btn = await page.wait_for_selector(
                '[data-e2e="comment-icon"], [data-e2e="comment-count"], button[class*="tux"]:has-text("Comentarios"), button[class*="tux"]:has-text("Comments")',
                timeout=8000
            )
            if btn:
                logger.info("Botón de comentarios encontrado. Haciendo clic nativo...")
                await btn.click()
                for _ in range(12):
                    if len(captured_comments) >= max_comments:
                        break
                    await asyncio.sleep(0.5)

            # Si aún no se capturaron comentarios, intentar clic en la pestaña de Comentarios
            if not captured_comments:
                tab_btn = await page.query_selector('button[class*="tux"]:has-text("Comentarios"), button[class*="tux"]:has-text("Comments")')
                if tab_btn:
                    await tab_btn.click()
                    for _ in range(8):
                        if len(captured_comments) >= max_comments:
                            break
                        await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"Aviso al hacer clic en comentarios: {e}")

        # Fallback por si la API no atrapó suficientes comentarios: extraer de DOM
        if len(captured_comments) < max_comments:
            try:
                dom_comments = await page.evaluate("""() => {
                    const list = [];
                    const items = document.querySelectorAll('[data-e2e="comment-item"], div[class*="DivCommentItemContainer"], div[class*="CommentItem"]');
                    for (let el of items) {
                        const userEl = el.querySelector('[data-e2e="comment-username"], a[href*="/@"], span[class*="SpanUserName"]');
                        const textEl = el.querySelector('[data-e2e="comment-level-1"], p[class*="PCommentText"], span[class*="SpanCommentText"]');
                        const likeEl = el.querySelector('[data-e2e="comment-like-count"], span[class*="SpanCount"]');
                        if (textEl && textEl.innerText.trim()) {
                            list.push({
                                username: userEl ? userEl.innerText.trim().replace(/^@/, '') : "",
                                text: textEl.innerText.trim(),
                                likes_text: likeEl ? likeEl.innerText.trim() : "0"
                            });
                        }
                    }
                    return list;
                }""")
                for dc in dom_comments:
                    if not any(x["text"] == dc["text"] for x in captured_comments):
                        captured_comments.append({
                            "comment_id": "",
                            "username": dc.get("username", ""),
                            "nickname": dc.get("username", ""),
                            "avatar_url": "",
                            "text": dc.get("text", ""),
                            "likes_count": 0,
                            "replies_count": 0,
                            "create_time": 0,
                            "date": ""
                        })
            except Exception:
                pass

        page.remove_listener("response", intercept_comments)
        await page.close()
        video_info["comments"] = captured_comments[:max_comments]
        return video_info


def scrape_tiktok_user(
    username: str,
    session_id: Optional[str] = None,
    max_videos: int = 10,
    max_comments: int = 20
) -> Dict[str, Any]:
    """Helper sincrónico para ejecutar el scraper de TikTok con videos y comentarios."""
    scraper = TikTokScraper(session_id=session_id)
    return asyncio.run(scraper.scrape(username, max_videos=max_videos, max_comments_per_video=max_comments))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    user_to_test = sys.argv[1] if len(sys.argv) > 1 else "tiktok"
    print(f"Probando scraper completo para: @{user_to_test}...")
    res = scrape_tiktok_user(user_to_test, max_videos=3, max_comments=5)
    print(json.dumps(res, indent=2, ensure_ascii=False))
