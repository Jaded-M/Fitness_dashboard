from __future__ import annotations

from html import escape

import streamlit as st
from streamlit.components.v1 import html as render_html


STATUS_STYLE = {
    "Ready": {"fill": "#33ff33", "glow": "rgba(51,255,51,0.35)", "label": "Ready"},
    "Manage load": {"fill": "#e0b45d", "glow": "rgba(224,180,93,0.30)", "label": "Manage"},
    "Fatigued": {"fill": "#ef6b75", "glow": "rgba(239,107,117,0.30)", "label": "Fatigued"},
    "Empty": {"fill": "#1a2a1a", "glow": "rgba(51,255,51,0.06)", "label": "Empty"},
}


# ── Proven path coordinates (front center x=155, back center x=385) ──

FRONT_PATHS: list[dict] = [
    {
        "id": "chest",
        "name": "Chest",
        "muscle_key": "Chest",
        "paths": [
            "M124 128 C136 118 149 121 155 136 L155 178 L119 169 C116 151 118 139 124 128 Z",
            "M186 128 C174 118 161 121 155 136 L155 178 L191 169 C194 151 192 139 186 128 Z",
        ],
    },
    {
        "id": "core",
        "name": "Core",
        "muscle_key": "Core",
        "paths": [
            "M129 177 L155 184 L181 177 L176 251 L155 260 L134 251 Z",
        ],
    },
    {
        "id": "shoulders",
        "name": "Shoulders",
        "muscle_key": "Shoulders",
        "paths": [
            "M104 130 C111 111 132 113 139 129 C128 140 116 150 103 160 C96 151 96 140 104 130 Z",
            "M206 130 C199 111 178 113 171 129 C182 140 194 150 207 160 C214 151 214 140 206 130 Z",
        ],
    },
    {
        "id": "biceps",
        "name": "Biceps",
        "muscle_key": "Biceps",
        "paths": [
            "M93 158 C104 158 111 167 108 180 L96 225 C93 236 78 232 80 219 L88 177 C89 169 89 162 93 158 Z",
            "M217 158 C206 158 199 167 202 180 L214 225 C217 236 232 232 230 219 L222 177 C221 169 221 162 217 158 Z",
        ],
    },
    {
        "id": "forearms",
        "name": "Forearms",
        "muscle_key": "Forearms",
        "paths": [
            "M80 223 C90 225 96 234 93 245 L84 292 C81 305 65 302 67 288 L72 241 C73 231 75 225 80 223 Z",
            "M230 223 C220 225 214 234 217 245 L226 292 C229 305 245 302 243 288 L238 241 C237 231 235 225 230 223 Z",
        ],
    },
    {
        "id": "quads",
        "name": "Quads",
        "muscle_key": "Quads",
        "paths": [
            "M132 269 L153 265 L151 363 C148 382 126 381 125 361 L123 303 C123 288 126 276 132 269 Z",
            "M178 269 L157 265 L159 363 C162 382 184 381 185 361 L187 303 C187 288 184 276 178 269 Z",
        ],
    },
    {
        "id": "calves",
        "name": "Calves",
        "muscle_key": "Calves",
        "paths": [
            "M126 366 C137 372 146 372 151 365 L146 433 C145 449 124 449 123 432 Z",
            "M184 366 C173 372 164 372 159 365 L164 433 C165 449 186 449 187 432 Z",
        ],
    },
]

BACK_PATHS: list[dict] = [
    {
        "id": "back",
        "name": "Back",
        "muscle_key": "Back",
        "paths": [
            "M354 127 C365 115 405 115 416 127 L407 214 C397 230 373 230 363 214 Z",
        ],
    },
    {
        "id": "shoulders",
        "name": "Shoulders",
        "muscle_key": "Shoulders",
        "paths": [
            "M334 130 C342 112 362 113 369 129 C358 141 346 151 333 160 C326 151 326 140 334 130 Z",
            "M436 130 C428 112 408 113 401 129 C412 141 424 151 437 160 C444 151 444 140 436 130 Z",
        ],
    },
    {
        "id": "triceps",
        "name": "Triceps",
        "muscle_key": "Triceps",
        "paths": [
            "M323 158 C334 158 341 167 338 181 L326 226 C323 237 308 233 310 219 L318 177 C319 169 319 162 323 158 Z",
            "M447 158 C436 158 429 167 432 181 L444 226 C447 237 462 233 460 219 L452 177 C451 169 451 162 447 158 Z",
        ],
    },
    {
        "id": "forearms",
        "name": "Forearms",
        "muscle_key": "Forearms",
        "paths": [
            "M310 223 C320 225 326 234 323 245 L314 292 C311 305 295 302 297 288 L302 241 C303 231 305 225 310 223 Z",
            "M460 223 C450 225 444 234 447 245 L456 292 C459 305 475 302 473 288 L468 241 C467 231 465 225 460 223 Z",
        ],
    },
    {
        "id": "glutes",
        "name": "Glutes",
        "muscle_key": "Glutes",
        "paths": [
            "M363 225 C374 218 396 218 407 225 L405 270 C393 279 377 279 365 270 Z",
        ],
    },
    {
        "id": "hamstrings",
        "name": "Hamstrings",
        "muscle_key": "Hamstrings",
        "paths": [
            "M362 269 L383 265 L381 363 C378 382 356 381 355 361 L353 303 C353 288 356 276 362 269 Z",
            "M408 269 L387 265 L389 363 C392 382 414 381 415 361 L417 303 C417 288 414 276 408 269 Z",
        ],
    },
    {
        "id": "calves",
        "name": "Calves",
        "muscle_key": "Calves",
        "paths": [
            "M356 366 C367 372 376 372 381 365 L376 433 C375 449 354 449 353 432 Z",
            "M414 366 C403 372 394 372 389 365 L394 433 C395 449 416 449 417 432 Z",
        ],
    },
]


def _build_lookup(readiness_status: list[dict]) -> dict[str, dict]:
    return {str(item.get("muscle", "")).lower(): item for item in readiness_status}


def _style_for(rows: dict, *names: str) -> dict:
    row = None
    for name in names:
        row = rows.get(name.lower())
        if row:
            break
    if not row:
        row = {"muscle": names[0], "status": "Empty", "readiness": 0, "fatigue": 0, "load_7d": 0}
    status = str(row.get("status", "Empty"))
    style = STATUS_STYLE.get(status, STATUS_STYLE["Empty"])
    readiness = float(row.get("readiness", 0) or 0)
    base_opacity = 0.30 if status == "Empty" else 0.45
    var_opacity = readiness / 100 * 0.50 if status != "Empty" else 0
    opacity = base_opacity + var_opacity
    return {
        "fill": style["fill"],
        "glow": style["glow"],
        "opacity": f"{min(opacity, 0.95):.2f}",
        "label": style["label"],
        "readiness": int(readiness),
        "status": status,
    }


def _render_muscle_svg(rows: dict, group: dict) -> str:
    s = _style_for(rows, group["muscle_key"])
    cls = f"phi-muscle {group['id']}"
    title = escape(f"{group['name']}: {s['label']} ({s['readiness']}%)")
    parts = []
    for d in group["paths"]:
        parts.append(
            f'<path class="{cls}" d="{d}" '
            f'fill="{s["fill"]}" fill-opacity="{s["opacity"]}" '
            f'stroke="{s["fill"]}" stroke-opacity="0.15" stroke-width="1" '
            f'data-muscle="{group["muscle_key"]}" '
            f'data-name="{escape(group["name"])}" '
            f'data-readiness="{s["readiness"]}" '
            f'data-status="{s["status"]}">'
            f"<title>{title}</title></path>"
        )
    return "\n".join(parts)


def generate_body_svg(readiness_status: list[dict]) -> str:
    """Pure standalone SVG — embed anywhere (mobile, web, file)."""
    rows = _build_lookup(readiness_status)
    front = "\n".join(_render_muscle_svg(rows, g) for g in FRONT_PATHS)
    back = "\n".join(_render_muscle_svg(rows, g) for g in BACK_PATHS)

    ready = sum(1 for r in readiness_status if r.get("status") == "Ready")
    manage = sum(1 for r in readiness_status if r.get("status") == "Manage load")
    fatigued = sum(1 for r in readiness_status if r.get("status") == "Fatigued")

    return f"""<svg class="phi-body-svg" xmlns="http://www.w3.org/2000/svg"
 viewBox="0 0 540 500" role="img" aria-label="Muscle readiness body map"
 style="width:100%;height:auto;display:block;">
  <defs>
    <radialGradient id="bgGlow" cx="50%" cy="20%" r="75%">
      <stop offset="0%" stop-color="rgba(51,255,51,0.06)"/>
      <stop offset="50%" stop-color="rgba(51,255,51,0.02)"/>
      <stop offset="100%" stop-color="rgba(51,255,51,0)"/>
    </radialGradient>
    <filter id="neonGlow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="dotGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect x="0" y="0" width="540" height="500" fill="#000000"/>
  <rect x="16" y="16" width="508" height="468" rx="0" fill="url(#bgGlow)"
   stroke="rgba(51,255,51,0.10)" stroke-width="1"/>

  <!-- Scanlines -->
  <rect x="0" y="0" width="540" height="500" fill="url(#scanlines)" opacity="0.04"
   style="background-image:repeating-linear-gradient(0deg,transparent,transparent 1px,rgba(51,255,51,0.03) 1px,rgba(51,255,51,0.03) 2px);background-size:100% 2px"/>

  <!-- Center divider -->
  <line x1="270" y1="56" x2="270" y2="456" stroke="rgba(51,255,51,0.08)" stroke-dasharray="3 6"/>

  <!-- FRONT / BACK labels -->
  <text x="135" y="46" text-anchor="middle" fill="rgba(51,255,51,0.50)"
   font-family="'IBM Plex Mono','JetBrains Mono',monospace" font-size="10"
   font-weight="600" letter-spacing="0.15em">FRONT</text>
  <text x="405" y="46" text-anchor="middle" fill="rgba(51,255,51,0.50)"
   font-family="'IBM Plex Mono','JetBrains Mono',monospace" font-size="10"
   font-weight="600" letter-spacing="0.15em">BACK</text>

  <!-- Heads -->
  <circle cx="155" cy="82" r="22" fill="rgba(51,255,51,0.06)"
   stroke="rgba(51,255,51,0.12)" stroke-width="1.2"/>
  <circle cx="385" cy="82" r="22" fill="rgba(51,255,51,0.06)"
   stroke="rgba(51,255,51,0.12)" stroke-width="1.2"/>

  <!-- Body silhouettes -->
  <g opacity="0.06">
    <path d="M135 104 C150 104 162 110 168 124 L168 450 L135 450 Z" fill="#33ff33"/>
    <path d="M405 104 C390 104 378 110 372 124 L372 450 L405 450 Z" fill="#33ff33"/>
  </g>

  <!-- Front muscles -->
  <g class="front-group">{front}</g>

  <!-- Back muscles -->
  <g class="back-group">{back}</g>

  <!-- Labels -->
  <g font-family="'IBM Plex Mono','JetBrains Mono',monospace" font-size="8"
   fill="rgba(51,255,51,0.45)" font-weight="600" letter-spacing="0.10em">
    <circle cx="34" cy="145" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="42" y="148">Shoulders</text>
    <circle cx="34" cy="200" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="42" y="203">Biceps</text>
    <circle cx="34" cy="255" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="42" y="258">Forearms</text>
    <circle cx="34" cy="330" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="42" y="333">Quads</text>
    <circle cx="34" cy="410" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="42" y="413">Calves</text>
    <circle cx="500" cy="145" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="508" y="148" text-anchor="end">Back</text>
    <circle cx="500" cy="200" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="508" y="203" text-anchor="end">Triceps</text>
    <circle cx="500" cy="255" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="508" y="258" text-anchor="end">Forearms</text>
    <circle cx="500" cy="330" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="508" y="333" text-anchor="end">Hamstrings</text>
    <circle cx="500" cy="410" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="508" y="413" text-anchor="end">Calves</text>
    <circle cx="270" cy="145" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="278" y="148">Chest</text>
    <circle cx="270" cy="210" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="278" y="213">Core</text>
    <circle cx="270" cy="305" r="2.5" fill="#33ff33" filter="url(#dotGlow)"/>
    <text x="278" y="308">Glutes</text>
  </g>

  <!-- Legend -->
  <g font-family="'IBM Plex Mono','JetBrains Mono',monospace" font-size="7"
   fill="rgba(51,255,51,0.35)" letter-spacing="0.05em">
    <rect x="22" y="460" width="6" height="6" fill="#33ff33" opacity="0.7"/>
    <text x="32" y="465">{ready} ready</text>
    <rect x="82" y="460" width="6" height="6" fill="#e0b45d" opacity="0.7"/>
    <text x="92" y="465">{manage} manage</text>
    <rect x="158" y="460" width="6" height="6" fill="#ef6b75" opacity="0.7"/>
    <text x="168" y="465">{fatigued} fatigued</text>
  </g>
</svg>"""


def export_svg_string(readiness_status: list[dict]) -> str:
    """Return standalone SVG — save to file, use in mobile apps, etc."""
    return generate_body_svg(readiness_status)


def render_svg_body_heatmap(readiness_status: list[dict]) -> None:
    """Render interactive body heatmap in Streamlit with PHI dark theme."""
    rows = _build_lookup(readiness_status)
    svg = generate_body_svg(readiness_status)

    ready = sum(1 for r in readiness_status if r.get("status") == "Ready")
    manage = sum(1 for r in readiness_status if r.get("status") == "Manage load")
    fatigued = sum(1 for r in readiness_status if r.get("status") == "Fatigued")

    html = f"""<div id="phi-heatmap" style="
  background:#000000; border:1px solid rgba(51,255,51,0.10); padding:0;
  position:relative; overflow:hidden;
  font-family:'IBM Plex Mono','JetBrains Mono',monospace;">
  <div style="
    display:flex; align-items:center; justify-content:space-between;
    padding:12px 18px 0 18px;">
    <div>
      <div style="
        font-size:9px; color:rgba(51,255,51,0.50);
        letter-spacing:0.12em; text-transform:uppercase;
        margin-bottom:2px;">Muscle atlas</div>
      <div style="
        font-size:15px; font-weight:700; color:#33ff33;
        letter-spacing:-0.02em;">Recovery Map</div>
    </div>
    <div style="display:flex; gap:8px; align-items:center;">
      <span style="display:inline-flex;align-items:center;gap:4px;
        color:rgba(51,255,51,0.50);font-size:9px;">
        <i style="width:6px;height:6px;background:#33ff33;display:inline-block;
        box-shadow:0 0 8px rgba(51,255,51,0.5);"></i>{ready} ready</span>
      <span style="display:inline-flex;align-items:center;gap:4px;
        color:rgba(224,180,93,0.50);font-size:9px;">
        <i style="width:6px;height:6px;background:#e0b45d;display:inline-block;
        box-shadow:0 0 8px rgba(224,180,93,0.5);"></i>{manage} manage</span>
      <span style="display:inline-flex;align-items:center;gap:4px;
        color:rgba(239,107,117,0.50);font-size:9px;">
        <i style="width:6px;height:6px;background:#ef6b75;display:inline-block;
        box-shadow:0 0 8px rgba(239,107,117,0.5);"></i>{fatigued} fatigued</span>
    </div>
  </div>

  {svg}

  <div id="phi-detail" style="
    display:none; margin:0 16px 14px 16px;
    border:1px solid rgba(51,255,51,0.12);
    background:#0d110d; padding:12px 16px;">
    <div id="phi-detail-name" style="
      font-size:13px; font-weight:700; color:#33ff33;
      letter-spacing:0.05em; margin-bottom:8px;"></div>
    <div style="
      height:4px; background:rgba(51,255,51,0.08);
      margin-bottom:8px;">
      <div id="phi-detail-bar" style="
        height:100%; width:0%; background:#33ff33;
        transition:width 400ms ease;"></div>
    </div>
    <div style="
      display:flex; gap:16px; font-size:10px;
      color:rgba(51,255,51,0.45);">
      <span>Readiness <strong id="phi-readiness"
        style="color:#33ff33;font-weight:700;">0%</strong></span>
    </div>
  </div>

  <style>
    .phi-muscle {{
      transition: opacity 250ms ease, transform 250ms ease;
      transform-box: fill-box; transform-origin: center;
      cursor: pointer;
    }}
    .phi-muscle:hover {{
      opacity: 0.9 !important;
      transform: scale(1.04);
    }}
    .phi-muscle.selected {{
      opacity: 1 !important;
      transform: scale(1.05);
      stroke-opacity: 0.6 !important;
      stroke-width: 1.5 !important;
    }}
  </style>

  <script>
  (function(){{
    var root = document.getElementById('phi-heatmap');
    var detail = document.getElementById('phi-detail');
    var detailName = document.getElementById('phi-detail-name');
    var detailBar = document.getElementById('phi-detail-bar');
    var detailReadiness = document.getElementById('phi-readiness');
    var selected = null;

    root.querySelectorAll('.phi-muscle').forEach(function(el){{
      el.addEventListener('click', function(e){{
        var name = this.getAttribute('data-name');
        var readiness = this.getAttribute('data-readiness');
        var fill = this.getAttribute('fill');

        if (selected) selected.classList.remove('selected');
        if (selected === this) {{
          selected = null;
          detail.style.display = 'none';
          return;
        }}
        selected = this;
        selected.classList.add('selected');

        detailName.textContent = name;
        detailBar.style.width = readiness + '%';
        detailBar.style.background = fill;
        detailReadiness.textContent = readiness + '%';
        detail.style.display = 'block';
        e.stopPropagation();
      }});

      el.addEventListener('mouseenter', function(){{
        this.style.strokeOpacity = '0.35';
        this.style.strokeWidth = '1.5';
      }});
      el.addEventListener('mouseleave', function(){{
        this.style.strokeOpacity = '0.15';
        this.style.strokeWidth = '1';
      }});
    }});

    document.addEventListener('click', function(e){{
      if (!e.target.closest('.phi-muscle') && detail) {{
        detail.style.display = 'none';
        if (selected) {{ selected.classList.remove('selected'); selected = null; }}
      }}
    }});
  }})();
  </script>
</div>"""
    render_html(html, height=600, scrolling=False)
