#!/usr/bin/env python3
"""Report metadata completeness for the local saved JSON repositories."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CONF_PATH = REPO_ROOT / "conf.json"

MEDIA_LABELS = {
    "movies": "Movies",
    "series": "Series",
    "standup": "Standup",
}

REQUIRED_FIELDS = [
    "title",
    "year",
    "description",
    "genre",
    "languages",
    "rating",
    "votes",
    "running_time",
    "image_url",
    "url",
]

LIST_FIELDS = [
    "genre",
    "languages",
]


def load_config() -> dict:
    with CONF_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_saved_data(saved_data_path: str) -> dict:
    path = (REPO_ROOT / saved_data_path).resolve()
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def is_missing(value) -> bool:
    if value is None:
      return True
    if isinstance(value, str):
      return value.strip() == ""
    if isinstance(value, list):
      return len([item for item in value if str(item).strip() != ""]) == 0
    return False


def analyze_media_type(media_key: str, payload: dict) -> list[str]:
    saved_data_path = payload["saved_data"]
    items = load_saved_data(saved_data_path)

    total_items = len(items)
    missing_counts = Counter()
    malformed_list_counts = Counter()
    missing_titles_by_field: dict[str, list[str]] = {field: [] for field in REQUIRED_FIELDS}
    unique_genres = set()
    unique_languages = set()

    for title_key, item in items.items():
        title = item.get("title") or title_key

        for field in REQUIRED_FIELDS:
            value = item.get(field)
            if is_missing(value):
                missing_counts[field] += 1
                missing_titles_by_field[field].append(title)

        for field in LIST_FIELDS:
            value = item.get(field)
            if value is None:
                continue

            if not isinstance(value, list):
                malformed_list_counts[field] += 1
                continue

            cleaned = [str(entry).strip() for entry in value if str(entry).strip()]
            if field == "genre":
                unique_genres.update(cleaned)
            elif field == "languages":
                unique_languages.update(cleaned)

    lines: list[str] = []
    lines.append(f"{MEDIA_LABELS.get(media_key, media_key)}")
    lines.append(f"  Saved data: {saved_data_path}")
    lines.append(f"  Titles: {total_items}")
    lines.append(f"  Unique genres: {len(unique_genres)}")
    lines.append(f"  Unique languages: {len(unique_languages)}")

    if malformed_list_counts:
        lines.append("  Malformed list fields:")
        for field, count in sorted(malformed_list_counts.items()):
            lines.append(f"    - {field}: {count}")

    lines.append("  Missing fields:")
    for field in REQUIRED_FIELDS:
        count = missing_counts[field]
        if count == 0:
            continue
        lines.append(f"    - {field}: {count}")

    if all(missing_counts[field] == 0 for field in REQUIRED_FIELDS) and not malformed_list_counts:
        lines.append("    - none")

    lines.append("  Sample missing titles:")
    samples_added = False
    for field in REQUIRED_FIELDS:
        titles = missing_titles_by_field[field][:10]
        if not titles:
            continue
        samples_added = True
        sample_text = "; ".join(titles)
        lines.append(f"    - {field}: {sample_text}")

    if not samples_added:
        lines.append("    - none")

    return lines


def main() -> int:
    config = load_config()
    assets = config.get("assets", {})

    print("Metadata Completeness Report")
    print(f"Repository: {REPO_ROOT}")
    print("")

    for media_key in ["movies", "series", "standup"]:
        payload = assets.get(media_key)
        if not payload:
            continue

        for line in analyze_media_type(media_key, payload):
            print(line)
        print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
