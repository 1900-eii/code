from __future__ import annotations

import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from workflow.common import PROCESSED_DIR, ROOT, PLOTS_DIR, write_json


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> None:
    frontend_data_dir = ROOT / "frontend" / "data"
    frontend_data_dir.mkdir(parents=True, exist_ok=True)

    ml_summary = json.loads((PROCESSED_DIR / "ml_interactions_summary.json").read_text(encoding="utf-8"))
    datasets = pd.read_csv(PROCESSED_DIR / "scraped_datasets.csv")
    structured_rows = pd.read_csv(PROCESSED_DIR / "scraped_structured_rows.csv")
    methods = pd.read_csv(PROCESSED_DIR / "vector_method_summary.csv")
    top_terms = pd.read_csv(PROCESSED_DIR / "text_top_terms.csv")
    mock_rules = json.loads((PROCESSED_DIR / "mock_api_design_rules.json").read_text(encoding="utf-8"))
    scene = json.loads((ROOT / "frontend" / "data" / "scene.json").read_text(encoding="utf-8"))

    datasets_payload = []
    for row in datasets.itertuples(index=False):
        terms = top_terms[top_terms["dataset_name"] == row.dataset_name].head(2)
        datasets_payload.append(
            {
                "dataset_name": row.dataset_name,
                "dataset_type": row.dataset_type,
                "source_site": row.source_site,
                "title": row.title,
                "topic": row.topic,
                "row_count": int(row.row_count),
                "paragraph_count": int(row.paragraph_count),
                "summary_text": row.summary_text,
                "top_terms": terms["top_terms"].tolist(),
            }
        )

    plot_cards = [
        {
            "title": "Interaction Taxonomy Distribution",
            "description": "How often each interaction-related space type appears in the final ML evidence.",
            "path": rel(PLOTS_DIR / "taxonomy_distribution.png"),
        },
        {
            "title": "Interaction Timeline",
            "description": "When interaction evidence appears across the source video.",
            "path": rel(PLOTS_DIR / "interaction_timeline.png"),
        },
        {
            "title": "Engineered Feature PCA",
            "description": "Dimensionality reduction over crop metrics, color, coverage, and taxonomy indicators.",
            "path": rel(PLOTS_DIR / "engineered_pca.png"),
        },
        {
            "title": "CLIP Feature PCA",
            "description": "Projection of nearest-keyframe CLIP embeddings linked to each interaction.",
            "path": rel(PLOTS_DIR / "clip_pca.png"),
        },
        {
            "title": "Structured Scraped Row Counts",
            "description": "How many structured playground records were scraped per geospatial dataset.",
            "path": rel(PLOTS_DIR / "scraped_row_counts.png"),
        },
        {
            "title": "TF-IDF Dataset Projection",
            "description": "Semantic relationship between scraped reference datasets after text vectorisation.",
            "path": rel(PLOTS_DIR / "tfidf_projection.png"),
        },
        {
            "title": "Count Similarity Heatmap",
            "description": "Term-frequency similarity across datasets.",
            "path": rel(PLOTS_DIR / "count_similarity_heatmap.png"),
        },
        {
            "title": "TF-IDF Similarity Heatmap",
            "description": "Keyword-weighted similarity across datasets.",
            "path": rel(PLOTS_DIR / "tfidf_similarity_heatmap.png"),
        },
    ]

    architecture_steps = [
        {
            "stage": "01",
            "title": "Video Observation",
            "body": "A real-world video is sampled into frames and keyframes to make human behavior searchable.",
        },
        {
            "stage": "02",
            "title": "ML Interaction Extraction",
            "body": "YOLO detects children and space elements, SAM segments them, and CLIP filters for meaningful interaction scenes.",
        },
        {
            "stage": "03",
            "title": "Reference Data Scraping",
            "body": "Public playground and spatial-access datasets are collected from OpenStreetMap and reference articles.",
        },
        {
            "stage": "04",
            "title": "Vectorisation + Comparison",
            "body": "Image evidence keeps CLIP vectors while scraped text and dataset summaries are vectorised with CountVectorizer and TF-IDF.",
        },
        {
            "stage": "05",
            "title": "Design Rule Synthesis",
            "body": "The mock API layer converts evidence into taxonomy-specific geometry, material, interaction, and color rules.",
        },
        {
            "stage": "06",
            "title": "Fragment Rendering + Export",
            "body": "The system renders fragment families, then exports Blender-ready JSON and CSV packages for downstream modeling.",
        },
    ]

    payload = {
        "project": {
            "title": "Child-Space Interaction Analysis and Design Translation Workflow",
            "subtitle": "A full-stack research prototype combining scraping, ML, vectorisation, visualization, mock rule generation, front-end rendering, and Blender export.",
            "status": "Delivery Demo Build",
        },
        "highlights": {
            "ml_records": int(ml_summary["record_count"]),
            "scraped_datasets": int(len(datasets)),
            "structured_rows": int(len(structured_rows)),
            "fragment_count": int(scene["fragment_count"]),
            "vector_methods": methods["method"].tolist(),
        },
        "taxonomy_counts": ml_summary["taxonomy_counts"],
        "datasets": datasets_payload,
        "architecture_steps": architecture_steps,
        "plot_cards": plot_cards,
        "mock_rules": mock_rules["responses"],
        "deliverables": [
            {"label": "ML interaction table", "path": rel(PROCESSED_DIR / "ml_interactions.csv")},
            {"label": "Scraped structured rows", "path": rel(PROCESSED_DIR / "scraped_structured_rows.csv")},
            {"label": "Mock API design rules", "path": rel(PROCESSED_DIR / "mock_api_design_rules.json")},
            {"label": "Blender-ready JSON", "path": rel(PROCESSED_DIR / "blender_ready_fragments.json")},
            {"label": "Submission notes", "path": rel(ROOT / "SUBMISSION_NOTES.md")},
        ],
    }
    write_json(frontend_data_dir / "dashboard.json", payload)
    print(f"Saved dashboard payload to {frontend_data_dir / 'dashboard.json'}")


if __name__ == "__main__":
    main()
