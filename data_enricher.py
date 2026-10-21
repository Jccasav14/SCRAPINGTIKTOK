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


