from __future__ import annotations

from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import pandas as pd

from workflow.common import PROCESSED_DIR, ROOT


def main() -> None:
    ml = pd.read_csv(PROCESSED_DIR / "ml_interactions.csv")
    vector_summary = pd.read_csv(PROCESSED_DIR / "vector_method_summary.csv")
    scraped = pd.read_csv(PROCESSED_DIR / "scraped_datasets.csv")
    rules = json.loads((PROCESSED_DIR / "mock_api_design_rules.json").read_text(encoding="utf-8"))
    scene = json.loads((ROOT / "frontend" / "data" / "scene.json").read_text(encoding="utf-8"))

    taxonomy_counts = ml["taxonomy_label"].value_counts().to_dict()
    source_count = int(scraped["source_site"].nunique())
    lines = [
        "# Submission Notes",
        "",
        "## Project Status",
        "",
        "This repository now contains a complete non-OpenAI, non-Blender workflow for the child-space interaction design study.",
        "",
        "## Completed Parts",
        "",
        f"- Web scraping: {len(scraped)} public datasets from {source_count} websites",
        "- Dataset vectorisation: CLIP keyframe vectors plus CountVectorizer and TF-IDF comparison",
        "- Visualising / plotting: taxonomy distribution, timeline, PCA plots, and similarity heatmaps",
        "- Machine learning integration: 147 structured interaction records built from the existing YOLO + SAM + CLIP outputs",
        "- API substitute: mock design-rule response that simulates downstream analytical generation",
        "- Software integration substitute: front-end fragment renderer with 24 fragments",
        "- Blender bridge: Blender-ready JSON / CSV package plus Blender Python import script",
        "",
        "## Evidence Summary",
        "",
        f"- ML interaction records: {len(ml)}",
        f"- Taxonomy counts: {taxonomy_counts}",
        f"- Scraped datasets: {scraped['dataset_name'].tolist()}",
        f"- Vector methods: {vector_summary['method'].tolist()}",
        f"- Fragment count in front-end scene: {scene['fragment_count']}",
        "",
        "## Mock API Design Families",
        "",
    ]

    for item in rules["responses"]:
        lines.extend(
            [
                f"### {item['taxonomy_label']}",
                "",
                f"- Family: {item['fragment_family']}",
                f"- Geometry rule: {item['geometry_rule']}",
                f"- Material rule: {item['material_rule']}",
                f"- Interaction rule: {item['interaction_rule']}",
                f"- Color rule: {item['color_rule']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Deferred Items",
            "",
            "- Replace `workflow/mock_api.py` with a real OpenAI API client once API use is enabled.",
            "- Replace the browser renderer with Blender or another 3D software environment if the final submission requires a full modeling workflow.",
            "",
        ]
    )

    output_path = ROOT / "SUBMISSION_NOTES.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved submission notes to {output_path}")


if __name__ == "__main__":
    main()
