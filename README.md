# TikTok Profile, Videos & Comments Scraper

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg) ![Playwright](https://img.shields.io/badge/playwright-v1.40-green.svg) ![FastAPI](https://img.shields.io/badge/fastAPI-0.100%2B-teal.svg) ![License](https://img.shields.io/badge/license-MIT-purple.svg)

Scraper profesional para perfiles de TikTok desarrollado en Python con **Playwright**, **Playwright-Stealth** y **FastAPI**. Extrae información completa de usuarios, métricas de videos y comentarios en tiempo real sin requerir APIs oficiales de pago.

---

## 🚀 Características Principales

- **Datos de Perfil Completos**:
  - Nickname, usuario único (`@username`), biografía y verificación oficial.
  - Foto de perfil en máxima resolución (avatar HD).
  - Métricas globales: seguidores, seguidos, me gusta totales y total de videos publicados.
- **Listas de Seguidores y Seguidos**:
  - Extracción directa mediante scroll inteligente en modal nativo.
  - Detección automática de listas privadas (código TikTok `10222`).
- **Últimos Videos e Interacciones**:
  - Extracción de videos recientes ordenados cronológicamente por Snowflake ID.
  - Métricas individuales: Likes, Comentarios, Vistas (play count), Shares y Guardados.
  - Metadatos de música/audio (título de canción y artista).
- **Comentarios Reales por Video**:
  - Intercepción asíncrona de eventos de red hacia `api/comment/list`.
  - Fallback por evaluación de DOM ante respuestas bloqueadas o dinámicas.
  - Identificación del autor de cada comentario, fecha formateada y likes recibidos.
- **Doble Modo de Uso**:
  - Consola interactiva (CLI) con salida enriquecida y exportación JSON.
  - Servidor REST (FastAPI) con Swagger UI interactivo listo para apps móviles.

---

## 🏗️ Arquitectura Modular

```
ScrapyTikTok/
│
├── tiktok_scraper.py   # Motor principal de scraping asíncrono con Playwright Stealth
├── cli.py              # Interfaz de línea de comandos para terminal
├── api.py              # API RESTful con FastAPI y Swagger UI
├── requirements.txt    # Dependencias del proyecto
├── .env.example        # Plantilla para cookie opcional TIKTOK_SESSION_ID
└── README.md           # Documentación y manual de uso
```

### Flujo de Ejecución

1. **Evasión Anti-Detección**: Playwright inicia Chromium enmascarando `navigator.webdriver` y flags de automatización.
2. **Rehidratación de Datos**: Navega al perfil e intercepta `__UNIVERSAL_DATA_FOR_REHYDRATION__` para obtener estadísticas exactas.
3. **Pestañas Aisladas por Video**: Cada video se procesa en un contexto limpio para evitar rate limits de TikTok.
4. **Intercepción de Comentarios**: Escucha el endpoint `comment/list` de TikTok al disparar el botón nativo de comentarios.

---

## 📦 Instalación y Configuración

```bash
# 1. Clonar el repositorio
git clone https://github.com/Jccasav14/SCRAPINGTIKTOK.git
cd SCRAPINGTIKTOK

# 2. Instalar dependencias de Python
pip install -r requirements.txt

# 3. Instalar binarios de Chromium para Playwright
playwright install chromium
```

---

## 💻 Uso en Terminal (CLI)

```bash
# Scraping básico de un usuario (ejemplo: tiktok)
python cli.py tiktok

# Scraping especificando límite de videos y comentarios
python cli.py mrbeast --max-videos 5 --max-comments 10

# Usando cookie de sesión para saltar login walls
python cli.py khaby.lame --session-id "TU_COOKIE_SESSIONID"
```

---

## 🌐 Servidor API REST (FastAPI)

Inicia el servidor localmente con Uvicorn:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Visita la documentación interactiva en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints Principales

- `GET /health` - Estado de salud del servicio.
- `GET /api/tiktok/{username}` - Scraping rápido vía parámetros de URL.
- `POST /api/tiktok/scrape` - Scraping vía JSON body (ideal para Flutter/React Native/Android).

---

## 🛠️ Preguntas Frecuentes y Solución de Problemas

### ¿Cómo obtener la cookie `sessionid` de TikTok?
1. Inicia sesión en [tiktok.com](https://www.tiktok.com) desde tu navegador (Chrome/Edge/Firefox).
2. Abre las Herramientas de Desarrollador (`F12`) y ve a la pestaña **Application** (o **Almacenamiento**).
3. En el menú izquierdo, despliega **Cookies** -> `https://www.tiktok.com`.
4. Busca la cookie con nombre `sessionid` y copia su valor.
5. Puedes colocarla en un archivo `.env`:
   ```env
   TIKTOK_SESSION_ID=tu_cookie_copiada_aqui
   ```

### ¿Por qué la lista de seguidos aparece como privada?
TikTok permite a cada usuario configurar su lista de seguidos como privada ('Solo yo'). En esos casos la API de TikTok responde con código `10222` y el scraper lo notifica explícitamente sin romper el flujo de ejecución.

### Despliegue en la Nube (Railway / Render / VPS)
Para desplegar `api.py` en producción:
```bash
playwright install --with-deps chromium
uvicorn api:app --host 0.0.0.0 --port 8000
```

---
*Desarrollado para la materia de Programación para Dispositivos Móviles - Décimo Semestre.* 🚀
