# file: ion_flux_emitter.py
# No external libs
# Usage: python ion_flux_emitter.py

import os
import json
import random
import math
from datetime import datetime

def generate_ion_values(count=256):
    values = []
    for i in range(count):
        # псевдо-фізична формула для вигляду "реального" шуму
        angle = i * random.uniform(0.01, 0.05)
        flux = math.sin(angle) * random.uniform(0.5, 3.0) + random.uniform(-0.2, 0.2)
        values.append(round(flux, 6))
    return values

def write_dat(path, values):
    with open(path, "w") as f:
        f.write("# Ion flux signature data\n")
        for v in values:
            f.write(f"{v}\n")

def write_metadata(path, count):
    meta = {
        "file": os.path.basename(path),
        "entries": count,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "type": "ion-flux-dataset",
        "description": "Randomly generated ion flux emission dataset for GitHub release assets.",
        "noise_profile": f"{random.uniform(0.1, 1.0):.3f}",
        "signature_id": random.randint(100000, 999999),
        "tags": ["ion", "flux", "dataset", "random"]
    }
    with open(path + ".json", "w") as f:
        json.dump(meta, f, indent=2)

def main():
    out_dir = "ion_flux_output"
    os.makedirs(out_dir, exist_ok=True)

    name = f"flux_{random.randint(1000,9999)}.dat"
    full_path = os.path.join(out_dir, name)

    print(f"✨ Generating ion flux dataset: {name}")

    values = generate_ion_values()
    write_dat(full_path, values)
    write_metadata(full_path, len(values))

    print("✅ Data file created:", full_path)
    print("📄 Metadata created:", full_path + ".json")
    print("Ready for GitHub upload.")

if __name__ == "__main__":
    main()
