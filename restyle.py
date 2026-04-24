import os
from pathlib import Path

path = Path("styles.py")
content = path.read_text(encoding="utf-8")

replacements = {
    "#f59e0b": "#00d2ff",         # Amber -> Cyan
    "#fb923c": "#b14fff",         # Orange -> Purple
    "#d97706": "#008bbf",         # Dark Orange -> Dark Cyan
    "rgba(245, 158, 11": "rgba(0, 210, 255", 
    "radial-gradient(circle at top right, #1a1a1a, #0a0a0a)": "radial-gradient(circle at top right, #0a0514, #05070a)",
    "radial-gradient(circle at bottom left, #161616, #0a0a0a)": "radial-gradient(circle at bottom left, #05141d, #05070a)",
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Also update the tooltip hover glow
content = content.replace("0 0 5px rgba(245, 158, 11", "0 0 5px rgba(0, 210, 255")
content = content.replace("0 0 20px rgba(245, 158, 11", "0 0 20px rgba(0, 210, 255")

path.write_text(content, encoding="utf-8")
print("CSS Updated")
