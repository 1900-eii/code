from __future__ import annotations

import json
import pickle
import re
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_SCRAPED_DIR = DATA_DIR / "raw_scraped"
PROCESSED_DIR = DATA_DIR / "processed"
PLOTS_DIR = DATA_DIR / "plots"
BLENDER_DIR = ROOT / "blender"
OUTPUT_DIR = ROOT / "output"
FINAL_RESULTS_DIR = OUTPUT_DIR / "final_results"
VIDEO_INDEX_PATH = OUTPUT_DIR / "video_index.pkl"
VIDEO_PATH = ROOT / "video" / "input.mp4"

RESULT_PATTERN = re.compile(
    r"^(?P<label>.+)_(?P<frame>\d{5})_(?P<variant>A_cutout|B_source_box|C_raw_crop|D_analysis)\.(?P<ext>png|jpg)$"
)


SCRAPE_SPECS = [
    {
        "dataset_name": "london_playgrounds_osm",
        "dataset_type": "structured_geospatial",
        "source_site": "Overpass API / OpenStreetMap",
        "url": "https://overpass-api.de/api/interpreter",
        "topic": "mapped playground locations across Greater London",
        "place_name": "London",
        "query": '[out:json][timeout:25];area["name"="London"]->.a;(node["leisure"="playground"](area.a);way["leisure"="playground"](area.a);relation["leisure"="playground"](area.a););out center 250;',
    },
    {
        "dataset_name": "camden_playgrounds_osm",
        "dataset_type": "structured_geospatial",
        "source_site": "Overpass API / OpenStreetMap",
        "url": "https://overpass-api.de/api/interpreter",
        "topic": "mapped playground locations in the London Borough of Camden",
        "place_name": "Camden",
        "query": '[out:json][timeout:25];area["name"="Camden"]->.a;(node["leisure"="playground"](area.a);way["leisure"="playground"](area.a);relation["leisure"="playground"](area.a););out center 180;',
    },
    {
        "dataset_name": "islington_playgrounds_osm",
        "dataset_type": "structured_geospatial",
        "source_site": "Overpass API / OpenStreetMap",
        "url": "https://overpass-api.de/api/interpreter",
        "topic": "mapped playground locations in the London Borough of Islington",
        "place_name": "Islington",
        "query": '[out:json][timeout:25];area["name"="Islington"]->.a;(node["leisure"="playground"](area.a);way["leisure"="playground"](area.a);relation["leisure"="playground"](area.a););out center 120;',
    },
    {
        "dataset_name": "playscapes_global_map",
        "dataset_type": "text_reference",
        "source_site": "Spacescape",
        "url": "https://www.spacescape.se/try-playscapes-a-new-global-playground-map/",
        "topic": "global playground access and urban playability overview",
    },
]


def ensure_directories() -> None:
    for path in (DATA_DIR, RAW_SCRAPED_DIR, PROCESSED_DIR, PLOTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_pickle(path: Path) -> object:
    with path.open("rb") as handle:
        return pickle.load(handle)


def iter_text_chunks(lines: Iterable[str]) -> list[str]:
    cleaned = []
    seen = set()
    for raw_line in lines:
        line = " ".join(raw_line.split())
        if len(line) < 40:
            continue
        words = line.split()
        if len(words) < 8 and not any(punct in line for punct in ".:;!?"):
            continue
        if line in seen:
            continue
        seen.add(line)
        cleaned.append(line)
    return cleaned
