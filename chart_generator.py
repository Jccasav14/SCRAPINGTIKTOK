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
