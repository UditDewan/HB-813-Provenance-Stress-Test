# HB 813 Provenance Stress Test

Ohio HB 813 (Cockley, Miller) would require AI-generated products to carry a
watermark. This repository measures whether such marks survive ordinary
handling — saving, resizing, cropping, screenshotting, and passing through the
platforms Ohioans actually use.

It is a measurement study, not an advocacy project, and not a tool for removing
watermarks. Negative results are the point: a sponsor who learns her mandate is
technically weak from her own volunteers can amend it.

## Quick start

```bash
uv sync
uv run python -m src.corpus fetch    # 27 reference-library fixtures, 11 of them signed
uv run python -m src.sweep           # every local transform over every corpus image
uv run python -m src.report          # tables + figures into results/
uv run pytest
```

Or `make report`, which does all of it.

If `uv` fails with `invalid peer certificate: UnknownIssuer`, your network is
intercepting HTTPS. Set `UV_SYSTEM_CERTS=1` (or pass `--system-certs`). If it
fails with `os error 396` on a hardlink, the clone is inside a cloud-synced
folder such as OneDrive; set `UV_LINK_MODE=copy`.

Verified to reproduce from a clean clone on 2026-08-29: identical outcomes for
all 540 experiments, byte-identical `results/tables.md`.

## What gets measured

Detection is three-valued, and the middle value is the reason:

| Outcome | Meaning | Why it is its own case |
|---|---|---|
| `present_valid` | manifest present and verifies | the mark did its job |
| `present_invalid` | manifest present, does not verify | somebody vouched for this image and then something changed it — evidence exists, but not of what |
| `absent` | no manifest at all | nothing to enforce against |

A fourth situation — an image whose provenance is only a URL pointing at a
vendor's server — records as `absent` with the `remote_manifest_ref` flag set.
It carries nothing self-verifying, and it depends on that server still being up.

Every experiment appends one row to `data/results/runs.csv`. That file is the
evidence; `results/tables.md` and the figures are derived from it and nothing
else. Nothing hand-edits the CSV.

## Adding your own images

The seed corpus is the C2PA reference library's own test fixtures — 27 images,
11 of them carrying a valid manifest. They cover a wide range of *manifest
structures* over a narrow range of *photographs*, which is enough to show that
manifest structure does not change the answer and not enough to say anything
about image content.

The real corpus is 40–60 images across the five classes in `CLASSES`
(`src/corpus.py`), collected by hand: Adobe Firefly exports, CAI camera samples,
open-weight local generation, the team's own photos, and generator overlay
watermarks. None of it can be downloaded, which is why it is not here yet.
Images are not committed (licensing); `data/corpus/manifest.json` is, so anyone
can confirm they are testing the same bytes.

```bash
# drop files into data/corpus/, then:
uv run python -m src.corpus scan     # hashes them, stubs unknowns for you to classify
uv run python -m src.corpus verify   # re-hash and report drift
```

## Platform round-trips

Uploads are performed by a human, never by code — automating them would violate
platform terms of service. `src/roundtrip.py` structures the manual work and
does the measuring. Read `docs/PLATFORM-PROTOCOL.md` before starting.

```bash
uv run python -m src.roundtrip start --platform instagram --image C.jpg
# upload, save what comes back into inbox/
uv run python -m src.roundtrip finish --run-id <id> --file inbox/download.jpg
```

## Layout

| Path | What lives there |
|---|---|
| `src/` | the harness — see `CONTRIBUTING.md` for the module map |
| `data/results/runs.csv` | every experiment ever run; committed |
| `results/` | `findings-memo.md`, generated `tables.md`, `figures/` |
| `policy/state-comparison.md` | statutory comparison, read from primary sources |
| `docs/PLATFORM-PROTOCOL.md` | how to run a platform test reproducibly |
| `CONTRIBUTING.md` | project constraints; read before contributing |

## Scope

This project does not touch HB 524 (AI systems and self-harm content) in any
form. See constraint 3 in `CONTRIBUTING.md`.

Licensed under the MIT License.
