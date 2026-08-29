"""Log a manual platform round-trip.

A human uploads an image to a platform, saves the copy the platform serves
back, and this CLI does the measuring. Nothing here talks to a platform:
automating uploads would violate their terms of service, and the point of the
study is what happens to an ordinary person's image, not what happens to a bot's.

    python -m src.roundtrip start --platform instagram --image C.jpg
    ... human uploads, then saves the returned image into inbox/ ...
    python -m src.roundtrip finish --run-id 3f9a1c --file inbox/download.jpg

start records the intent; finish hashes what came back, runs detection, and
appends the row. See docs/PLATFORM-PROTOCOL.md for the exact steps to follow so
two people testing the same platform produce comparable rows.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src import corpus, runs
from src.detect import describe

PENDING = Path("data/results/pending")


def start(platform: str, image: str) -> None:
    entries = corpus.load()
    if image not in entries:
        raise SystemExit(f"{image} is not in the corpus manifest; run: python -m src.corpus scan")
    source = corpus.CORPUS / image
    base = describe(source)
    run_id = runs.new_id()
    PENDING.mkdir(parents=True, exist_ok=True)
    (PENDING / f"{run_id}.json").write_text(json.dumps({
        "run_id": run_id,
        "timestamp": runs.now(),
        "method": "platform",
        "platform": platform,
        "source_file": image,
        "source_sha256": base["sha256"],
        "source_class": entries[image]["class"],
        "source_state": base["c2pa_state"],
        "source_size": [base["width"], base["height"]],
        "source_bytes": base["bytes"],
    }, indent=2), encoding="utf-8")
    print(f"run_id {run_id}")
    print(f"upload {source} to {platform}, then save what it serves back and run:")
    print(f"  python -m src.roundtrip finish --run-id {run_id} --file inbox/<downloaded>")


def finish(run_id: str, file: str, notes: str = "") -> None:
    pending = PENDING / f"{run_id}.json"
    if not pending.exists():
        raise SystemExit(f"no pending run {run_id}; see: python -m src.roundtrip list")
    intent = json.loads(pending.read_text(encoding="utf-8"))
    result = describe(file)

    observed = []
    if result["sha256"] == intent["source_sha256"]:
        observed.append("bytes identical, platform did not re-encode")
    else:
        observed.append("re-encoded")
    if [result["width"], result["height"]] != intent["source_size"]:
        observed.append(f"resized {intent['source_size'][0]}x{intent['source_size'][1]}"
                        f" -> {result['width']}x{result['height']}")

    runs.append({
        "run_id": run_id,
        "timestamp": runs.now(),
        "method": "platform",
        "platform": intent["platform"],
        "source_file": intent["source_file"],
        "source_sha256": intent["source_sha256"],
        "source_class": intent["source_class"],
        "source_state": intent["source_state"],
        "transform_chain": f"platform:{intent['platform']}",
        "transform_label": f"Uploaded to {intent['platform']} and saved back",
        "result_sha256": result["sha256"],
        "bytes": result["bytes"],
        "width": result["width"],
        "height": result["height"],
        "c2pa_state": result["c2pa_state"],
        "remote_manifest_ref": result["remote_manifest_ref"],
        "exif_present": result["exif_present"],
        "xmp_present": result["xmp_present"],
        "notes": "; ".join(observed + ([notes] if notes else [])),
    })
    pending.unlink()
    print(f"{intent['platform']}: {result['c2pa_state']} ({'; '.join(observed)})")


def show_pending() -> None:
    for path in sorted(PENDING.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        print(f"{d['run_id']}  {d['platform']:<12} {d['source_file']}  started {d['timestamp']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("start")
    s.add_argument("--platform", required=True)
    s.add_argument("--image", required=True, help="filename as listed in the corpus manifest")
    f = sub.add_parser("finish")
    f.add_argument("--run-id", required=True)
    f.add_argument("--file", required=True, help="the image the platform served back")
    f.add_argument("--notes", default="", help="anything the numbers do not capture")
    sub.add_parser("list")

    a = ap.parse_args()
    if a.command == "start":
        start(a.platform, a.image)
    elif a.command == "finish":
        finish(a.run_id, a.file, a.notes)
    else:
        show_pending()
