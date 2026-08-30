"""Aggregate runs.csv into the tables and figures the memo cites.

    python -m src.report

Writes results/tables.md and results/figures/*.png. Every number in the memo
comes from here, so the memo never carries a figure that runs.csv cannot back.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.runs import RUNS_CSV  # noqa: E402

RESULTS = Path("results")
FIGURES = RESULTS / "figures"

OUTCOMES = ["present_valid", "present_invalid", "absent"]

# A fourth display category, not a fourth detection outcome. Some transforms are
# a no-op on some files: deleting the EXIF block from an image that has no EXIF
# hands back the identical bytes. Those runs come out `present_valid` and are
# not evidence that anything survived anything.
#
# This category exists because the chart is the artifact that gets photographed
# and quoted. Folding no-ops into "survived" would put an 82% green bar next to
# the word metadata_scrub, and that bar would say the opposite of what the run
# actually showed. Separating it is the difference between a true chart and a
# chart that is technically sourced.
UNCHANGED = "unchanged"
SEGMENTS = [UNCHANGED, *OUTCOMES]
SEGMENT_LABEL = {
    UNCHANGED: "File unchanged (no-op)",
    "present_valid": "Signature survived",
    "present_invalid": "Present but broken",
    "absent": "Gone entirely",
}
# Status palette, not categorical: these are ordered states of one thing, and a
# reader should feel the severity. Every segment is named in the legend and in
# the table, so hue never carries the meaning on its own. The no-op segment is
# deliberately a neutral, not a status colour -- nothing happened.
SEGMENT_COLOR = {
    UNCHANGED: "#b9b7ab",
    "present_valid": "#0ca30c",
    "present_invalid": "#fab219",
    "absent": "#d03b3b",
}

SURFACE, INK, MUTED, HAIRLINE = "#fcfcfb", "#0b0b0b", "#898781", "#e1e0d9"


def load() -> pd.DataFrame:
    if not RUNS_CSV.exists():
        raise SystemExit(f"{RUNS_CSV} not found -- run: python -m src.sweep")
    df = pd.read_csv(RUNS_CSV)
    # The CSV is append-only, so a re-run leaves older rows behind. One
    # experiment is one (source, transform chain, platform); keep its latest.
    key = ["source_sha256", "transform_chain", "platform"]
    return df.sort_values("timestamp").drop_duplicates(subset=key, keep="last")


def breakdown(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Outcome counts per group, plus a survival rate. Signed sources only.

    Survival is measured over the runs that actually changed the file. A no-op
    cannot demonstrate survival, so counting it as one would inflate the rate
    for exactly the transform where it matters most.
    """
    signed = df[(df.source_state == "present_valid") & (df.transform_chain != "none")]
    if signed.empty:
        return pd.DataFrame()
    segment = signed.c2pa_state.where(
        signed.result_sha256 != signed.source_sha256, UNCHANGED)
    table = (
        segment.groupby(signed[by]).value_counts().unstack(fill_value=0)
        .reindex(columns=SEGMENTS, fill_value=0)
    )
    table["n"] = table.sum(axis=1)
    changed = table.n - table[UNCHANGED]
    table["survival"] = (table.present_valid / changed).where(changed > 0)
    return table.sort_values(["survival", "n"], ascending=[False, False], na_position="first")


def headline(df: pd.DataFrame) -> list[str]:
    """The study's central claim, computed rather than asserted.

    Some transforms are a no-op on some files -- deleting the EXIF block from an
    image that has no EXIF returns the identical bytes. Those runs are real
    (they are what that user behavior does to that file) but they say nothing
    about fragility, so the headline separates them out by comparing hashes.
    """
    signed = df[(df.source_state == "present_valid") & (df.transform_chain != "none")]
    if signed.empty:
        return []
    changed = signed[signed.result_sha256 != signed.source_sha256]
    if changed.empty:
        return []
    counts = changed.c2pa_state.value_counts()
    kept, broke, gone = (int(counts.get(k, 0)) for k in OUTCOMES)  # noqa: F841
    return [
        "## The headline",
        "",
        f"Of **{len(changed)}** experiments that changed the file by even one byte, "
        f"**{kept}** left a valid manifest behind. "
        f"{broke} left a manifest that no longer verifies; {gone} left none at all.",
        "",
        f"The remaining {len(signed) - len(changed)} experiments returned byte-identical "
        "files -- a transform that was a no-op on that file. They are broken out as their "
        "own column and their own bar segment below, because a transform that did nothing "
        "cannot show that anything survived it.",
        "",
    ]


def to_markdown(table: pd.DataFrame, index_name: str) -> str:
    rows = [f"| {index_name} | n | No-op | Survived | Broken | Gone | Survival rate |",
            "|---|---:|---:|---:|---:|---:|---:|"]
    for name, r in table.iterrows():
        # Chain ids join with "|", which would end the Markdown cell.
        name = str(name).replace("|", " then ")
        rate = "n/a" if pd.isna(r.survival) else f"{r.survival:.0%}"
        rows.append(f"| {name} | {r.n:.0f} | {r[UNCHANGED]:.0f} | {r.present_valid:.0f} "
                    f"| {r.present_invalid:.0f} | {r.absent:.0f} | {rate} |")
    return "\n".join(rows)


def figure(table: pd.DataFrame, title: str, subtitle: str, path: Path) -> None:
    """100% stacked bar: for each row, where its images ended up."""
    labels = [str(i).replace("|", " + ") for i in table.index]
    height = 1.6 + 0.34 * len(labels)
    fig, ax = plt.subplots(figsize=(9, height), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    left = pd.Series(0.0, index=table.index)
    for outcome in SEGMENTS:
        width = table[outcome] / table.n
        ax.barh(labels, width, left=left, color=SEGMENT_COLOR[outcome],
                label=SEGMENT_LABEL[outcome], height=0.62,
                # A surface-coloured edge is the gap between stacked segments,
                # not a border: it never contrasts with the background.
                edgecolor=SURFACE, linewidth=1.5)
        for y, (w, l) in enumerate(zip(width, left)):
            # Label only where the text fits with padding; the table carries the rest.
            if w >= 0.14:
                ax.text(l + w / 2, y, f"{w:.0%}", ha="center", va="center",
                        color="#ffffff" if outcome == "absent" else INK,
                        fontsize=9)
        left += width

    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.invert_yaxis()
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.set_title(title, color=INK, fontsize=13, loc="left", pad=28, fontweight="bold")
    ax.text(0, 1.03, subtitle, transform=ax.transAxes, color=MUTED, fontsize=9, va="bottom")
    fig.legend(*ax.get_legend_handles_labels(), loc="lower left", bbox_to_anchor=(0.01, 0.005),
               ncol=4, frameon=False, fontsize=9, labelcolor=INK)
    fig.tight_layout(rect=(0, 0.06 * 4 / height, 1, 1))
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    df = load()
    FIGURES.mkdir(parents=True, exist_ok=True)

    local = df[df.method == "local"]
    platform = df[df.method == "platform"]
    by_transform = breakdown(local, "transform_chain")
    by_platform = breakdown(platform, "platform")

    signed_sources = df[df.source_state == "present_valid"].source_sha256.nunique()
    sections = [
        "# Result tables",
        "",
        "Generated by `python -m src.report` from `data/results/runs.csv`. Do not edit by hand.",
        "",
        f"- Corpus images tested: **{df.source_sha256.nunique()}** "
        f"(**{signed_sources}** carrying a valid C2PA manifest to begin with)",
        f"- Local transform experiments: **{len(local)}**",
        f"- Platform round-trips: **{len(platform)}**",
        "",
        "Survival rates below count only images that started with a valid manifest -- an "
        "image with nothing to lose cannot lose it -- and are measured over the runs that "
        "actually changed the file, so a no-op is never counted as a survival.",
        "",
        *headline(df),
    ]

    if by_transform.empty:
        sections += ["## C2PA survival by transform", "",
                     "_No signed images in the corpus yet._", ""]
    else:
        sections += ["## C2PA survival by transform", "",
                     to_markdown(by_transform, "Transform"), "",
                     "![Survival by transform](figures/survival_by_transform.png)", ""]
        figure(by_transform, "Does a C2PA signature survive ordinary handling?",
               "Share of signed images by outcome, per transformation",
               FIGURES / "survival_by_transform.png")

    if by_platform.empty:
        sections += ["## C2PA survival by platform", "",
                     "_No platform round-trips logged yet. See `docs/PLATFORM-PROTOCOL.md`._", ""]
    else:
        sections += ["## C2PA survival by platform", "",
                     to_markdown(by_platform, "Platform"), "",
                     "![Survival by platform](figures/survival_by_platform.png)", ""]
        figure(by_platform, "Does a C2PA signature survive a trip through a platform?",
               "Share of signed images by outcome, per platform round-trip",
               FIGURES / "survival_by_platform.png")

    # EXIF is not what HB 813 asks for, but it is what most people mean by "the
    # metadata", and it is the signal a phone actually attaches today.
    had_exif = df[df.exif_present & (df.transform_chain == "none")].source_sha256
    exif_runs = df[df.source_sha256.isin(had_exif) & (df.transform_chain != "none")]
    if not exif_runs.empty:
        kept = exif_runs.groupby("transform_chain").exif_present.mean()
        sections += ["## EXIF survival, for comparison", "",
                     "| Transform | EXIF retained |", "|---|---:|"]
        sections += [f"| {str(k).replace('|', ' then ')} | {v:.0%} |"
                     for k, v in kept.sort_values(ascending=False).items()]
        sections += [""]

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "tables.md").write_text("\n".join(sections), encoding="utf-8")
    print(f"wrote {RESULTS / 'tables.md'}")
    if not by_transform.empty:
        changed = by_transform.n.sum() - by_transform[UNCHANGED].sum()
        print(f"C2PA survived {by_transform.present_valid.sum():.0f} of {changed:.0f} "
              "local transforms that changed the file")


if __name__ == "__main__":
    main()
