import os
import sys
import json
import asyncio
import argparse
from tiktok_scraper import TikTokScraper

def parse_args():
    parser = argparse.ArgumentParser(description="TikTok Scraper CLI")
    parser.add_argument("username", help="Usuario de TikTok")
    parser.add_argument("--max-videos", type=int, default=10, help="Videos recientes a extraer")
    parser.add_argument("--max-comments", type=int, default=15, help="Comentarios por video")
    parser.add_argument("--max-list-items", type=int, default=30, help="Máximo seguidores/seguidos")
    return parser.parse_args()
