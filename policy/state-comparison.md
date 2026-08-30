# Provenance and disclosure mandates: jurisdiction comparison

Every cell below was read from the statutory or regulatory text itself, not from
a summary, a tracker, or a client alert. Where a source could not be retrieved,
the cell says so rather than guessing. Constraint 6 in `CONTRIBUTING.md`.

Verified as of **2026-08-29**. Statutes move; recheck before quoting in
committee.

| Jurisdiction | Source read | Verified |
|---|---|---|
| Ohio HB 813 (136th GA, as introduced) | bill text, R.C. 1349.12–1349.16 | yes |
| California SB 942 + AB 853 | Bus. & Prof. Code §§ 22757–22757.3.3 | yes |
| Colorado SB 24-205 | bill page and amendment history | partly — see below |
| Utah SB 149 (2024) | enrolled bill, Utah Code 13-2-12 | yes |
| EU AI Act art. 50 | — | **no — could not retrieve** |
| China, AI content labeling measures | CAC 国信办通字〔2025〕2号, full text | yes |

**The EU row is empty on purpose.** EUR-Lex returns the current Official
Journal index rather than CELEX 32024R1689 to every retrieval method available
here — direct fetch, `curl`, and a rendering scraper alike. Article 50 is the
one provision in this set that mandates machine-readable marking with an express
robustness qualifier, so it is worth a person opening
<https://eur-lex.europa.eu/eli/reg/2024/1689/oj> by hand and filling this in.
Do not fill it from memory.

---

## The column that decides everything: who must keep the mark

Our measurements show a mark applied at generation does not survive the file
being handled. So the question that determines whether any of these regimes
works is not who applies the mark. It is **who is responsible once the mark is
gone.** Three answers appear in the set:

| Jurisdiction | Duty on whoever distributes the content |
|---|---|
| **China** | **Affirmative and specific.** A distribution platform must check the file's metadata for an implicit label, label the post accordingly, and write its own propagation data back into the file. Art. 6. |
| **California** | **Affirmative, negative form.** A large online platform "shall not, to the extent technically feasible, knowingly strip any system provenance data or digital signature." § 22757.3.1. Operative 1 Jan 2027. |
| **Ohio HB 813** | **Prohibition, no preservation duty.** No person may *distribute* an AI-generated product without a watermark — but nothing requires anyone to preserve a watermark they received. R.C. 1349.13(B). |
| **Utah** | Silent. No marking requirement of any kind. |
| **Colorado** | Silent. Not a provenance statute. |
| **EU** | Not verified. |

Ohio is the only one of the three marking regimes that imposes a distribution
duty **without** a corresponding preservation duty. Section 6 below is about
what that gap does.

---

## Ohio HB 813, 136th General Assembly, as introduced

Reps. Cockley and Miller, plus nine cosponsors. Enacts R.C. 1349.12 through
1349.16. As of 2026-08-29 it is in House committee; the only document published
is the As Introduced text, and **LSC has not published a bill analysis**, so
there is no official summary to point a member at.

Text: <https://search-prod.lis.state.oh.us/api/v2/general_assembly_136/legislation/hb813/00_IN/pdf/>

### Definitions, R.C. 1349.12

Three terms are defined: "artificial intelligence system," "AI-generated
product" (also "AI-product"), and "content."

> "AI-generated product" or "AI-product" means content that is substantially
> created or modified by an artificial intelligence system such that the use of
> the artificial intelligence system materially alters the content.

**"Watermark" is not defined.** The word carries the entire operative weight of
the bill and appears nowhere in the definitions section. That is the single most
consequential drafting fact we found, and Section 6 returns to it.

The definition of AI-generated product carries an exclusion that matters to this
study:

> "AI-generated product" or "AI-product" does not include content where part or
> all of the original digital data is compressed or encoded through software
> algorithms for the purpose of optimization in storage, transmission, or
> encryption if the software or algorithm does not alter the original meaning of
> the content.

### Duties, R.C. 1349.13

- **(A)** AI systems "shall be programmed to provide a distinctive watermark on
  any AI-generated product that informs the user that the particular content was
  generated using an artificial intelligence system." A design duty on the
  system.
- **(B)** "No person, business, or organization shall distribute for public or
  commercial use any AI-generated product that does not include a distinctive
  watermark." A duty on **whoever distributes** — much broader than the
  generator, and the provision our measurements bear on most directly.
- **(C)** Anyone using an AI system "shall clearly and conspicuously inform any
  user whenever the artificial intelligence system is acting as or emulating a
  human person."
- **(D)** Does not apply to AI-generated product "generated at the prompting of a
  user solely for personal, noncommercial use."

### Enforcement, R.C. 1349.14 through 1349.16

Complaints go to the Attorney General through a web form; the AG may investigate
on complaint or on its own inquiry, and must give written notice identifying each
alleged violation.

- **Private right of action.** Any person aggrieved may sue for damages.
  R.C. 1349.15(A).
- **AG civil action.** Injunctive relief plus a civil penalty of not less than
  $2,500 per instance of noncompliance and not more than $10,000 per violation
  or instance. R.C. 1349.15(B).
- **Seven-day cure.** The AG may not sue if, within seven days of notice, the
  party cures every violation in the notice and states in writing that it has
  done so and will not do it again. R.C. 1349.15(C). The safe harbor is lost for
  repeat violations of the same type. R.C. 1349.15(D), (E).
- Penalty amounts turn on seriousness, intent, history and harm; collections go
  to the consumer protection enforcement fund under R.C. 1345.51. R.C. 1349.16.

No effective-date section, so the ordinary ninety-day rule would apply.

---

## California: SB 942 (2024) as amended by AB 853 (2025)

Bus. & Prof. Code §§ 22757–22757.6, with §§ 22757.3.1–22757.3.3 added by AB 853.
The most developed provenance regime in the set, and the only one that pairs a
marking duty with a way to check compliance.

**Who bears it.** A "covered provider" — a GenAI system with over 1,000,000
monthly visitors or users that is publicly accessible in California.
§ 22757.1(b). A threshold Ohio's bill does not have.

**What must be applied.** Two things, on the same content:

- A **manifest** disclosure the user may opt into — "manifest" meaning "easily
  perceived, understood, or recognized by a natural person." §§ 22757.1(e),
  22757.3(a).
- A **latent** disclosure, always — "latent" meaning "present but not manifest."
  It must carry system provenance data (provider, version, time, identifier), be
  detectable by the provider's own detection tool, and be "permanent or
  extraordinarily difficult to remove, to the extent … technically feasible."
  §§ 22757.1(d), 22757.3(b), (b)(4).

Note what that qualifier concedes. California requires durability *as far as
technically feasible* rather than durability outright — the drafters appear to
have understood that the mark can be destroyed.

**Verification.** § 22757.2 requires the covered provider to publish a **free,
publicly accessible AI detection tool** accepting uploads and API access, and
forbids it from retaining personal provenance data. This is how California
answers the question Ohio leaves open: who checks, with what.

**Licensing.** A covered provider must revoke a third-party license within 96
hours of learning the licensee has disabled the disclosure capability, and the
licensee must stop using the system. § 22757.3(c).

**Downstream — the part that matters here.** AB 853 adds § 22757.3.1, operative
1 January 2027, imposing three duties on large online platforms: detect whether
distributed content carries provenance data conforming to widely adopted
specifications; expose that provenance to users through an interface; and

> shall not, to the extent technically feasible, knowingly strip any system
> provenance data or digital signature

from content uploaded to or distributed on the platform. § 22757.3.3 extends
latent-disclosure duties to **capture device** manufacturers for devices first
produced for sale after 1 January 2028 — closing the loop at the camera.

**Enforcement.** Civil penalty of $5,000 per violation per day, each day a
discrete violation; enforceable by the Attorney General, city attorneys, and
county counsels; fees and costs recoverable. § 22757.4.

**Exemptions.** Non-user-generated video games, television, streaming, movies
and interactive experiences. § 22757.5.

**Dates.** The act was originally operative 1 January 2026; AB 853 moved the
main operative date to 2 August 2026, with platform duties from 1 January 2027
and capture-device duties from 1 January 2028. *(Two of these dates came from
separate readings of the amended text — confirm against § 22757.6 as chaptered
before quoting.)*

---

## Colorado: SB 24-205 (2024)

**Not a provenance statute, and worth saying so plainly** so nobody in committee
assumes Colorado solved this problem. It governs algorithmic discrimination in
consequential decisions: developer and deployer duties, impact assessments, risk
management programs, consumer notice, correction and appeal, and disclosure to
the Attorney General. It contains **no watermarking, marking, or machine-readable
provenance requirement.**

Its one point of contact with HB 813 is a general duty to disclose to a consumer
that they are interacting with an AI system — the analogue of R.C. 1349.13(C).

Enforcement is exclusively by the Attorney General, with violations treated as
deceptive trade practices under the Colorado Consumer Protection Act.

**Status is unsettled and worth tracking.** Requirements were originally
effective 1 February 2026; SB 25B-004 extended that to 30 June 2026; SB 26-189,
signed May 2026, repeals and reenacts the provisions with new automated
decision-making requirements effective 1 January 2027.

*Unverified in this pass: the codified C.R.S. section numbers, and the operative
text of SB 26-189. The bill page does not carry them. Fill from the session laws
before citing.*

---

## Utah: SB 149 (2024), Artificial Intelligence Policy Act

Enrolled text read in full. Enacts Utah Code 13-2-12, 13-70-101 and 13-70-201
through 13-70-305, and 76-2-107; amends 13-11-4, 13-61-101 and 63I-2-213.

**No marking requirement of any kind.** Utah's approach is liability and
disclosure, not provenance:

- Generative AI is **no defense**. It is not a defense to violating a consumer
  protection statute that generative AI "made the violative statement,"
  "undertook the violative act," or "was used in furtherance of the violation."
  13-2-12(2). Ohio's bill has no equivalent, and it is a cheap, robust provision:
  it does not depend on any mark surviving anything.
- **Disclosure on request.** A person using GenAI to interact with someone in
  connection with consumer protection law must clearly and conspicuously
  disclose that fact — but only "if asked or prompted by the person."
  13-2-12(3).
- **Disclosure without request, in regulated occupations.** A person providing
  the services of a regulated occupation "shall prominently disclose when a
  person is interacting with a generative artificial intelligence," verbally at
  the start of an oral exchange and electronically before a written one.
  13-2-12(4)(a), (5).

**Enforcement.** The Division of Consumer Protection administers it. Administrative
fine up to $2,500 per violation; court action for injunction, disgorgement and
fines up to $2,500 per violation; up to $5,000 per violation for violating an
order; fees, costs and investigative fees awarded to the division. 13-2-12(6)–(10).

Signed 13 March 2024. *Unverified in this pass: 2025 amendments to the Act.*

---

## China: Measures for Labeling AI-Generated Synthetic Content

《人工智能生成合成内容标识办法》, 国信办通字〔2025〕2号 — issued jointly by the
Cyberspace Administration of China, the Ministry of Industry and Information
Technology, the Ministry of Public Security and the National Radio and Television
Administration on 7 March 2025, **effective 1 September 2025**. Full text read at
<https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm>.

*Translations below are ours from the Chinese text; article numbers are exact,
wording is not authoritative.*

**Two kinds of label, defined separately (art. 3).** An *explicit* label (显式标识)
is presented in the content or interface as text, sound or graphics and is
plainly perceivable by the user. An *implicit* label (隐式标识) is added by
technical means into the content file's data and is not readily perceivable.
Ohio's bill has one undefined word where China has two defined categories.

**Explicit labels (art. 4).** Required in the deep-synthesis situations covered
by article 17 ¶1 of the Deep Synthesis Provisions, with per-medium placement
rules for text, audio, images, video and virtual scenes. Critically: when a
provider offers download, copy or export, it "shall ensure the file contains a
conforming explicit label."

**Implicit labels (art. 5).** Must go **in the file's metadata**, and must carry
the content's attribute information, the provider's name or code, and a content
number. Metadata is defined in the article as descriptive information embedded in
the file header. Digital watermarking is **encouraged, not required** — a
distinction worth noting, since it is the opposite of what "watermark" in Ohio's
bill sounds like it means.

**Distribution platforms (art. 6).** The provision that answers this study's
central question. A provider of network content dissemination services must:

1. verify whether the file metadata contains an implicit label; if the metadata
   clearly marks the content as AI-generated, add a conspicuous notice around the
   published content;
2. where no implicit label is found but the **user has declared** the content to
   be AI-generated, add a notice that it **may be** AI-generated;
3. where there is neither, but the platform **detects an explicit label or other
   traces** of generation, treat it as *suspected* AI-generated and label it as
   such;
4. provide labeling functionality and prompt users to declare.

And in each of situations 1 through 3, the platform must **write its own
propagation information back into the file metadata** — content attributes,
platform name or code, content number.

Two things follow. First, China assumes the mark will often be missing and
builds an explicit fallback chain rather than a single duty. Second, that chain
is structured on exactly the distinction this study's detector makes: label
present, label absent but content declared, label absent and content merely
suspected. A regulator who wrote article 6 had already worked out that
"marked" and "unmarked" are not the only two states.

**Other duties.** App distribution platforms must check labeling materials at
review (art. 7). Terms of service must explain the labeling scheme (art. 8). A
user may request content without an explicit label, and the provider may supply
it after fixing the user's obligations by agreement, retaining logs for at least
six months (art. 9). Users must declare AI content when publishing, and **no
organization or individual may maliciously delete, alter, forge or conceal a
label, or provide tools or services enabling others to do so** (art. 10).
Providers must also meet mandatory national standards (art. 11) — here GB
45438-2025. Enforcement runs through the existing sectoral regulators (art. 13).

---

## What this means for HB 813

Six observations, each traceable to text quoted above and to a row in
`data/results/runs.csv`. These are observations, not recommendations. The office
drafts.

**1. "Watermark" is undefined, and the choice it hides is the whole ballgame.**
R.C. 1349.12 defines three terms and not that one. Every other marking regime in
this set defines its terms and, more importantly, distinguishes a *perceivable*
mark from a *machine-readable* one — California as manifest and latent
(§ 22757.1(d), (e)), China as 显式 and 隐式 (art. 3). The two behave in opposite
ways under ordinary handling. A visible overlay survives re-encoding and is
removed by a crop. An embedded manifest survives a crop only in the sense that
nothing survives a crop: our sweep destroyed it in **0 of 200** experiments that
changed the file at all. Until the word is defined, nobody can say which failure
mode the statute is buying.

**2. R.C. 1349.13(B) creates liability for people who did nothing but save a
file.** The subsection forbids distributing an AI-generated product without a
distinctive watermark. It does not require anyone to *preserve* a watermark, and
our measurements show ordinary handling removes it: re-saving at a quality no
eye can distinguish, resizing, cropping, rotating, screenshotting. So a person
who receives a properly marked image, opens it, saves it, and posts it has
distributed an unmarked AI-generated product. On the face of the text that is a
violation, exposed to a $2,500 to $10,000 penalty and a private damages suit,
with no intent requirement anywhere in the section.

**3. The seven-day cure provision does not fit a stripping problem.**
R.C. 1349.15(C) assumes noncompliance is something a party can fix. If the mark
was destroyed by the act of distribution, there is nothing to cure: the original
is gone, and re-marking after the fact means asserting provenance the distributor
cannot verify. The safe harbor was drafted for a party who forgot to label, not
for one whose file was re-encoded in transit.

**4. The compression carve-out may swallow the rule, or may do nothing.** The
definition of AI-generated product excludes content whose data has been
"compressed or encoded … for the purpose of optimization in storage,
transmission, or encryption" where the meaning is not altered. Every step we
tested is exactly that: JPEG re-encoding is compression for storage and
transmission and does not alter meaning. One reading is that a recompressed image
ceases to be an AI-generated product and no duty attaches to anyone — which would
exempt most of what circulates. Another is that the clause was meant only to stop
compression from *making* something count as AI-generated. The text supports
both, and the difference is the scope of the whole bill.

**5. Nothing says who verifies, or with what.** Enforcement runs through the
Attorney General on a complaint form (R.C. 1349.14(A)), and no standard, format
or detector is named. California solves this by requiring every covered provider
to publish a free public detection tool (§ 22757.2). China solves it by pointing
at a mandatory national standard (art. 11, GB 45438-2025). Ohio's bill points at
nothing, which leaves the AG's office to determine, per complaint, whether an
undefined mark is present.

**6. Two jurisdictions have already written the missing duty, in opposite
grammars.** California states it negatively — a large online platform "shall
not … knowingly strip any system provenance data or digital signature"
(§ 22757.3.1), qualified by technical feasibility and knowledge. China states it
positively — a distribution platform must check the metadata, label the post,
and add its own data (art. 6), with no feasibility qualifier and an explicit
fallback for content arriving unmarked. They are different instruments with
different costs, and either shape is available to Ohio.
