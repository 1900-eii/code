from __future__ import annotations

from pathlib import Path
import sys
import json
import time

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import requests
from bs4 import BeautifulSoup

from workflow.common import PROCESSED_DIR, RAW_SCRAPED_DIR, SCRAPE_SPECS, ensure_directories, iter_text_chunks, write_json


def extract_text(html: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else "untitled"
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    candidates = []
    for node in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = node.get_text(" ", strip=True)
        candidates.append(text)
    return title, iter_text_chunks(candidates)


def fetch_overpass(session: requests.Session, query: str, cache_path: Path) -> dict:
    for attempt in range(4):
        response = session.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query},
            timeout=90,
        )
        if response.status_code == 200:
            payload = response.json()
            write_json(cache_path, payload)
            return payload
        if response.status_code in {429, 504} and attempt < 3:
            time.sleep(3 + attempt * 3)
            continue
        break
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    response.raise_for_status()


def normalize_osm_element(dataset_name: str, source_site: str, topic: str, place_name: str, element: dict) -> dict:
    tags = element.get("tags", {})
    center = {
        "lat": element.get("lat", element.get("center", {}).get("lat")),
        "lon": element.get("lon", element.get("center", {}).get("lon")),
    }
    return {
        "dataset_name": dataset_name,
        "source_site": source_site,
        "topic": topic,
        "place_name": place_name,
        "osm_type": element.get("type"),
        "osm_id": element.get("id"),
        "name": tags.get("name", ""),
        "access": tags.get("access", ""),
        "operator": tags.get("operator", ""),
        "surface": tags.get("surface", ""),
        "playground_type": tags.get("playground", ""),
        "lat": center["lat"],
        "lon": center["lon"],
        "tag_count": len(tags),
        "tags_json": json.dumps(tags, ensure_ascii=False, sort_keys=True),
    }


def summarize_osm_rows(spec: dict, rows: list[dict]) -> str:
    frame = pd.DataFrame(rows)
    named_count = int(frame["name"].astype(bool).sum()) if not frame.empty else 0
    access_counts = frame["access"].replace("", "unspecified").value_counts().head(4).to_dict() if not frame.empty else {}
    surface_counts = frame["surface"].replace("", "unspecified").value_counts().head(4).to_dict() if not frame.empty else {}
    return (
        f"{spec['place_name']} playground dataset extracted from OpenStreetMap with {len(rows)} mapped playground elements. "
        f"{named_count} records include a name tag. "
        f"Most common access tags: {access_counts}. "
        f"Most common surface tags: {surface_counts}. "
        f"These records describe public play locations, tags, and approximate coordinates that can be compared with the video-based interaction evidence."
    )


def main() -> None:
    ensure_directories()
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (compatible; workshop2-scraper/1.0)",
        }
    )

    paragraph_rows = []
    dataset_rows = []
    structured_rows = []
    for spec in SCRAPE_SPECS:
        slug = spec["dataset_name"]
        dataset_type = spec["dataset_type"]
        if dataset_type == "structured_geospatial":
            json_path = RAW_SCRAPED_DIR / f"{slug}.json"
            payload = fetch_overpass(session, spec["query"], json_path)
            rows = [
                normalize_osm_element(
                    dataset_name=slug,
                    source_site=spec["source_site"],
                    topic=spec["topic"],
                    place_name=spec["place_name"],
                    element=element,
                )
                for element in payload.get("elements", [])
            ]
            structured_rows.extend(rows)
            summary_text = summarize_osm_rows(spec, rows)
            dataset_rows.append(
                {
                    "dataset_name": slug,
                    "dataset_type": dataset_type,
                    "source_site": spec["source_site"],
                    "url": spec["url"],
                    "topic": spec["topic"],
                    "title": f"{spec['place_name']} playgrounds from OpenStreetMap",
                    "row_count": len(rows),
                    "paragraph_count": 1,
                    "summary_text": summary_text,
                    "full_text": summary_text,
                }
            )
            paragraph_rows.append(
                {
                    "dataset_name": slug,
                    "dataset_type": dataset_type,
                    "source_site": spec["source_site"],
                    "url": spec["url"],
                    "paragraph_id": 1,
                    "text": summary_text,
                }
            )
        else:
            response = session.get(spec["url"], timeout=30)
            response.raise_for_status()
            title, paragraphs = extract_text(response.text)
            html_path = RAW_SCRAPED_DIR / f"{slug}.html"
            html_path.write_text(response.text, encoding="utf-8")

            dataset_rows.append(
                {
                    "dataset_name": slug,
                    "dataset_type": dataset_type,
                    "source_site": spec["source_site"],
                    "url": spec["url"],
                    "topic": spec["topic"],
                    "title": title,
                    "row_count": len(paragraphs),
                    "paragraph_count": len(paragraphs),
                    "summary_text": "\n".join(paragraphs[:3]) if paragraphs else f"{title}. {spec['topic']}",
                    "full_text": "\n".join(paragraphs) if paragraphs else f"{title}. {spec['topic']}",
                }
            )
            for idx, paragraph in enumerate(paragraphs, start=1):
                paragraph_rows.append(
                    {
                        "dataset_name": slug,
                        "dataset_type": dataset_type,
                        "source_site": spec["source_site"],
                        "url": spec["url"],
                        "paragraph_id": idx,
                        "text": paragraph,
                    }
                )

    datasets_df = pd.DataFrame(dataset_rows)
    paragraphs_df = pd.DataFrame(paragraph_rows)
    structured_df = pd.DataFrame(structured_rows)

    datasets_df.to_csv(PROCESSED_DIR / "scraped_datasets.csv", index=False)
    paragraphs_df.to_csv(PROCESSED_DIR / "scraped_paragraphs.csv", index=False)
    structured_df.to_csv(PROCESSED_DIR / "scraped_structured_rows.csv", index=False)
    write_json(
        PROCESSED_DIR / "scraped_datasets_manifest.json",
        {
            "dataset_count": int(len(datasets_df)),
            "sources": datasets_df[["dataset_name", "dataset_type", "source_site", "url", "row_count", "paragraph_count"]].to_dict(orient="records"),
        },
    )
    print(
        f"Scraped {len(datasets_df)} datasets, {len(paragraphs_df)} text segments, "
        f"and {len(structured_df)} structured rows"
    )


if __name__ == "__main__":
    main()
