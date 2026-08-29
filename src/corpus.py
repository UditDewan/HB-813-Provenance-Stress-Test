"""Build and verify the test image set.

Images are content-addressed by SHA-256; filenames are convenience only. The
images themselves are not committed (licensing, and they are re-fetchable or
re-capturable) but data/corpus/manifest.json is, so anyone can check they are
testing the same bytes we did.

    python -m src.corpus fetch    seed the three public fixtures
    python -m src.corpus scan     hash everything present, stub out new files
    python -m src.corpus verify   re-hash and report drift
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import date
from pathlib import Path

from src.detect import sha256

CORPUS = Path("data/corpus")
MANIFEST = CORPUS / "manifest.json"

CLASSES = [
    "c2pa_signed_ai",       # Firefly and other CAI-participating generators
    "c2pa_signed_camera",   # Leica M11-P and the CAI camera test set
    "ai_unsigned",          # open-weight local generation -- the realistic case
    "human_unsigned",       # team-captured photos, negative control
    "visible_watermark",    # generator default overlays, a different failure mode
]

# Enough to prove the harness runs from a clean clone. The real 40-60 image
# corpus is collected by hand: Firefly exports, Leica samples, local generation,
# and the team's own photos. Those cannot be fetched from a URL.
SEED = {
    "C.jpg": ("c2pa_signed_camera", "signed fixture, valid embedded manifest"),
    "A.jpg": ("human_unsigned", "unsigned, carries EXIF and XMP"),
    "cloud.jpg": ("c2pa_signed_ai", "provenance is a remote URL, nothing embedded"),
}
SEED_BASE = "https://raw.githubusercontent.com/contentauth/c2pa-python/main/tests/fixtures"
SEED_LICENSE = "Apache-2.0 (contentauth/c2pa-python test fixtures)"


def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}


def save(entries: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch() -> None:
    CORPUS.mkdir(parents=True, exist_ok=True)
    entries = load()
    for name, (cls, note) in SEED.items():
        path = CORPUS / name
        if not path.exists():
            urllib.request.urlretrieve(f"{SEED_BASE}/{name}", path)
            print(f"downloaded {name}")
        entries[name] = {
            "sha256": sha256(path),
            "class": cls,
            "source": f"{SEED_BASE}/{name}",
            "license": SEED_LICENSE,
            "acquired": entries.get(name, {}).get("acquired", str(date.today())),
            "note": note,
        }
    save(entries)
    print(f"{len(entries)} images in manifest")


def scan() -> None:
    """Hash every image present. New files get a stub for a human to fill in."""
    entries = load()
    for path in sorted(CORPUS.iterdir()):
        if path.name == "manifest.json" or not path.is_file():
            continue
        entry = entries.setdefault(
            path.name,
            {"class": "UNKNOWN", "source": "", "license": "", "acquired": str(date.today()), "note": ""},
        )
        entry["sha256"] = sha256(path)
    save(entries)
    todo = [n for n, e in entries.items() if e["class"] == "UNKNOWN"]
    print(f"{len(entries)} images; {len(todo)} need a class in manifest.json: {todo}")


def verify() -> int:
    entries, bad = load(), 0
    for name, entry in sorted(entries.items()):
        path = CORPUS / name
        if not path.exists():
            print(f"MISSING  {name}")
            bad += 1
        elif sha256(path) != entry["sha256"]:
            print(f"CHANGED  {name}")
            bad += 1
        elif entry["class"] not in CLASSES:
            print(f"BAD CLASS {name}: {entry['class']}")
            bad += 1
    print(f"{len(entries) - bad}/{len(entries)} verified")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["fetch", "scan", "verify"])
    cmd = ap.parse_args().command
    if cmd == "verify":
        raise SystemExit(1 if verify() else 0)
    {"fetch": fetch, "scan": scan}[cmd]()
