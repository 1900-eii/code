from __future__ import annotations

import math
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from workflow.common import PROCESSED_DIR, ROOT, write_json


FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DATA_DIR = FRONTEND_DIR / "data"

PALETTES = {
    "edge_condition": ["#146356", "#f8b400", "#f6f5f5"],
    "playable_surface": ["#ef6c57", "#ffd166", "#1f5c7a"],
    "sloped_platform": ["#7c5535", "#e09f3e", "#f4f1de"],
}


def build_fragments() -> list[dict]:
    interactions = pd.read_csv(PROCESSED_DIR / "ml_interactions.csv")
    rules = pd.read_json(PROCESSED_DIR / "mock_api_design_rules.json")["responses"]
    rules_by_taxonomy = {item["taxonomy_label"]: item for item in rules}

    fragments = []
    per_taxonomy = 8
    for taxonomy, group in interactions.groupby("taxonomy_label"):
        family_rule = rules_by_taxonomy[taxonomy]
        group = group.sort_values(["alpha_coverage_ratio", "raw_brightness"], ascending=[False, False]).head(per_taxonomy)
        palette = PALETTES[taxonomy]
        for idx, row in enumerate(group.itertuples(index=False), start=1):
            width = max(160, min(380, int(row.crop_width * 0.14)))
            height = max(120, min(260, int(row.crop_height * 0.16)))
            depth = max(32, min(120, int((row.alpha_coverage_ratio * 180) + 20)))
            fragments.append(
                {
                    "id": row.record_id,
                    "taxonomy": taxonomy,
                    "family": family_rule["fragment_family"],
                    "title": f"{taxonomy.replace('_', ' ').title()} #{idx}",
                    "timestamp_sec": float(row.timestamp_sec),
                    "size": {"width": width, "height": height, "depth": depth},
                    "tilt": round(((idx % 4) - 1.5) * 6, 2),
                    "elevation": round(18 + (idx % 3) * 12 + row.alpha_coverage_ratio * 28, 2),
                    "radius": round(8 + (row.aspect_ratio * 3), 2),
                    "alpha_coverage_ratio": float(row.alpha_coverage_ratio),
                    "brightness": float(row.raw_brightness),
                    "source_image": row.analysis_path,
                    "nearest_keyframe": row.nearest_keyframe_path,
                    "palette": palette,
                    "rules": {
                        "geometry": family_rule["geometry_rule"],
                        "material": family_rule["material_rule"],
                        "interaction": family_rule["interaction_rule"],
                        "color": family_rule["color_rule"],
                    },
                }
            )
    return fragments


def main() -> None:
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    fragments = build_fragments()
    payload = {
        "project": "Child-Space Interaction Fragment Renderer",
        "render_mode": "frontend-substitute-for-blender",
        "note": "This scene is a front-end rendering prototype that stands in for the deferred Blender stage.",
        "fragment_count": len(fragments),
        "fragments": fragments,
    }
    write_json(FRONTEND_DATA_DIR / "scene.json", payload)
    print(f"Saved {len(fragments)} front-end fragments to {FRONTEND_DATA_DIR / 'scene.json'}")


if __name__ == "__main__":
    main()
