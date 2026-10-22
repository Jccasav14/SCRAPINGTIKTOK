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


