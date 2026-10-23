"""
Generador de Gráficos Vectoriales (SVG) para Swagger UI y Visualización Web
Diseño Claro (Light Mode) 100% integrado con el tema blanco oficial de Swagger UI.
"""

from typing import Dict, Any


def generate_benford_svg(benford_res: Dict[str, Any], username: str) -> str:
    sample_size = benford_res.get("sample_size", 0)
    chi2 = benford_res.get("chi2_statistic", 0.0)
    p_val = benford_res.get("p_value", 0.0)
    conforms = benford_res.get("conforms_to_benford", True)
    comp = benford_res.get("digits_comparison", {})

    status_text = "CONFORME A BENFORD: Interacciones naturales y orgánicas (Baja sospecha de bots)" if conforms else "DESVIACIÓN DETECTADA: Concentración anómala o volumen reducido"
    status_bg = "#f0fdf4" if conforms else "#fffbeb"
    status_border = "#86efac" if conforms else "#fde68a"
    status_color = "#166534" if conforms else "#b45309"
    status_icon = "✅" if conforms else "⚠️"

    svg_width = 860
    svg_height = 490

    chart_x = 65
    chart_y = 105
    chart_w = 730
    chart_h = 230
    max_pct = 36.0

    bars_svg = []
    group_width = chart_w / 9
    bar_w = 26

    for i in range(1, 10):
        item = comp.get(i, comp.get(str(i), {}))
        obs = float(item.get("observed_pct", 0.0))
        exp = float(item.get("expected_pct", 0.0))

        gx = chart_x + (i - 1) * group_width + (group_width - (bar_w * 2 + 4)) / 2

        obs_h = max(2.0, (obs / max_pct) * chart_h)
        exp_h = max(2.0, (exp / max_pct) * chart_h)

        obs_y = chart_y + chart_h - obs_h
        exp_y = chart_y + chart_h - exp_h

        # Barra Observado (Azul Swagger / Celeste)
        bars_svg.append(f'<rect x="{gx:.1f}" y="{obs_y:.1f}" width="{bar_w}" height="{obs_h:.1f}" fill="#0284c7" rx="3"/>')
        bars_svg.append(f'<text x="{gx + bar_w/2:.1f}" y="{obs_y - 6:.1f}" fill="#0369a1" font-size="11" font-weight="bold" text-anchor="middle">{obs:.1f}%</text>')

        # Barra Esperado Benford (Rojo / Frambuesa)
        bars_svg.append(f'<rect x="{gx + bar_w + 4:.1f}" y="{exp_y:.1f}" width="{bar_w}" height="{exp_h:.1f}" fill="#e11d48" rx="3"/>')
        bars_svg.append(f'<text x="{gx + bar_w + 4 + bar_w/2:.1f}" y="{exp_y - 6:.1f}" fill="#be123c" font-size="11" font-weight="bold" text-anchor="middle">{exp:.1f}%</text>')

        # Etiqueta del dígito
        bars_svg.append(f'<text x="{gx + bar_w + 2:.1f}" y="{chart_y + chart_h + 22}" fill="#334155" font-size="13" font-weight="bold" text-anchor="middle">Dígito {i}</text>')

    grid_svg = []
    for pct in [10, 20, 30]:
        gy = chart_y + chart_h - (pct / max_pct) * chart_h
        grid_svg.append(f'<line x1="{chart_x}" y1="{gy:.1f}" x2="{chart_x + chart_w}" y2="{gy:.1f}" stroke="#e2e8f0" stroke-dasharray="4"/>')
        grid_svg.append(f'<text x="{chart_x - 12}" y="{gy + 4:.1f}" fill="#64748b" font-size="11" text-anchor="end">{pct}%</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%" style="background:#ffffff; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; border-radius:8px; border:1px solid #e2e8f0;">
  <!-- Título y subtítulo -->
  <text x="32" y="42" fill="#0f172a" font-size="19" font-weight="bold">📊 Ley de Benford: Comparativa de Barras Forenses</text>
  <text x="32" y="68" fill="#64748b" font-size="13">Perfil auditado: <tspan fill="#0284c7" font-weight="bold">@{username}</tspan> | Muestra: <tspan fill="#0f172a" font-weight="600">{sample_size} números</tspan> | χ² = <tspan fill="#0f172a" font-weight="600">{chi2}</tspan> | p-valor = <tspan fill="#0f172a" font-weight="600">{p_val}</tspan></text>

  <!-- Leyenda -->
  <rect x="520" y="28" width="14" height="14" fill="#0284c7" rx="3"/>
  <text x="542" y="40" fill="#334155" font-size="12" font-weight="500">Observado en TikTok (%)</text>
  <rect x="690" y="28" width="14" height="14" fill="#e11d48" rx="3"/>
  <text x="712" y="40" fill="#334155" font-size="12" font-weight="500">Ley Teórica Benford (%)</text>

  <!-- Líneas de cuadrícula -->
  {''.join(grid_svg)}

  <!-- Línea base horizontal -->
  <line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x + chart_w}" y2="{chart_y + chart_h}" stroke="#cbd5e1" stroke-width="1.5"/>

  <!-- Barras -->
  {''.join(bars_svg)}

  <!-- Caja de Conclusión Inferior -->
  <rect x="{chart_x}" y="{chart_y + chart_h + 46}" width="{chart_w}" height="54" fill="{status_bg}" stroke="{status_border}" rx="8"/>
  <text x="{chart_x + 20}" y="{chart_y + chart_h + 79}" fill="{status_color}" font-size="13.5" font-weight="bold">{status_icon} {status_text}</text>
</svg>"""


def generate_big_five_svg(big_five_res: Dict[str, Any], username: str) -> str:
    archetype = big_five_res.get("archetype", "Perfil Creativo Multifacético")
    traits = big_five_res.get("ocean_traits", {})
    audience = big_five_res.get("audience_profile", {})
    sentiment = audience.get("community_sentiment", "Sentimiento positivo y entusiasta de la audiencia.")
    primary_emotion = audience.get("primary_emotion", "Admiración / Curiosidad")

    svg_width = 860
    svg_height = 550

    traits_config = [
        ("openness", "Apertura a Experiencias (O)", "🎨", "#0284c7"),
        ("conscientiousness", "Responsabilidad y Logro (C)", "📐", "#16a34a"),
        ("extraversion", "Extraversión y Energía (E)", "⚡", "#d97706"),
        ("agreeableness", "Amabilidad y Altruismo (A)", "🤝", "#7c3aed"),
        ("neuroticism", "Neuroticismo / Tensión (N)", "🧘", "#dc2626"),
    ]

    bars_svg = []
    start_y = 110
    bar_max_w = 480

    for idx, (k, name, icon, color) in enumerate(traits_config):
        t_data = traits.get(k, {})
        score = int(t_data.get("score", 50))
        level = t_data.get("level", "N/A")
        analysis = t_data.get("analysis", "")[:75]
        if len(t_data.get("analysis", "")) > 75:
            analysis += "..."

        y = start_y + idx * 62
        fill_w = max(10, int((score / 100) * bar_max_w))

        bars_svg.append(f"""
        <!-- Trait {k} -->
        <text x="36" y="{y + 16}" fill="#0f172a" font-size="13" font-weight="bold">{icon} {name}</text>
        <text x="36" y="{y + 34}" fill="#64748b" font-size="11">{analysis}</text>

        <!-- Bar background -->
        <rect x="290" y="{y + 4}" width="{bar_max_w}" height="18" fill="#f1f5f9" rx="9"/>
        <!-- Bar fill -->
        <rect x="290" y="{y + 4}" width="{fill_w}" height="18" fill="{color}" rx="9"/>
        <!-- Score text -->
        <text x="{290 + bar_max_w + 14}" y="{y + 18}" fill="#0f172a" font-size="13" font-weight="bold">{score}% <tspan fill="#64748b" font-size="11">({level})</tspan></text>
        """)

    if len(sentiment) > 130:
        sentiment = sentiment[:127] + "..."

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%" style="background:#ffffff; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; border-radius:8px; border:1px solid #e2e8f0;">
  <!-- Título -->
  <text x="32" y="40" fill="#0f172a" font-size="19" font-weight="bold">🧠 Distribución Psicométrica Big Five (OCEAN: 100%) & Emociones</text>
  <text x="32" y="65" fill="#64748b" font-size="13">Perfil auditado: <tspan fill="#0284c7" font-weight="bold">@{username}</tspan> | Distribución de peso entre los 5 rasgos (Suma total = 100%) | Evaluado con: <tspan fill="#0f172a" font-weight="600">Google Gemini AI</tspan></text>

  <!-- Banner Arquetipo -->
  <rect x="32" y="80" width="796" height="34" fill="#faf5ff" stroke="#e9d5ff" rx="6"/>
  <text x="48" y="102" fill="#7c3aed" font-size="13" font-weight="bold">🎭 Arquetipo: <tspan fill="#581c87">{archetype}</tspan></text>

  <!-- Barras OCEAN -->
  {''.join(bars_svg)}

  <!-- Caja de Audiencia y Emociones -->
  <rect x="32" y="435" width="796" height="90" fill="#f8fafc" stroke="#e2e8f0" rx="8"/>
  <text x="50" y="462" fill="#0f172a" font-size="14" font-weight="bold">👥 Emociones y Percepción de la Comunidad:</text>
  <text x="50" y="486" fill="#334155" font-size="12.5">• <tspan fill="#64748b">Emoción Primaria:</tspan> <tspan font-weight="bold" fill="#0284c7">{primary_emotion}</tspan></text>
  <text x="50" y="508" fill="#334155" font-size="12.5">• <tspan fill="#64748b">Clima Emocional:</tspan> {sentiment}</text>
</svg>"""


def generate_crisis_radar_svg(crisis_res: Dict[str, Any], username: str) -> str:
    score = int(crisis_res.get("crisis_score", 15))
    level = crisis_res.get("alert_level", "SEGURO")
    badge_color = crisis_res.get("badge_color", "#16a34a")
    summary = crisis_res.get("status_summary", "Ambiente comunitario estable y sin fricciones detectadas.")
    if len(summary) > 230:
        summary = summary[:227] + "..."

    rb = crisis_res.get("reaction_breakdown", {})
    apoyo = int(rb.get("apoyo_admiracion", 70))
    critica = int(rb.get("critica_hostilidad", 5))
    burla = int(rb.get("sarcasmo_burla", 10))
    neutro = int(rb.get("indiferencia_neutro", 15))

    playbook = crisis_res.get("containment_playbook", {})
    action = playbook.get("recommended_action", "Monitoreo Preventivo")
    del_vid = "SÍ (Recomendado)" if playbook.get("should_delete_video") else "No requerido"
    dis_comm = "SÍ (Preventivo)" if playbook.get("should_disable_comments") else "Abiertos"
    stmt = "SÍ (Comunicado oficial)" if playbook.get("should_issue_statement") else "No escalar"

    epicenter = crisis_res.get("epicenter_video", {})
    has_epi = epicenter.get("has_epicenter", False)
    epi_text = f"Video #{epicenter.get('video_index', 1)}: {epicenter.get('trigger_reason', 'Tensión focalizada')}" if has_epi else "Ningún video detonante de hostilidad detectado."
    if len(epi_text) > 110:
        epi_text = epi_text[:107] + "..."

    svg_width = 860
    svg_height = 540

    # Ancho del termómetro (base 796px)
    meter_w = max(16, int((score / 100) * 796))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%" style="background:#ffffff; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; border-radius:8px; border:1px solid #e2e8f0;">
  <!-- Encabezado -->
  <text x="32" y="38" fill="#0f172a" font-size="19" font-weight="bold">🚨 Radar de Cancelación & Gestión de Crisis</text>
  <text x="32" y="62" fill="#64748b" font-size="13">Perfil auditado: <tspan fill="#0284c7" font-weight="bold">@{username}</tspan> | Telemetría en tiempo real: <tspan fill="#0f172a" font-weight="600">{crisis_res.get('scanned_comments_count', 0)} comentarios</tspan> en los últimos videos</text>

  <!-- Termómetro Principal de Riesgo (0-100) -->
  <rect x="32" y="78" width="796" height="42" fill="#f8fafc" stroke="#e2e8f0" rx="8"/>
  <rect x="32" y="78" width="{meter_w}" height="42" fill="{badge_color}" rx="8"/>
  
  <text x="48" y="105" fill="#ffffff" font-size="14" font-weight="bold" style="text-shadow: 0 1px 2px rgba(0,0,0,0.4);">ÍNDICE DE RIESGO DE CRISIS: {score}/100</text>
  <rect x="670" y="85" width="148" height="28" fill="#ffffff" rx="6"/>
  <text x="744" y="104" fill="{badge_color}" font-size="12" font-weight="bold" text-anchor="middle">{level}</text>

  <!-- Diagnóstico Reputacional -->
  <rect x="32" y="132" width="796" height="68" fill="#f8fafc" stroke="#e2e8f0" rx="8"/>
  <text x="48" y="154" fill="#0f172a" font-size="12.5" font-weight="bold">📋 Diagnóstico de Temperatura Comunitaria:</text>
  <text x="48" y="176" fill="#475569" font-size="11.5">{summary}</text>

  <!-- 4 Barras de Reacción Comunitaria (100%) -->
  <text x="32" y="224" fill="#0f172a" font-size="13" font-weight="bold">🌡️ Desglose de Reacción en Comentarios (Total = 100%):</text>

  <!-- Apoyo -->
  <text x="32" y="250" fill="#334155" font-size="12">🤝 Apoyo y Admiración: <tspan font-weight="bold" fill="#16a34a">{apoyo}%</tspan></text>
  <rect x="230" y="238" width="598" height="15" fill="#f1f5f9" rx="7"/>
  <rect x="230" y="238" width="{int((apoyo/100)*598)}" height="15" fill="#16a34a" rx="7"/>

  <!-- Crítica / Hostilidad -->
  <text x="32" y="280" fill="#334155" font-size="12">😡 Crítica y Hostilidad: <tspan font-weight="bold" fill="#dc2626">{critica}%</tspan></text>
  <rect x="230" y="268" width="598" height="15" fill="#f1f5f9" rx="7"/>
  <rect x="230" y="268" width="{int((critica/100)*598)}" height="15" fill="#dc2626" rx="7"/>

  <!-- Sarcasmo / Burla -->
  <text x="32" y="310" fill="#334155" font-size="12">🎭 Sarcasmo y Memes: <tspan font-weight="bold" fill="#d97706">{burla}%</tspan></text>
  <rect x="230" y="298" width="598" height="15" fill="#f1f5f9" rx="7"/>
  <rect x="230" y="298" width="{int((burla/100)*598)}" height="15" fill="#d97706" rx="7"/>

  <!-- Neutro -->
  <text x="32" y="340" fill="#334155" font-size="12">😐 Neutro / Consultas: <tspan font-weight="bold" fill="#64748b">{neutro}%</tspan></text>
  <rect x="230" y="328" width="598" height="15" fill="#f1f5f9" rx="7"/>
  <rect x="230" y="328" width="{int((neutro/100)*598)}" height="15" fill="#64748b" rx="7"/>

  <!-- Epicentro de la Crisis -->
  <rect x="32" y="360" width="796" height="42" fill="#fff7ed" stroke="#fed7aa" rx="6"/>
  <text x="48" y="386" fill="#c2410c" font-size="12" font-weight="bold">🎯 Epicentro de Fricción: <tspan font-weight="normal" fill="#7c2d12">{epi_text}</tspan></text>

  <!-- Protocolo de Contención de Daños (Playbook) -->
  <rect x="32" y="414" width="796" height="106" fill="#f8fafc" stroke="#e2e8f0" rx="8"/>
  <text x="48" y="438" fill="#0f172a" font-size="13" font-weight="bold">🛡️ Playbook de Contención y Relaciones Públicas:</text>
  <text x="48" y="462" fill="#334155" font-size="12">• <tspan fill="#64748b">Acción Estratégica:</tspan> <tspan font-weight="bold" fill="#0284c7">{action}</tspan></text>
  <text x="48" y="484" fill="#334155" font-size="12">• <tspan fill="#64748b">¿Eliminar Video?:</tspan> <tspan font-weight="bold">{del_vid}</tspan> | <tspan fill="#64748b">¿Cerrar Comentarios?:</tspan> <tspan font-weight="bold">{dis_comm}</tspan> | <tspan fill="#64748b">¿Emitir Comunicado?:</tspan> <tspan font-weight="bold">{stmt}</tspan></text>
  <text x="48" y="504" fill="#334155" font-size="11.5">• <tspan fill="#64748b">Amenaza a Patrocinadores / Boicot:</tspan> {'⚠️ DETECTADA (Riesgo comercial)' if crisis_res.get('boycott_threat') else '✅ Ninguna detectada'}</text>
</svg>"""
