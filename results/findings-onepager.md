# HB 813: does the watermark survive? — one page

**Preliminary.** Local testing complete; platform testing not yet run. Numbers
below come from 1 signed image × 19 transformations. Full memo:
`results/findings-memo.md`. Evidence: `data/results/runs.csv`.

## The question

HB 813 requires AI-generated products to carry a watermark, enforced by the AG.
That only works if the mark is still there when someone checks. We measured
whether it is.

We tested C2PA — the signed provenance record Adobe, Leica and others attach at
creation. It is the strongest mark in real deployment. If it does not survive,
nothing weaker does.

## What we found

**Re-encoding an image destroys the mark. Every time.**

| Ordinary thing a person does | Mark survives? |
|---|---|
| Saves the image at slightly lower quality | **No** |
| Resizes it | **No** |
| Crops it | **No** |
| Rotates it | **No** |
| Screenshots it | **No** |
| Opens it in an editor and saves | **No** |
| Uses "remove properties before sharing" | **Yes** |

Not degradation — deletion. Saving at a quality no human eye can distinguish
from the original removes the mark as completely as shrinking the image to a
quarter of its size.

And the one operation that *keeps* the mark is the one people perform
deliberately to strip metadata for privacy.

## Why it matters for the bill

A mark applied at generation does not survive the file being handled. If HB 813
places the duty on the generator alone, then: the generator marks the image, the
next person to touch it saves it, the mark is gone, and everyone in the chain has
complied. The duty is satisfied. The goal is not.

## What we still need to measure

**Platform uploads.** Almost nobody sees an image as the file that left the
generator; they see it after Facebook, Instagram, or a messaging app has
processed it. Whether those platforms preserve the mark decides whether the bill
reaches the images Ohioans actually encounter. Protocol is written; testing is
next.

## Questions the office may want to answer

1. Does anyone downstream — a platform, an editor, a distributor — have a duty
   to preserve a mark they receive?
2. Does "watermark" mean a visible overlay, embedded metadata, or a
   cryptographic manifest? They fail in opposite ways.
3. What tool does the Attorney General use to verify compliance? For most text
   watermarking, no public detector exists.
4. Is a broken mark treated differently from a missing one? Technically and
   evidentially they are different.

*We are not proposing language. We are reporting what we measured.*
