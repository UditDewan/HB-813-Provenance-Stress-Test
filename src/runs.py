"""The evidence file. Every experiment, local or platform, appends one row here.

Nothing hand-edits this CSV. If a row is wrong, rerun the experiment.
"""

from __future__ import annotations

import csv
import uuid
from datetime import datetime, timezone
from pathlib import Path

RUNS_CSV = Path("data/results/runs.csv")

COLUMNS = [
    "run_id",
    "timestamp",
    "method",           # local | platform
    "platform",         # empty for local runs
    "source_file",
    "source_sha256",
    "source_class",
    "source_state",     # the source's own c2pa_state, so survival is conditional
    "transform_chain",  # "|"-joined transform names, or "none" for a baseline row
    "transform_label",  # plain language, for the memo
    "result_sha256",
    "bytes",
    "width",
    "height",
    "c2pa_state",
    "remote_manifest_ref",
    "exif_present",
    "xmp_present",
    "notes",
]


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append(row: dict) -> None:
    unknown = set(row) - set(COLUMNS)
    if unknown:
        raise ValueError(f"unknown columns: {sorted(unknown)}")
    RUNS_CSV.parent.mkdir(parents=True, exist_ok=True)
    fresh = not RUNS_CSV.exists()
    with RUNS_CSV.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, COLUMNS)
        if fresh:
            writer.writeheader()
        writer.writerow({c: row.get(c, "") for c in COLUMNS})
