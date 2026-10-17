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

# Configurar encoding en Windows si es necesario
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Configurar logging con formato limpio para mostrar el progreso en tiempo real
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
    avatar = data.get('avatar_url', '')
    print(f" • Foto de Perfil HD:  {avatar[:80]}..." if len(avatar) > 80 else f" • Foto de Perfil HD:  {avatar}")
    print("-" * 65)

