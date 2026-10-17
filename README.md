# 📱 TikTok Scraper (ScrapyTikTok)

Scraper automatizado y API REST para extraer información de perfiles de **TikTok** utilizando únicamente el **nick o nombre de usuario** como entrada.

Diseñado tanto para ejecución directa en consola como para ser consumido como backend desde aplicaciones móviles (Android, iOS, Flutter, React Native).

---

## 🚀 Datos Extraídos por Usuario

Con solo ingresar el nick (por ejemplo `@mrbeast` o `tiktok`), el sistema extrae:
- **Nick / Nombre de usuario:** (`username`, ej. `@mrbeast`)
- **Nombre visible / Apodo:** (`nickname`, ej. `MrBeast`)
- **Foto o imagen de perfil en alta resolución:** (`avatar_url`, resolución 1080x1080)
- **Número de seguidores:** (`followers_count`, ej. `144,200,000`)
- **Número de seguidos:** (`following_count`, ej. `346`)
- **Total de Me Gusta (Hearts):** (`heart_count`, con soporte para cuentas multimillonarias)
- **Total de videos publicados:** (`video_count`)
- **Biografía / Descripción:** (`bio`)
- **Estado de verificación:** (`verified`)
- **Listado de cuentas asociadas / sugeridas:** (`following_list`, con nick, nombre, seguidores y avatar de cada uno)
- **Exportación automática en formato JSON:** `tiktok_<username>.json`

---

## 📦 Requisitos Previos

- **Python 3.10+** (probado en Python 3.12)
- Navegador Chromium para Playwright

### Instalación de dependencias:

```bash
# 1. Instalar librerías de Python
pip install -r requirements.txt

# 2. Instalar el binario de Chromium para Playwright
playwright install chromium
```

---

## 💻 1. Uso desde Consola (CLI)

### Modo interactivo:
Simplemente ejecuta:
```bash
python cli.py
```
El sistema te pedirá el nombre de usuario:
```text
👉 Ingrese el nick o nombre de usuario de TikTok: khaby.lame
```

### Modo directo con argumento:
```bash
python cli.py tiktok
python cli.py mrbeast
python cli.py khaby.lame
```

### Opciones adicionales:
- `--session-id <cookie>`: *(Opcional)* Si deseas pasar una cookie de sesión de TikTok para desbloquear el modal estricto de seguidores.
- `--max-items <num>`: Límite de cuentas a extraer en las listas (por defecto: 30).

---

## 🌐 2. Modo API REST (Para Apps Móviles)

Puedes levantar el servidor API para que tu aplicación móvil haga peticiones HTTP:

```bash
python api.py
```
O con `uvicorn`:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

- **Documentación Swagger interactiva:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Endpoint GET:** `GET http://localhost:8000/api/tiktok/{username}`
- **Endpoint POST:** `POST http://localhost:8000/api/tiktok/scrape`

### Ejemplo de respuesta JSON:

```json
{
  "success": true,
  "username": "khaby.lame",
  "nickname": "Khabane lame",
  "avatar_url": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/...~tplv-tiktokx-cropcenter:1080:1080.jpeg",
  "followers_count": 163000000,
  "following_count": 81,
  "heart_count": 2689396109,
  "video_count": 1359,
  "bio": "Se vuoi ridere sei nel posto giusto😎",
  "verified": true,
  "private_account": false,
  "following_list": [
    {
      "username": "alexmateo_p",
      "nickname": "🔥• Alex Mateo • 🔥",
      "avatar_url": "https://p16-common-sign.tiktokcdn.com/...",
      "followers_count": 1500000,
      "following_count": 2718,
      "verified": false
    }
  ],
  "videos": [
    {
      "video_id": "7697653789007908126",
      "video_url": "https://www.tiktok.com/@mrbeast/video/7697653789007908126",
      "description": "It really be like that 😭",
      "date": "2026-10-17 15:08:26 UTC",
      "likes_count": 827700,
      "comments_count": 17800,
      "views_count": 5200000,
      "shares_count": 12400,
      "bookmarks_count": 41994,
      "music_title": "sonido original",
      "music_author": "MrBeast",
      "comments": [
        {
          "comment_id": "7426861234567890123",
          "username": "dew",
          "nickname": "Dew",
          "avatar_url": "https://p16-common-sign.tiktokcdn.com/...",
          "text": "ok",
          "likes_count": 31770,
          "replies_count": 124,
          "date": "2026-10-17 15:10:00 UTC"
        }
      ]
    }
  ]
}
```

---

## 🔒 Aspectos Técnicos Destacados

1. **Evasión de WAF y Anti-Bot:** TikTok utiliza Cloudflare / Akamai / Slardar WAF. Este proyecto implementa **Playwright Stealth**, emulación de Chrome nativo y contextos aislados por video para evitar bloqueos y rate-limits.
2. **Orden Cronológico Descendente:** Los videos descubiertos se ordenan automáticamente utilizando sus identificadores numéricos Snowflake de 64 bits (`ID mayor = video más reciente`), garantizando los 10 últimos videos reales.
3. **Métricas de Interacción Completas:** Para cada video se extraen likes, contador de comentarios, reproducciones (views), compartidos (shares) y guardados en favoritos (bookmarks).
4. **Captura Dinámica de Comentarios:** Mediante clics nativos en el componente de comentarios se activa la API interna de TikTok, capturando los comentarios con autor, texto, me gusta y fecha.
5. **Cero Dependencia de Cuentas Específicas:** Funciona con cualquier nick público de TikTok de manera universal.