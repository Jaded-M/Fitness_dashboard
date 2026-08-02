# ============================================================
# PHI chart theme
# ============================================================
import copy

from design_tokens import *

PHI_COLORS = {
    "blue": PRIMARY,
    "green": PRIMARY_GLOW,
    "amber": AMBER,
    "rose": ROSE,
    "violet": PRIMARY_FAINT,
    "olive": CHART_SECONDARY,
    "orange": STATUS_WARN,
    "muted": PRIMARY_DIM,
    "ink": PRIMARY,
    "grid": BORDER_FAINT,
}

CHART_CONFIG = {
    'displayModeBar': False,
    'displaylogo': False,
    'responsive': True,
    'scrollZoom': False,
}

CHART_LAYOUT = dict(
    font=dict(family=FONT_MONO, color=PHI_COLORS["muted"], size=12),
    margin=dict(l=20, r=20, t=44, b=34),
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showline=False, 
        tickcolor=PRIMARY_GHOST,
        title_font=dict(size=12, color=PHI_COLORS["muted"]),
        tickfont=dict(size=11, color=PHI_COLORS["muted"])
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor=PHI_COLORS["grid"], 
        zeroline=False, 
        showline=False, 
        tickcolor=PRIMARY_GHOST,
        title_font=dict(size=12, color=PHI_COLORS["muted"]),
        tickfont=dict(size=11, color=PHI_COLORS["muted"])
    ),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor=PANEL,
        bordercolor=PRIMARY_FAINT,
        font_size=13, 
        font_family=FONT_MONO,
        font_color=PHI_COLORS["ink"]
    ),
    colorway=[
        PHI_COLORS["blue"],
        PHI_COLORS["green"],
        PHI_COLORS["amber"],
        PHI_COLORS["orange"],
        PHI_COLORS["violet"],
        PHI_COLORS["rose"],
        PHI_COLORS["olive"],
    ],
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor=PANEL,
        bordercolor=PRIMARY_GHOST,
        font=dict(size=11, color=PHI_COLORS["muted"])
    )
)

BASE_LAYOUT = CHART_LAYOUT # For compatibility

def chart_layout(**overrides):
    """Helper to generate a layout with overrides, for compatibility."""
    layout = copy.deepcopy(CHART_LAYOUT)
    for k, v in overrides.items():
        if isinstance(v, dict) and k in layout and isinstance(layout[k], dict):
            layout[k].update(v)
        else:
            layout[k] = v
    return layout

CYAN = PHI_COLORS["blue"]
PURPLE = PHI_COLORS["violet"]
PINK = PHI_COLORS["rose"]
SURFACE = PANEL
RED = PHI_COLORS["rose"]
