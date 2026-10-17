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


@app.get("/api/tiktok/{username}")
async def get_tiktok_profile(
    username: str,
    session_id: Optional[str] = Query(None, description="Cookie 'sessionid' opcional de TikTok"),
    max_items: int = Query(30, description="Límite de usuarios en listas de seguidores/seguidos"),
    max_videos: int = Query(10, description="Cantidad de videos recientes a extraer"),
    max_comments: int = Query(15, description="Cantidad de comentarios a extraer por video"),
):
    """
    Endpoint GET para scrapear perfil de TikTok ingresando solo el nick o username.
    """
    scraper = TikTokScraper(session_id=session_id, headless=True)
    data = await scraper.scrape(
        username=username,
        max_list_items=max_items,
        max_videos=max_videos,
        max_comments_per_video=max_comments
    )
    
    if not data.get("success"):
        raise HTTPException(
            status_code=404 if "no encontrado" in data.get("error", "") else 500,
            detail=data.get("error", "Error al procesar la solicitud.")
        )
    return data


@app.post("/api/tiktok/scrape")
async def post_tiktok_scrape(payload: ScrapeRequest):
    """
    Endpoint POST para recibir parámetros en formato JSON desde una aplicación móvil.
    """
    scraper = TikTokScraper(session_id=payload.session_id, headless=True)
    data = await scraper.scrape(
        username=payload.username,
        max_list_items=payload.max_list_items or 30,
        max_videos=payload.max_videos or 10,
        max_comments_per_video=payload.max_comments_per_video or 15
    )
    
    if not data.get("success"):
        raise HTTPException(
            status_code=404 if "no encontrado" in data.get("error", "") else 500,
            detail=data.get("error", "Error al procesar la solicitud.")
        )
    return data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
