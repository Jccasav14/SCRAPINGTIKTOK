# TikTok Profile, Videos & Comments Scraper

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg) ![Playwright](https://img.shields.io/badge/playwright-v1.40-green.svg) ![FastAPI](https://img.shields.io/badge/fastAPI-0.100%2B-teal.svg) ![License](https://img.shields.io/badge/license-MIT-purple.svg)




## 🛠️ Preguntas Frecuentes y Solución de Problemas

### ¿Por qué la lista de seguidos aparece como privada?
TikTok permite a cada usuario configurar su lista de seguidos como privada ('Solo yo'). En esos casos la API devuelve código `10222` y el scraper lo notifica explícitamente.

### Despliegue en la Nube (Railway / Render / VPS)
Puedes desplegar `api.py` fácilmente ejecutando:
```bash
playwright install --with-deps chromium
uvicorn api:app --host 0.0.0.0 --port 8000
```
