"""
design_tokens.py — Single source of truth for all PHI visual tokens.
Swap these values to change the entire app theme in one place.
"""

# ── Core palette ──────────────────────────────────────────────
PRIMARY         = "#33FF33"
PRIMARY_DIM     = "rgba(51, 255, 51, 0.75)"
PRIMARY_FAINT   = "rgba(51, 255, 51, 0.50)"
PRIMARY_GHOST   = "rgba(51, 255, 51, 0.15)"
PRIMARY_GLOW    = "rgba(51, 255, 51, 0.4)"

BG              = "#0a0d0a"
PANEL           = "#0d110d"
PANEL_2         = "#101410"
PANEL_3         = "#121612"

AMBER           = "#e0b45d"
ROSE            = "#ef6b75"
WHITE           = "#ffffff"

BORDER          = PRIMARY
BORDER_FAINT    = "rgba(51, 255, 51, 0.2)"
SHADOW          = "0 0 12px rgba(51, 255, 51, 0.25)"
SHADOW_SOFT     = "0 0 6px rgba(51, 255, 51, 0.15)"

# ── Typography ────────────────────────────────────────────────
FONT_MONO       = "'JetBrains Mono', 'IBM Plex Mono', monospace"
FONT_SIZE_SM    = 10
FONT_SIZE_MD    = 12
FONT_SIZE_LG    = 14

# ── Status colors ─────────────────────────────────────────────
STATUS_GOOD     = PRIMARY
STATUS_WARN     = AMBER
STATUS_RISK     = ROSE

# ── Plotly chart theme ────────────────────────────────────────
PLOTLY_THEME = {
    "paper_bgcolor": BG,
    "plot_bgcolor":  PANEL,
    "font": {
        "color":  PRIMARY,
        "family": FONT_MONO,
        "size":   FONT_SIZE_SM,
    },
    "xaxis": {
        "gridcolor":  "rgba(51, 255, 51, 0.08)",
        "linecolor":  BORDER_FAINT,
        "tickfont":   {"color": PRIMARY},
        "showgrid":   True,
        "zeroline":   False,
    },
    "yaxis": {
        "gridcolor":  "rgba(51, 255, 51, 0.08)",
        "linecolor":  BORDER_FAINT,
        "tickfont":   {"color": PRIMARY},
        "showgrid":   True,
        "zeroline":   False,
    },
    "legend": {
        "bgcolor":    "rgba(0,0,0,0)",
        "font":       {"color": PRIMARY},
    },
}

# ── Chart colors ──────────────────────────────────────────────
CHART_LINE      = PRIMARY
CHART_BAR_GOOD  = PRIMARY
CHART_BAR_BAD   = ROSE
CHART_TARGET    = AMBER
CHART_SECONDARY = PRIMARY_DIM
CHART_FILL      = PRIMARY_GHOST

# ── Animation timings ─────────────────────────────────────────
ANIM_FAST       = "0.2s"
ANIM_MED        = "0.6s"
ANIM_SLOW       = "1.2s"
GLOW_PULSE      = "1.6s"

# ── Layout helper ─────────────────────────────────────────────
from copy import deepcopy

def plotly_layout(**overrides) -> dict:
    """Deep-merge PLOTLY_THEME with per-chart overrides.
    Use this instead of **PLOTLY_THEME to avoid duplicate keyword arg errors.
    Usage: fig.update_layout(plotly_layout(title=..., yaxis=dict(...)))
    """
    layout = deepcopy(PLOTLY_THEME)
    for key, value in overrides.items():
        if isinstance(value, dict) and key in layout and isinstance(layout[key], dict):
            layout[key].update(value)
        else:
            layout[key] = value
    return layout
