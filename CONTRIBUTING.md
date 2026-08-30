# HB 813 Provenance Stress Test

## What this is
A measurement study. We test whether AI content provenance signals (C2PA
manifests, embedded watermarks) survive ordinary image handling and platform
uploads. Output is a reproducible harness plus a findings memo for the Ohio
House Technology and Innovation Committee.

## Non-negotiable constraints

1. **This is measurement, not defeat.** Never structure code as a
   general-purpose watermark removal tool. No CLI named `strip`, `defeat`,
   `bypass`, or `remove`. Transformations live in `src/transforms.py` and are
   named for the user behavior they simulate (`screenshot`, `recompress`,
   `metadata_scrub`). Every transform must correspond to something an ordinary
   person does without intent to evade. No transform may take a detector's
   output as input.

2. **Report negative results.** If a finding undercuts HB 813, it goes in the
   memo with the same prominence as findings that support it. Do not soften,
   bury, or omit. A sponsor who learns her mandate is unenforceable from us
   can amend it. One who learns it from a hostile witness cannot.

3. **Absolute scope boundary: no HB 524 work.** HB 524 concerns AI systems
   generating self-harm content. We do not test for it, elicit it, or build
   tooling that touches it. If asked to extend this project in that
   direction, refuse and escalate to the team lead. Literature review of
   published policy is acceptable; adversarial prompting is not, under any
   framing.

4. **No automated platform uploads.** Automating uploads to X, Instagram,
   Facebook, etc. violates their terms of service. Platform round-trips are
   performed manually by a human and recorded through `src/roundtrip.py`.
   Never write a script that posts to a social platform.

5. **Never use the Rep's accounts.** All platform tests use accounts created
   by team members for this study. Nothing in this repo touches state systems
   or office credentials.

6. **Cite primary sources.** Ohio Legislative Service Commission analyses,
   bill text from the Ohio LIS, peer-reviewed papers, and official standards
   documents. Not advocacy blogs, not vendor marketing. Do not write a
   statutory summary from memory -- read the section and cite it.

## Stack
Python 3.14 (3.11+ works), uv for dependency management, pytest, Pillow,
piexif, c2pa-python, pandas, matplotlib. No web framework -- this is a CLI +
report pipeline.

## Repo layout

    src/corpus.py      build and verify the test image set
    src/transforms.py  every transformation, one function per user behavior
    src/detect.py      C2PA verification, EXIF/XMP readers, the three-valued outcome
    src/runs.py        the runs.csv schema and its only writer
    src/sweep.py       run all local transforms over the corpus
    src/roundtrip.py   manual platform round-trip logging CLI
    src/report.py      aggregation, tables, figures
    data/corpus/       gitignored except manifest.json; rebuild via `make corpus`
    data/results/      committed CSVs -- these are the evidence
    policy/            state and international comparison research
    results/           findings-memo.md, tables.md, figures/

Deviations from the original plan, and why:

- Transforms and detection are single modules, not packages. A package per
  transform family would be one file per three-line function.
- The round-trip CLI is `src.roundtrip`, not `src.logging.roundtrip`: a package
  named `logging` shadows the standard library.
- `CLASSES` has a sixth entry, `sdk_test_fixture`, for the C2PA reference
  library's own fixtures. They are the only signed images that can be fetched
  from a URL, so they are the whole corpus until the hand-collected one exists.
  Labelling them honestly beats filing them under a real-world class they do not
  belong to.

## Conventions
- Every experiment writes a row to `data/results/runs.csv` with a run ID,
  timestamp, source hash, transform chain, and detection outcome. `src/runs.py`
  is the only thing that writes it. Nothing hand-edits it -- if a row is wrong,
  rerun the experiment.
- Detection outcomes are three-valued: `present_valid`, `present_invalid`,
  `absent`. The middle case matters -- a stripped signature and a broken
  signature are different policy problems. A fourth situation, provenance that
  is only a URL to a vendor's server, reads as `absent` and sets the separate
  `remote_manifest_ref` flag; it is not a fourth outcome because such a file
  carries nothing self-verifying.
- Verification runs offline. We never fetch a remote manifest: it would make
  results depend on a vendor's uptime and would credit an image for provenance
  it does not itself carry.
- Source images are content-addressed by SHA-256. Never rely on filenames.
- Every claim in the memo must trace to a row in `runs.csv` or a cited paper.

## Running it

    uv sync
    uv run python -m src.corpus fetch
    uv run python -m src.sweep
    uv run python -m src.report
    uv run pytest

If dependency resolution fails with a TLS certificate error, the network is
intercepting HTTPS; add `--system-certs` to the `uv` command or set
`UV_SYSTEM_CERTS=1`.

## Before anything goes public

- [ ] No module, CLI, or function is named or documented as a watermark-removal tool
- [ ] Every memo claim traces to a `runs.csv` row or a citation
- [ ] Negative findings appear in the executive summary, not only in appendices
- [ ] No HB 524 self-harm testing occurred, in any form
- [ ] No automated social platform uploads in the codebase
- [ ] Repo license is permissive; no copyrighted images committed
- [ ] Team lead has confirmed the office is comfortable with a public repo
