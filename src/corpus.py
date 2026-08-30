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
    "sdk_test_fixture",     # the reference library's own fixtures -- see below
]

# The seed corpus is the C2PA reference library's test fixtures. They are the
# only signed assets that can be fetched from a URL, and they are the reason
# this study has an n at all before the hand-collected corpus exists.
#
# Be honest about what they are. They cover a wide range of *manifest*
# structures -- single claim, nested ingredients, remote URI, box hash, OCSP
# response, CAWG identity data -- over a narrow range of *images*: several are
# the same photograph at two sizes. So the seed measures whether manifest
# structure changes the answer (it does not) and cannot measure whether image
# content does. That is what the 40-60 image hand-collected corpus is for:
# Firefly exports, Leica samples, local generation, the team's own photos.
# None of those can be downloaded, which is why they are not here.
SEED = {
    # Signed, valid manifest -- the survival denominator.
    "C.jpg": "one signed claim, no ingredients",
    "CA.jpg": "signed claim over one signed ingredient",
    "CA_ct.jpg": "as CA.jpg, with a trusted timestamp",
    "CACA.jpg": "two levels of signed ingredients",
    "CACAE-uri-CA.jpg": "nested ingredients, one referenced by URI",
    "CIE-sig-CA.jpg": "signed claim with an embedded ingredient",
    "C_with_CAWG_data.jpg": "carries CAWG identity assertions",
    "boxhash.jpg": "box hash rather than a data hash",
    "legacy_ingredient_hash.jpg": "older ingredient hash form",
    "ocsp.jpg": "signature carries a stapled OCSP response",
    "update_manifest.jpg": "update manifest over a prior claim",
    # Manifest present, does not verify -- the middle outcome, at the source.
    "XCA.jpg": "signature does not match the claim",
    "E-sig-CA.jpg": "expired or otherwise invalid signature",
    "adobe-20220124-E-clm-CAICAI.jpg": "long ingredient chain, claim fails",
    "no_alg.jpg": "unknown hash algorithm -- verifier refuses to check it",
    "prerelease.jpg": "pre-release spec manifest -- verifier refuses to check it",
    # Provenance is only a URL to a vendor's server; nothing embedded.
    "cloud.jpg": "remote manifest reference, JPEG",
    "libpng-test_with_url.png": "remote manifest reference, PNG",
    # No provenance at all -- controls, and the EXIF/XMP comparison arm.
    "IMG_0003.jpg": "unsigned, carries EXIF and XMP",
    "P1000827.jpg": "unsigned camera original, EXIF and XMP",
    "no_manifest.jpg": "unsigned, large, EXIF and XMP",
    "earth_apollo17.jpg": "unsigned, EXIF and XMP",
    "sample1.png": "unsigned PNG carrying EXIF",
    "sample1.webp": "unsigned WEBP",
    "test_xmp.webp": "unsigned WEBP carrying EXIF and XMP",
    "mars.webp": "unsigned WEBP, no metadata",
    "libpng-test.png": "unsigned PNG, no metadata",
}
SEED_CLASS = "sdk_test_fixture"
SEED_BASE = "https://raw.githubusercontent.com/contentauth/c2pa-rs/main/sdk/tests/fixtures"
SEED_LICENSE = "MIT OR Apache-2.0 (contentauth/c2pa-rs test fixtures)"


def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}


def save(entries: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch() -> None:
    CORPUS.mkdir(parents=True, exist_ok=True)
    entries = load()
    for name, note in SEED.items():
        path = CORPUS / name
        if not path.exists():
            urllib.request.urlretrieve(f"{SEED_BASE}/{name}", path)
            print(f"downloaded {name}")
        entries[name] = {
            "sha256": sha256(path),
            "class": SEED_CLASS,
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
