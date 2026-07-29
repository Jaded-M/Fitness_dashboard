# ============================================================
# PHI chart theme
# ============================================================
import copy

PHI_COLORS = {
    "blue": "#32d8ff",
    "green": "#40f2a0",
    "amber": "#ffd166",
    "rose": "#ff5c8a",
    "violet": "#b56cff",
    "olive": "#78d86f",
    "orange": "#ff8a3d",
    "muted": "#9aa7b8",
    "ink": "#f6fbff",
    "grid": "rgba(50, 216, 255, 0.12)",
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
    font=dict(family='Inter, Space Grotesk, sans-serif', color=PHI_COLORS["muted"], size=12),
    margin=dict(l=20, r=20, t=44, b=34),
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showline=False, 
        tickcolor='rgba(50, 216, 255, 0.18)',
        title_font=dict(size=12, color=PHI_COLORS["muted"]),
        tickfont=dict(size=11, color=PHI_COLORS["muted"])
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor=PHI_COLORS["grid"], 
        zeroline=False, 
        showline=False, 
        tickcolor='rgba(50, 216, 255, 0.18)',
        title_font=dict(size=12, color=PHI_COLORS["muted"]),
        tickfont=dict(size=11, color=PHI_COLORS["muted"])
    ),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='rgba(12, 18, 31, 0.96)',
        bordercolor='rgba(50,216,255,0.28)',
        font_size=13, 
        font_family='Inter, Space Grotesk, sans-serif',
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
        bgcolor="rgba(12,18,31,0.72)",
        bordercolor="rgba(50,216,255,0.16)",
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
