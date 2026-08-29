# Provenance and disclosure mandates: jurisdiction comparison

**Status: scaffold. The cells are deliberately empty.**

Constraint 6 in `CONTRIBUTING.md` says: read the actual statutory text, cite primary
sources, do not summarize summaries. Filling this table from memory or from
secondary coverage would put unverified claims about other states' law in front
of a legislator, which is exactly the failure mode the constraint exists to
prevent. Each row gets filled by someone who has read the section and can cite
it by number.

## How to fill a row

1. Find the enacted text, not a bill tracker's summary, not a law firm client
   alert, not a vendor blog. For Ohio, the Ohio Legislative Service Commission
   analysis and the bill text on the Ohio Legislature's site. For other states,
   the state's own code or session-law site. For the EU, the Official Journal.
2. Quote or cite the specific section for every cell you fill.
3. Where a statute is silent on a column, write **silent** — not "no". Silence
   and an explicit exclusion are different drafting facts.
4. Note amendment and litigation history in the last column, with citations.

## The matrix

| | Ohio HB 813 (as introduced) | California SB 942 | Colorado SB 24-205 | Utah SB 149 | EU AI Act Art. 50 | China deep synthesis provisions |
|---|---|---|---|---|---|---|
| Citation (section-level) | ORC 1349.12–1349.16 (proposed) | | | | | |
| How "AI-generated" is defined | | | | | | |
| **Who bears the obligation** (developer / deployer / distributor / platform) | | | | | | |
| Machine-readable marking required? | | | | | | |
| Visible marking required? | | | | | | |
| Duty to *preserve* a mark downstream? | | | | | | |
| Disclosure when a system acts as a human | | | | | | |
| Exemptions | | | | | | |
| Enforcement mechanism | | | | | | |
| Effective date | | | | | | |
| Amendment / litigation history | | | | | | |

## The column that matters most

**Who bears the obligation.** This study's local results already show that a
mark placed at generation time does not survive the file being re-saved. If
HB 813 places the duty on the generator alone, a compliant generator marks the
image, a platform re-encodes it on upload, the mark is gone, and the duty was
satisfied while the goal was defeated. Nobody in that chain broke the law.

The row **"duty to preserve a mark downstream?"** is therefore the actionable
one. Whether any of these jurisdictions imposed a preservation or
non-degradation duty on distributors and platforms — and if so, how they drafted
it — is directly usable drafting information for the sponsor.

## What goes in the memo

Section 5 of `results/findings-memo.md` draws from this file. Frame it as *"the
bill as introduced does not appear to address X; here is how jurisdiction Y
approached it"* — evidence, not proposed language. The office drafts.
