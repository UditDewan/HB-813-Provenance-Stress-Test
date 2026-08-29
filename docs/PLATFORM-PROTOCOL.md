# Platform round-trip protocol

The point of this document is that two people running the same platform get the
same row. If your numbers disagree with someone else's, the protocol is
underspecified — say so and fix this file, don't reconcile the numbers by hand.

## Rules

- **Uploads are manual.** Automating them violates platform terms of service,
  and a bot's upload is not the thing we are trying to measure. Nothing in this
  repo posts to a platform.
- **Use a study account.** Accounts created by team members for this project.
  Never the Representative's accounts, never a personal account you care about,
  never anything belonging to the office.
- **Post nothing that stays up.** Delete the test post as soon as you have saved
  the returned file. Keep test posts non-public where the platform allows it.
- **Never hand-edit `runs.csv`.** `src/roundtrip.py` writes it.

## The steps

1. Pick a corpus image that starts with a valid manifest. Check first:

       uv run python -m src.corpus verify

2. Open the run:

       uv run python -m src.roundtrip start --platform instagram --image C.jpg

   Write down the `run_id` it prints.

3. Upload `data/corpus/<image>` to the platform from a **desktop web browser**,
   at original resolution, with any "high quality" or "original size" option the
   platform offers left at its **default**. We are measuring what happens to an
   ordinary person, and ordinary people do not change upload settings.

4. Retrieve the image the way a viewer would: open the post, right-click the
   image, "Save image as". Not the platform's own "download your data" export,
   which often returns the original bytes and would flatter the result.

   Where a platform serves several derivatives at different display sizes, take
   the one a viewer gets from "save image" at the default view. Note which one
   you took in `--notes`.

5. Save it into `inbox/` and close the run:

       uv run python -m src.roundtrip finish --run-id <id> --file inbox/download.jpg \
           --notes "saved from desktop web, default view"

6. Delete the test post.

## What to record in `--notes`

The CLI already detects re-encoding and dimension changes. Add anything it
cannot see:

- which derivative you saved, if the platform serves more than one
- whether the platform showed any provenance indicator of its own
  (a "made with AI" label, a content-credentials badge)
- app vs. web, and mobile vs. desktop, if you tested a non-default path
- anything that made the run unusual

## Coverage

Cover, in this order — the earlier ones carry the most Ohioans:

| Platform | Tested by | Second tester | Done |
|---|---|---|---|
| Facebook | | | |
| Instagram | | | |
| X | | | |
| Reddit | | | |
| LinkedIn | | | |
| Discord | | | |
| WhatsApp | | | |
| iMessage | | | |
| SMS / MMS | | | |
| Gmail attachment | | | |
| Google Drive share link | | | |

**Two team members independently run at least three platforms.** Disagreement
between them is a defect in this document, not a data point.

## Known confounds

- Platforms change their pipelines without announcement. Every row carries a
  timestamp for this reason; a result is a result *as of that date*.
- Some platforms serve different bytes to logged-in and logged-out viewers. Test
  logged-out where the platform allows it, and say which you did.
- A platform that preserves the manifest but re-encodes the pixels produces
  `present_invalid`, not `present_valid`. That is a real and different outcome:
  the claim is still attached but no longer verifies. Do not collapse it.
