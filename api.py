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
