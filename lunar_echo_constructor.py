# file: lunar_echo_constructor.py
# No external libraries required
# Usage: python lunar_echo_constructor.py

import os
import random
import math
from datetime import datetime
import json


def generate_wave_points(count=180):
    """Генерує хвильові точки для 'місячного ехо'."""
    points = []
    freq = random.uniform(0.2, 1.4)
    amp = random.uniform(0.8, 2.5)
    noise = random.uniform(0.01, 0.2)

    for i in range(count):
        x = i
        wave = math.sin(i * freq) * amp
        distorted = wave + (random.uniform(-noise, noise))
        points.append(round(distorted, 6))

    return points, freq, amp, noise


def save_lec_file(path, points, freq, amp, noise):
    """Зберігає файл формату LEC."""
    with open(path, "w") as f:
        f.write("# Lunar Echo Capture (LEC)\n")
        f.write(f"# points={len(points)} freq={freq:.3f} amp={amp:.3f} noise={noise:.3f}\n")
        for p in points:
            f.write(f"{p}\n")


def save_metadata(path, size, freq, amp, noise):
    meta = {
        "file": os.path.basename(path),
        "type": "lunar-echo-capture",
        "entries": size,
        "frequency": freq,
        "amplitude": amp,
        "noise_factor": noise,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "description": "Synthetic lunar echo wave dataset for GitHub assets.",
        "tags": ["lunar", "echo", "wave", "synthetic", "asset"]
    }
    with open(path + ".json", "w") as f:
        json.dump(meta, f, indent=2)


def main():
    out_dir = "lunar_echo_output"
    os.makedirs(out_dir, exist_ok=True)

    name = f"lunar_echo_{random.randint(1000,9999)}.lec"
    full_path = os.path.join(out_dir, name)

    print(f"🌙 Constructing lunar echo: {name}")

    points, freq, amp, noise = generate_wave_points()
    save_lec_file(full_path, points, freq, amp, noise)
    save_metadata(full_path, len(points), freq, amp, noise)

    print("✅ Echo file created:", full_path)
    print("📄 Metadata:", full_path + ".json")
    print("Ready for GitHub release upload.")


if __name__ == "__main__":
    main()
