# ============================================================
# CHART THEME CONFIGURATION (SaaS Minimalist)
# ============================================================
import copy

CHART_CONFIG = {
    'displayModeBar': False,
    'responsive': True
}

CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='#888888', size=12),
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showline=False, 
        tickcolor='#222222',
        title_font=dict(size=13, color='#888888'),
        tickfont=dict(size=11, color='#666666')
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='#111111', 
        zeroline=False, 
        showline=False, 
        tickcolor='#222222',
        title_font=dict(size=13, color='#888888'),
        tickfont=dict(size=11, color='#666666')
    ),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='#0A0A0A', 
        bordercolor='#222222',
        font_size=13, 
        font_family='Inter, sans-serif',
        font_color='#FFFFFF'
    ),
    colorway=['#FFFFFF', '#888888', '#444444', '#222222'], # Minimalist monochrome colorway
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=12, color='#888888')
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

# Monochrome compatibility colors
CYAN = "#FFFFFF"
PURPLE = "#888888"
PINK = "#444444"
SURFACE = "#0A0A0A"
RED = "#FF453A" # Keep red for alerts/over-limit
