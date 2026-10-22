#!/usr/bin/env python3

import os
import sys
import json
import math
import argparse
import logging
from typing import Dict, Any, List, Optional
import requests

try:
    from scipy.stats import chisquare
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S", stream=sys.stdout)
logger = logging.getLogger("DataEnricher")


def load_env_key(key_name: str = "GEMINI_API_KEY") -> Optional[str]:
    env_val = os.getenv(key_name)
    if env_val:
        return env_val.strip()

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
    return None


BENFORD_THEORETICAL = {
    1: math.log10(1 + 1 / 1),
    2: math.log10(1 + 1 / 2),
    3: math.log10(1 + 1 / 3),
    4: math.log10(1 + 1 / 4),
    5: math.log10(1 + 1 / 5),
    6: math.log10(1 + 1 / 6),
    7: math.log10(1 + 1 / 7),
    8: math.log10(1 + 1 / 8),
    9: math.log10(1 + 1 / 9),
}


def extract_numbers_from_data(data: Dict[str, Any]) -> List[int]:
    numbers = []

    for key in ["followers_count", "following_count", "heart_count", "video_count"]:
        val = data.get(key)
        if isinstance(val, (int, float)) and val >= 10:
            numbers.append(int(val))

    for follower in data.get("followers_list", []):
        f_count = follower.get("followers_count")
        if isinstance(f_count, (int, float)) and f_count >= 10:
            numbers.append(int(f_count))
        fg_count = follower.get("following_count")
        if isinstance(fg_count, (int, float)) and fg_count >= 10:
            numbers.append(int(fg_count))

    for following in data.get("following_list", []):
        f_count = following.get("followers_count")
        if isinstance(f_count, (int, float)) and f_count >= 10:
            numbers.append(int(f_count))

    for video in data.get("videos", []):
        for v_key in ["likes_count", "comments_count", "views_count", "shares_count", "bookmarks_count"]:
            val = video.get(v_key)
            if isinstance(val, (int, float)) and val >= 10:
                numbers.append(int(val))

        for comment in video.get("comments", []):
            c_likes = comment.get("likes_count")
            if isinstance(c_likes, (int, float)) and c_likes >= 10:
                numbers.append(int(c_likes))

    return numbers


def analyze_benford(data: Dict[str, Any]) -> Dict[str, Any]:
    numbers = extract_numbers_from_data(data)
    total_samples = len(numbers)

    if total_samples < 20:
        return {
            "status": "insufficient_data",
            "sample_size": total_samples,
            "message": f"Muestra insuficiente ({total_samples} números). Se recomiendan al menos 20-30 datos."
        }

    first_digits = []
    for n in numbers:
        s = str(abs(n)).lstrip("0")
        if s and s[0].isdigit() and s[0] != "0":
            first_digits.append(int(s[0]))

    observed_counts = {d: 0 for d in range(1, 10)}
    for d in first_digits:
        observed_counts[d] += 1

    digits_data = {}
    f_obs = []
    f_exp = []

    for d in range(1, 10):
        obs_count = observed_counts[d]
        obs_pct = (obs_count / total_samples) * 100
        exp_pct = BENFORD_THEORETICAL[d] * 100
        exp_count = total_samples * BENFORD_THEORETICAL[d]

        f_obs.append(obs_count)
        f_exp.append(exp_count)

        digits_data[d] = {
            "digit": d,
            "observed_count": obs_count,
            "observed_pct": round(obs_pct, 2),
            "expected_pct": round(exp_pct, 2),
            "difference_pct": round(obs_pct - exp_pct, 2)
        }

    if HAS_SCIPY:
        chi2_stat, p_value = chisquare(f_obs, f_exp)
    else:
        chi2_stat = sum(((o - e) ** 2) / e for o, e in zip(f_obs, f_exp))
        p_value = 0.051 if chi2_stat <= 15.507 else 0.001

    conforms = bool(p_value > 0.05)
    interpretation = (
        "Las métricas de interacción siguen la distribución natural de Benford (baja sospecha de manipulación artificial masiva)."
        if conforms
        else "Se detectan desviaciones frente a la distribución teórica de Benford (patrones concentrados o volumen reducido)."
    )

    return {
        "status": "success",
        "sample_size": total_samples,
        "chi2_statistic": round(float(chi2_stat), 4),
        "p_value": round(float(p_value), 5),
        "conforms_to_benford": conforms,
        "significance_level": 0.05,
        "interpretation": interpretation,
        "digits_comparison": digits_data
    }


def analyze_big_five_gemini(data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or load_env_key("GEMINI_API_KEY")
    if not key or key == "tu_gemini_api_key_aqui":
        return {
            "status": "missing_api_key",
            "message": "Falta la clave 'GEMINI_API_KEY' en tu archivo .env. Consíguela gratis en https://aistudio.google.com/ e ingrésala en .env"
        }

    username = data.get("username", "desconocido")
    nickname = data.get("nickname", username)
    bio = data.get("bio", "Sin biografía")
    bio_link = data.get("bio_link", "Ninguno")
    followers = data.get("followers_count", 0)

    videos = data.get("videos", [])
    video_summaries = []
    sample_comments = []

    for idx, v in enumerate(videos[:10], 1):
        desc = v.get("description", "")
        dur = v.get("duration", 0)
        views = v.get("views_count", 0)
        likes = v.get("likes_count", 0)
        tags = ", ".join(v.get("hashtags", [])[:5])
        video_summaries.append(f"- Video {idx}: '{desc}' | Duración: {dur}s | Vistas: {views:,} | Likes: {likes:,} | Tags: {tags}")

        for c in v.get("comments", [])[:4]:
            t = c.get("text", "").replace("\n", " ")
            if t and len(t) > 3:
                sample_comments.append(f"@{c.get('username')}: \"{t}\"")

    prompt_payload = f"""
Eres un psicólogo computacional y analista de datos de redes sociales experto.
Analiza la huella digital del siguiente creador de TikTok a partir de sus publicaciones, temas, métricas y los comentarios reales de su comunidad.

DATOS DEL CREADOR:
- Usuario: @{username} ({nickname})
- Biografía: {bio}
- Enlace Externo: {bio_link}
- Total de Seguidores: {followers:,}

RESUMEN DE SUS VIDEOS RECIENTES:
{chr(10).join(video_summaries)}

MUESTRA DE COMENTARIOS DE SU COMUNIDAD:
{chr(10).join(sample_comments[:30])}

INSTRUCCIONES DE ANÁLISIS:
Evalúa las 5 dimensiones del modelo de personalidad Big Five (OCEAN):
1. Openness (Apertura a nuevas experiencias / Creatividad / Originalidad)
2. Conscientiousness (Responsabilidad / Organización / Enfoque al logro)
3. Extraversion (Extraversión / Sociabilidad / Energía / Dinamismo)
4. Agreeableness (Amabilidad / Altruismo / Empatía / Filantropía)
5. Neuroticism (Neuroticismo / Ansiedad / Emotividad negativa)

Responde EXCLUSIVAMENTE con un objeto JSON válido con la siguiente estructura (sin formato Markdown adicional, solo el JSON puro):
{{
  "archetype": "Nombre del Arquetipo (ej: El Filántropo Visionario, El Artista Dinámico, etc.)",
  "summary": "Resumen ejecutivo del perfil psicológico del creador (máximo 3 párrafos concisos)",
  "ocean_traits": {{
    "openness": {{
      "score": 90,
      "level": "Muy Alto",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "conscientiousness": {{
      "score": 85,
      "level": "Alto",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "extraversion": {{
      "score": 95,
      "level": "Muy Alto",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "agreeableness": {{
      "score": 80,
      "level": "Alto",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "neuroticism": {{
      "score": 15,
      "level": "Bajo",
      "analysis": "Justificación basada en el contenido analizado"
    }}
  }},
  "audience_profile": {{
    "community_sentiment": "Descripción del ánimo y reacción de los seguidores",
    "primary_emotion": "Humor / Admiración / Curiosidad / etc."
  }}
}}
"""

    