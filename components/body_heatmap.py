from __future__ import annotations

from html import escape

import streamlit as st
from streamlit.components.v1 import html as render_html


STATUS_STYLE = {
    "Ready": {"color": "#2f9f68", "glow": "rgba(47,159,104,0.30)", "label": "Ready"},
    "Manage load": {"color": "#c98a18", "glow": "rgba(201,138,24,0.28)", "label": "Manage"},
    "Fatigued": {"color": "#d95f5f", "glow": "rgba(217,95,95,0.30)", "label": "Fatigued"},
    "Empty": {"color": "#d9e2dc", "glow": "rgba(104,118,111,0.10)", "label": "No data"},
}


def render_svg_body_heatmap(readiness_status: list[dict]):
    """Render a front/back muscle readiness atlas with richer visual hierarchy."""
    rows = {str(item.get("muscle", "")).lower(): item for item in readiness_status}

    def data_for(*names: str) -> dict:
        for name in names:
            row = rows.get(name.lower())
            if row:
                return row
        return {"muscle": names[0], "status": "Empty", "readiness": 0, "fatigue": 0, "load_7d": 0}

    def style_for(*names: str) -> dict:
        row = data_for(*names)
        status = str(row.get("status", "Empty"))
        style = STATUS_STYLE.get(status, STATUS_STYLE["Empty"])
        readiness = float(row.get("readiness", 0) or 0)
        opacity = 0.34 + (readiness / 100 * 0.58) if status != "Empty" else 0.28
        return {
            "color": style["color"],
            "glow": style["glow"],
            "opacity": f"{min(opacity, 0.96):.2f}",
            "label": style["label"],
            "readiness": int(readiness),
            "status": status,
        }

    def part(name: str, d: str, *muscles: str) -> str:
        s = style_for(*muscles)
        title = escape(f"{name}: {s['label']} ({s['readiness']}%)")
        return (
            f'<path class="phi-body-part" d="{d}" fill="{s["color"]}" '
            f'fill-opacity="{s["opacity"]}" stroke="rgba(35,49,43,0.24)" '
            f'stroke-width="1.4" filter="url(#glow-{s["status"].replace(" ", "-")})">'
            f"<title>{title}</title></path>"
        )

    def label(x: int, y: int, text: str, *muscles: str) -> str:
        s = style_for(*muscles)
        return (
            f'<g class="phi-body-label">'
            f'<circle cx="{x}" cy="{y - 4}" r="3" fill="{s["color"]}" filter="url(#dotGlow)"/>'
            f'<text x="{x + 8}" y="{y}" fill="#39443f">{escape(text)}</text>'
            f"</g>"
        )

    ready_count = sum(1 for row in readiness_status if row.get("status") == "Ready")
    manage_count = sum(1 for row in readiness_status if row.get("status") == "Manage load")
    fatigued_count = sum(1 for row in readiness_status if row.get("status") == "Fatigued")

    svg = f"""
    <div class="phi-body-atlas">
        <div class="phi-body-atlas-head">
            <div>
                <div class="phi-label">Muscle atlas</div>
                <div class="phi-body-atlas-title">Recovery Map</div>
            </div>
            <div class="phi-body-atlas-legend">
                <span><i style="background:#2f9f68"></i>{ready_count} ready</span>
                <span><i style="background:#c98a18"></i>{manage_count} manage</span>
                <span><i style="background:#d95f5f"></i>{fatigued_count} fatigued</span>
            </div>
        </div>
        <svg class="phi-body-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 500" role="img" aria-label="Muscle readiness body map">
            <defs>
                <radialGradient id="bodyCoreGlow" cx="50%" cy="18%" r="75%">
                    <stop offset="0%" stop-color="rgba(47,159,104,0.18)"/>
                    <stop offset="58%" stop-color="rgba(47,159,104,0.05)"/>
                    <stop offset="100%" stop-color="rgba(47,159,104,0)"/>
                </radialGradient>
                <filter id="dotGlow"><feGaussianBlur stdDeviation="2.8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                <filter id="glow-Ready"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="rgba(47,159,104,0.28)"/></filter>
                <filter id="glow-Manage-load"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="rgba(201,138,24,0.28)"/></filter>
                <filter id="glow-Fatigued"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="rgba(217,95,95,0.28)"/></filter>
                <filter id="glow-Empty"><feDropShadow dx="0" dy="0" stdDeviation="2" flood-color="rgba(104,118,111,0.12)"/></filter>
                <linearGradient id="skeletonLine" x1="0" x2="1">
                    <stop offset="0%" stop-color="rgba(104,118,111,0.10)"/>
                    <stop offset="50%" stop-color="rgba(35,49,43,0.22)"/>
                    <stop offset="100%" stop-color="rgba(104,118,111,0.10)"/>
                </linearGradient>
            </defs>

            <rect x="18" y="18" width="504" height="448" rx="18" fill="url(#bodyCoreGlow)" stroke="rgba(35,49,43,0.12)"/>
            <line x1="270" y1="62" x2="270" y2="430" stroke="rgba(35,49,43,0.12)" stroke-dasharray="5 8"/>
            <text x="155" y="55" text-anchor="middle" fill="#39443f" font-size="13" font-weight="800">FRONT</text>
            <text x="385" y="55" text-anchor="middle" fill="#39443f" font-size="13" font-weight="800">BACK</text>

            <g opacity="0.9">
                <circle cx="155" cy="86" r="23" fill="#edf3ee" stroke="url(#skeletonLine)" stroke-width="1.5"/>
                <path d="M132 126 C139 108 171 108 178 126 L191 170 C199 201 191 226 176 246 L174 277 L136 277 L134 246 C119 226 111 201 119 170 Z" fill="rgba(237,243,238,0.82)" stroke="rgba(35,49,43,0.12)" stroke-width="1.5"/>
                <circle cx="385" cy="86" r="23" fill="#edf3ee" stroke="url(#skeletonLine)" stroke-width="1.5"/>
                <path d="M362 126 C369 108 401 108 408 126 L421 170 C429 201 421 226 406 246 L404 277 L366 277 L364 246 C349 226 341 201 349 170 Z" fill="rgba(237,243,238,0.82)" stroke="rgba(35,49,43,0.12)" stroke-width="1.5"/>
            </g>

            <g class="front-map">
                {part("Shoulders", "M104 130 C111 111 132 113 139 129 C128 140 116 150 103 160 C96 151 96 140 104 130 Z", "Shoulders")}
                {part("Shoulders", "M206 130 C199 111 178 113 171 129 C182 140 194 150 207 160 C214 151 214 140 206 130 Z", "Shoulders")}
                {part("Chest", "M124 128 C136 118 149 121 155 136 L155 178 L119 169 C116 151 118 139 124 128 Z", "Chest")}
                {part("Chest", "M186 128 C174 118 161 121 155 136 L155 178 L191 169 C194 151 192 139 186 128 Z", "Chest")}
                {part("Core", "M129 177 L155 184 L181 177 L176 251 L155 260 L134 251 Z", "Core")}
                {part("Biceps", "M93 158 C104 158 111 167 108 180 L96 225 C93 236 78 232 80 219 L88 177 C89 169 89 162 93 158 Z", "Biceps")}
                {part("Biceps", "M217 158 C206 158 199 167 202 180 L214 225 C217 236 232 232 230 219 L222 177 C221 169 221 162 217 158 Z", "Biceps")}
                {part("Forearms", "M80 223 C90 225 96 234 93 245 L84 292 C81 305 65 302 67 288 L72 241 C73 231 75 225 80 223 Z", "Forearms")}
                {part("Forearms", "M230 223 C220 225 214 234 217 245 L226 292 C229 305 245 302 243 288 L238 241 C237 231 235 225 230 223 Z", "Forearms")}
                {part("Quads", "M132 269 L153 265 L151 363 C148 382 126 381 125 361 L123 303 C123 288 126 276 132 269 Z", "Quads")}
                {part("Quads", "M178 269 L157 265 L159 363 C162 382 184 381 185 361 L187 303 C187 288 184 276 178 269 Z", "Quads")}
                {part("Calves", "M126 366 C137 372 146 372 151 365 L146 433 C145 449 124 449 123 432 Z", "Calves")}
                {part("Calves", "M184 366 C173 372 164 372 159 365 L164 433 C165 449 186 449 187 432 Z", "Calves")}
            </g>

            <g class="back-map">
                {part("Back", "M354 127 C365 115 405 115 416 127 L407 214 C397 230 373 230 363 214 Z", "Back")}
                {part("Shoulders", "M334 130 C342 112 362 113 369 129 C358 141 346 151 333 160 C326 151 326 140 334 130 Z", "Shoulders")}
                {part("Shoulders", "M436 130 C428 112 408 113 401 129 C412 141 424 151 437 160 C444 151 444 140 436 130 Z", "Shoulders")}
                {part("Triceps", "M323 158 C334 158 341 167 338 181 L326 226 C323 237 308 233 310 219 L318 177 C319 169 319 162 323 158 Z", "Triceps")}
                {part("Triceps", "M447 158 C436 158 429 167 432 181 L444 226 C447 237 462 233 460 219 L452 177 C451 169 451 162 447 158 Z", "Triceps")}
                {part("Forearms", "M310 223 C320 225 326 234 323 245 L314 292 C311 305 295 302 297 288 L302 241 C303 231 305 225 310 223 Z", "Forearms")}
                {part("Forearms", "M460 223 C450 225 444 234 447 245 L456 292 C459 305 475 302 473 288 L468 241 C467 231 465 225 460 223 Z", "Forearms")}
                {part("Glutes", "M363 225 C374 218 396 218 407 225 L405 270 C393 279 377 279 365 270 Z", "Glutes")}
                {part("Hamstrings", "M362 269 L383 265 L381 363 C378 382 356 381 355 361 L353 303 C353 288 356 276 362 269 Z", "Hamstrings")}
                {part("Hamstrings", "M408 269 L387 265 L389 363 C392 382 414 381 415 361 L417 303 C417 288 414 276 408 269 Z", "Hamstrings")}
                {part("Calves", "M356 366 C367 372 376 372 381 365 L376 433 C375 449 354 449 353 432 Z", "Calves")}
                {part("Calves", "M414 366 C403 372 394 372 389 365 L394 433 C395 449 416 449 417 432 Z", "Calves")}
            </g>

            <g font-family="Inter, sans-serif" font-size="10" font-weight="800">
                {label(32, 147, "Shoulders", "Shoulders")}
                {label(34, 202, "Arms", "Biceps", "Triceps", "Forearms")}
                {label(34, 318, "Legs", "Quads", "Hamstrings")}
                {label(438, 147, "Back", "Back")}
                {label(438, 240, "Glutes", "Glutes")}
                {label(438, 374, "Calves", "Calves")}
            </g>
        </svg>
    </div>
    <style>
        .phi-body-atlas {{
            position: relative;
            overflow: hidden;
            padding: 1rem;
            border: 1px solid rgba(35,49,43,0.11);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 8px 22px rgba(25,37,31,0.10);
        }}
        .phi-body-atlas::after {{
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background-image: linear-gradient(rgba(35,49,43,0.035) 1px, transparent 1px);
            background-size: 100% 18px;
            opacity: 0.55;
        }}
        .phi-body-atlas-head {{
            position: relative;
            z-index: 1;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.45rem;
        }}
        .phi-body-atlas-title {{
            color: #17201c;
            font-family: "Outfit", "Plus Jakarta Sans", Inter, sans-serif;
            font-size: 1.25rem;
            font-weight: 850;
            letter-spacing: -0.03em;
            margin-top: 0.22rem;
        }}
        .phi-body-atlas-legend {{
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 0.35rem;
        }}
        .phi-body-atlas-legend span {{
            display: inline-flex;
            align-items: center;
            gap: 0.34rem;
            padding: 0.26rem 0.46rem;
            border: 1px solid rgba(35,49,43,0.12);
            border-radius: 999px;
            color: #68766f;
            background: #f3f6f2;
            font-size: 0.68rem;
            font-weight: 850;
        }}
        .phi-body-atlas-legend i {{
            width: 0.45rem;
            height: 0.45rem;
            border-radius: 999px;
            box-shadow: 0 0 12px currentColor;
        }}
        .phi-body-svg {{
            position: relative;
            z-index: 1;
            width: 100%;
            min-height: 410px;
            display: block;
        }}
        .phi-body-part {{
            transition: opacity 160ms ease, transform 160ms ease, filter 160ms ease;
            transform-box: fill-box;
            transform-origin: center;
        }}
        .phi-body-part:hover {{
            opacity: 1;
            transform: scale(1.018);
            stroke: rgba(35,49,43,0.42);
            stroke-width: 2;
        }}
        .phi-body-label text {{
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
    </style>
    """

    render_html(svg, height=560, scrolling=False)
