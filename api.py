import os
import sys
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel

from tiktok_scraper import TikTokScraper
from data_enricher import analyze_benford, analyze_big_five_gemini
from chart_generator import generate_benford_svg, generate_big_five_svg

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

app = FastAPI(
    title="TikTok Intelligence & Scraper API",
    docs_url=None,
    redoc_url="/redoc",
    description="""
API REST con interfaz Swagger para extracción y enriquecimiento de datos de TikTok:
* 📥 **Scraper**: Perfil, seguidores/seguidos, últimos videos con todas sus métricas y comentarios reales.
* 📊 **Análisis Forense (Ley de Benford & χ²)**: Detección de patrones orgánicos vs granjas de bots.
* 🧠 **Perfil Psicométrico Big Five (OCEAN)**: Arquetipo y emociones evaluados con Google Gemini AI.
* 🎨 **Gráficos Visuales**: Renderizado gráfico de barras y emociones integrado directamente en Swagger.
* 📂 **Gestión de Archivos**: Almacenamiento organizado en `scraped_data/` y `enriched_data/`.
""",
    version="2.6.0",
    openapi_tags=[
        {"name": "Visual Charts", "description": "Gráficos visuales de Benford y Emociones integrados en Swagger"},
        {"name": "Enrichment", "description": "Modelos avanzados: Ley de Benford (χ²) y Psicometría Big Five (OCEAN)"},
        {"name": "Scraper", "description": "Extracción de datos en vivo desde TikTok"},
        {"name": "Files", "description": "Consulta y descarga de JSONs guardados en el servidor"},
        {"name": "Health", "description": "Estado y salud del microservicio"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    username: str
    max_list_items: Optional[int] = 30
    max_videos: Optional[int] = 10
    max_comments_per_video: Optional[int] = 15


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    swagger_res = get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title)
    html = swagger_res.body.decode("utf-8")

    top_banner = """
    <div id="swagger-top-bar" style="background:#ffffff; border-bottom:1px solid #e2e8f0; padding:12px 24px; color:#3b4151; display:flex; align-items:center; gap:12px; flex-wrap:wrap; position:sticky; top:0; z-index:9999; box-shadow:0 2px 6px rgba(0,0,0,0.05); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
      <span style="font-weight:700; color:#3b4151; font-size:0.95rem; display:flex; align-items:center; gap:6px;">
        🎯 Usuario TikTok:
      </span>
      <input id="global-tiktok-user" type="text" value="mrbeast" placeholder="ej: mrbeast" style="padding:6px 12px; border-radius:4px; border:1px solid #cbd5e1; background:#f8fafc; color:#1e293b; font-size:0.9rem; width:170px; outline:none;" />
      
      <button onclick="applyUserToAllSwagger()" style="background:#49cc90; color:#fff; border:none; padding:7px 14px; border-radius:4px; font-weight:700; font-size:0.85rem; cursor:pointer; transition:all 0.15s;">
        ⚡ Rellenar en Swagger
      </button>

      <button onclick="displaySwaggerChart('benford')" style="background:#4990e2; color:#fff; border:none; padding:7px 14px; border-radius:4px; font-weight:700; font-size:0.85rem; cursor:pointer; transition:all 0.15s;">
        📊 Ver Gráfico Benford
      </button>

      <button onclick="displaySwaggerChart('big-five')" style="background:#61affe; color:#fff; border:none; padding:7px 14px; border-radius:4px; font-weight:700; font-size:0.85rem; cursor:pointer; transition:all 0.15s;">
        🧠 Ver Gráfico Emociones
      </button>

      <div style="margin-left:auto; display:flex; align-items:center; gap:6px;">
        <span style="font-size:0.82rem; color:#64748b;">Rápidos:</span>
        <a href="javascript:void(0)" onclick="setQuickUser('mrbeast')" style="color:#4990e2; font-weight:600; font-size:0.85rem; text-decoration:none; margin-right:6px;">@mrbeast</a>
        <a href="javascript:void(0)" onclick="setQuickUser('nayelimacas52')" style="color:#4990e2; font-weight:600; font-size:0.85rem; text-decoration:none;">@nayelimacas52</a>
      </div>
    </div>

    <!-- Visor de Gráficos integrado directamente en Swagger (Tema Blanco) -->
    <div id="swagger-chart-viewer" style="display:none; background:#ffffff; padding:20px; text-align:center; border-bottom:1px solid #e2e8f0; box-shadow:0 4px 12px rgba(0,0,0,0.04);">
      <div style="max-width:880px; margin:0 auto 10px; display:flex; justify-content:space-between; align-items:center;">
        <span style="color:#0f172a; font-weight:700; font-size:1.05rem;" id="chart-viewer-title">Gráfico</span>
        <button onclick="document.getElementById('swagger-chart-viewer').style.display='none'" style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; border-radius:4px; padding:4px 12px; font-size:0.85rem; font-weight:600; cursor:pointer;">
          ✖ Ocultar
        </button>
      </div>
      <div id="chart-svg-target" style="max-width:880px; margin:0 auto; overflow:auto;"></div>
    </div>

    <script>
      function setQuickUser(u) {
        document.getElementById('global-tiktok-user').value = u;
        applyUserToAllSwagger();
      }

      function applyUserToAllSwagger() {
        const u = document.getElementById('global-tiktok-user').value.trim().replace(/^@/, '');
        if (!u) return;

        const inputs = document.querySelectorAll('input');
        let count = 0;
        inputs.forEach(inp => {
          if (inp.id !== 'global-tiktok-user') {
            const p = (inp.placeholder || '').toLowerCase();
            const n = (inp.name || '').toLowerCase();
            if (p.includes('username') || n.includes('username') || p.includes('usuario')) {
              inp.value = u;
              inp.dispatchEvent(new Event('input', { bubbles: true }));
              inp.dispatchEvent(new Event('change', { bubbles: true }));
              count++;
            }
          }
        });
        const btn = event.target;
        const originalText = btn.innerText;
        btn.innerText = '✅ ¡Rellenado!';
        setTimeout(() => { btn.innerText = originalText; }, 1600);
      }

      function displaySwaggerChart(type) {
        const u = document.getElementById('global-tiktok-user').value.trim().replace(/^@/, '') || 'mrbeast';
        const viewer = document.getElementById('swagger-chart-viewer');
        const target = document.getElementById('chart-svg-target');
        const title = document.getElementById('chart-viewer-title');

        title.innerText = type === 'benford' ? '📊 Ley de Benford - Gráfico de Barras (@' + u + ')' : '🧠 Psicometría Big Five y Emociones (@' + u + ')';
        viewer.style.display = 'block';
        target.innerHTML = '<div style="color:#0284c7; padding:30px; font-size:1rem;">⏳ Cargando gráfico para @' + u + '...</div>';

        fetch('/api/tiktok/' + u + '/chart/' + type)
          .then(r => {
            if (!r.ok) throw new Error('No se encontraron datos para @' + u + '. Ejecuta primero el método /enrich o /scrape en Swagger.');
            return r.text();
          })
          .then(svg => {
            target.innerHTML = svg;
          })
          .catch(err => {
            target.innerHTML = '<div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; color:#b91c1c; padding:14px; margin:16px auto; max-width:600px;">⚠️ ' + err.message + '</div>';
          });
      }
    </script>
    """

    if '<div id="swagger-ui">' in html:
        html = html.replace('<div id="swagger-ui">', top_banner + '<div id="swagger-ui">')
    return HTMLResponse(content=html)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "tiktok-intelligence-api"}


def _get_or_scrape_data(username: str) -> Dict[str, Any]:
    clean_user = username.lstrip("@").strip()
    candidate_scraped = os.path.join("scraped_data", f"tiktok_{clean_user}.json")
    if os.path.exists(candidate_scraped):
        with open(candidate_scraped, "r", encoding="utf-8") as f:
            return json.load(f)

    candidate_enriched = os.path.join("enriched_data", f"tiktok_{clean_user}_enriched.json")
    if os.path.exists(candidate_enriched):
        with open(candidate_enriched, "r", encoding="utf-8") as f:
            return json.load(f)

    if os.path.exists(f"tiktok_{clean_user}.json"):
        with open(f"tiktok_{clean_user}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# =============================================================================
# GRÁFICOS VISUALES EN SWAGGER
# =============================================================================

@app.get(
    "/api/tiktok/{username}/chart/benford",
    tags=["Visual Charts"],
    summary="📊 Gráfico de Barras de la Ley de Benford (SVG)",
    response_class=Response,
    responses={
        200: {
            "content": {"image/svg+xml": {}},
            "description": "Renderiza el gráfico de barras comparativas directamente dentro de Swagger."
        }
    }
)
async def get_benford_chart(username: str):
    clean_user = username.lstrip("@").strip()
    data = _get_or_scrape_data(clean_user)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos guardados para @{clean_user}. Ejecútalo primero en el scraper o /enrich."
        )

    benford_res = data.get("data_enrichment", {}).get("benford_law_analysis")
    if not benford_res:
        benford_res = analyze_benford(data)

    svg_content = generate_benford_svg(benford_res, clean_user)
    return Response(content=svg_content, media_type="image/svg+xml")


@app.get(
    "/api/tiktok/{username}/chart/big-five",
    tags=["Visual Charts"],
    summary="🧠 Gráfico de Psicometría Big Five y Emociones (SVG)",
    response_class=Response,
    responses={
        200: {
            "content": {"image/svg+xml": {}},
            "description": "Renderiza las barras de los 5 rasgos OCEAN y emociones directamente en Swagger."
        }
    }
)
async def get_big_five_chart(username: str):
    clean_user = username.lstrip("@").strip()
    data = _get_or_scrape_data(clean_user)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos guardados para @{clean_user}. Ejecútalo primero en el scraper o /enrich."
        )

    big_five_res = data.get("data_enrichment", {}).get("big_five_ocean_profile")
    if not big_five_res or big_five_res.get("status") != "success":
        big_five_res = analyze_big_five_gemini(data)

    svg_content = generate_big_five_svg(big_five_res, clean_user)
    return Response(content=svg_content, media_type="image/svg+xml")


# =============================================================================
# ENRIQUECIMIENTO DE DATOS
# =============================================================================

@app.post("/api/tiktok/{username}/enrich", tags=["Enrichment"])
async def enrich_tiktok_user(
    username: str,
    force_rescrape: bool = Query(False, description="Si es True, vuelve a scrapear aunque ya exista en 'scraped_data/'")
):
    clean_user = username.lstrip("@").strip()
    data = None if force_rescrape else _get_or_scrape_data(clean_user)

    if not data:
        scraper = TikTokScraper(headless=True)
        data = await scraper.scrape(username=clean_user, max_list_items=30, max_videos=10, max_comments_per_video=15)
        if not data.get("success"):
            raise HTTPException(status_code=500, detail=f"No se pudo scrapear: {data.get('error')}")
        os.makedirs("scraped_data", exist_ok=True)
        with open(os.path.join("scraped_data", f"tiktok_{clean_user}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    benford_res = analyze_benford(data)
    big_five_res = analyze_big_five_gemini(data)

    enriched = dict(data)
    enriched["data_enrichment"] = {
        "benford_law_analysis": benford_res,
        "big_five_ocean_profile": big_five_res
    }

    os.makedirs("enriched_data", exist_ok=True)
    out_file = os.path.join("enriched_data", f"tiktok_{clean_user}_enriched.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "username": clean_user,
        "saved_to": out_file,
        "benford_law": benford_res,
        "big_five_ocean": big_five_res,
        "full_data": enriched
    }


@app.get("/api/tiktok/{username}/benford", tags=["Enrichment"])
async def get_benford_law(username: str):
    clean_user = username.lstrip("@").strip()
    data = _get_or_scrape_data(clean_user)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos guardados para @{clean_user}. Primero ejecútalo en /api/tiktok/{clean_user} o /enrich."
        )
    return analyze_benford(data)


@app.get("/api/tiktok/{username}/big-five", tags=["Enrichment"])
async def get_big_five_profile(username: str):
    clean_user = username.lstrip("@").strip()
    data = _get_or_scrape_data(clean_user)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos guardados para @{clean_user}. Primero ejecútalo en /api/tiktok/{clean_user} o /enrich."
        )
    return analyze_big_five_gemini(data)


# =============================================================================
# SCRAPER ENDPOINTS
# =============================================================================

@app.get("/api/tiktok/{username}", tags=["Scraper"])
async def get_tiktok_profile(
    username: str,
    max_items: int = Query(30, description="Límite de usuarios en listas de seguidores/seguidos"),
    max_videos: int = Query(10, description="Cantidad de videos recientes a extraer"),
    max_comments: int = Query(15, description="Cantidad de comentarios a extraer por cada video"),
):
    clean_user = username.lstrip("@").strip()
    scraper = TikTokScraper(headless=True)
    data = await scraper.scrape(
        username=clean_user,
        max_list_items=max_items,
        max_videos=max_videos,
        max_comments_per_video=max_comments
    )
    
    if not data.get("success"):
        raise HTTPException(
            status_code=404 if "no encontrado" in data.get("error", "") else 500,
            detail=data.get("error", "Error al procesar la solicitud.")
        )

    out_dir = "scraped_data"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"tiktok_{clean_user}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data


@app.post("/api/tiktok/scrape", tags=["Scraper"])
async def post_tiktok_scrape(payload: ScrapeRequest):
    clean_user = payload.username.lstrip("@").strip()
    scraper = TikTokScraper(headless=True)
    data = await scraper.scrape(
        username=clean_user,
        max_list_items=payload.max_list_items or 30,
        max_videos=payload.max_videos or 10,
        max_comments_per_video=payload.max_comments_per_video or 15
    )
    
    if not data.get("success"):
        raise HTTPException(
            status_code=404 if "no encontrado" in data.get("error", "") else 500,
            detail=data.get("error", "Error al procesar la solicitud.")
        )

    out_dir = "scraped_data"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"tiktok_{clean_user}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data


# =============================================================================
# GESTIÓN DE ARCHIVOS
# =============================================================================

@app.get("/api/files", tags=["Files"])
def list_files():
    scraped = os.listdir("scraped_data") if os.path.exists("scraped_data") else []
    enriched = os.listdir("enriched_data") if os.path.exists("enriched_data") else []
    return {
        "scraped_files_count": len(scraped),
        "scraped_files": scraped,
        "enriched_files_count": len(enriched),
        "enriched_files": enriched
    }


@app.get("/api/files/{category}/{filename}", tags=["Files"])
def get_file_content(category: str, filename: str):
    if category not in ["scraped", "enriched"]:
        raise HTTPException(status_code=400, detail="Categoría inválida. Usa 'scraped' o 'enriched'.")
    folder = "scraped_data" if category == "scraped" else "enriched_data"
    path = os.path.join(folder, os.path.basename(filename))
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Puerto de escucha (por defecto 8000)")
    args, _ = parser.parse_known_args()

    print("\n" + "=" * 65)
    print(f"🚀 SERVIDOR SWAGGER ACTIVO: http://127.0.0.1:{args.port}/docs")
    print("   Presiona Ctrl + C para detener el servidor cuando desees.")
    print("=" * 65 + "\n")
    try:
        uvicorn.run("api:app", host="127.0.0.1", port=args.port, reload=True)
    except Exception as e:
        print(f"\n⚠️ Error al abrir el puerto {args.port}: {e}")
        print(f"Probando automáticamente en el puerto 8080...")
        uvicorn.run("api:app", host="127.0.0.1", port=8080, reload=True)
