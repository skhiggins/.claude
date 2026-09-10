---
name: draft-report
description: Draft a referee report on a paper in the user's style, based on a full read of the manuscript (and appendix, registration, and any existing draft comments). Use when the user invokes /draft-report, optionally passing the paper PDF(s), the journal, and/or an existing comments.txt as arguments, or asks to draft, extend, or add points to a referee report.
---

# Draft a referee report in the user's style

Goal: produce a referee report (or add points to an existing draft) that reads like the user's own reports: a one-paragraph summary, two to three main comments led by identification, a short list of minor comments, no closing paragraph. Every claim in the report must be verifiable against the paper with a page or exhibit citation.

The style rules below were derived from the user's 2018–2026 reports, with 2024–2026 practice taking precedence where practice changed over time.

## Step 1: Identify the inputs

- **Paper**: the PDF(s) passed as arguments, or else the manuscript and online appendix in the current folder. Read both if an appendix exists.
- **Journal and round**: infer from the folder path (e.g., `2026/REStud`, `.../re`, `.../R1`); ask if unclear. The journal determines the bar stated in the report and the section headings (see Step 5). Revision rounds follow the "Revision mode" section at the end.
- **Existing draft**: if `comments.txt` (or `comments.tex`) exists in the folder, read it in full. Treat the user's existing points as fixed: keep their wording verbatim, keep their numbering, and add new points after them (or, for minor points, in the minor section). Do not rewrite the user's points unless asked.
- **Registration**: if an AEA registry or pre-analysis-plan file exists in the folder (e.g., `AEARCTR-*.txt`), read it; the user checks whether outcomes and heterogeneity were pre-specified.
- **Prior reports**: for revisions, read the user's previous `comments.txt`, the authors' response letter, and the editor's letter if present.

## Step 2: Read the paper in full

Invoke the `read-pdf` skill on every PDF and follow it completely (convert to `.txt` in `.claude/references/`, read every chunk sequentially). Do not draft from a partial read. While reading, note for each table and figure: sample, N, clustering, what is and is not reported, and any number that can be recomputed from the paper's own statistics.

## Step 3: Analyze the paper along the dimensions the user raises most often

Work through this list in order; it is ordered by how often the user's recent reports raise each point. Not every item applies to every paper. For each item that applies, record the specific evidence (page, table, coefficient) before writing.

1. **Identification / endogeneity / selection.** Almost always comment 1. The user's signature move is to name a specific omitted factor, hypothetical or observable ("for the purposes of this argument I'll call it 'tech savviness'"), and trace step by step how it would produce the paper's result even if the paper's mechanism were absent. Check: where the identifying variation comes from and who chose it; whether the paper's exogeneity argument answers the right objection (selection vs. exclusion); whether matching or controls address unobservables (they do not); bad controls; the "ideal experiment" benchmark and how the design departs from it; for IVs, the exclusion restriction stated concretely. If the paper's own text supports the concern (a citation used for exogeneity that also implies persistent bank/firm differences; a control that shows imbalance), use it.
2. **Parallel trends / event studies.** Count pre-periods shown vs. post-periods; count statistically significant pre-period coefficients ("18 out of 105, 17%"); check whether every DID result has an event-study version, whether the omitted period is stated, whether the pre-period is a mechanical zero, whether pre-trends can rule out the confound in item 1 (often they cannot if the confounding change began after the pre-period). Cite Roth (2022 AER: Insights) and Rambachan and Roth (2023 REStud) where relevant.
3. **Inference.** Cluster at the level at which treatment is assigned (Bertrand, Duflo, and Mullainathan 2004 QJE); few effective clusters (Cameron, Gelbach, and Miller 2008 REStat; wild cluster bootstrap; MacKinnon and Webb); serial correlation within unit; multiple-hypothesis families; standard errors rather than t-statistics in tables.
4. **Power, small samples, low take-up.** Minimum detectable effect from Duflo, Glennerster, and Kremer (2007) equation 13; power inverse-quadratic in compliance; wide confidence intervals are not nulls. Standard package: winsorize, control for the baseline outcome (McKenzie 2012), pool waves, drop underpowered heterogeneity.
5. **Contribution / literature.** State what is already known, with one or two named papers, and whether the increment clears the journal's bar. Only cite papers whose content is known; verify any citation via web search before including it (authors, title, journal, year), or mark it unverified.
6. **Magnitudes and internal inconsistencies.** Recompute effect sizes at the mean and in economic units, show the arithmetic inline ("0.4388 × 0.14 = 0.061, i.e., 6.3%, not 6.8%"), check that magnitudes in text match tables and footnotes, that sample sizes are consistent across tables and text, that results are not implausibly large, and that "elasticities" are not extrapolated beyond what the variation supports.
7. **Measurement / data quality / sample construction.** Who is in the data and who is not; arbitrary sample cuts and researcher degrees of freedom (prefer median splits); attrition; survey representativeness; proxies that measure only part of the object (e.g., one payment provider standing in for all digital payments).
8. **Mechanisms and alternative explanations.** Lay out two models that both fit the headline result and say what would distinguish them.
9. **RCT and reporting hygiene** (usually minor comments): omnibus F-test in balance tables; control-mean and number-of-clusters rows; results without controls; formal tests of differences between subgroups (a significant coefficient in one group and not another is not a difference); pre-analysis plan public; no results "available upon request" or "untabulated" (all results described in the text belong in the paper or an online appendix table); figure and table notes that state N and the specification.
10. **Presentation.** Nonsignificant results described as if significant (preferred rewrite: "we do not find a statistically significant effect on ..."); "significant" without "statistically"; 95% rather than 90% confidence intervals; too many footnotes or main exhibits; axis labels and captions that mislead (e.g., year labels placed at Q4); typos collected in one list.

Also record every internal error found while reading (wrong footnote arithmetic, caption/text mismatches, mislabeled tables, outdated references); these become minor comments.

## Step 4: Decide what goes in and how long the report is

- **Main comments: two to three** (never more than five). Identification first. Each main comment is 150–500 words and may have lettered sub-points 1a), 1b).
- **Length** (body text): about 400–700 words for a clear rejection at a top journal (two to three main points, few or no minor comments); 800–1,200 words is typical; 1,500–2,300 words only when there is a path to publication and the paper needs detailed guidance (typically RCTs at field journals), with 5–12 minor comments.
- **Minor comments**: 0–3 in a rejection, 5–12 in a revise-and-resubmit-type report. Order by importance, not by page.
- Do not pad. A single-flaw rejection is a short report.
- Do not include the recommendation to the editor in the report unless stating the journal's bar explicitly ("not a large enough contribution for a top-3 finance journal"; "on its own it is not enough for the JFE"; "there is a path to publication at the JPE"). Give the suggested recommendation to the user in dialog instead.

## Step 5: Write the report in the user's format

Plain text (`comments.txt`), unless the user asks for the LaTeX template. Structure:

1. **Summary paragraph** (100–250 words, no heading or the heading "Summary"). First sentence states the research question, usually as "This paper asks [an important question]: ...?" or the question itself followed by why it matters. Then setting, identification strategy, and data in two to four sentences, at the level of "what the paper does," not a catalog of estimates. Report the paper's findings in the summary only if the identification strategy is believable, i.e., the report does not have a main comment arguing that the estimates cannot be interpreted causally; in that case one sentence with the headline result suffices. If the report's main comment is that identification fails, do not state the magnitudes in the summary (stating them as findings concedes what the report disputes; the numbers belong in the main comments where they are questioned). End with specific praise, almost always "The authors should be commended for ..." (the data assembled, the partnership, the question). The summary is neutral; the verdict comes in the main comments. Optionally, for top journals, a one-paragraph "Assessment" between the summary and the comments, or a single bridging sentence: "My main concern with the paper is the identification strategy."
2. **Headings**, plain text on their own line: "Main comments" then "Minor comments" (default); "Essential points" then "Suggestions" for JFE/RFS templates; "Major issues" then "Suggestions" for RF; an optional third tier "Suggestions (up to authors' discretion)" or "Additional comments".
3. **Numbering**: "1)", "2)", ... continuous across sections (minor comments do not restart at 1); sub-points "1a)", "1b)"; third level with "--" dashes. Each numbered point opens with a short topic label and a period: "1) Identification strategy.", "2) Contribution.", "3) Standard errors.", "6) Winsorizing."
4. **Closing**: none. The report ends on the last minor comment or the typo list. If papers are cited that the manuscript does not already cite, add a final list headed "References (excluding the ones already cited in the paper)" with full citations including journal names.
5. **Typos**: one final numbered item containing a "--" bulleted list with page or table references and the correction ("'Shoter' --> 'Shorter' in Table 6").

## Step 6: Phrasing rules

- Claim, then why it matters, then the fix. Every concern states its consequence for the paper's claim ("This is important because ...", "The reason is that ...") before any request.
- Direct, not hedged: "This seems wrong", "I disagree with this claim", "This is not the right test", "There is no way the exclusion restriction holds." No praise inside comments; praise lives in the summary paragraph only.
- First person sparingly and for judgment: "My main concern is ...", "I suspect ...", "In my view ...", "I did not understand why ...", "based on my own calculations". Never "I think" as filler.
- "The paper" is the subject for claims, findings, and specifications ("The paper claims ...", "the paper should ..."); "the authors" for actions and decisions ("the authors should be commended", "do the authors have data on ..."). "The author" for a solo paper.
- Modal language: "the paper should" / "the authors should" (dominant) for required changes; "It would be useful/helpful to", "I would consider", "at a minimum", "My preference would be" for lower-priority items; "This is free disposal if the authors disagree" or "This is more based on taste" for optional ones.
- Requests are concrete: write the regression in text ("y_ij = beta_1 FD_j + beta_2 FE_j + epsilon_ij"), name the table columns and rows to add, name the outcome transformation, name the clustering level.
- Show arithmetic inline: "(= 0.06/0.33 from Table 7A, Panel A, column 1)", "1315/2130 = 62%".
- Page references in parentheses "(p. 16)"; exact exhibit references "Table 5 Panel B, column 6", "Figure 3b", "footnote 20". Quote the paper verbatim in double quotes before rebutting it.
- Constructed examples to make a mechanism concrete: "Suppose there are two groups of four identical borrowers ...", "Consider the following example (which I take to the extreme) ...".
- Literature inline as Author (year, journal abbreviation optional): "Young 2019 QJE", "Chen and Roth (2024)". Own work is cited by name when it is the right example.
- Present tense throughout. Emphasis with *asterisks* in .txt. Dashes as "--" in .txt.
- Concede when appropriate: "this would require data the authors might not have access to"; "the important part of the test is not whether the results remain statistically significant but whether the coefficient remains similar."
- Do not write about how the authors would reply or what would "preempt" a response; the authors do not get to reply if the paper is rejected (see project CLAUDE.md). Evaluate each point on whether it is correct and supported.
- Global writing rules apply: no "honest/honestly/genuine/genuinely/real" as fillers, no figurative language about what words or arguments do, no "sharper", no mystery-novel framing, no "Not X. Just Y." constructions, keep verbs near their subjects.

## Step 7: Verify, then write the file

Before writing, check every number, page reference, quotation, and exhibit reference in the draft against the converted text. Verify any citation not already in the paper via web search or mark it "[citation unverified]". Do not state facts about the setting from memory without flagging them as unverified.

Output:
- If no `comments.txt` exists in the folder, write the report to `comments.txt` there.
- If `comments.txt` exists, do not overwrite it. Write the combined report (user's points verbatim, new points appended in the user's numbering) to `comments_draft.txt` in the same folder, and list in dialog which numbered points are new.
- In dialog, give: the suggested recommendation to the editor, the two or three points the report hinges on, and anything left unverified.

## Revision mode (folder named re, R1, R2, or the user says it is a revision)

- Open with a one-paragraph assessment of the revision ("This is a much-improved version ..." or a direct statement of what was and was not addressed).
- Reuse the original comment numbers: "Below I use the same comment numbers as in my previous referee report (so comment numbers that are skipped refer to comments that were sufficiently addressed in the revision)."
- For each remaining point: quote the authors' response letter, then check the claim against the revised paper (e.g., N unchanged in every table despite a claimed sample addition; evidence in the response document that did not make it into the paper; a pre-analysis plan still not public). Use pointed language where warranted: "the authors incorrectly claim ...", "I do not find this argument convincing".
- If the revision is good, say so and narrow to "My only remaining main comment ...". Final rounds can be two or three sentences.
- If the report is being reused at a new journal after rejection elsewhere, open with a one-sentence disclosure: "I previously reviewed this paper for [journal]. My referee report is largely the same ..."
