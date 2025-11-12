# file: random_asset_generator.py
# Requires: pip install pillow
# Usage: python random_asset_generator.py --name "my-asset" --width 1024 --height 512

import os
import io
import json
import argparse
import random
import string
import hashlib
import zipfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def rand_string(n=8):
    "Повертає випадковий алфанітно-цифровий рядок."
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def make_image(path, width=800, height=450, text=None):
    "Створює просте PNG-зображення з випадковим фоном і текстом."
    img = Image.new('RGBA', (width, height), (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255))
    draw = ImageDraw.Draw(img)
    # Простий вибір системного шрифту (fallback якщо немає)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=max(20, width//15))
    except Exception:
        font = ImageFont.load_default()
    if not text:
        text = f"asset-{rand_string(6)}"
    w, h = draw.textsize(text, font=font)
    draw.text(((width-w)/2, (height-h)/2), text, fill=(255,255,255), font=font)
    img.save(path, "PNG")
    return path

def compute_sha256(path):
    "Обчислює SHA-256 файлу."
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def make_metadata(name, filename, width, height, sha256):
    "Повертає словник метаданих для актива."
    return {
        "name": name,
        "filename": filename,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "dimensions": {"width": width, "height": height},
        "sha256": sha256,
        "tags": ["random", "generated", "asset"],
        "description": f"Auto-generated asset {name}"
    }

def bundle_asset(image_path, metadata, out_zip):
    "Пакує зображення і metadata.json в ZIP."
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(image_path, arcname=os.path.basename(image_path))
        meta_bytes = json.dumps(metadata, indent=2).encode("utf-8")
        z.writestr("metadata.json", meta_bytes)
    return out_zip

def main():
    p = argparse.ArgumentParser(description="Random Asset Generator for GitHub release assets")
    p.add_argument("--name", type=str, default=f"asset-{rand_string(6)}", help="Назва активу")
    p.add_argument("--width", type=int, default=1024, help="Ширина зображення")
    p.add_argument("--height", type=int, default=512, help="Висота зображення")
    p.add_argument("--out-dir", type=str, default="dist", help="Папка куди зберегти")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    base_name = args.name
    img_filename = f"{base_name}.png"
    img_path = os.path.join(args.out_dir, img_filename)

    print(f"Генерую зображення {img_path} ...")
    make_image(img_path, width=args.width, height=args.height, text=base_name)

    print("Обчислюю SHA-256 ...")
    sha = compute_sha256(img_path)

    print("Створюю metadata.json ...")
    metadata = make_metadata(base_name, img_filename, args.width, args.height, sha)
    meta_path = os.path.join(args.out_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    zip_name = os.path.join(args.out_dir, f"{base_name}.zip")
    print(f"Пакую в {zip_name} ...")
    bundle_asset(img_path, metadata, zip_name)

    print("Готово:")
    print(" - image:", img_path)
    print(" - metadata:", meta_path)
    print(" - zip:", zip_name)
    print("SHA256:", sha)

if __name__ == "__main__":
    main()
