from pathlib import Path

file_path = Path("Fitness.py")
lines = file_path.read_text("utf-8").splitlines()

in_dash_section = False
new_lines = []

for line in lines:
    if line.strip() == "if not workout_ready:":
        in_dash_section = True
        
    if in_dash_section and line.startswith("    "):
        new_lines.append(line[4:])
    else:
        new_lines.append(line)

file_path.write_text("\n".join(new_lines), "utf-8")
print("Unindented dashboard section.")
