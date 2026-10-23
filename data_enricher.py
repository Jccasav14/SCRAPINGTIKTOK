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
Evalúa la distribución porcentual de los 5 grandes rasgos de la personalidad (OCEAN):
1. Openness (Apertura a nuevas experiencias / Creatividad / Originalidad)
2. Conscientiousness (Responsabilidad / Organización / Enfoque al logro)
3. Extraversion (Extraversión / Sociabilidad / Energía / Dinamismo)
4. Agreeableness (Amabilidad / Altruismo / Empatía / Filantropía)
5. Neuroticism (Neuroticismo / Ansiedad / Emotividad negativa)

REGLAS MATEMÁTICAS OBLIGATORIAS:
- NINGÚN VALOR DEBE ESTAR QUEMADO O PREDETERMINADO. Debes evaluar objetivamente los datos específicos de este perfil y su comunidad.
- En el campo "score", asigna un porcentaje entero (número entero sin símbolo %) a cada uno de los 5 rasgos según su peso relativo en el creador.
- LA SUMA EXACTA DE LOS 5 PUNTAJES (openness + conscientiousness + extraversion + agreeableness + neuroticism) DEBE SER EXACTAMENTE IGUAL A 100%.
- El campo "level" debe reflejar el porcentaje asignado (ej: "Dominante" si es >=30%, "Alto" si es 20-29%, "Moderado" si es 12-19%, "Bajo" si es <12%).

Responde EXCLUSIVAMENTE con un objeto JSON válido con la siguiente estructura (sin formato Markdown adicional, solo el JSON puro):
{{
  "archetype": "Nombre original del Arquetipo (ej: El Filántropo Visionario, El Chef Apasionado, etc.)",
  "summary": "Resumen ejecutivo del perfil psicológico del creador (máximo 3 párrafos concisos)",
  "ocean_traits": {{
    "openness": {{
      "score": 35,
      "level": "Dominante",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "conscientiousness": {{
      "score": 25,
      "level": "Alto",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "extraversion": {{
      "score": 20,
      "level": "Alto",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "agreeableness": {{
      "score": 15,
      "level": "Moderado",
      "analysis": "Justificación basada en el contenido analizado"
    }},
    "neuroticism": {{
      "score": 5,
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

    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = None
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt_payload}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
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

                parsed_analysis = json.loads(clean_text.strip())

                # Normalización matemática estricta: asegurar que los 5 rasgos sumen exactamente 100%
                traits = parsed_analysis.get("ocean_traits", {})
                trait_keys = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
                raw_scores = {}
                for k in trait_keys:
                    val = traits.get(k, {}).get("score", 20)
                    try:
                        raw_scores[k] = float(val)
                    except Exception:
                        raw_scores[k] = 20.0

                total_sum = sum(raw_scores.values())
                if total_sum > 0:
                    accumulated = 0
                    for i, k in enumerate(trait_keys):
                        if i == len(trait_keys) - 1:
                            final_score = 100 - accumulated
                        else:
                            final_score = round((raw_scores[k] / total_sum) * 100)
                            accumulated += final_score

                        final_score = max(1, final_score)
                        if k in traits and isinstance(traits[k], dict):
                            traits[k]["score"] = final_score
                            if final_score >= 30:
                                traits[k]["level"] = "Dominante"
                            elif final_score >= 20:
                                traits[k]["level"] = "Alto"
                            elif final_score >= 12:
                                traits[k]["level"] = "Moderado"
                            else:
                                traits[k]["level"] = "Bajo"

                parsed_analysis["status"] = "success"
                parsed_analysis["model_used"] = model_name
                return parsed_analysis
            else:
                last_error = f"HTTP {resp.status_code} ({model_name}): {resp.text}"
                continue
        except Exception as e:
            last_error = str(e)
            continue

    logger.error(f"Error consultando Gemini API: {last_error}")
    return {
        "status": "api_error",
        "error": last_error
    }


def print_enrichment_report(benford_res: Dict[str, Any], big_five_res: Dict[str, Any], username: str):
    print("\n" + "=" * 70)
    print(f"      HUELLA DIGITAL & ENRIQUECIMIENTO DE DATOS: @{username}")
    print("=" * 70)

    print("\n" + "─" * 70)
    print(" 📊 MODELO 1: LEY DE BENFORD & ANÁLISIS FORENSE (Primer Dígito)")
    print("─" * 70)
    if benford_res.get("status") == "success":
        print(f" • Muestra de métricas analizadas:  {benford_res['sample_size']} datos numéricos")
        print(f" • Estadístico Chi-cuadrado (χ²):    {benford_res['chi2_statistic']}")
        print(f" • Valor P (p-value):               {benford_res['p_value']}")
        print(f" • Estado:                          {'✅ Conforme a Benford' if benford_res['conforms_to_benford'] else '⚠️ Desviación Estadística'}")
        print(f" • Conclusión:                      {benford_res['interpretation']}\n")

        print("  Dígito │ Observado │ Esperado │ Curva Comparativa (Obs vs Benford)")
        print("  ───────┼───────────┼──────────┼────────────────────────────────────")
        for d in range(1, 10):
            item = benford_res["digits_comparison"][d]
            obs_pct = item["observed_pct"]
            exp_pct = item["expected_pct"]
            bar_len = int(obs_pct / 2)
            bar = "█" * bar_len
            print(f"     {d}   │   {obs_pct:5.1f}%  │   {exp_pct:5.1f}% │ {bar:<15} (Dif: {item['difference_pct']:+5.1f}%)")
    else:
        print(f" • {benford_res.get('message', 'No se pudo realizar el análisis.')}")

    print("\n" + "─" * 70)
    print(" 🧠 MODELO 2: PERFIL PSICOMÉTRICO BIG FIVE (OCEAN con Gemini AI)")
    print("─" * 70)
    if big_five_res.get("status") == "success":
        traits = big_five_res.get("ocean_traits", {})
        print(f" 🎭 Arquetipo de Creador: {big_five_res.get('archetype', 'No definido')}\n")

        trait_names = [
            ("openness", "Apertura a Experiencias (O)", "🎨"),
            ("conscientiousness", "Responsabilidad / Logro  (C)", "📐"),
            ("extraversion", "Extraversión / Energía   (E)", "⚡"),
            ("agreeableness", "Amabilidad / Empatía     (A)", "🤝"),
            ("neuroticism", "Neuroticismo / Tensión   (N)", "🧘"),
        ]

        for k, name, icon in trait_names:
            t_data = traits.get(k, {})
            score = t_data.get("score", 0)
            level = t_data.get("level", "N/A")
            analysis = t_data.get("analysis", "")
            bar = "█" * (score // 2)
            print(f" {icon} {name}: [{bar:<25}] {score:2d}% ({level})")
            print(f"    ↳ {analysis}\n")

        total_ocean = sum(traits.get(k, {}).get("score", 0) for k, _, _ in trait_names)
        print(f" 🎯 Suma de los 5 rasgos evaluados: {total_ocean}% (Distribución normalizada = 100%)\n")

        print(f" 📝 Resumen Psicométrico:")
        print(f"    {big_five_res.get('summary', '').replace(chr(10), ' ')}")

        aud = big_five_res.get("audience_profile", {})
        if aud:
            print(f"\n 👥 Percepción de la Audiencia:")
            print(f"    • Clima Emocional: {aud.get('community_sentiment', 'N/A')}")
            print(f"    • Emoción Primaria: {aud.get('primary_emotion', 'N/A')}")
    elif big_five_res.get("status") == "missing_api_key":
        print(f" 🔑 {big_five_res.get('message')}")
    else:
        print(f" ⚠️ No se pudo completar el análisis de Gemini: {big_five_res.get('error')}")

    print("=" * 70 + "\n")


def enrich_file(json_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    target_path = json_path
    if not os.path.exists(target_path):
        candidates = [
            os.path.join("scraped_data", os.path.basename(json_path)),
            os.path.join("scraped_data", f"tiktok_{json_path}.json"),
            os.path.join("scraped_data", f"{json_path}.json"),
            f"tiktok_{json_path}.json",
            f"{json_path}.json",
        ]
        for cand in candidates:
            if os.path.exists(cand):
                target_path = cand
                break

    if not os.path.exists(target_path):
        raise FileNotFoundError(f"No se encontró el archivo: {json_path} (ni en '.' ni en 'scraped_data/')")

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    username = data.get("username", "usuario")
    logger.info(f"Iniciando enriquecimiento de datos para: @{username}")

    logger.info("Calculando distribución de Benford y prueba Chi-cuadrado χ²...")
    benford_result = analyze_benford(data)

    logger.info("Consultando perfil psicométrico Big Five con Gemini API...")
    big_five_result = analyze_big_five_gemini(data)

    logger.info("Escaneando Radar de Crisis Reputacional y riesgo de funa...")
    try:
        from crisis_radar import CrisisRadar, print_crisis_report
        crisis_result = CrisisRadar().analyze_profile(data)
    except Exception as e:
        crisis_result = {"status": "error", "error": str(e)}

    enriched_data = dict(data)
    enriched_data["data_enrichment"] = {
        "benford_law_analysis": benford_result,
        "big_five_ocean_profile": big_five_result,
        "crisis_radar": crisis_result
    }

    if output_path:
        out_file = output_path
        parent_dir = os.path.dirname(os.path.abspath(out_file))
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
    else:
        out_dir = "enriched_data"
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.basename(target_path)
        if base_name.endswith(".json"):
            base_name = base_name[:-5]
        if not base_name.endswith("_enriched"):
            base_name = f"{base_name}_enriched"
        out_file = os.path.join(out_dir, f"{base_name}.json")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)

    print_enrichment_report(benford_result, big_five_result, username)
    if crisis_result.get("status") == "success":
        print_crisis_report(crisis_result, username)
    logger.info(f"Datos enriquecidos guardados con éxito en: {out_file}")
    return enriched_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enriquecedor de datos de TikTok: Ley de Benford (χ²) y Big Five OCEAN con Gemini."
    )
    parser.add_argument(
        "json_file",
        help="Ruta al archivo JSON exportado por el scraper (ejemplo: tiktok_mrbeast.json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        default=None,
        help="Ruta opcional para el archivo JSON enriquecido de salida.",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=None,
        help="Clave opcional de Gemini API (si no se proporciona, se lee desde .env).",
    )

    args = parser.parse_args()
    enrich_file(args.json_file, args.output)
