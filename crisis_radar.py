#!/usr/bin/env python3
"""
Módulo de Inteligencia de Crisis y Radar de Cancelación para TikTok (CrisisRadar)
Analiza comentarios, sentimiento hostil, llamados a boicot y riesgo reputacional en tiempo real
utilizando modelos de lenguaje de última generación (Google Gemini AI).
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S", stream=sys.stdout)
logger = logging.getLogger("CrisisRadar")


def load_env_key(key_name: str = "GEMINI_API_KEY") -> Optional[str]:
    candidates = []
    if "__file__" in globals():
        candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    candidates.append(os.path.join(os.getcwd(), ".env"))

    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f"{key_name}=") and not line.startswith("#"):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass

    env_val = os.getenv(key_name)
    if env_val:
        return env_val.strip()
    return None


class CrisisRadar:
    """
    Motor de Detección Temprana de Funa y Auditoría de Crisis Reputacional.
    Evalúa la toxicidad comunitaria, hostilidad, sarcasmo y amenazas de boicot.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or load_env_key("GEMINI_API_KEY")
        self.models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]

    def analyze_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el escaneo de radar de crisis sobre un perfil extraído de TikTok.
        """
        key = self.api_key or load_env_key("GEMINI_API_KEY")
        if not key or key == "tu_gemini_api_key_aqui":
            return {
                "status": "missing_api_key",
                "message": "Falta la clave 'GEMINI_API_KEY' en tu archivo .env para el radar de crisis."
            }

        username = data.get("username", "desconocido")
        nickname = data.get("nickname", username)
        followers = data.get("followers_count", 0)
        videos = data.get("videos", [])

        if not videos:
            return {
                "status": "insufficient_data",
                "message": f"El perfil @{username} no contiene videos para evaluar comentarios."
            }

        # Extraer comentarios estructurados video por video
        video_payloads = []
        total_comments_scanned = 0

        for idx, v in enumerate(videos[:10], start=1):
            caption = v.get("description", v.get("caption", "Sin descripción"))
            v_url = v.get("url", f"https://www.tiktok.com/@{username}/video/{v.get('id', '')}")
            v_likes = v.get("likes_count", 0)
            v_views = v.get("views_count", 0)
            comments = v.get("comments", [])
            total_comments_scanned += len(comments)

            # Tomar los 10 comentarios con más interacciones por video
            sorted_comments = sorted(comments, key=lambda x: x.get("likes_count", 0), reverse=True)
            formatted_comments = []
            for c in sorted_comments[:10]:
                text = c.get("text", "").replace("\n", " ").strip()
                c_user = c.get("username", c.get("author", "anon"))
                c_likes = c.get("likes_count", 0)
                if text and len(text) > 2:
                    formatted_comments.append(f"  * @{c_user} ({c_likes:,} likes): \"{text[:150]}\"")

            video_payloads.append(
                f"[VIDEO #{idx}]\n"
                f"URL: {v_url}\n"
                f"Descripción: '{caption[:120]}' | Vistas: {v_views:,} | Likes: {v_likes:,}\n"
                f"Muestra de comentarios ({len(formatted_comments)}):\n" +
                (chr(10).join(formatted_comments) if formatted_comments else "  (Sin comentarios)")
            )

        # Contexto de Benford o Big Five si ya existen
        extra_context = []
        enrichment = data.get("data_enrichment", {})
        benford = enrichment.get("benford_law_analysis", {})
        if benford.get("status") == "success":
            extra_context.append(f"- Diagnóstico Benford: {'Tráfico Orgánico' if benford.get('conforms_to_benford') else 'Anomalía/Posible Raid de Bots'}")
        
        big_five = enrichment.get("big_five_ocean_profile", {})
        if big_five.get("status") == "success":
            extra_context.append(f"- Arquetipo del creador: {big_five.get('archetype', 'N/A')}")
            traits = big_five.get("ocean_traits", {})
            extra_context.append(f"- Neuroticismo del Creador: {traits.get('neuroticism', {}).get('score', 0)}%")

        context_str = "\n".join(extra_context) if extra_context else "No disponible"

        prompt = f"""
Eres un Director de Gestión de Crisis de Relaciones Públicas (PR Crisis Manager) y experto en ciberpsicología de redes sociales.
Tu misión es auditar la temperatura emocional y el riesgo de CANCELACIÓN (funa, boicot o crisis reputacional masiva) del creador @{username} en TikTok.

DATOS DEL PERFIL:
- Creador: @{username} ({nickname})
- Seguidores: {followers:,}
- Contexto previo:
{context_str}

REVISIÓN DE COMENTARIOS POR VIDEO:
{chr(10).join(video_payloads)}

DIRECTRICES DE AUDITORÍA:
1. Analiza si existen ataques coordinados, insultos, burlas ácidas, quejas graves o llamados explícitos a 'dejar de seguir', 'cancelar' o 'denunciar'.
2. Evalúa la distribución porcentual exacta de la reacción comunitaria en 4 cuadrantes (DEBEN SUMAR EXACTAMENTE 100%):
   - apoyo_admiracion: porcentaje de comentarios que defienden, felicitan o apoyan al creador.
   - critica_hostilidad: porcentaje de comentarios de queja, odio directo, reclamos o condena.
   - sarcasmo_burla: porcentaje de comentarios con mofa, memes destructivos o ironía despectiva.
   - indiferencia_neutro: porcentaje de comentarios informales, dudas prácticas o нейтраles.
3. Calcula un "crisis_score" de 0 a 100:
   - 0 a 25: SEGURO (Comunidad sana, feedback positivo).
   - 26 a 50: ALERTA MODERADA (Debates aislados o desacuerdos normales).
   - 51 a 75: ALERTA ALTA (Tensión creciente, riesgo serio de escalada).
   - 76 a 100: CRISIS CRÍTICA / FUNA ACTIVA (Rechazo masivo, llamados a boicot, daño de marca).
4. Identifica cuál de los videos es el epicentro de la mayor tensión (si aplica).
5. Diseña un Plan Táctico de Contención de Daños con un borrador de disculpa o respuesta estratégica si fuera necesario.

Responde ÚNICAMENTE con un JSON válido con la siguiente estructura (sin formato Markdown adicional):
{{
  "crisis_score": 18,
  "alert_level": "SEGURO",
  "status_summary": "Diagnóstico conciso del clima reputacional del creador (máximo 2 párrafos).",
  "reaction_breakdown": {{
    "apoyo_admiracion": 70,
    "critica_hostilidad": 5,
    "sarcasmo_burla": 10,
    "indiferencia_neutro": 15
  }},
  "boycott_threat": false,
  "boycott_details": "Detalle sobre si hay amenazas a patrocinadores o llamados a boicot, o 'Ninguno detectado'.",
  "epicenter_video": {{
    "has_epicenter": false,
    "video_index": 1,
    "video_url": "url_del_video_detonante",
    "trigger_reason": "Motivo por el cual este video generó fricción o 'N/A'.",
    "sample_toxic_comments": [
      "comentario representativo 1",
      "comentario representativo 2"
    ]
  }},
  "containment_playbook": {{
    "should_delete_video": false,
    "should_disable_comments": false,
    "should_issue_statement": false,
    "recommended_action": "Monitoreo Preventivo / Mantener la calma / Aclaración en comentarios / Comunicado oficial",
    "pr_statement_draft": "Borrador de disculpa o declaración inteligente en primera persona adaptada al tono de TikTok si amerita disculpa, o 'No se requiere declaración pública'.",
    "do_tips": [
      "Consejo 1 de qué SÍ hacer",
      "Consejo 2 de qué SÍ hacer"
    ],
    "dont_tips": [
      "Consejo 1 de qué NUNCA hacer (ej: no pelear con seguidores)",
      "Consejo 2 de qué NUNCA hacer"
    ]
  }}
}}
"""

        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
        }

        last_error = None
        for model_name in self.models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
            try:
                resp = requests.post(url, headers=headers, json=body, timeout=60)
                if resp.status_code == 200:
                    res_json = resp.json()
                    raw_text = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

                    clean_text = raw_text.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.startswith("```"):
                        clean_text = clean_text[3:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]

                    parsed = json.loads(clean_text.strip())

                    # Normalizar los porcentajes para que sumen estrictamente 100%
                    breakdown = parsed.get("reaction_breakdown", {})
                    b_keys = ["apoyo_admiracion", "critica_hostilidad", "sarcasmo_burla", "indiferencia_neutro"]
                    raw_vals = {k: float(breakdown.get(k, 25)) for k in b_keys}
                    total_b = sum(raw_vals.values()) or 100.0

                    accum = 0
                    for i, k in enumerate(b_keys):
                        if i == len(b_keys) - 1:
                            val_norm = 100 - accum
                        else:
                            val_norm = round((raw_vals[k] / total_b) * 100)
                            accum += val_norm
                        breakdown[k] = max(0, val_norm)

                    # Determinar color de badge
                    score = int(parsed.get("crisis_score", 15))
                    if score <= 25:
                        badge_color = "#16a34a"  # Verde
                        level_label = "SEGURO"
                    elif score <= 50:
                        badge_color = "#ca8a04"  # Amarillo/Dorado
                        level_label = "ALERTA MODERADA"
                    elif score <= 75:
                        badge_color = "#ea580c"  # Naranja
                        level_label = "ALERTA ALTA"
                    else:
                        badge_color = "#dc2626"  # Rojo
                        level_label = "CRISIS CRÍTICA / FUNA"

                    parsed["crisis_score"] = score
                    parsed["alert_level"] = level_label
                    parsed["badge_color"] = badge_color
                    parsed["scanned_comments_count"] = total_comments_scanned
                    parsed["scanned_videos_count"] = len(videos[:10])
                    parsed["status"] = "success"
                    parsed["model_used"] = model_name
                    return parsed
                else:
                    last_error = f"HTTP {resp.status_code} ({model_name}): {resp.text}"
            except Exception as e:
                last_error = str(e)
                continue

        logger.error(f"Error consultando Gemini API para Radar de Crisis: {last_error}")
        return {
            "status": "api_error",
            "error": last_error
        }


def print_crisis_report(crisis_res: Dict[str, Any], username: str):
    """
    Imprime un informe visual de control de crisis en la consola.
    """
    print("\n" + "=" * 70)
    print(f"      🚨 RADAR DE CANCELACIÓN & GESTIÓN DE CRISIS: @{username}")
    print("=" * 70)

    if crisis_res.get("status") != "success":
        print(f" ⚠️ No se pudo completar el análisis de crisis: {crisis_res.get('message') or crisis_res.get('error')}")
        print("=" * 70 + "\n")
        return

    score = crisis_res.get("crisis_score", 0)
    level = crisis_res.get("alert_level", "N/A")
    total_comments = crisis_res.get("scanned_comments_count", 0)
    total_videos = crisis_res.get("scanned_videos_count", 0)

    # Termómetro visual
    meter_bars = score // 4
    meter = "█" * meter_bars + "░" * (25 - meter_bars)

    print(f"\n 📊 ÍNDICE DE RIESGO DE CANCELACIÓN: [{meter}] {score}/100")
    print(f" 🚦 ESTADO DEL RADAR:               {level}")
    print(f" 🔍 TELEMETRÍA ANALIZADA:           {total_comments} comentarios en los últimos {total_videos} videos")
    print(f" 🚫 AMENAZA DE BOICOT:              {'⚠️ DETECTADA' if crisis_res.get('boycott_threat') else '✅ Ninguna Detectada'}")

    print("\n" + "─" * 70)
    print(" 🌡️ DESGLOSE DE REACCIÓN COMUNITARIA (100%):")
    print("─" * 70)
    rb = crisis_res.get("reaction_breakdown", {})
    print(f" • 🤝 Apoyo y Admiración:      {rb.get('apoyo_admiracion', 0):2d}%  ({'█' * (rb.get('apoyo_admiracion', 0)//4)})")
    print(f" • 😡 Crítica y Hostilidad:    {rb.get('critica_hostilidad', 0):2d}%  ({'█' * (rb.get('critica_hostilidad', 0)//4)})")
    print(f" • 🎭 Sarcasmo y Burla:        {rb.get('sarcasmo_burla', 0):2d}%  ({'█' * (rb.get('sarcasmo_burla', 0)//4)})")
    print(f" • 😐 Indiferencia / Neutro:   {rb.get('indiferencia_neutro', 0):2d}%  ({'█' * (rb.get('indiferencia_neutro', 0)//4)})")

    print("\n" + "─" * 70)
    print(" 📝 DIAGNÓSTICO REPUTACIONAL:")
    print("─" * 70)
    print(f" {crisis_res.get('status_summary', 'Sin resumen disponible.').replace(chr(10), ' ')}")

    epicenter = crisis_res.get("epicenter_video", {})
    if epicenter.get("has_epicenter"):
        print("\n" + "─" * 70)
        print(" 🎯 EPICENTRO DE LA FRICCIÓN (Video Detonante):")
        print("─" * 70)
        print(f" • Video #{epicenter.get('video_index', 1)}: {epicenter.get('video_url', 'N/A')}")
        print(f" • Motivo: {epicenter.get('trigger_reason', 'N/A')}")
        toxics = epicenter.get("sample_toxic_comments", [])
        if toxics:
            print(" • Comentarios Tóxicos Señalados:")
            for t in toxics:
                print(f"    - \"{t}\"")

    playbook = crisis_res.get("containment_playbook", {})
    print("\n" + "─" * 70)
    print(" 🛡️ PROTOCOLO DE CONTENCIÓN Y RELACIONES PÚBLICAS:")
    print("─" * 70)
    print(f" • Acción Estratégica:     {playbook.get('recommended_action', 'Monitoreo preventivo')}")
    print(f" • ¿Eliminar Video?:       {'🚨 SÍ (Recomendado)' if playbook.get('should_delete_video') else '❌ No es necesario'}")
    print(f" • ¿Bloquear Comentarios?: {'⚠️ SÍ (Cierre preventivo)' if playbook.get('should_disable_comments') else '❌ Mantener abiertos'}")
    print(f" • ¿Emitir Comunicado?:    {'📢 SÍ (Respuesta requerida)' if playbook.get('should_issue_statement') else '❌ No escalar'}")

    draft = playbook.get("pr_statement_draft", "")
    if draft and draft != "No se requiere declaración pública":
        print(f"\n 📜 Borrador de Respuesta / Comunicado Sugerido:\n   \"{draft}\"")

    dos = playbook.get("do_tips", [])
    if dos:
        print("\n ✅ Qué SÍ hacer:")
        for tip in dos:
            print(f"   • {tip}")

    donts = playbook.get("dont_tips", [])
    if donts:
        print("\n ❌ Qué NUNCA hacer:")
        for tip in donts:
            print(f"   • {tip}")

    print("=" * 70 + "\n")


def scan_crisis_file(target: str) -> Dict[str, Any]:
    """
    Carga un archivo o usuario y ejecuta el Radar de Crisis.
    """
    candidate_path = target
    if not os.path.exists(candidate_path):
        candidates = [
            os.path.join("scraped_data", f"tiktok_{target}.json"),
            os.path.join("scraped_data", f"{target}.json"),
            os.path.join("enriched_data", f"tiktok_{target}_enriched.json"),
            f"tiktok_{target}.json",
            f"{target}.json",
        ]
        for c in candidates:
            if os.path.exists(c):
                candidate_path = c
                break

    if not os.path.exists(candidate_path):
        raise FileNotFoundError(f"No se encontró archivo para: {target} (busca en 'scraped_data/')")

    with open(candidate_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clean_user = data.get("username", target)
    logger.info(f"Escaneando Radar de Crisis Reputacional para: @{clean_user}")

    radar = CrisisRadar()
    crisis_res = radar.analyze_profile(data)

    print_crisis_report(crisis_res, clean_user)

    # Sincronización automática directa con Figma en ejecución
    try:
        from figma_sync import send_to_figma
        payload = dict(crisis_res)
        payload["username"] = clean_user
        figma_res = send_to_figma(payload)
        if figma_res.get("status") == "success":
            logger.info(f"📡 [FigmaSync] Radar de Crisis enviado en vivo a Figma (Pin ID: {figma_res.get('comment_id')} en Dashboard)")
        elif figma_res.get("status") != "missing_credentials":
            logger.warning(f"⚠️ [FigmaSync] Aviso Figma: {figma_res.get('message') or figma_res.get('error')}")
    except Exception as figma_err:
        logger.debug(f"[FigmaSync] Error omitido: {figma_err}")

    return crisis_res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Radar de Cancelación y Gestión de Crisis para Creadores de TikTok.")
    parser.add_argument("target", help="Nombre de usuario o ruta a JSON (ejemplo: mrbeast)")
    args = parser.parse_args()
    scan_crisis_file(args.target)
