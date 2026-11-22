#!/usr/bin/env python3
"""Export missing metadata to CSV and apply overrides back into saved JSON."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CONF_PATH = REPO_ROOT / "conf.json"

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

LIST_FIELDS = {"genre", "languages"}


def load_config() -> dict:
    with CONF_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_saved_data_paths() -> dict[str, Path]:
    config = load_config()
    assets = config.get("assets", {})
    return {
        media_key: (REPO_ROOT / payload["saved_data"]).resolve()
        for media_key, payload in assets.items()
        if "saved_data" in payload
    }


def load_saved_data(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_saved_data(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4, ensure_ascii=False)


def is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len([item for item in value if str(item).strip() != ""]) == 0
    return False


def stringify_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " | ".join(str(item).strip() for item in value if str(item).strip())
    return str(value)


def parse_override_value(field: str, raw_value: str):
    if field in LIST_FIELDS:
        if raw_value.strip() == "":
            return []

        if "|" in raw_value:
            parts = raw_value.split("|")
        elif ";" in raw_value:
            parts = raw_value.split(";")
        else:
            parts = raw_value.split(",")

        return [part.strip() for part in parts if part.strip()]

    return raw_value.strip()


def export_missing(output_path: Path) -> int:
    saved_data_paths = get_saved_data_paths()
    rows: list[dict[str, str]] = []

    for media_type, path in saved_data_paths.items():
        items = load_saved_data(path)
        for title_key, item in items.items():
            title = item.get("title") or title_key
            for field in REQUIRED_FIELDS:
                current_value = item.get(field)
                if not is_missing(current_value):
                    continue

                rows.append(
                    {
                        "media_type": media_type,
                        "title_key": title_key,
                        "title": title,
                        "field": field,
                        "field_type": "list" if field in LIST_FIELDS else "scalar",
                        "current_value": stringify_value(current_value),
                        "override_value": "",
                        "notes": "For list fields, separate multiple values with ' | '.",
                    }
                )

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "media_type",
                "title_key",
                "title",
                "field",
                "field_type",
                "current_value",
                "override_value",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} missing-metadata rows to {output_path}")
    return 0


def apply_overrides(csv_path: Path, write: bool) -> int:
    saved_data_paths = get_saved_data_paths()
    saved_data_cache = {
        media_type: load_saved_data(path)
        for media_type, path in saved_data_paths.items()
    }

    updated_rows = 0
    skipped_rows = 0

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            override_value = (row.get("override_value") or "").strip()
            if override_value == "":
                skipped_rows += 1
                continue

            media_type = row["media_type"]
            title_key = row["title_key"]
            field = row["field"]

            items = saved_data_cache.get(media_type)
            if items is None or title_key not in items:
                print(f"Skipping missing item: media_type={media_type} title_key={title_key}")
                skipped_rows += 1
                continue

            items[title_key][field] = parse_override_value(field, override_value)
            updated_rows += 1

    if write:
        for media_type, payload in saved_data_cache.items():
            write_saved_data(saved_data_paths[media_type], payload)
        print(f"Applied {updated_rows} override rows and wrote JSON updates.")
    else:
        print(f"Dry run: would apply {updated_rows} override rows.")

    print(f"Skipped {skipped_rows} CSV rows without usable overrides.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export missing metadata to CSV and apply local overrides."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export-missing", help="Write missing metadata rows to CSV.")
    export_parser.add_argument(
        "output_csv",
        nargs="?",
        default=str(REPO_ROOT / "scripts" / "metadata_missing_overrides.csv"),
        help="Output CSV path.",
    )

    apply_parser = subparsers.add_parser("apply", help="Apply override values from a CSV file.")
    apply_parser.add_argument(
        "input_csv",
        nargs="?",
        default=str(REPO_ROOT / "scripts" / "metadata_missing_overrides.csv"),
        help="Input CSV path.",
    )
    apply_parser.add_argument(
        "--write",
        action="store_true",
        help="Persist the overrides back into the saved JSON files. Without this flag, apply runs as a dry run.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "export-missing":
        return export_missing(Path(args.output_csv).resolve())

    if args.command == "apply":
        return apply_overrides(Path(args.input_csv).resolve(), args.write)

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
