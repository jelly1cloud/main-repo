# file: nebula_asset_maker.py
# Requires: pip install pillow
# Usage: python nebula_asset_maker.py

import os, json, random, math
from datetime import datetime
from PIL import Image, ImageDraw

def random_color():
    return tuple(random.randint(0, 255) for _ in range(3))

def generate_nebula(width=800, height=800, layers=12):
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(layers):
        x, y = random.randint(0, width), random.randint(0, height)
        radius = random.randint(100, 400)
        color = (*random_color(), random.randint(40, 120))
        for r in range(radius, 0, -5):
            alpha = int(255 * (1 - r / radius) * 0.5)
            c = (*color[:3], alpha)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return img

def make_metadata(filename, width, height):
    return {
        "name": filename,
        "type": "nebula-art",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "size": f"{width}x{height}",
        "tags": ["nebula", "random", "asset", "github"],
        "description": "Procedurally generated nebula asset for GitHub releases."
    }

def main():
    out_dir = "nebula_assets"
    os.makedirs(out_dir, exist_ok=True)

    name = f"nebula_{random.randint(1000,9999)}"
    img_path = os.path.join(out_dir, f"{name}.png")
    meta_path = os.path.join(out_dir, f"{name}.json")

    print(f"🌀 Generating {name} ...")
    img = generate_nebula()
    img.save(img_path)

    metadata = make_metadata(f"{name}.png", 800, 800)
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Created {img_path} and {meta_path}")
    print("Upload these as assets to your GitHub release!")

if __name__ == "__main__":
    main()
