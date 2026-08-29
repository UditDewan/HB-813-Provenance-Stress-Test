"""Run every local transform against every corpus image and record the outcome.

    python -m src.sweep

Writes derived files to data/derived/ (gitignored) and one row per experiment to
data/results/runs.csv. Re-running is safe: it appends, so the CSV is a log of
every run ever done, and report.py takes the latest row per experiment.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src import corpus, runs
from src.detect import describe
from src.transforms import CHAINS, TRANSFORMS, apply_chain, label

DERIVED = Path("data/derived")


def sweep(keep_files: bool = False) -> int:
    entries = corpus.load()
    if not entries:
        raise SystemExit("corpus is empty -- run: python -m src.corpus fetch")
    DERIVED.mkdir(parents=True, exist_ok=True)

    experiments = [(name,) for name in TRANSFORMS] + [tuple(c) for c in CHAINS]
    written = 0

    for name, entry in sorted(entries.items()):
        source = corpus.CORPUS / name
        base = describe(source)
        common = {
            "method": "local",
            "source_file": name,
            "source_sha256": base["sha256"],
            "source_class": entry["class"],
            "source_state": base["c2pa_state"],
        }
        # A baseline row, so survival is always measured against what the source
        # actually carried rather than against an assumption.
        runs.append({
            **common, "run_id": runs.new_id(), "timestamp": runs.now(),
            "transform_chain": "none", "transform_label": "Untouched original",
            "result_sha256": base["sha256"], **_result(base),
        })
        written += 1

        data = source.read_bytes()
        for chain in experiments:
            out = apply_chain(data, chain)
            chain_id = "|".join(chain)
            out_path = DERIVED / f"{base['sha256'][:12]}__{chain_id.replace('|', '__')}{_ext(out)}"
            out_path.write_bytes(out)
            result = describe(out_path)
            runs.append({
                **common, "run_id": runs.new_id(), "timestamp": runs.now(),
                "transform_chain": chain_id, "transform_label": label(chain),
                "result_sha256": result["sha256"], **_result(result),
            })
            written += 1
            if not keep_files:
                out_path.unlink()

    print(f"{written} rows -> {runs.RUNS_CSV}")
    return written


def _result(d: dict) -> dict:
    return {k: d[k] for k in ("bytes", "width", "height", "c2pa_state",
                              "remote_manifest_ref", "exif_present", "xmp_present")}


def _ext(data: bytes) -> str:
    return ".png" if data[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--keep-files", action="store_true",
                    help="leave the transformed images in data/derived/ for inspection")
    sweep(ap.parse_args().keep_files)
