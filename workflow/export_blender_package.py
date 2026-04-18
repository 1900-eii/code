from __future__ import annotations

import math
import csv
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import json

from workflow.common import BLENDER_DIR, PROCESSED_DIR, ROOT, write_json


def color_hex_to_rgba(hex_color: str) -> list[float]:
    value = hex_color.lstrip("#")
    return [round(int(value[i : i + 2], 16) / 255, 4) for i in (0, 2, 4)] + [1.0]


def taxonomy_object_type(taxonomy: str) -> str:
    return {
        "edge_condition": "wall_panel",
        "playable_surface": "ground_tile",
        "sloped_platform": "stepped_ramp",
    }.get(taxonomy, "generic_block")


def build_geometry_params(fragment: dict, width_m: float, depth_m: float, height_m: float) -> dict:
    taxonomy = fragment["taxonomy"]
    coverage = fragment["alpha_coverage_ratio"]
    brightness = fragment["brightness"]
    if taxonomy == "edge_condition":
        rib_count = max(3, min(9, int(round(width_m * 1.6))))
        return {
            "primitive": "ribbed_wall",
            "panel_count": rib_count,
            "panel_spacing_m": round(width_m / max(rib_count, 1), 3),
            "panel_thickness_m": round(max(0.06, depth_m / 8), 3),
            "perforation_ratio": round(min(0.65, 0.18 + coverage * 0.42), 3),
        }
    if taxonomy == "playable_surface":
        marker_count = max(4, min(14, int(round((width_m + depth_m) * 1.2))))
        return {
            "primitive": "marker_field",
            "marker_count": marker_count,
            "marker_radius_m": round(max(0.12, min(0.4, width_m / 10)), 3),
            "surface_thickness_m": round(max(0.04, height_m / 8), 3),
            "pattern_shift_m": round((brightness / 255) * 0.8, 3),
        }
    if taxonomy == "sloped_platform":
        step_count = max(3, min(8, int(round(height_m / 0.24))))
        return {
            "primitive": "stepped_slope",
            "step_count": step_count,
            "step_height_m": round(max(0.12, height_m / max(step_count, 1)), 3),
            "step_depth_m": round(max(0.22, width_m / max(step_count, 1)), 3),
            "slope_ratio": round(height_m / max(width_m, 0.01), 3),
        }
    return {"primitive": "generic_block"}


def build_blender_fragments() -> tuple[dict, list[dict]]:
    scene_path = ROOT / "frontend" / "data" / "scene.json"
    payload = json.loads(scene_path.read_text(encoding="utf-8"))
    fragments = payload["fragments"]

    table_rows = []
    blender_fragments = []
    current_x = 0.0
    row_depth = 0.0

    for idx, fragment in enumerate(fragments):
        size = fragment["size"]
        width_m = round(size["width"] / 100.0, 3)
        height_m = round(size["height"] / 100.0, 3)
        depth_m = round(size["depth"] / 100.0, 3)

        if idx % 6 == 0 and idx > 0:
            current_x = 0.0
            row_depth += 4.8

        location = [round(current_x, 3), round(row_depth, 3), round(height_m / 2, 3)]
        rotation = [0.0, 0.0, round(math.radians(fragment["tilt"]), 4)]
        current_x += max(2.4, width_m + 0.9)

        blender_fragment = {
            "id": fragment["id"],
            "name": fragment["title"],
            "taxonomy": fragment["taxonomy"],
            "family": fragment["family"],
            "object_type": taxonomy_object_type(fragment["taxonomy"]),
            "dimensions_m": {
                "width": width_m,
                "depth": depth_m,
                "height": height_m,
            },
            "transform": {
                "location": location,
                "rotation_euler": rotation,
                "bevel_radius": round(fragment["radius"] / 100.0, 3),
                "elevation_hint": round(fragment["elevation"] / 100.0, 3),
            },
            "visual": {
                "palette_rgba": [color_hex_to_rgba(color) for color in fragment["palette"]],
                "brightness": round(fragment["brightness"], 3),
                "alpha_coverage_ratio": round(fragment["alpha_coverage_ratio"], 4),
            },
            "geometry_params": build_geometry_params(fragment, width_m, depth_m, height_m),
            "rules": fragment["rules"],
            "source_refs": {
                "analysis_image": fragment["source_image"],
                "nearest_keyframe": fragment["nearest_keyframe"],
                "record_id": fragment["id"],
                "timestamp_sec": fragment["timestamp_sec"],
            },
        }
        blender_fragments.append(blender_fragment)

        table_rows.append(
            {
                "id": fragment["id"],
                "name": fragment["title"],
                "taxonomy": fragment["taxonomy"],
                "family": fragment["family"],
                "object_type": blender_fragment["object_type"],
                "width_m": width_m,
                "depth_m": depth_m,
                "height_m": height_m,
                "loc_x": location[0],
                "loc_y": location[1],
                "loc_z": location[2],
                "rot_z_rad": rotation[2],
                "brightness": fragment["brightness"],
                "alpha_coverage_ratio": fragment["alpha_coverage_ratio"],
                "primitive": blender_fragment["geometry_params"]["primitive"],
                "analysis_image": fragment["source_image"],
            }
        )

    export_payload = {
        "project": "Child-Space Interaction Blender Export",
        "schema_version": "1.0",
        "units": "meters",
        "generator": "workflow.export_blender_package",
        "fragment_count": len(blender_fragments),
        "fragments": blender_fragments,
    }
    return export_payload, table_rows


def main() -> None:
    BLENDER_DIR.mkdir(parents=True, exist_ok=True)
    export_payload, table_rows = build_blender_fragments()

    json_path = PROCESSED_DIR / "blender_ready_fragments.json"
    csv_path = PROCESSED_DIR / "blender_ready_fragments.csv"
    blender_json_path = BLENDER_DIR / "blender_ready_fragments.json"
    blender_csv_path = BLENDER_DIR / "blender_ready_fragments.csv"

    write_json(json_path, export_payload)
    write_json(blender_json_path, export_payload)

    header = list(table_rows[0].keys()) if table_rows else []
    for target in (csv_path, blender_csv_path):
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header)
            writer.writeheader()
            writer.writerows(table_rows)

    print(f"Saved Blender package to {json_path} and {csv_path}")


if __name__ == "__main__":
    main()
