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
OUTCOME_LABEL = {
    "present_valid": "Signature survived",
    "present_invalid": "Present but broken",
    "absent": "Gone entirely",
}
# Status palette, not categorical: these are ordered states of one thing, and a
# reader should feel the severity. Every segment is named in the legend and in
# the table, so hue never carries the meaning on its own.
OUTCOME_COLOR = {"present_valid": "#0ca30c", "present_invalid": "#fab219", "absent": "#d03b3b"}

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
    """Outcome counts per group, plus a survival rate. Signed sources only."""
    signed = df[(df.source_state == "present_valid") & (df.transform_chain != "none")]
    if signed.empty:
        return pd.DataFrame()
    table = (
        signed.groupby(by).c2pa_state.value_counts().unstack(fill_value=0)
        .reindex(columns=OUTCOMES, fill_value=0)
    )
    table["n"] = table.sum(axis=1)
    table["survival"] = table.present_valid / table.n
    return table.sort_values(["survival", "n"], ascending=[False, False])


def to_markdown(table: pd.DataFrame, index_name: str) -> str:
    rows = [f"| {index_name} | n | Survived | Broken | Gone | Survival rate |",
            "|---|---:|---:|---:|---:|---:|"]
    for name, r in table.iterrows():
        # Chain ids join with "|", which would end the Markdown cell.
        name = str(name).replace("|", " then ")
        rows.append(f"| {name} | {r.n:.0f} | {r.present_valid:.0f} | {r.present_invalid:.0f} "
                    f"| {r.absent:.0f} | {r.survival:.0%} |")
    return "\n".join(rows)


def figure(table: pd.DataFrame, title: str, subtitle: str, path: Path) -> None:
    """100% stacked bar: for each row, where its images ended up."""
    labels = [str(i).replace("|", " + ") for i in table.index]
    height = 1.6 + 0.34 * len(labels)
    fig, ax = plt.subplots(figsize=(9, height), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    left = pd.Series(0.0, index=table.index)
    for outcome in OUTCOMES:
        width = table[outcome] / table.n
        ax.barh(labels, width, left=left, color=OUTCOME_COLOR[outcome],
                label=OUTCOME_LABEL[outcome], height=0.62,
                # A surface-coloured edge is the gap between stacked segments,
                # not a border: it never contrasts with the background.
                edgecolor=SURFACE, linewidth=1.5)
        for y, (w, l) in enumerate(zip(width, left)):
            # Label only where the text fits with padding; the table carries the rest.
            if w >= 0.14:
                ax.text(l + w / 2, y, f"{w:.0%}", ha="center", va="center",
                        color=INK if outcome == "present_invalid" else "#ffffff",
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
               ncol=3, frameon=False, fontsize=9, labelcolor=INK)
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
        "Survival rates below count only images that started with a valid manifest. "
        "An image with nothing to lose cannot lose it.",
        "",
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
        rate = by_transform.present_valid.sum() / by_transform.n.sum()
        print(f"overall C2PA survival across local transforms: {rate:.0%}")


if __name__ == "__main__":
    main()
