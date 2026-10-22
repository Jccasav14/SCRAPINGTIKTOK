# INFORME TÉCNICO DE PROYECTO: SISTEMA DE EXTRACCIÓN, AUDITORÍA FORENSE Y PERFILAMIENTO PSICOMÉTRICO EN TIKTOK

**Asignatura:** Programación para Dispositivos Móviles  
**Nivel Académico:** Décimo Semestre  
**Institución:** Carrera de Ingeniería en Sistemas de Información  
**Repositorio Oficial:** https://github.com/Jccasav14/SCRAPINGTIKTOK.git  
**Fecha de Publicación:** Octubre de 2026  
**Versión del Sistema:** 2.6.0  

---

## TABLA DE CONTENIDOS

1. Resumen Ejecutivo
2. Objetivos del Proyecto
   - 2.1. Objetivo General
   - 2.2. Objetivos Específicos
3. Arquitectura del Sistema
   - 3.1. Diagrama de Capas y Flujo de Procesamiento
   - 3.2. Tecnologías y Bibliotecas Principales
4. Módulos Funcionales
   - 4.1. Módulo 1: Extracción de Datos en Tiempo Real (tiktok_scraper.py)
   - 4.2. Módulo 2: Enriquecimiento Forense y Ley de Benford (data_enricher.py)
   - 4.3. Módulo 3: Perfilamiento Psicométrico Big Five y Emociones (data_enricher.py)
   - 4.4. Módulo 4: Renderizado de Gráficos Vectoriales SVG (chart_generator.py)
   - 4.5. Módulo 5: Interfaz de Consola y Automatización (cli.py)
   - 4.6. Módulo 6: Servicio Web API REST y Swagger UI (api.py)
5. Estructura de Directorios y Persistencia de Archivos
6. Fundamentos Matemáticos y Metodológicos
   - 6.1. Formulación de la Ley de Benford
   - 6.2. Prueba de Bondad de Ajuste Chi-cuadrado
   - 6.3. Modelo Psicométrico OCEAN (Cinco Grandes Rasgos de Personalidad)
7. Catálogo de Endpoints de la API REST
8. Diccionario y Estructura de Datos (JSON)
9. Requisitos del Entorno e Instalación
10. Guía de Ejecución y Manual de Operación
    - 10.1. Configuración de Variables de Entorno
    - 10.2. Uso por Línea de Comandos (CLI)
    - 10.3. Despliegue del Servidor Web FastAPI
    - 10.4. Interacción con la Interfaz Swagger UI
11. Mecanismos de Evasión Anti-Bot y Manejo de Excepciones
12. Conclusiones y Recomendaciones Técnicas

---

## 1. RESUMEN EJECUTIVO

El presente proyecto documenta el diseño, desarrollo e implementación de una plataforma integral de inteligencia de datos orientada a la red social TikTok. El sistema resuelve la necesidad de auditar y analizar perfiles de creadores de contenido, comunidades e interacciones digitales sin depender de interfaces de programación de aplicaciones (API) comerciales restringidas o de pago.

La solución se estructura en tres pilares esenciales:
- **Extracción de Datos de Alto Rendimiento:** Emplea automatización de navegadores basada en Playwright en modo asíncrono con técnicas de camuflaje anti-detección (stealth), intercepción de tráfico de red y parseo resiliente de estructuras JSON en el DOM.
- **Auditoría Forense de Tráfico (Detección de Anomalías):** Aplica la Ley de Benford combinada con la prueba estadística Chi-cuadrado ($\chi^2$) sobre muestras numéricas masivas (métricas de seguidores, seguidos, reproducciones, me gusta y comentarios) para calcular la probabilidad de manipulación artificial mediante granjas de bots.
- **Perfilamiento Psicométrico mediante Inteligencia Artificial Generativa:** Conexión con los modelos de lenguaje de última generación de Google Gemini para procesar transcripciones, descripciones y comentarios comunitarios, evaluando los cinco grandes factores de la personalidad humana (OCEAN) y el espectro emocional dominante de la audiencia.

Los resultados son presentados a través de una API RESTful construida con FastAPI, documentada con OpenAPI y Swagger UI, integrando una barra interactiva de control y visualización de gráficos vectoriales SVG directamente dentro de la interfaz Swagger.

---

## 2. OBJETIVOS DEL PROYECTO

### 2.1. Objetivo General
Diseñar e implementar un sistema de software modular en Python para la recolección automatizada, auditoría estadística y análisis psicométrico de perfiles de TikTok, exponiendo los datos y representaciones gráficas a través de servicios web REST optimizados para el consumo desde clientes móviles y de escritorio.

### 2.2. Objetivos Específicos
- Desarrollar un motor de scraping asíncrono basado en Chromium capaz de evadir firmas de automatización (`navigator.webdriver`) e interceptar eventos de red de TikTok.
- Extraer metadatos de usuario, listas de seguidores/seguidos con manejo de privacidad (código `10222`), últimos videos con orden cronológico basado en Snowflake ID y comentarios reales por video.
- Formular e implementar un motor de auditoría estadística que contraste la distribución empírica del primer dígito de las métricas contra la distribución logarítmica de Benford.
- Integrar la API de Google Gemini (modelo `gemini-2.5-flash`) para transformar texto informal y comentarios en métricas cuantitativas psicométricas (OCEAN) y análisis de sentimiento.
- Diseñar un módulo generador de gráficos vectoriales SVG ligeros con tema visual armónico e integrarlos de manera nativa en la documentación interactiva de Swagger UI.
- Separar de manera estricta los conjuntos de datos en crudo (`scraped_data/`) de los resultados procesados (`enriched_data/`), garantizando la trazabilidad y la privacidad de las credenciales.

---

## 3. ARQUITECTURA DEL SISTEMA

### 3.1. Diagrama de Capas y Flujo de Procesamiento

El flujo de información en el sistema se compone de capas independientes de adquisición, procesamiento analítico, renderizado y exposición:

```
[ Cliente: Navegador Web / Swagger UI / App Móvil / CLI ]
                           │
                           ▼
          [ Capa de Exposición: FastAPI (api.py) ]
          ├── Endpoints JSON de Scraping y Auditoría
          ├── Endpoints SVG de Gráficos Vectoriales
          └── Middleware CORS y Custom Swagger UI HTML
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
[ Capa de Scraping ]                [ Capa de Enriquecimiento ]
(tiktok_scraper.py)                 (data_enricher.py)
├── Playwright Chromium             ├── Módulo Ley de Benford
├── Stealth Context                  │   ├── Extractor de dígitos
├── Intercepción de Red              │   └── Bondad de Ajuste Chi^2
│   └── comment/list                └── Módulo Google Gemini AI
└── Parseo DOM y Rehidratación          ├── Modelo gemini-2.5-flash
       │                                ├── Arquetipo Psicométrico
       ▼                                └── Sentimiento y Emociones
[ Directorio de Persistencia ]                 │
(scraped_data/usuario.json) ───────►───────────┘
                                               │
                                               ▼
                              [ Capa Gráfica: chart_generator.py ]
                              ├── Gráfico de Barras Benford (SVG)
                              └── Panel Psicométrico OCEAN (SVG)
                                               │
                                               ▼
                              [ Directorio de Persistencia ]
                              (enriched_data/usuario_enriched.json)
```

### 3.2. Tecnologías y Bibliotecas Principales

| Componente / Biblioteca | Versión Mínima | Función Principal |
| :--- | :--- | :--- |
| **Python** | 3.10+ | Lenguaje base del proyecto con tipado estático opcional (`typing`). |
| **Playwright** | 1.40+ | Automatización asíncrona de navegador web Chromium. |
| **Playwright-Stealth** | 1.0.6+ | Eliminación de atributos y huellas de automatización del navegador. |
| **FastAPI** | 0.100+ | Framework web asíncrono para la construcción de la API REST. |
| **Uvicorn** | 0.22+ | Servidor ASGI de alto rendimiento para FastAPI. |
| **Pydantic** | 2.0+ | Validación y serialización estricta de esquemas de datos. |
| **Requests** | 2.31+ | Cliente HTTP síncrono para interacción con la API REST de Google Gemini. |
| **SciPy** | 1.11+ (Opcional) | Cálculo de valores p para distribuciones acumuladas Chi-cuadrado con fallback algebraico. |
| **Python-Dotenv** | 1.0+ | Gestión y carga segura de variables de entorno desde `.env`. |

---

## 4. MÓDULOS FUNCIONALES

### 4.1. Módulo 1: Extracción de Datos en Tiempo Real (`tiktok_scraper.py`)
Encapsula la clase `TikTokScraper`, responsable de interactuar con los servidores de TikTok simulando navegación humana.
- **Inicialización y Camuflaje:** Lanza Chromium con banderas `--disable-blink-features=AutomationControlled`, argumentos de sandbox restringido y resolución estándar de pantalla (1280x800).
- **Gestión de Sesión:** Soporta la inyección opcional de la cookie `sessionid` para perfiles con restricciones de acceso geográfico o edad.
- **Extracción de Perfil:** Obtiene los datos base a partir del bloque de rehidratación `__UNIVERSAL_DATA_FOR_REHYDRATION__` incrustado en el HTML del perfil de TikTok.
- **Listas de Seguidores y Seguidos:** Automatiza la apertura de los diálogos modales correspondientes, realiza desplazamiento progresivo e intercepta la respuesta interna. Si el perfil tiene la lista protegida, detecta el código `10222` e informa el estado privado sin interrumpir el proceso.
- **Métricas de Video y Comentarios:** Accede individualmente a los videos más recientes, extrae estadísticas de interacción (reproducciones, likes, compartidos, comentarios y guardados) e intercepta el endpoint de red `api/comment/list`. Ante ventanas flotantes superpuestas (`TUXModal-overlay`), remueve los elementos obstructores del DOM y ejecuta clics nativos vía JavaScript (`page.evaluate`).

### 4.2. Módulo 2: Enriquecimiento Forense y Ley de Benford (`data_enricher.py`)
Implementa las funciones `extract_numbers_from_data` y `analyze_benford`.
- Recorre de manera recursiva la totalidad de números enteros mayores o iguales a 10 presentes en el perfil (seguidores, seguidos, likes globales, conteo de videos, estadísticas de videos individuales y likes en comentarios).
- Extrae el primer dígito significativo ($d \in \{1, 2, \dots, 9\}$) de cada observación.
- Calcula las frecuencias relativas observadas frente a las probabilidades teóricas logarítmicas.
- Aplica el estadístico Chi-cuadrado para determinar si la distribución de los datos se aparta de manera anómala de la ley natural, generando un diagnóstico cualitativo:
  - *Distribución Orgánica/Natural:* $p \ge 0.05$.
  - *Leve Desviación:* $0.01 \le p < 0.05$.
  - *Anomalía Significativa (Sospecha de Manipulación/Bots):* $p < 0.01$.

### 4.3. Módulo 3: Perfilamiento Psicométrico Big Five y Emociones (`data_enricher.py`)
Implementa la función `analyze_big_five_gemini`.
- Construye un corpus condensado a partir de la biografía del creador, títulos y descripciones de sus videos más populares y una muestra representativa de los comentarios generados por su audiencia.
- Envía un requerimiento estructurado a la API de Google Gemini utilizando el modelo `gemini-2.5-flash` (con respaldo automático a `gemini-flash-latest`).
- Obtiene una estructura JSON con:
  - Puntuaciones cuantitativas (0 a 100) para cada dimensión OCEAN: Apertura a la Experiencia, Responsabilidad, Extraversión, Amabilidad y Neuroticismo.
  - Arquetipo de personalidad asignado y justificación textual.
  - Distribución porcentual de emociones comunitarias (Alegría, Curiosidad, Admiración, Escepticismo, Hostilidad, Neutralidad).
  - Sentimiento global consolidado (Positivo, Neutral o Negativo).

### 4.4. Módulo 4: Renderizado de Gráficos Vectoriales SVG (`chart_generator.py`)
Diseña y genera documentos SVG nativos con temática clara, tipografía moderna del sistema y dimensiones responsivas:
- `generate_benford_svg`: Produce un gráfico de barras comparativas dobles (frecuencia observada vs. frecuencia esperada de Benford para cada dígito del 1 al 9), complementado con una tarjeta resumen que reporta el tamaño de la muestra, el estadístico $\chi^2$ y el veredicto de autenticidad.
- `generate_big_five_svg`: Construye un panel psicométrico que despliega barras horizontales de progreso con colores diferenciados para cada dimensión OCEAN, acompañadas del arquetipo del creador, pastillas de emociones comunitarias y una barra de balance de sentimiento de la comunidad.

### 4.5. Módulo 5: Interfaz de Consola y Automatización (`cli.py`)
Provee una interfaz por terminal con argumentos flexibles (`--max-videos`, `--max-comments`, `--enrich`, `--headless`, `--session-id`). Incluye formateo tabular en texto plano e integración automática para guardar los resultados en las carpetas designadas.

### 4.6. Módulo 6: Servicio Web API REST y Swagger UI (`api.py`)
Expone todos los servicios mediante FastAPI. Incorpora:
- Inyección de una barra superior flotante en Swagger UI con campo de texto único para el nombre de usuario y botón de sincronización de rutas, optimizando la experiencia de prueba.
- Endpoints dedicados para visualización directa de gráficos vectoriales SVG dentro de las respuestas de Swagger UI o mediante URLs navegables.
- Endpoints de descarga y lectura de archivos procesados.

---

## 5. ESTRUCTURA DE DIRECTORIOS Y PERSISTENCIA DE ARCHIVOS

El repositorio mantiene una estricta separación de responsabilidades, aislando los datos en crudo de los datos enriquecidos para evitar colisiones y mantener un control de versiones ordenado:

```
ScrapyTikTok/
│
├── api.py                    # Servidor FastAPI, endpoints y personalización de Swagger UI
├── chart_generator.py        # Generador de gráficos vectoriales SVG (Benford y Big Five)
├── cli.py                    # Cliente interactivo de línea de comandos (Terminal)
├── data_enricher.py          # Lógica de Ley de Benford, Chi-cuadrado y Google Gemini AI
├── tiktok_scraper.py         # Motor de extracción web asíncrono con Playwright Stealth
│
├── requirements.txt          # Dependencias y librerías de Python
├── .env.example              # Plantilla de variables de entorno requeridas
├── .gitignore                # Reglas de exclusión para Git (sin comentarios)
├── README.md                 # Informe técnico y documentación del proyecto
│
├── scraped_data/             # Almacén de perfiles extraídos en formato JSON crudo
│   ├── mrbeast.json
│   └── asados.del.torito8.json
│
└── enriched_data/            # Almacén de perfiles analizados y enriquecidos (Forense + IA)
    ├── mrbeast_enriched.json
    └── asados.del.torito8_enriched.json
```

---

## 6. FUNDAMENTOS MATEMÁTICOS Y METODOLÓGICOS

### 6.1. Formulación de la Ley de Benford

La Ley de Benford (o Ley del Primer Dígito) postula que en conjuntos de datos numéricos que crecen de manera exponencial o que surgen de procesos naturales no restringidos, la probabilidad $P(d)$ de que un número tenga como primer dígito significativo a $d \in \{1, 2, \dots, 9\}$ se expresa mediante la fórmula logarítmica:

$$P(d) = \log_{10}\left(1 + \frac{1}{d}\right)$$

La siguiente tabla detalla la distribución probabilística teórica esperada:

| Primer Dígito ($d$) | Probabilidad Teórica ($P(d)$) | Porcentaje Esperado |
| :---: | :---: | :---: |
| **1** | $\log_{10}(2) \approx 0.3010$ | 30.1% |
| **2** | $\log_{10}(1.5) \approx 0.1761$ | 17.6% |
| **3** | $\log_{10}(1.3333) \approx 0.1249$ | 12.5% |
| **4** | $\log_{10}(1.25) \approx 0.0969$ | 9.7% |
| **5** | $\log_{10}(1.2) \approx 0.0792$ | 7.9% |
| **6** | $\log_{10}(1.1667) \approx 0.0669$ | 6.7% |
| **7** | $\log_{10}(1.1429) \approx 0.0580$ | 5.8% |
| **8** | $\log_{10}(1.125) \approx 0.0512$ | 5.1% |
| **9** | $\log_{10}(1.1111) \approx 0.0458$ | 4.6% |

Las redes sociales orgánicas presentan métricas distribuidas a través de múltiples órdenes de magnitud, cumpliendo con esta ley. Desviaciones marcadas sugieren manipulación artificial, valores truncados o intervención de cuentas sintéticas automatizadas.

### 6.2. Prueba de Bondad de Ajuste Chi-cuadrado

Para determinar formalmente si las frecuencias observadas ($O_d$) de los primeros dígitos se ajustan a las frecuencias teóricas esperadas ($E_d = N \cdot P(d)$), donde $N$ es el tamaño total de la muestra, se evalúa el estadístico de Pearson:

$$\chi^2 = \sum_{d=1}^{9} \frac{(O_d - E_d)^2}{E_d}$$

Con un número de grados de libertad $df = 9 - 1 = 8$.

El valor $p$ resultante se contrasta contra los niveles de significancia tradicionales:
- **Hipótesis Nula ($H_0$):** Los datos observados siguen una distribución natural de Benford.
- Si $p \ge 0.05$, no se rechaza $H_0$; el tráfico y las métricas se consideran consistentes con un comportamiento orgánico.
- Si $p < 0.05$ (o $p < 0.01$), se rechaza $H_0$ con evidencia estadística de anomalías numéricas.

### 6.3. Modelo Psicométrico OCEAN (Cinco Grandes Rasgos de Personalidad)

El modelo de los Cinco Grandes factores es el estándar contemporáneo de la psicología para la evaluación de la personalidad:
- **Apertura a la Experiencia (Openness):** Curiosidad intelectual, creatividad y disposición a ideas no convencionales.
- **Responsabilidad (Conscientiousness):** Nivel de disciplina, organización y orientación al cumplimiento de metas.
- **Extraversión (Extraversion):** Energía social, asertividad, entusiasmo y dinamismo en la comunicación.
- **Amabilidad (Agreeableness):** Empatía, cooperación, calidez y actitud conciliadora con la comunidad.
- **Neuroticismo (Neuroticism):** Reactividad emocional ante el estrés, susceptibilidad y volatilidad en el tono discursivo.

El sistema sintetiza el comportamiento del creador y de su comunidad mediante un prompt estructurado procesado por Google Gemini, obteniendo un perfil numérico normalizado (0 a 100) junto a un arquetipo cualitativo (ejemplo: "Líder Inspirador", "Creador Emprendedor").

---

## 7. CATÁLOGO DE ENDPOINTS DE LA API REST

La API se encuentra documentada de acuerdo al estándar OpenAPI 3.0. A continuación se detallan los endpoints disponibles en el servicio:

| Método | Ruta | Tag | Descripción | Respuesta Principal |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/health` | Health | Verificación del estado operativo y versión del microservicio. | JSON (`{"status": "ok"}`) |
| **GET** | `/` | Documentación | Redirección automática a la interfaz interactiva `/docs`. | HTTP 307 Redirect |
| **GET** | `/api/tiktok/{username}` | Scraper | Ejecuta la extracción en vivo de los datos del perfil indicado. | JSON (Datos completos del perfil) |
| **POST** | `/api/tiktok/scrape` | Scraper | Endpoint alternativo de extracción que recibe un cuerpo JSON. | JSON (Datos completos del perfil) |
| **GET** | `/api/tiktok/{username}/benford` | Enrichment | Aplica exclusivamente la prueba de Benford y Chi-cuadrado. | JSON (Estadísticos forenses) |
| **GET** | `/api/tiktok/{username}/big-five` | Enrichment | Aplica exclusivamente el análisis psicométrico con Gemini AI. | JSON (OCEAN y Arquetipo) |
| **GET** | `/api/tiktok/{username}/enrich` | Enrichment | Ejecuta tanto Benford como Big Five y consolida el informe. | JSON (Informe unificado de enriquecimiento) |
| **GET** | `/api/tiktok/{username}/chart/benford` | Visual Charts | Retorna un gráfico vectorial SVG con la comparativa de barras de Benford. | `image/svg+xml` |
| **GET** | `/api/tiktok/{username}/chart/big-five` | Visual Charts | Retorna un gráfico vectorial SVG con las barras OCEAN y emociones. | `image/svg+xml` |
| **GET** | `/api/files/list` | Files | Lista los archivos JSON disponibles en `scraped_data/` y `enriched_data/`. | JSON (Listado de archivos) |
| **GET** | `/api/files/download/{cat}/{file}` | Files | Permite la descarga directa de un archivo JSON del servidor. | `application/json` (File Download) |

---

## 8. DICCIONARIO Y ESTRUCTURA DE DATOS (JSON)

### 8.1. Estructura de Extracción Base (`scraped_data/usuario.json`)
```json
{
  "username": "mrbeast",
  "nickname": "MrBeast",
  "verified": true,
  "signature": "I want to make the world a better place",
  "avatar_url": "https://p16-sign.tiktokcdn-us.com/...",
  "followers_count": 105000000,
  "following_count": 312,
  "heart_count": 950000000,
  "video_count": 480,
  "followers_list": [
    {
      "username": "usuario_ejemplo",
      "nickname": "Ejemplo",
      "followers_count": 1200,
      "following_count": 450
    }
  ],
  "following_list": [],
  "videos": [
    {
      "id": "7198273648123984",
      "url": "https://www.tiktok.com/@mrbeast/video/7198273648123984",
      "caption": "Surviving 7 days in the desert...",
      "created_at": "2026-10-15 14:30:00",
      "views_count": 45000000,
      "likes_count": 6200000,
      "comments_count": 48000,
      "shares_count": 12000,
      "bookmarks_count": 34000,
      "music": {
        "title": "Original Sound",
        "author": "MrBeast"
      },
      "comments": [
        {
          "author": "fan_1",
          "nickname": "Juan",
          "text": "Increible produccion como siempre",
          "likes_count": 1540,
          "created_at": "2026-10-15 15:00:00"
        }
      ]
    }
  ]
}
```

### 8.2. Estructura Enriquecida (`enriched_data/usuario_enriched.json`)
```json
{
  "username": "mrbeast",
  "scraped_at": "2026-10-21 21:00:00",
  "benford_analysis": {
    "sample_size": 184,
    "chi_square_stat": 4.12,
    "p_value": 0.8461,
    "natural_traffic": true,
    "risk_level": "Bajo (Orgánico)",
    "digit_frequencies": {
      "1": { "observed": 55, "observed_pct": 29.89, "expected_pct": 30.10 },
      "2": { "observed": 32, "observed_pct": 17.39, "expected_pct": 17.61 }
    }
  },
  "psychometric_analysis": {
    "archetype": "Filántropo Conquistador",
    "openness": 88,
    "conscientiousness": 95,
    "extraversion": 92,
    "agreeableness": 85,
    "neuroticism": 18,
    "summary": "Perfil altamente extrovertido y planificador orientado al entretenimiento de alto impacto.",
    "community_emotions": {
      "Admiración": 45,
      "Alegría": 35,
      "Curiosidad": 20
    },
    "community_sentiment": "Mayormente Positivo"
  }
}
```

---

## 9. REQUISITOS DEL ENTORNO E INSTALACIÓN

### Requisitos Previos
- Sistema Operativo: Windows 10/11, Ubuntu 20.04+ o macOS 12+.
- Python 3.10 o superior instalado en el PATH.
- Conexión a Internet activa.
- Cuenta o clave de API de Google Gemini (Google AI Studio).

### Procedimiento de Instalación Paso a Paso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Jccasav14/SCRAPINGTIKTOK.git
   cd SCRAPINGTIKTOK
   ```

2. **Crear y activar un entorno virtual (Recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux / macOS:
   source venv/bin/activate
   ```

3. **Instalar dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar los binarios de Chromium para Playwright:**
   ```bash
   playwright install chromium
   ```

---

## 10. GUÍA DE EJECUCIÓN Y MANUAL DE OPERACIÓN

### 10.1. Configuración de Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto tomando como referencia `.env.example`:

```env
# Clave de API de Google Gemini para perfilamiento psicométrico
GEMINI_API_KEY=tu_clave_de_google_ai_studio_aqui

# Cookie de sesión opcional para evitar login walls en TikTok
TIKTOK_SESSION_ID=tu_cookie_sessionid_opcional
```

### 10.2. Uso por Línea de Comandos (CLI)

El archivo `cli.py` permite realizar ejecuciones rápidas y diagnósticos directos por terminal.

```bash
# Extracción básica de perfil con valores predeterminados (10 videos, 15 comentarios)
python cli.py mrbeast

# Extracción personalizada con enriquecimiento automático y reporte por consola
python cli.py mrbeast --max-videos 5 --max-comments 10 --enrich

# Ejecución en modo visible (no headless) para depuración visual
python cli.py mrbeast --no-headless

# Enriquecer directamente un archivo previamente descargado sin volver a scrapear
python data_enricher.py scraped_data/mrbeast.json
```

### 10.3. Despliegue del Servidor Web FastAPI

Para inicializar la API REST con recarga automática:

```bash
# Ejecución directa del script principal de la API
python api.py

# O alternativamente utilizando uvicorn directamente
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

### 10.4. Interacción con la Interfaz Swagger UI

1. Abra su navegador web e ingrese a `http://127.0.0.1:8000/docs`.
2. Observe la barra superior fija integrada en el encabezado de Swagger UI.
3. Escriba el nombre de usuario de TikTok deseado en el campo **TikTok Username** (por ejemplo: `mrbeast` o `asados.del.torito8`).
4. Haga clic en el botón **Sincronizar Rutas**. Todos los parámetros de ruta `{username}` en la interfaz se actualizarán automáticamente.
5. Despliegue cualquier endpoint (por ejemplo `/api/tiktok/{username}/chart/benford`), presione **Try it out** y luego **Execute** para visualizar los gráficos vectoriales y los resultados directamente.

---

## 11. MECANISMOS DE EVASIÓN ANTI-BOT Y MANEJO DE EXCEPCIONES

TikTok implementa defensas dinámicas basadas en telemetría de navegador y límites de frecuencia. El sistema implementa soluciones a cada uno de estos desafíos:

1. **Detección de WebDriver:**
   - La librería `playwright-stealth` sobreescribe las propiedades `navigator.webdriver`, las interfaces de plugins, el proveedor de WebGL y la función de resolución de permisos de Chromium para simular una sesión de usuario humano real.
2. **Superposición de Modales (TUXModal-Overlay):**
   - Cuando TikTok detecta actividad de navegación automática, puede desplegar contenedores modales transparentes u oscuros que bloquean las acciones del cursor. El motor elimina estas capas superpuestas del árbol DOM antes de interactuar y utiliza disparadores nativos de JavaScript (`page.evaluate("(el) => el.click()", btn)`) para garantizar la ejecución del evento de apertura de comentarios o seguidores.
3. **Restricciones de Privacidad (Código 10222):**
   - Si la lista de seguidores o seguidos está restringida por la configuración del perfil, la API interna responde con el error `10222`. El scraper intercepta este código y marca la lista como privada en el JSON resultante sin provocar caídas de ejecución.
4. **Respaldo de Modelos de Lenguaje (Gemini Fallback):**
   - En caso de que el modelo principal `gemini-2.5-flash` presente latencia o indisponibilidad por cuotas, el enriquecedor conmuta de forma transparente hacia `gemini-flash-latest`, garantizando la continuidad del análisis.
5. **Fallback Estadístico sin SciPy:**
   - Si el entorno de ejecución no cuenta con la biblioteca `scipy`, el sistema cuenta con un algoritmo aproximado de integración de la función Chi-cuadrado con 8 grados de libertad, manteniendo el cálculo del valor $p$ sin dependencias externas obligatorias.

---

## 12. CONCLUSIONES Y RECOMENDACIONES TÉCNICAS

1. **Eficacia de la Auditoría Forense:** La combinación de la Ley de Benford con la prueba Chi-cuadrado sobre colecciones de métricas heterogéneas demuestra ser un método matemático fiable para identificar perfiles cuyas cifras presentan distribuciones artificiales inducidas por compra de interacciones o granjas de bots.
2. **Potencial del Enriquecimiento con LLMs:** La inferencia psicométrica de Big Five y el análisis de sentimiento a partir de comentarios permiten pasar de una simple recolección cuantitativa a un diagnóstico cualitativo de reputación y tono de comunidad.
3. **Ventaja del Renderizado Vectorial SVG:** La generación de gráficos SVG en el backend elimina la necesidad de librerías JavaScript pesadas en el frontend (como Chart.js o D3.js) y permite que los gráficos se visualicen de forma nativa en cualquier cliente HTTP, navegador o visor integrado de Swagger UI.
4. **Recomendaciones Operativas:**
   - Se recomienda el uso de proxies rotativos residenciales si se planea la extracción masiva continua de más de 50 perfiles por hora para mitigar bloqueos temporales por dirección IP.
   - Para perfiles corporativos o de gran volumen, se sugiere mantener actualizada la variable `TIKTOK_SESSION_ID` con una cuenta de prueba regular.

---
*Documento elaborado como parte del proyecto de fin de curso de Programación para Dispositivos Móviles.*
