#!/usr/bin/env python3
"""
Módulo de Sincronización Automática con Figma (FigmaSync)
Envía en vivo los datos de telemetría, Ley de Benford, Big Five y Radar de Crisis
directamente al archivo y marco de Figma mediante su API oficial.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("FigmaSync")


def load_env_figma() -> tuple[Optional[str], Optional[str]]:
    token = None
    file_key = None

    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.getcwd(), ".env")
    ]

    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("FIGMA_ACCESS_TOKEN="):
                            token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        elif line.startswith("FIGMA_FILE_KEY="):
                            file_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass

    token = token or os.getenv("FIGMA_ACCESS_TOKEN")
    file_key = file_key or os.getenv("FIGMA_FILE_KEY")
    return token, file_key


def format_figma_telemetry_message(data: Dict[str, Any]) -> str:
    username = data.get("username", "usuario")
    nickname = data.get("nickname", username)
    followers = data.get("followers_count", 0)
    hearts = data.get("heart_count", 0)
    videos_cnt = data.get("video_count", len(data.get("videos", [])))

    enrichment = data.get("data_enrichment", {})
    benford = enrichment.get("benford_law_analysis", {})
    big_five = enrichment.get("big_five_ocean_profile", {})
    crisis = enrichment.get("crisis_radar", {})

    # Si los datos vienen directo de crisis_radar.py
    if not crisis and "crisis_score" in data:
        crisis = data

    lines = [
        f"🚨 CRISISRADAR AI: TELEMETRÍA EN VIVO (@{username})",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]

    # Sección de Crisis si está presente
    if crisis and crisis.get("status") == "success":
        risk_score = crisis.get("crisis_score", 0)
        alert_lvl = crisis.get("alert_level", "SEGURO")
        rb = crisis.get("reaction_breakdown", {})
        apoyo = rb.get("apoyo_admiracion", 0)
        critica = rb.get("critica_hostilidad", 0)
        sarcasmo = rb.get("sarcasmo_burla", 0)
        neutro = rb.get("indiferencia_neutro", 0)

        playbook = crisis.get("containment_playbook", {})
        del_vid = "NO BORRAR" if not playbook.get("should_delete_video") else "BORRAR INMEDIATO"
        dis_com = "ABIERTOS" if not playbook.get("should_disable_comments") else "BLOQUEAR"
        stmt = "NO ESCALAR" if not playbook.get("should_issue_statement") else "EMITIR COMUNICADO"
        draft = playbook.get("pr_statement_draft", "No se requiere declaración pública.")

        lines.extend([
            f"📊 ÍNDICE DE RIESGO: {risk_score}/100 ({alert_lvl})",
            f"🤝 REACCIÓN: {apoyo}% Apoyo | {critica}% Hostil | {sarcasmo}% Memes | {neutro}% Neutro",
            f"🚫 BOICOT: {'⚠️ DETECTADO' if crisis.get('boycott_threat') else '✅ Ninguno detectado'}",
            "",
            "🛡️ PROTOCOLO DE RELACIONES PÚBLICAS:",
            f"  • ¿Eliminar Video?: {del_vid}",
            f"  • ¿Cerrar Comentarios?: {dis_com}",
            f"  • ¿Emitir Comunicado?: {stmt}",
            f'  • Borrador: "{draft[:95]}..."'
        ])

    # Sección Forense y Psicometría si está presente
    if benford and benford.get("total_values_analyzed", 0) > 0:
        b_status = "Orgánico" if benford.get("conforms_to_benford") else "Anomalía / Raids"
        chi2 = benford.get("chi2_statistic", "N/A")
        lines.append("")
        lines.append(f"🔬 FORENSE BENFORD: Tráfico {b_status} (χ²: {chi2})")

    if big_five and big_five.get("status") == "success":
        archetype = big_five.get("archetype", "Creador Digital")
        traits = big_five.get("ocean_traits", {})
        o_score = traits.get("openness", {}).get("score", "-")
        n_score = traits.get("neuroticism", {}).get("score", "-")
        lines.append(f"🧠 ARQUETIPO: {archetype} (Apertura: {o_score}%, Neuroticismo: {n_score}%)")

    # Si es solo perfil básico sin enriquecimiento
    if not crisis and not benford:
        lines.extend([
            f"👤 Creador: {nickname} (@{username})",
            f"👥 Seguidores: {followers:,} | Me Gusta: {hearts:,}",
            f"🎬 Total Videos: {videos_cnt:,}",
            "ℹ️ Ejecuta '--enrich' para activar Benford, Big Five y Radar de Crisis."
        ])

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "(Sincronizado automáticamente en vivo desde ejecución de Python)"
    ])

    return "\n".join(lines)


def send_to_figma(data: Dict[str, Any], token: Optional[str] = None, file_key: Optional[str] = None, node_id: str = "1:2706") -> Dict[str, Any]:
    env_token, env_file_key = load_env_figma()
    final_token = token or env_token
    final_key = file_key or env_file_key

    # Guardar siempre la telemetría en disco para consumo de Figma / Claude / MCP
    try:
        from datetime import datetime
        payload_local = {
            "timestamp": datetime.now().isoformat(),
            "target_node": node_id,
            "target_file_key": final_key,
            "data": data
        }
        with open("latest_figma_telemetry.json", "w", encoding="utf-8") as f:
            json.dump(payload_local, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    if not final_token or not final_key:
        return {
            "status": "missing_credentials",
            "message": "Falta FIGMA_ACCESS_TOKEN o FIGMA_FILE_KEY en el archivo .env"
        }

    headers = {
        "X-Figma-Token": final_token,
        "Content-Type": "application/json"
    }

    msg = format_figma_telemetry_message(data)

    payload = {
        "message": msg,
        "client_meta": {
            "node_id": node_id,
            "node_offset": {"x": 20, "y": 20}
        }
    }

    url = f"https://api.figma.com/v1/files/{final_key}/comments"
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            res_data = resp.json()
            return {
                "status": "success",
                "comment_id": res_data.get("id"),
                "file_key": final_key,
                "node_id": node_id,
                "message": "Telemetría sincronizada con éxito en Figma."
            }
        else:
            return {
                "status": "error",
                "code": resp.status_code,
                "error": resp.text
            }
    except Exception as e:
        return {
            "status": "exception",
            "error": str(e)
        }


def sync_user_to_figma(username_or_file: str):
    target = username_or_file
    if not os.path.exists(target):
        candidates = [
            os.path.join("enriched_data", f"tiktok_{target}_enriched.json"),
            os.path.join("scraped_data", f"tiktok_{target}.json"),
            f"tiktok_{target}.json",
            target
        ]
        for c in candidates:
            if os.path.exists(c):
                target = c
                break

    if not os.path.exists(target):
        print(f"❌ No se encontró archivo para: {username_or_file}")
        return

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)

    user = data.get("username", username_or_file)
    print(f"\n📡 Sincronizando datos de @{user} con tu archivo de Figma...")
    res = send_to_figma(data)
    if res.get("status") == "success":
        print(f"✅ ¡Éxito! Datos inyectados en Figma (ID de evento: {res.get('comment_id')})")
        print(f"👉 Abre tu Figma y verás el pin de datos actualizado en tu pantalla.")
    else:
        print(f"⚠️ Error al sincronizar con Figma: {res.get('message') or res.get('error')}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "mrbeast"
    sync_user_to_figma(target)
