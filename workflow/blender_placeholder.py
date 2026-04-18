from __future__ import annotations

import pandas as pd
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from workflow.common import PROCESSED_DIR


def build_fragment_seed_table() -> pd.DataFrame:
    interactions = pd.read_csv(PROCESSED_DIR / "ml_interactions.csv")
    grouped = (
        interactions.groupby("taxonomy_label")
        .agg(
            mean_width=("crop_width", "mean"),
            mean_height=("crop_height", "mean"),
            mean_alpha=("alpha_coverage_ratio", "mean"),
            exemplar_count=("record_id", "count"),
        )
        .reset_index()
    )
    grouped["suggested_blender_action"] = grouped["taxonomy_label"].map(
        {
            "edge_condition": "extrude edge frames into porous wall fragments",
            "playable_surface": "flatten into patterned ground tiles",
            "sloped_platform": "loft into stepped seating or ramps",
        }
    ).fillna("review manually")
    return grouped


if __name__ == "__main__":
    output = build_fragment_seed_table()
    output.to_csv(PROCESSED_DIR / "blender_fragment_seed_table.csv", index=False)
    print(f"Saved Blender placeholder seed table to {PROCESSED_DIR / 'blender_fragment_seed_table.csv'}")
