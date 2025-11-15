# file: stellar_packet_forge.py
# No external libraries required
# Usage: python stellar_packet_forge.py

import os
import json
import random
import struct
import hashlib
from datetime import datetime

def random_bytes(n=256):
    return bytes(random.getrandbits(8) for _ in range(n))

def encode_header(packet_id, size):
    # Простий двобайтний заголовок: ID + розмір
    return struct.pack(">HI", packet_id, size)

def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def create_packet(out_path):
    packet_id = random.randint(1000, 9999)
    data = random_bytes(1024 + random.randint(0, 4096))
    header = encode_header(packet_id, len(data))
    packet = header + data

    with open(out_path, "wb") as f:
        f.write(packet)

    return packet_id, len(packet)

def write_metadata(path, packet_id, byte_size, sha):
    metadata = {
        "packet_id": packet_id,
        "file": os.path.basename(path),
        "bytes": byte_size,
        "sha256": sha,
        "type": "stellar-packet",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "origin": "stellar_packet_forge.py",
        "info": "Random binary artifact for GitHub release assets."
    }
    meta_path = path + ".json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    return meta_path

def main():
    out_dir = "stellar_output"
    os.makedirs(out_dir, exist_ok=True)

    name = f"packet_{random.randint(10000,99999)}.bin"
    packet_path = os.path.join(out_dir, name)

    print(f"🌌 Creating random stellar packet: {name}")

    packet_id, size = create_packet(packet_path)
    sha = compute_sha256(packet_path)

    meta_path = write_metadata(packet_path, packet_id, size, sha)

    print(f"✅ Packet created: {packet_path}")
    print(f"📄 Metadata: {meta_path}")
    print(f"SHA256: {sha}")
    print("Ready for GitHub releases.")

if __name__ == "__main__":
    main()
