import os
import sys
import json
import asyncio
import argparse
from tiktok_scraper import TikTokScraper

BANNER = """
==================================================================
        TIKTOK SCRAPER - PERFIL, VIDEOS & COMENTARIOS
==================================================================
"""

def parse_args():
    parser = argparse.ArgumentParser(description="TikTok Scraper CLI")
    parser.add_argument("username", help="Usuario de TikTok")
    return parser.parse_args()
