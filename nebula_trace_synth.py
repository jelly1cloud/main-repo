# file: nebula_trace_synth.py
# No external libraries required
# Usage: python nebula_trace_synth.py

import os
import random
import math
import json
from datetime import datetime


def generate_trace_points(count=150):
    """Генерує векторні точки космічної 'туманності'."""
    points = []
    swirl = random.uniform(0.3, 1.2)
    chaos = random.uniform(0.01, 0.15)

    for i in range(count):
        angle = i * swirl
        radius = i * random.uniform(0.7, 1.3)

        x = radius * math.cos(angle) + random.uniform(-chaos, chaos)
        y = radius * math.sin(angle) + random.uniform(-chaos, chaos)

        points.append((round(x, 4), round(y, 4)))

    return points, swirl, chaos


def save_ntrace(path, points, swirl, chaos):
    """Формує файл вигаданого формату .ntrace."""
    with open(path, "w") as f:
        f.write("# Nebula Trace File (.ntrace)\n")
        f.write(f"# swirl={swirl:.3f} chaos={chaos:.3f} entries={len(points)}\n")
        for x, y in points:
            f.write(f"{x},{y}\n")


def save_metadata(path, points, swirl, chaos):
    meta = {
        "file": os.path.basename(path),
        "type": "nebula-trace",
        "entries": len(points),
        "swirl_factor": swirl,
        "chaos_factor": chaos,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "description": "Procedurally generated nebula vector trace for GitHub assets.",
        "tags": ["nebula", "trace", "vector", "synthetic", "asset"]
    }
    with open(path + ".json", "w") as f:
        json.dump(meta, f, indent=2)


def main():
    out_dir = "nebula_traces"
    os.makedirs(out_dir, exist_ok=True)

    name = f"trace_{random.randint(1000,9999)}.ntrace"
    full_path = os.path.join(out_dir, name)

    print(f"✨ Synthesizing nebula trace: {name}")

    points, swirl, chaos = generate_trace_points()
    save_ntrace(full_path, points, swirl, chaos)
    save_metadata(full_path, points, swirl, chaos)

    print("✅ Trace generated:", full_path)
    print("📄 Metadata:", full_path + ".json")
    print("Ready for GitHub release upload.")


if __name__ == "__main__":
    main()
