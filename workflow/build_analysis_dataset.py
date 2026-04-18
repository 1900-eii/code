from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
import pandas as pd
from PIL import Image

from workflow.common import (
    FINAL_RESULTS_DIR,
    PROCESSED_DIR,
    RESULT_PATTERN,
    VIDEO_INDEX_PATH,
    VIDEO_PATH,
    ensure_directories,
    read_pickle,
    write_json,
)


@dataclass
class ResultSet:
    label: str
    frame_idx: int
    cutout_path: Path
    source_box_path: Path
    raw_crop_path: Path
    analysis_path: Path


def load_video_fps() -> float:
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if not fps:
        raise RuntimeError(f"Unable to read FPS from {VIDEO_PATH}")
    return fps


def collect_result_sets() -> list[ResultSet]:
    grouped: dict[tuple[str, int], dict[str, Path]] = {}
    for path in sorted(FINAL_RESULTS_DIR.iterdir()):
        match = RESULT_PATTERN.match(path.name)
        if not match:
            continue
        label = match.group("label")
        frame_idx = int(match.group("frame"))
        variant = match.group("variant")
        grouped.setdefault((label, frame_idx), {})[variant] = path

    result_sets = []
    for (label, frame_idx), variants in grouped.items():
        expected = {"A_cutout", "B_source_box", "C_raw_crop", "D_analysis"}
        if set(variants) != expected:
            continue
        result_sets.append(
            ResultSet(
                label=label,
                frame_idx=frame_idx,
                cutout_path=variants["A_cutout"],
                source_box_path=variants["B_source_box"],
                raw_crop_path=variants["C_raw_crop"],
                analysis_path=variants["D_analysis"],
            )
        )
    return sorted(result_sets, key=lambda item: item.frame_idx)


def image_metrics(result: ResultSet) -> dict[str, float]:
    cutout = np.array(Image.open(result.cutout_path).convert("RGBA"))
    raw = np.array(Image.open(result.raw_crop_path).convert("RGB"))
    analysis = np.array(Image.open(result.analysis_path).convert("RGB"))

    alpha = cutout[..., 3] > 0
    coverage = float(alpha.mean())
    raw_mean_rgb = raw.mean(axis=(0, 1))
    analysis_std_rgb = analysis.std(axis=(0, 1))
    aspect_ratio = raw.shape[1] / max(raw.shape[0], 1)

    return {
        "crop_width": int(raw.shape[1]),
        "crop_height": int(raw.shape[0]),
        "aspect_ratio": aspect_ratio,
        "alpha_coverage_ratio": coverage,
        "raw_mean_r": float(raw_mean_rgb[0]),
        "raw_mean_g": float(raw_mean_rgb[1]),
        "raw_mean_b": float(raw_mean_rgb[2]),
        "raw_brightness": float(raw.mean()),
        "analysis_std_r": float(analysis_std_rgb[0]),
        "analysis_std_g": float(analysis_std_rgb[1]),
        "analysis_std_b": float(analysis_std_rgb[2]),
    }


def closest_clip_feature(timestamp: float, metadata: list[dict], features: np.ndarray) -> tuple[int, np.ndarray, float]:
    timestamps = np.array([row["timestamp"] for row in metadata], dtype=float)
    idx = int(np.argmin(np.abs(timestamps - timestamp)))
    distance = float(abs(timestamps[idx] - timestamp))
    return idx, features[idx], distance


def main() -> None:
    ensure_directories()
    fps = load_video_fps()
    video_index = read_pickle(VIDEO_INDEX_PATH)
    keyframe_metadata = video_index["metadata"]
    clip_features = np.vstack([np.asarray(item).reshape(1, -1) for item in video_index["features"]])

    rows = []
    clip_rows = []
    for result in collect_result_sets():
        timestamp_sec = result.frame_idx / fps
        clip_idx, clip_vector, clip_distance = closest_clip_feature(timestamp_sec, keyframe_metadata, clip_features)
        metrics = image_metrics(result)
        rows.append(
            {
                "record_id": f"{result.label}_{result.frame_idx:05d}",
                "taxonomy_label": result.label,
                "frame_idx": result.frame_idx,
                "timestamp_sec": round(timestamp_sec, 3),
                "nearest_keyframe_idx": int(keyframe_metadata[clip_idx]["frame_idx"]),
                "nearest_keyframe_path": keyframe_metadata[clip_idx]["path"].replace("\\", "/"),
                "nearest_keyframe_time_delta_sec": round(clip_distance, 3),
                "cutout_path": str(result.cutout_path.relative_to(PROCESSED_DIR.parents[1])).replace("\\", "/"),
                "source_box_path": str(result.source_box_path.relative_to(PROCESSED_DIR.parents[1])).replace("\\", "/"),
                "raw_crop_path": str(result.raw_crop_path.relative_to(PROCESSED_DIR.parents[1])).replace("\\", "/"),
                "analysis_path": str(result.analysis_path.relative_to(PROCESSED_DIR.parents[1])).replace("\\", "/"),
                **metrics,
            }
        )
        clip_rows.append(clip_vector.astype(np.float32))

    df = pd.DataFrame(rows)
    df["duration_bucket"] = pd.cut(
        df["timestamp_sec"],
        bins=6,
        labels=[f"segment_{idx}" for idx in range(1, 7)],
        include_lowest=True,
    )
    df.sort_values(["frame_idx", "taxonomy_label"], inplace=True)
    df.to_csv(PROCESSED_DIR / "ml_interactions.csv", index=False)
    np.save(PROCESSED_DIR / "ml_clip_vectors.npy", np.vstack(clip_rows))

    summary = {
        "record_count": int(len(df)),
        "taxonomy_counts": df["taxonomy_label"].value_counts().to_dict(),
        "time_range_sec": [float(df["timestamp_sec"].min()), float(df["timestamp_sec"].max())],
        "mean_alpha_coverage_ratio": round(float(df["alpha_coverage_ratio"].mean()), 4),
        "mean_crop_area": round(float((df["crop_width"] * df["crop_height"]).mean()), 2),
        "clip_vector_dim": int(np.vstack(clip_rows).shape[1]),
    }
    write_json(PROCESSED_DIR / "ml_interactions_summary.json", summary)
    print(f"Saved {len(df)} ML interaction records to {PROCESSED_DIR / 'ml_interactions.csv'}")


if __name__ == "__main__":
    main()
