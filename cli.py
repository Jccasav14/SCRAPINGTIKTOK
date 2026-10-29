#!/usr/bin/env python3
"""
TikTok Scraper CLI
Ejecución en terminal: solo requiere el nick o nombre de usuario de TikTok.
Extrae perfil, seguidores, seguidos, los últimos 10 videos con todas sus métricas
de interacción (likes, comentarios, vistas, shares, guardados) y sus comentarios.
"""

import sys
import os
import json
import argparse
import logging
from tiktok_scraper import TikTokScraper, scrape_tiktok_user

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logging.getLogger("TikTokScraper").setLevel(logging.INFO)


def print_banner():
    print(r"""
==================================================================
        TIKTOK SCRAPER - PERFIL, VIDEOS & COMENTARIOS
==================================================================
""")


def display_results(data: dict):
    if not data.get("success", False):
        print("\n❌ ERROR AL SCRAPEAR:")
        print(f"   {data.get('error', 'Error desconocido')}\n")
        return

    print("\n" + "=" * 65)
    print("                DATOS DEL PERFIL EXTRAÍDOS")
    print("=" * 65)
    print(f" • Nick / Usuario:     @{data.get('username')}")
    print(f" • Nombre / Apodo:     {data.get('nickname')}")
    print(f" • Verificado:         {'✅ Sí' if data.get('verified') else '❌ No'}")
    print(f" • Cuenta Privada:     {'🔒 Sí (Privada)' if data.get('private_account') else '🌍 Pública'}")
    print(f" • Seguidores:         {data.get('followers_count', 0):,}")
    print(f" • Seguidos:           {data.get('following_count', 0):,}")
    print(f" • Me Gusta Totales:   {data.get('heart_count', 0):,}")
    print(f" • Total de Videos:    {data.get('video_count', 0):,}")
    if data.get("bio"):
        print(f" • Biografía:          {data.get('bio')}")
    if data.get("bio_link"):
        print(f" • Enlace Bio:         {data.get('bio_link')}")
    avatar = data.get('avatar_url', '')
    print(f" • Foto de Perfil HD:  {avatar[:80]}..." if len(avatar) > 80 else f" • Foto de Perfil HD:  {avatar}")
    print("-" * 65)

    following_list = data.get("following_list", [])
    followers_list = data.get("followers_list", [])
    
    if following_list or followers_list or data.get("following_list_private"):
        if following_list:
            print(f"\n📋 LISTADO DE SEGUIDOS ({len(following_list)} cuentas extraídas):")
            print("-" * 65)
            for i, u in enumerate(following_list, start=1):
                verified_mark = " ✓" if u.get("verified") else ""
                print(f" [{i:02d}] @{u.get('username')}{verified_mark} - {u.get('nickname')} ({u.get('followers_count', 0):,} seguidores)")
        elif data.get("following_list_private"):
            print(f"\n🔒 LISTADO DE SEGUIDOS:")
            print("   ℹ️ La lista de seguidos está configurada como PRIVADA ('Solo yo') por este usuario en TikTok.")
        
        if followers_list:
            print(f"\n📋 LISTADO DE SEGUIDORES ({len(followers_list)} cuentas extraídas):")
            print("-" * 65)
            for i, u in enumerate(followers_list, start=1):
                verified_mark = " ✓" if u.get("verified") else ""
                print(f" [{i:02d}] @{u.get('username')}{verified_mark} - {u.get('nickname')} ({u.get('followers_count', 0):,} seguidores)")
    else:
        print("\n🔒 Listados individuales de seguidores/seguidos:")
        print("   TikTok bloquea la lista de usuarios anónimos con un 'Login Wall'.")
        print("   Para desbloquear la lista de nombres, puedes pasar tu cookie con:")
        print("   python cli.py <usuario> --session-id TU_COOKIE_SESSIONID")

    videos = data.get("videos", [])
    if videos:
        print("\n" + "=" * 65)
        print(f" 🎬 ÚLTIMOS {len(videos)} VIDEOS E INTERACCIONES")
        print("=" * 65)
        for idx, v in enumerate(videos, start=1):
            desc = v.get("description", "").replace("\n", " ")
            if len(desc) > 75:
                desc = desc[:72] + "..."
            print(f"\n[{idx:02d}] Video ID: {v.get('video_id')}")
            print(f"     URL:         {v.get('video_url')}")
            if desc:
                print(f"     Descripción: \"{desc}\"")
            if v.get("date"):
                print(f"     Fecha:       {v.get('date')}")
            if v.get("duration"):
                print(f"     ⏱️ Duración:   {v.get('duration')}s")
            if v.get("hashtags"):
                tags_str = " ".join(["#" + h.lstrip("#") for h in v.get("hashtags", [])[:6]])
                print(f"     🏷️ Hashtags:   {tags_str}")
            print(f"     ❤️ Likes:       {v.get('likes_count', 0):,}")
            print(f"     💬 Comentarios: {v.get('comments_count', 0):,}")
            print(f"     👁️ Vistas:      {v.get('views_count', 0):,}")
            print(f"     🔄 Shares:      {v.get('shares_count', 0):,}")
            print(f"     ⭐ Guardados:   {v.get('bookmarks_count', 0):,}")

            comments = v.get("comments", [])
            if comments:
                print(f"     💬 Comentarios extraídos ({len(comments)}):")
                for c_idx, c in enumerate(comments[:5], start=1):
                    c_user = c.get('username') or c.get('nickname') or 'anónimo'
                    c_text = c.get('text', '').replace('\n', ' ')
                    if len(c_text) > 80:
                        c_text = c_text[:77] + '...'
                    c_likes = f"❤️ {c.get('likes_count', 0):,}" if c.get('likes_count') else ""
                    badges = []
                    if c.get("author_liked"):
                        badges.append("❤️ [Autor]")
                    if c.get("is_pinned"):
                        badges.append("📌 [Fijado]")
                    badge_str = " ".join(badges)
                    print(f"        {c_idx}. @{c_user}: \"{c_text}\" {c_likes} {badge_str}".strip())
                if len(comments) > 5:
                    print(f"        ... y {len(comments) - 5} comentarios más guardados en el archivo JSON.")
            else:
                print("     💬 Comentarios: No hay comentarios públicos o no se pudieron extraer.")
            print("-" * 65)
    else:
        print("\nℹ️ No se encontraron videos públicos para este usuario.")

    username = data.get("username", "resultado")
    out_dir = "scraped_data"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"tiktok_{username}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("\n" + "=" * 65)
    print(f"💾 Resultados completos exportados a: {out_file}")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Scraper de perfiles de TikTok: perfil, seguidores, seguidos, últimos 10 videos y comentarios."
    )
    parser.add_argument(
        "username",
        nargs="?",
        help="Nick o nombre de usuario de TikTok (ejemplo: 'mrbeast', 'khaby.lame', 'tiktok')",
    )
    parser.add_argument(
        "--session-id",
        dest="session_id",
        default=None,
        help="(Opcional) Cookie 'sessionid' de TikTok para desbloquear listas de seguidores/seguidos.",
    )
    parser.add_argument(
        "--max-items",
        dest="max_items",
        type=int,
        default=30,
        help="Máximo de seguidores/seguidos a extraer (por defecto: 30).",
    )
    parser.add_argument(
        "--max-videos",
        dest="max_videos",
        type=int,
        default=10,
        help="Cantidad de videos recientes a extraer (por defecto: 10).",
    )
    parser.add_argument(
        "--max-comments",
        dest="max_comments",
        type=int,
        default=15,
        help="Cantidad de comentarios a extraer por cada video (por defecto: 15).",
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Ejecuta automáticamente la Ley de Benford (χ²), Psicometría Big Five (OCEAN) y Radar de Crisis tras el scraping.",
    )
    parser.add_argument(
        "--crisis",
        action="store_true",
        help="Ejecuta el Radar de Cancelación y Detección de Funa / Crisis tras el scraping.",
    )

    args = parser.parse_args()

    print_banner()

    target_user = args.username
    if not target_user:
        try:
            target_user = input("👉 Ingrese el nick o nombre de usuario de TikTok: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            return

    if not target_user:
        print("❌ Debe proporcionar un nick o usuario válido.")
        return

    clean_user = target_user.lstrip("@").strip()
    print(f"⏳ Iniciando scraping para: @{clean_user}")
    print("   (Conectando con Playwright Stealth y resolviendo encabezados...")
    print(f"   (Buscando perfil, seguidores/seguidos, últimos {args.max_videos} videos y comentarios por video...)")
    
    scraper = TikTokScraper(session_id=args.session_id, headless=True)
    import asyncio
    data = asyncio.run(scraper.scrape(
        username=clean_user,
        max_list_items=args.max_items,
        max_videos=args.max_videos,
        max_comments_per_video=args.max_comments
    ))
    display_results(data)

    if args.enrich and data.get("success"):
        json_path = os.path.join("scraped_data", f"tiktok_{clean_user}.json")
        if not os.path.exists(json_path):
            json_path = f"tiktok_{clean_user}.json"
        if os.path.exists(json_path):
            from data_enricher import enrich_file
            print("\n🔮 Ejecutando enriquecimiento forense, psicométrico y radar de crisis...")
            enrich_file(json_path)
    elif args.crisis and data.get("success"):
        json_path = os.path.join("scraped_data", f"tiktok_{clean_user}.json")
        if not os.path.exists(json_path):
            json_path = f"tiktok_{clean_user}.json"
        if os.path.exists(json_path):
            from crisis_radar import scan_crisis_file
            print("\n🚨 Ejecutando Radar de Crisis Reputacional y riesgo de funa...")
            scan_crisis_file(json_path)
    elif data.get("success"):
        try:
            from figma_sync import send_to_figma
            f_res = send_to_figma(data)
            if f_res.get("status") == "success":
                print(f"\n📡 [FigmaSync] Perfil de @{clean_user} sincronizado en vivo con Figma (Pin ID: {f_res.get('comment_id')} en Dashboard)")
        except Exception:
            pass


if __name__ == "__main__":
    main()
