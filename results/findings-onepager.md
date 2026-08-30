# HB 813: does the watermark survive? — one page

**Preliminary.** Local testing complete: 27 images, 540 experiments. Platform
testing not yet run. Full memo: `results/findings-memo.md`. Evidence:
`data/results/runs.csv`. Statutory citations: `policy/state-comparison.md`.

## The question

HB 813 requires AI-generated products to carry a watermark, enforced by the
Attorney General at $2,500–$10,000 per instance, with a private right of action.
That only works if the mark is still there when someone checks. We measured
whether it is.

We tested C2PA — the signed provenance record Adobe, Leica and others attach at
creation. It is the strongest mark in real deployment. If it does not survive,
nothing weaker does.

## What we found

**Of 200 experiments that changed a signed image by even one byte, 0 left a
valid mark behind.**

| Ordinary thing a person does | Mark survives? |
|---|---|
| Saves it at slightly lower quality | **No** |
| Resizes it | **No** |
| Crops it | **No** |
| Rotates it | **No** |
| Screenshots it | **No** |
| Opens it in an editor and saves | **No** |
| Uses "remove properties before sharing" | **No — and worse** |

Not degradation. Deletion. Saving at a quality no eye can distinguish from the
original removes the mark as completely as shrinking the image to a quarter.

The last row is the one to dwell on. "Remove properties and personal
information" is a privacy feature people are told to use. On every signed image
in our corpus that actually had metadata to remove, it left the provenance claim
attached and broke it — the image still says who made it, and the claim no longer
checks out. The user did nothing but protect their privacy.

## Why it matters for the bill

R.C. 1349.13(B) says no person may **distribute** an AI-generated product without
a watermark. Nothing in the bill requires anyone to **preserve** a watermark, and
the subsection has no intent requirement.

So: someone receives a properly marked image, opens it, saves it, posts it. The
mark is gone — through saving a file. On the text, that person has distributed an
unmarked AI-generated product and is exposed to a penalty and a private suit. The
generator that marked it correctly has complied.

**The duty is satisfied. The goal is defeated. The liability lands on the person
who did the least.**

Two other things in the text bear on this:

- **"Watermark" is not defined.** R.C. 1349.12 defines three terms and not that
  one. A visible overlay and an embedded manifest fail in opposite ways — an
  overlay survives re-encoding and is cropped off; a manifest is destroyed by
  both. The bill does not say which it means.
- **The compression carve-out may swallow the rule.** "AI-generated product"
  excludes content compressed "for the purpose of optimization in storage,
  transmission, or encryption." Every transformation we tested is literally that.

## What other states did about it

Two jurisdictions wrote the missing duty:

- **California** — a large online platform "shall not, to the extent technically
  feasible, knowingly strip any system provenance data or digital signature."
  Bus. & Prof. Code § 22757.3.1, operative 1 Jan 2027. California also requires
  every covered provider to publish a **free public detection tool** (§ 22757.2),
  which answers the "who checks, with what" question HB 813 leaves open.
- **China** — a distribution platform must check the file's metadata for a label,
  label the post accordingly, and write its own data back into the file, with an
  explicit fallback for content that arrives unmarked. Labeling Measures art. 6,
  effective 1 Sept 2025.

Utah requires no mark at all, but provides that generative AI is **no defense**
to a consumer protection violation — a rule that does not depend on anything
surviving. Colorado is not a provenance statute and should not be cited as one.

## What we still need to measure

**Platform uploads.** Almost nobody sees the file that left the generator; they
see what Facebook, Instagram or a messaging app served back. That decides whether
the bill reaches the images Ohioans actually encounter. Protocol is written;
testing is next.

Also outstanding: the hand-collected image corpus (ours is currently the
reference library's test fixtures), text watermarking, and the EU AI Act row of
the comparison.

*We are not proposing language. We are reporting what we measured and what the
text says.*
