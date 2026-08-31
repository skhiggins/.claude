---
name: check-hardcoded
description: Scan a LaTeX paper for hard-coded numbers that should instead be script-generated and pulled in via \input. Flags statistics that appear to be calculated from the project's data but are typed directly into the tex; skips numbers cited from other papers, design parameters, and bin/quantile labels. Produces a markdown report. Use when the user asks to check for hard-coded, hand-typed, or manually entered numbers in a paper.
---

# Hard-coded number audit

Scan a LaTeX paper for numbers typed directly into the text that appear to be **calculated from the project's data by scripts**. The motivation: every number our scripts compute should be printed by the script into a small `.tex` fragment and pulled into the paper with `\input{...}`, so the paper updates automatically when the data or code changes. Hand-typed copies of computed numbers silently go stale.

The argument (if given) is the main `.tex` file; otherwise find the paper's main file (the one with `\documentclass`) and confirm with the user if ambiguous.

## Step 1 — Collect the text to scan

1. Gather the main file plus every hand-written `\input`/`\include`d file that is part of the compiled document (e.g., section files, appendix files).
2. **Exclude script-generated fragments**: files that are themselves produced by Stata/R/Python (table fragments, number fragments — typically in a `tables/`, `figures/`, or `numbers/` folder, or recognizable by machine-generated headers/formatting). Numbers inside those are the *good* case, not hard-coding.
3. **Strip comments before scanning**: skip lines whose first non-whitespace character is `%`, and on every other line ignore everything after the first non-escaped `%` (a `\%` is an escaped percent sign, part of real text). Do not flag numbers in dead text.

## Step 2 — Identify candidate numbers

Scan the remaining text for numerals (including numbers written with `\%`, currency symbols/units, thousands separators, decimals, and negatives) in prose, footnotes, captions, and any hand-written table rows. Ignore:

- LaTeX-structural numbers: spacing/sizing arguments (`\vspace{2mm}`, `0.9\textwidth`), column specs, counters, label/ref numbers, font sizes, `\multicolumn{3}`, etc.
- Cross-references produced by `\ref`/`\Cref`/`\eqref` and citation years.
- Section/figure/table numbering.
- Numbers spelled out as words only when they are clearly non-statistical ("one of the two arms"); spelled-out statistics ("twelve percent of users") *do* count as candidates.

## Step 3 — Classify each candidate

For each candidate, read the surrounding sentence (and paragraph if needed) and classify:

- **Flag — hard-coded statistic**: the number appears to be *calculated from the project's data* — sample sizes, means, medians, shares/percentages of the sample, regression coefficients or effect sizes, p-values, standard deviations, monetary totals or averages computed from the data, counts of observations/users/transactions, take-up rates, etc. — and is typed literally rather than `\input`.
- **Skip — cited from another paper**: the number is attributed to another work (a citation in or near the sentence, or phrasing like "X et al. find…"). Do not flag.
- **Skip — not computed from the data**: design parameters and institutional facts — experiment/product parameters ("prizes of 400 pesos", "a 6-month term"), policy/institutional numbers, dates and durations ("over 7 years"), bin or quantile *definitions* ("the bottom 20% of users" when 20% defines the group being examined rather than being a computed share), round rhetorical numbers not tied to a calculation.
- **Unsure**: it is not clear whether the number is data-computed or a design/external fact — e.g., a share that could be either a bin definition or a computed statistic, a peso amount that might be a design parameter or a data-derived average. **Include these in the report and say you are unsure**, with a one-line note on what would resolve it.

When judging, prefer false positives with an "unsure" label over silently skipping: the user can dismiss an unsure entry quickly, but a missed stale number is costly.

## Step 4 — Write the report

Write `hardcoded_numbers.md` in the paper's directory (ask before overwriting an existing one from a previous run — or write `hardcoded_numbers_YYYY-MM-DD.md`). Structure:

```markdown
# Hard-coded number audit: <main file> (<date>)

Summary: N flagged, M unsure, across K files scanned. (Skipped items are not listed.)

## Flagged — hard-coded statistics

1. [file:line] "…sentence with the **number** bolded…" — why this looks data-computed; if apparent, which table/figure or script output it likely corresponds to.
2. …

## Unsure

1. [file:line] "…sentence…" — why it might be data-computed, why it might not, and what would resolve it.
2. …
```

- Order entries by appearance in the compiled document.
- Use markdown links with relative paths for every file:line reference.
- If several numbers in one sentence share a fate (e.g., a hand-typed summary of a table row), group them into a single entry.
- End with a short note listing any `\input` files you excluded as script-generated and any files you were unsure whether to scan.

## Practical notes

- Work through the document in order; for long papers, use TodoWrite to track sections and append to the report in batches so progress is not lost.
- If the project has a `numbers/` or similar fragment folder, note in each flagged entry whether an existing fragment already contains (or could easily contain) the number.
- Consult project memory (if any) for previously settled calls about specific numbers, and do not re-litigate them — report the settled call instead.
