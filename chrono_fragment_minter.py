# file: chrono_fragment_minter.py
# No external libraries required
# Usage: python chrono_fragment_minter.py

import os
import random
import hashlib
from datetime import datetime, timedelta


def random_hash():
    """Створює псевдо-криптографічний хеш."""
    raw = str(random.random()).encode()
    return hashlib.sha1(raw).hexdigest()


def generate_fragment(lines=40):
    """Генерує 'часовий фрагмент' із шумом."""
    fragment = ["# Chrono-Fragment Data\n"]
    start = datetime.utcnow()

    for i in range(lines):
        delta = timedelta(seconds=random.randint(1, 5000))
        t = start + delta
        noise = random_hash()[:12]
        entropy = random.uniform(0.001, 0.999)

        fragment.append(
            f"{t.isoformat()}Z | Δ={delta.total_seconds():.0f}s | sig:{noise} | ent:{entropy:.3f}"
        )

    return "\n".join(fragment)


def save_fragment(path, content):
    with open(path, "w") as f:
        f.write(content)


def save_metadata(path, lines):
    meta = {
        "file": os.path.basename(path),
        "entries": lines,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "format": "chrono-fragment",
        "description": "Synthetic temporal fragment asset for GitHub releases.",
        "entropy_seed": random.randint(1000000, 9999999),
        "version": "1.0",
        "tags": ["time", "fragment", "synthetic", "asset"]
    }
    with open(path + ".json", "w") as f:
        import json
        json.dump(meta, f, indent=2)


def main():
    out_dir = "chrono_fragments"
    os.makedirs(out_dir, exist_ok=True)

    name = f"fragment_{random.randint(1000, 9999)}.txt"
    full_path = os.path.join(out_dir, name)

    print(f"🌀 Minting chrono-fragment: {name}")

    content = generate_fragment()
    save_fragment(full_path, content)
    save_metadata(full_path, content.count("\n"))

    print("✅ Fragment created:", full_path)
    print("📄 Metadata:", full_path + ".json")
    print("Ready for GitHub release upload.")


if __name__ == "__main__":
    main()
