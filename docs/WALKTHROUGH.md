# 20-minute walkthrough for the office

For the meeting with Rep. Cockley's office. Bring the one-pager
(`results/findings-onepager.md`) printed, one copy each. Everything below
assumes fifteen minutes of attention and five of questions.

Do not open the repo on screen unless someone asks. The finding is the
deliverable; the code is the receipt.

---

## Minute 0-2 — What we did

"You asked what we could help with. HB 813 requires AI-generated content to
carry a watermark. We measured whether watermarks survive the things people
actually do to images. Here is what we found."

Do not explain C2PA yet. Do not explain the harness at all.

## Minute 2-6 — The one finding

Hand over the one-pager. Walk the table on it, top to bottom.

> Of 200 experiments that changed a signed image by even one byte, zero left a
> valid mark behind. Saving at slightly lower quality. Resizing. Cropping.
> Screenshotting. And "remove properties before sharing" — the privacy feature
> people are told to use — does not preserve the mark either. It leaves the
> claim attached and breaks it.

Land "zero out of two hundred," then stop talking. It is the whole meeting.

If asked how strong the mark was: we tested C2PA, the cryptographically signed
record Adobe and Leica attach at creation. It is the strongest mark in real
deployment. Nothing weaker survives what it did not.

## Minute 6-10 — Why it matters for her bill

One consequence, stated once:

> R.C. 1349.13(B) forbids *distributing* an unmarked AI-generated product, but
> nothing requires anyone to *preserve* a mark, and there is no intent element.
> So someone who receives a marked image, saves it, and posts it has distributed
> an unmarked product — through saving a file. The generator has complied. The
> liability lands on the person who did the least.

Then the open questions, not recommendations:

> Does anyone downstream have a duty to preserve a mark they receive? California
> and China each wrote that duty. And "watermark" is not defined anywhere in the
> bill, though a visible overlay and an embedded manifest fail in opposite ways.

**We are not proposing language.** If the conversation drifts toward drafting,
say that out loud and hand it back: "that's the office's call, we can tell you
what we measured."

## Minute 10-14 — What we have not measured yet

Say this before they ask. It is the reason to keep working together.

- **Platform uploads.** Nobody sees the file that left the generator; they see
  what Instagram served back. That decides whether the bill reaches the images
  Ohioans encounter. Protocol is written, testing is next.
- **Real images.** The corpus is the reference library's test fixtures: many
  manifest structures, few photographs. Enough to show structure makes no
  difference; not enough to say anything about image content.
- **Text watermarking.** Most production systems ship no public detector, so
  nobody outside the vendor can verify them. That gap is itself worth her
  knowing: a mark the AG cannot check is a mark the AG cannot enforce.
- **The EU.** Article 50 is the one provision mandating machine-readable marking
  with a robustness qualifier, and EUR-Lex would not serve us the text. That row
  is empty on purpose. Colorado, Utah, California and China are filled in from
  the statutes themselves.

## Minute 14-16 — The ask

Two questions, both of which they can answer in the room:

1. **Is the office comfortable with a public repo?** Currently private. It is
   the evidence behind every number, and it is more useful to the committee
   public than not. Team lead confirms before anything is pushed.
2. **Does the sponsor want the platform arm prioritized, or the hand-collected
   image corpus?** Both are ~3 weeks. The platform arm is the stronger exhibit;
   the corpus is what turns "the mechanism is established" into a rate.

## Minute 16-20 — Questions

Likely ones:

**"Does this mean the bill doesn't work?"**
No. It means a mark applied at generation does not survive handling, so where
the duty attaches decides whether the mandate does anything. That is a drafting
question, and it is answerable.

**"Are you saying we should kill it?"**
No. We are volunteers with measurements. What to do about them is the office's
job. We would rather she hear this from us than from an opposing witness.

**"Could someone use your tool to strip watermarks?"**
No, and it is not built that way. Every transformation is named for the ordinary
behavior it simulates, none of them takes a detector's output as input, and
there is nothing in it a person could not do with the Save As dialog. We are
measuring fragility, not causing it.

**"Are you sure about the statutory reading?"**
We read the As Introduced text, not a summary — there is no LSC analysis
published for HB 813 yet. Every quote in the memo cites a section. If the office
reads 1349.13(B) differently we would genuinely like to know; that is a question
for counsel, not for us.

**"Where do the numbers come from?"**
Every claim traces to a row in `data/results/runs.csv` with a run ID, timestamp,
and file hash. The tables and figures are generated from that file and nothing
else. Anyone can rerun it from a clean clone in about a minute.

**"What does this cost us?"**
Nothing. Student volunteers, one semester.

---

## What to leave behind

- The one-pager, printed.
- The repo link, if they said yes to public.
- One sentence in the follow-up email confirming which of the two questions in
  Minute 14-16 they answered, and how.

## What not to do

- Do not walk through the code.
- Do not say "watermark removal," in any sentence, for any reason.
- Say "zero of two hundred experiments," not "100% failure" — the denominator
  is the credible part, and it invites the right follow-up question.
- Do not propose statutory language, even if invited to. Especially if invited.
