from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from tiktok_scraper import TikTokScraper

app = FastAPI(title="TikTok Scraper API", version="2.0.0")
