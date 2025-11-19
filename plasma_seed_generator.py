# file: plasma_seed_generator.py
# No external libraries required
# Usage: python plasma_seed_generator.py

import os
import random
import hashlib
import json
from datetime import datetime


ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # без легко плутаних символів


def random_seed(length=32):
    """Генерує випадковий плазмовий seed."""
    return "".join(random.choice(ALPHABET) for _ in range(length))


def derive_checksum(seed):
    """Створює короткий контрольний хеш для seed."""
    return hashlib.sha256(seed.encode()).hexdigest()[:10]


def encode_plasma_key(seed, checksum):
    """Формує контент файлу .psdkey."""
    return (
        "---- PLASMA SEED KEY ----\n"
        f"seed: {seed}\n"
        f"checksum: {checksum}\n"
        "format: psdkey/v1\n"
        "--------------------------\n"
    )


def write_key(path, content):
    with open(path, "w") as f:
        f.write(content)


def write_metadata(path, seed, checksum):
    meta = {
        "file": os.path.basename(path),
        "type": "plasma-seed-key",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "entropy_level": f"{random.uniform(0.8, 1.0):.3f}",
        "seed_length": len(seed),
        "checksum": checksum,
        "tags": ["plasma", "seed", "crypto", "asset"]
    }
    with open(path + ".json", "w") as f:
        json.dump(meta, f, indent=2)


def main():
    out_dir = "plasma_keys"
    os.makedirs(out_dir, exist_ok=True)

    name = f"plasma_{random.randint(1000, 9999)}.psdkey"
    path = os.path.join(out_dir, name)

    print(f"⚡ Generating plasma seed key: {name}")

    seed = random_seed()
    checksum = derive_checksum(seed)
    content = encode_plasma_key(seed, checksum)

    write_key(path, content)
    write_metadata(path, seed, checksum)

    print("✅ Key generated:", path)
    print("📄 Metadata:", path + ".json")
    print("Ready for GitHub release upload.")


if __name__ == "__main__":
    main()
