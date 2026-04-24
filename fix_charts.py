import os

path = "ui/charts.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# The error is likely because multiple values for plot_bgcolor were passed
# CHART_LAYOUT already has it.

old_block = """        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )"""

new_block = """        height=400
    )"""

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    # Try with exact newline characters if windows-style
    old_block_w = old_block.replace("\n", "\r\n")
    new_block_w = new_block.replace("\n", "\r\n")
    if old_block_w in content:
        content = content.replace(old_block_w, new_block_w)
    else:
        # Final fallback, look for the lines specifically
        lines = content.splitlines()
        new_lines = []
        skip_next = 0
        for i, line in enumerate(lines):
            if skip_next > 0:
                skip_next -= 1
                continue
            if 'height=400,' in line and i + 2 < len(lines) and 'plot_bgcolor=' in lines[i+1] and 'paper_bgcolor=' in lines[i+2]:
                new_lines.append(line.replace("height=400,", "height=400"))
                skip_next = 2
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
