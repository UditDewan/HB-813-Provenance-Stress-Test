# Do AI watermarks survive contact with the real world?

**Preliminary findings for the Ohio House Technology and Innovation Committee**
Prepared by student volunteers for the office of Rep. Christine Cockley (D-06)
regarding HB 813, 136th General Assembly (R.C. 1349.12–1349.16, proposed)

> **Status: preliminary.** The local transform arm is complete: 27 images, 540
> experiments. The platform arm has not started — no social platform has been
> tested. The corpus is currently the C2PA reference library's own test
> fixtures, which cover many manifest structures over few photographs; see
> Limitations. Every number below carries its denominator.
>
> Generated tables and figures: `results/tables.md`. Every claim here traces to
> a row in `data/results/runs.csv` or to statutory text cited in
> `policy/state-comparison.md`.

---

## 1. What we tested and what we found

HB 813 would require AI-generated products to carry a watermark, enforced by the
Attorney General with penalties of $2,500 to $10,000 per instance and a private
right of action. The technical question the bill depends on is whether such a
mark is still there when someone looks.

We test the strongest mark currently deployed: a **C2PA manifest**, the
cryptographically signed provenance record that Adobe, Leica and others attach at
the moment of creation. If C2PA does not survive, nothing weaker will.

**Finding 1. The mark does not survive being handled. At all.**

Of **200** experiments in which a transformation changed a signed image by even
one byte, **0** left a valid manifest behind. 198 removed the manifest entirely.
2 left a manifest that no longer verifies. There is no middle ground and no
gradient: re-saving a JPEG at quality 95 — a change nobody can see — destroys the
manifest as completely as shrinking the image to a quarter of its size. The
manifest lives in a container segment beside the image data, and ordinary
encoders do not carry that segment forward.

**Finding 2. The privacy feature people are told to use does not preserve the
mark. It breaks it.**

"Remove properties and personal information," the Windows Explorer checkbox and
its equivalents, deletes the EXIF block without re-encoding the pixels. On the
signed images in our corpus that carried no EXIF, it changed nothing at all —
byte-identical output, manifest intact. But on **both** signed images that
actually carried EXIF, deleting that block changed bytes the manifest hashes
over. The manifest stayed attached and stopped verifying:
`assertion.dataHash.mismatch`.

That is the worst of the three outcomes for an enforcement agency. The image
still carries a provenance claim. The claim no longer checks out. And the person
who caused it was using a privacy feature they were advised to use, with no
intent to alter anything.

**Finding 3. R.C. 1349.13(B) exposes people who did nothing but save a file.**

The bill does contain a downstream duty — we expected it not to, and it does:
no person may *distribute* for public or commercial use an AI-generated product
that lacks a distinctive watermark. But it contains no duty to *preserve* a
watermark, and no intent requirement.

Put that next to Finding 1. Someone receives a properly marked image, opens it,
saves it, and posts it. The mark is now gone — not through evasion, through
saving a file. On the face of the text that person has distributed an unmarked
AI-generated product and is exposed to a civil penalty and a private damages
suit. The generator that marked it correctly has complied. The duty is satisfied
and the goal is defeated, and the person holding the liability is the one who did
the least.

**What we cannot yet say.** Whether platforms strip the mark on upload — the
question that decides whether the bill reaches the images Ohioans actually see.
That is Section 3, it is the study's core exhibit, and it has not been measured.

---

## 2. Survival by transform

**Corpus:** 27 images, of which **11** carried a valid C2PA manifest at baseline,
5 carried a manifest that already failed to verify, 2 carried only a remote
manifest reference, and 9 carried no provenance at all.
**Experiments:** 540 total; 209 of them on the 11 validly signed images.

Generated table and figure: `results/tables.md`,
`results/figures/survival_by_transform.png`. Regenerate with `make report`.

| Transformation | Signed images tested | Valid manifest survived |
|---|---:|---:|
| Re-saved as JPEG (quality 95, 75, 50) | 11 each | 0 |
| Resized (75%, 50%, 25%) | 11 each | 0 |
| Cropped (5%, 10%, 25% border) | 11 each | 0 |
| Rotated (90°, 180°) | 11 each | 0 |
| PNG → JPEG → PNG conversion | 11 | 0 |
| Screenshotted | 11 | 0 |
| Opened in an editor and saved | 11 | 0 |
| Screenshot then recompressed *(realistic worst case)* | 11 | 0 |
| EXIF block removed, image had EXIF | 2 | 0 — both broke |
| EXIF block removed, image had no EXIF | 9 | 9 — no-op, bytes unchanged |

`metadata_scrub` needs its two rows read together, and the generated table
separates them with a **No-op** column for exactly that reason. Nine of its
eleven runs returned a byte-identical file, because there was no EXIF block to
delete; a transform that did nothing cannot show that anything survived it. Of
the two runs where it did something, both broke the signature. The figure shows
this as a grey segment rather than a green one — there is no green anywhere in
the chart, which is the finding.

**Note on quality 95.** Re-saving at near-original quality destroys the manifest
as completely as any other transformation. The mark is not degraded by handling.
It is present or absent, and handling makes it absent.

**Note on the three-valued outcome.** We distinguish a manifest that is *gone*
from one that is *present but no longer verifies*. Both occurred, from different
causes: re-encoding produced the first, EXIF deletion the second. For an
enforcement agency these are different situations — no evidence at all, versus
evidence that something happened but not what — and a statute that treats them
identically cannot tell them apart. China's labeling measures, notably, build
their platform duty on exactly this distinction (art. 6; see
`policy/state-comparison.md`).

---

## 3. Survival by platform — **NOT YET MEASURED**

This section decides whether the bill's mechanism reaches the images Ohioans
actually encounter, because almost nobody views an image as the file that left
the generator. They view it after a platform has processed it.

Protocol is written (`docs/PLATFORM-PROTOCOL.md`), the logging harness works, and
the platform list is set: Facebook, Instagram, X, Reddit, LinkedIn, Discord,
WhatsApp, iMessage, SMS/MMS, Gmail attachment, Google Drive.

Uploads are performed by hand. Automating them would violate platform terms of
service, and a bot's upload is not the behavior we are trying to characterize.

*Fill from `results/tables.md` once round-trips are logged. Report the result
whichever way it comes out.*

---

## 4. Text watermarking — **NOT YET MEASURED**, and coverage will be limited

Be upfront about this in committee.

Most production text watermarking systems, including Google's SynthID-Text, ship
no public detector. We cannot measure them, and neither can anyone outside the
vendor. What we can measure is the open green-list scheme from Kirchenbauer et
al. against a model we run locally, degraded by paraphrase, round-trip
translation, synonym substitution, truncation, and interleaving human sentences.

That produces a **lower bound on fragility for one open scheme**, not a claim
about any vendor's system. We will say so in exactly those words.

The coverage gap is itself policy-relevant and belongs in the memo rather than a
footnote: **a mark the Attorney General has no way to verify is a mark the
Attorney General has no way to enforce.** California met this by requiring every
covered provider to publish a free public detection tool (Bus. & Prof. Code
§ 22757.2). HB 813 names no standard, format, or detector.

---

## 5. How other jurisdictions handled downstream stripping

Full citations, quoted text and method in `policy/state-comparison.md`. Every
cell there was read from the statute or regulation itself.

**The short version.** Three of the compared jurisdictions require marking. Of
those, two also say what happens once the content moves:

- **California** (Bus. & Prof. Code § 22757.3.1, added by AB 853, operative
  1 January 2027) states it negatively: a large online platform "shall not, to
  the extent technically feasible, knowingly strip any system provenance data or
  digital signature." It also requires platforms to detect provenance data and
  show it to users, and extends latent-disclosure duties to camera manufacturers
  from 2028.
- **China** (Measures for Labeling AI-Generated Synthetic Content, art. 6,
  effective 1 September 2025) states it positively: a distribution platform must
  check the file metadata for an implicit label, label the post accordingly, and
  write its own propagation data back into the file — with an explicit fallback
  chain for content that arrives with no label, covering both "user declared it"
  and "we detected traces of it."
- **Ohio HB 813** prohibits distributing an unmarked AI-generated product
  (R.C. 1349.13(B)) but imposes no duty to preserve a mark. It is the only
  marking regime in the set with a distribution prohibition and no preservation
  duty.

**Utah** (SB 149, 2024) requires no mark at all. Its approach is worth a look for
a different reason: Utah Code 13-2-12(2) provides that it is **no defense** to a
consumer protection violation that generative AI made the statement or was used
in furtherance of it. That provision does not depend on any mark surviving
anything.

**Colorado** (SB 24-205) is not a provenance statute and should not be cited as
one; it governs algorithmic discrimination in consequential decisions and is
silent on marking. Its effective date has moved twice and the provisions were
repealed and reenacted in May 2026.

**The EU AI Act, article 50, is not in this comparison and should have been.**
It is the one provision in the set that mandates machine-readable marking with
an express robustness qualifier. EUR-Lex would not serve the text to any
retrieval method we had, and we will not summarize it from memory. A person
should open it and fill the row in.

---

## 6. Questions HB 813 may want to answer

Open questions raised by the measurements and by the bill's own text, not
recommendations. The office decides what to do with them.

1. **What does "watermark" mean?** R.C. 1349.12 defines "artificial intelligence
   system," "AI-generated product" and "content," and does not define the word
   the bill turns on. California distinguishes *manifest* from *latent*
   disclosures; China distinguishes 显式 from 隐式 labels. The two behave in
   opposite ways: a visible overlay survives re-encoding and is removed by a
   crop; an embedded manifest is destroyed by both. Until the term is defined,
   the statute does not specify which failure mode it is buying.

2. **Does anyone have a duty to preserve a mark they receive?** R.C. 1349.13(B)
   forbids distributing unmarked content but requires nobody to keep a mark
   intact. Given Finding 1, a mark applied at generation will usually be gone
   before anyone downstream sees the file. California and China each wrote this
   duty, in different grammars.

3. **Is liability under 1349.13(B) intended to be strict?** The subsection has no
   knowledge or intent element. A person who re-saves a marked image and posts it
   has, on the text, distributed an unmarked AI-generated product. California's
   platform duty is qualified by both knowledge and technical feasibility.

4. **Does the compression carve-out swallow the rule?** The definition of
   AI-generated product excludes content whose data has been "compressed or
   encoded … for the purpose of optimization in storage, transmission, or
   encryption" without altering meaning. Every transformation we tested is
   literally that. One reading exempts most of what circulates; another confines
   the clause to preventing compression from *making* content count as
   AI-generated. The text supports both.

5. **Does the seven-day cure period fit this failure?** R.C. 1349.15(C) assumes
   noncompliance can be cured. If the mark was destroyed in the act of
   distribution, there is nothing to restore, and re-marking means asserting
   provenance the distributor cannot verify.

6. **Who verifies, and with what?** Enforcement runs through the Attorney General
   on a complaint form, and no standard, format or detector is named. California
   requires a free public detection tool; China points to a mandatory national
   standard. For C2PA a public verifier exists. For most text watermarking none
   does, and for pixel-domain watermarks the detector is usually the vendor's
   private property.

7. **Is a broken mark treated differently from a missing one?** The bill does not
   distinguish them. We produced both, from different innocent causes. They are
   evidentially different: one is an absence, the other is a claim that fails.

8. **Does provenance stored on a vendor's server count?** Two images in our
   corpus carry no embedded mark at all, only a URL pointing at a manifest the
   vendor holds. We record those as `absent` with a separate flag. That
   provenance disappears when the vendor does.

---

## 7. Method and reproduction

Everything is reproducible from a clean clone.

```bash
uv sync
uv run python -m src.corpus fetch    # or `scan` after adding your own images
uv run python -m src.sweep
uv run python -m src.report
uv run pytest
```

- **Detection** uses the C2PA reference library (`c2pa-python` 0.37.8, c2pa-rs
  0.90.15), offline: remote manifest fetching is disabled, so no result depends
  on a third party's uptime and no image is credited for provenance it does not
  itself carry.
- **Outcomes** are three-valued (`present_valid`, `present_invalid`, `absent`),
  recorded per experiment in `data/results/runs.csv` with a run ID, timestamp,
  source SHA-256, transform chain and result hash. Nothing hand-edits that file.
- **Transformations** are named for the human behavior they stand in for, and
  none takes a detector's output as input. This harness measures fragility. It
  is not a removal tool and is not structured as one.
- **Images** are content-addressed. `data/corpus/manifest.json` is committed; the
  images are not, for licensing reasons.
- **Statutory sources** were read directly: Ohio bill text from the Legislative
  Information Systems PDF, California from the Legislative Counsel's text, Utah
  from the enrolled bill, China from the Cyberspace Administration's published
  text. See `policy/state-comparison.md` for links and for what could not be
  retrieved.

### Known limitations

- **The corpus is the reference library's test fixtures.** They cover a wide
  range of *manifest structures* — nested ingredients, remote URIs, box hashes,
  stapled OCSP responses, CAWG identity data — over a narrow range of
  *photographs*; several are the same image at two sizes. So we can say manifest
  structure makes no difference to survival, and we cannot yet say anything about
  image content. The hand-collected 40–60 image corpus (Firefly exports, Leica
  samples, local generation, team photos) is what fixes this, and none of it can
  be downloaded.
- **No platform round-trips yet.** The most important arm is unmeasured.
- **Screenshots are simulated**, not captured from a physical screen: decoded
  pixels are composited onto a fresh canvas and re-encoded, which is what a screen
  capture produces. It does not model display scaling or photographing a screen.
- **HEIC and AVIF are untested.** They need additional decoders, and
  iPhone-native formats are a real-world path worth covering.
- **No video or audio.** HB 813's definition of "content" reaches both.
- **The EU row of the policy comparison is empty**, and two Colorado and Utah
  cells are marked unverified. They are marked, not guessed.
- **Platform behavior changes without notice.** Every row is timestamped. A
  platform result is a result as of that date.
