from __future__ import annotations

import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from workflow.common import PROCESSED_DIR, write_json


DESIGN_RULES = {
    "edge_condition": {
        "spatial_role": "threshold wall",
        "geometry_rule": "repeat narrow vertical ribs and offset every third panel",
        "material_rule": "use perforated metal or translucent acrylic panels",
        "interaction_rule": "keep apertures at child-eye level and alternate dense/open zones",
        "color_rule": "lean toward saturated warning tones with one bright accent",
    },
    "playable_surface": {
        "spatial_role": "ground field",
        "geometry_rule": "tile the surface with rhythmic circular or hopscotch-like markers",
        "material_rule": "use painted rubber, terrazzo, or textured paving",
        "interaction_rule": "encode movement prompts as directional traces and soft landing pockets",
        "color_rule": "use high-contrast stripes and warm ground colors",
    },
    "sloped_platform": {
        "spatial_role": "inhabitable slope",
        "geometry_rule": "stack broad terraces and taper every second edge to create climbable transitions",
        "material_rule": "use timber slats, coated plywood, or soft composite seating surfaces",
        "interaction_rule": "balance sitting, climbing, and pause zones across the slope",
        "color_rule": "keep the base warm and highlight slope transitions with brighter bands",
    },
}


def build_mock_response() -> dict:
    interactions = pd.read_csv(PROCESSED_DIR / "ml_interactions.csv")
    seeds = pd.read_csv(PROCESSED_DIR / "blender_fragment_seed_table.csv")
    top_terms = pd.read_csv(PROCESSED_DIR / "text_top_terms.csv")

    prompts = []
    for row in seeds.itertuples(index=False):
        taxonomy = row.taxonomy_label
        taxonomy_rows = interactions[interactions["taxonomy_label"] == taxonomy]
        representative_terms = top_terms[top_terms["dataset_name"] == "playscapes_global_map"]["top_terms"].head(1)
        prompts.append(
            {
                "taxonomy_label": taxonomy,
                "fragment_family": DESIGN_RULES[taxonomy]["spatial_role"],
                "geometry_rule": DESIGN_RULES[taxonomy]["geometry_rule"],
                "material_rule": DESIGN_RULES[taxonomy]["material_rule"],
                "interaction_rule": DESIGN_RULES[taxonomy]["interaction_rule"],
                "color_rule": DESIGN_RULES[taxonomy]["color_rule"],
                "observed_mean_width": round(float(row.mean_width), 2),
                "observed_mean_height": round(float(row.mean_height), 2),
                "observed_mean_alpha": round(float(row.mean_alpha), 4),
                "observed_count": int(row.exemplar_count),
                "supporting_terms": representative_terms.iloc[0] if not representative_terms.empty else "",
                "sample_records": taxonomy_rows["record_id"].head(5).tolist(),
            }
        )

    return {
        "mode": "mock",
        "status": "usable-substitute",
        "reason": "OpenAI API is deferred, so this file simulates downstream design-rule generation.",
        "system_prompt_stub": "Transform interaction evidence into spatial fragment rules for a child-friendly architecture workflow.",
        "responses": prompts,
    }


def main() -> None:
    payload = build_mock_response()
    output_path = PROCESSED_DIR / "mock_api_design_rules.json"
    write_json(output_path, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
