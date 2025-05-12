"""
image_manifest.py

Defines the mapping from canonical car names to image filenames for DMuffler.
Provides a validation utility to check manifest integrity and asset existence.
"""
import os
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class ImageEntry:
    car_name: str
    filename: str

# Canonical image manifest
CAR_IMAGE_MAP: Dict[str, str] = {
    "bmw_m4": "bmw_m4.png",
    "ferrari_laferrari": "ferrari_laferrari.png",
    "ford_model_t": "ford_model_t.png",
    "ford_mustang": "ford_mustang.png",
    "jaguar_e_type": "jaguar_e_type.png",
    "mclaren_artura": "mclaren_artura.png",
    "porsche_911": "porsche_911.png",
    "star_wars_podracer": "STAR_WARS_PODRACER.png",
    "subaru_wrx_sti": "SUBARU_WRX_STI.png",
    "tesla_roadster": "TESLA_ROADSTER.png",
}

def validate_image_manifest(image_dir: str = "static/images"):
    missing = []
    for car, fname in CAR_IMAGE_MAP.items():
        path = os.path.join(image_dir, fname)
        if not os.path.isfile(path):
            missing.append((car, fname))
    if missing:
        raise FileNotFoundError(f"Missing image files: {missing}")

