from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "workflow.scrape_datasets",
    "workflow.build_analysis_dataset",
    "workflow.vectorize_and_plot",
    "workflow.blender_placeholder",
    "workflow.mock_api",
    "workflow.export_frontend_scene",
    "workflow.export_blender_package",
    "workflow.export_dashboard_data",
    "workflow.generate_submission_notes",
]


def main() -> None:
    for module in MODULES:
        print(f"Running {module} ...")
        subprocess.run([sys.executable, "-m", module], check=True, cwd=ROOT)
    print("Workflow finished.")


if __name__ == "__main__":
    main()
