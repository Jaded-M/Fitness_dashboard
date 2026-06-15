# ============================================================
# PHI chart theme
# ============================================================
import copy

PHI_COLORS = {
    "blue": "#197f96",
    "green": "#2f9f68",
    "amber": "#c98a18",
    "rose": "#d95f5f",
    "violet": "#7469c9",
    "olive": "#6f8f3f",
    "orange": "#cf7240",
    "muted": "#68766f",
    "ink": "#17201c",
    "grid": "rgba(35, 49, 43, 0.12)",
}

CHART_CONFIG = {
    'displayModeBar': False,
    'displaylogo': False,
    'responsive': True,
    'scrollZoom': False,
}

CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Plus Jakarta Sans, Inter, sans-serif', color=PHI_COLORS["muted"], size=12),
    margin=dict(l=22, r=22, t=48, b=38),
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showline=False, 
        tickcolor='rgba(35, 49, 43, 0.20)',
        title_font=dict(size=12, color=PHI_COLORS["muted"]),
        tickfont=dict(size=11, color=PHI_COLORS["muted"])
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor=PHI_COLORS["grid"], 
        zeroline=False, 
        showline=False, 
        tickcolor='rgba(35, 49, 43, 0.20)',
        title_font=dict(size=12, color=PHI_COLORS["muted"]),
        tickfont=dict(size=11, color=PHI_COLORS["muted"])
    ),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='#ffffff',
        bordercolor='rgba(35,49,43,0.18)',
        font_size=13, 
        font_family='Plus Jakarta Sans, Inter, sans-serif',
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
        bgcolor="rgba(255,255,255,0.82)",
        bordercolor="rgba(35,49,43,0.12)",
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
SURFACE = "#11161d"
RED = PHI_COLORS["rose"]
