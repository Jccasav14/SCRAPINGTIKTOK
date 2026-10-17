"""
FastAPI Server for TikTok Scraper
Ideal para consumir desde aplicaciones móviles (Flutter, Android, iOS, React Native).
Retorna perfil completo, listas de seguidores/seguidos, los últimos videos con sus métricas
(likes, comentarios, vistas, shares, guardados) y el contenido de los comentarios.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from tiktok_scraper import TikTokScraper

app = FastAPI(
    title="TikTok Scraper API",
    description="API REST para obtener datos de perfiles de TikTok, videos e interacciones, y comentarios.",
    version="2.0.0",
)

# Habilitar CORS para permitir peticiones desde aplicaciones móviles o web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    username: str
    session_id: Optional[str] = None
    max_list_items: Optional[int] = 30
    max_videos: Optional[int] = 10
    max_comments_per_video: Optional[int] = 15


@app.get("/")
def read_root():
    return {
        "message": "TikTok Scraper API activa (v2.0 con Videos y Comentarios)",
        "documentation": "/docs",
        "example_endpoint": "/api/tiktok/{username}"
    }


