# file: quantum_drop_builder.py
# No external dependencies required
# Usage: python quantum_drop_builder.py

import os
import json
import random
from datetime import datetime

def random_hex():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def generate_svg(width=600, height=600, shapes=15):
    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="black"/>'
    ]
    for _ in range(shapes):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        r = random.randint(20, 120)
        color = random_hex()
        opacity = round(random.uniform(0.2, 0.8), 2)
        svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" fill-opacity="{opacity}"/>'
        )
    svg.append("</svg>")
    return "\n".join(svg)

def make_metadata(filename, width, height):
    return {
        "asset": filename,
        "type": "quantum-svg",
        "dimensions": f"{width}x{height}",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "description": "Procedurally generated quantum-style SVG asset.",
        "entropy_seed": random.randint(100000, 999999),
        "tags": ["quantum", "svg", "asset", "random"]
    }

def main():
    out_dir = "quantum_drop"
    os.makedirs(out_dir, exist_ok=True)

    name = f"quantum_{random.randint(1000, 9999)}"
    svg_file = os.path.join(out_dir, f"{name}.svg")
    json_file = os.path.join(out_dir, f"{name}.json")

    print(f"⚛️ Generating {name} ...")

    svg = generate_svg()
    with open(svg_file, "w") as f:
        f.write(svg)

    metadata = make_metadata(f"{name}.svg", 600, 600)
    with open(json_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Created SVG: {svg_file}")
    print(f"✅ Created Metadata: {json_file}")
    print("Ready for upload as GitHub release assets.")

if __name__ == "__main__":
    main()
