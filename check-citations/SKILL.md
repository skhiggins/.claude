---
name: check-citations
description: Audit every citation in a LaTeX paper, in order of appearance, for (1) content fit — does the cited work support the claim it is attached to — and (2) publication status — for works not yet published in an academic journal (forthcoming, working papers, SSRN/NBER, preprints), check whether they have since been published, including each author's website. Produces a markdown report with one section per citation. Use when the user asks to check, audit, or verify citations in a paper.
---

# Citation audit

Audit citations in a LaTeX paper one by one, in order of appearance. The argument (if given) is the main `.tex` file; otherwise find the paper's main file (the one with `\documentclass` and a bibliography command) and confirm with the user if ambiguous.

## Step 1 — Collect citations

1. Identify the bibliography file(s) actually loaded: `\addbibresource{...}` or `\bibliography{...}` in the main file. Ignore `.bib` files present in the folder but not loaded.
2. Extract every citation command from the main file **and any `\input`/`\include`d tex files that are part of the compiled document** (not script-generated table fragments). Match: `\cite`, `\citep`, `\citet`, `\citealt`, `\citeauthor`, `\citeyear`, `\textcite`, `\parencite`, `\autocite`, `\footcite`, `\fullcite` — with optional `*` and optional `[...]` arguments, possibly multiple comma-separated keys per command.
3. **Skip commented-out lines** (`%`-prefixed text) — do not audit citations in dead text, but if a commented cite of the same key exists, it may be noted as context.
4. Record for each occurrence: file, line number, and the full sentence (or clause) containing the citation — this is the *claim* the citation supports.
5. Group occurrences by citation key: multiple cites of the same key go in one report section. Order sections by the key's **first** appearance in the document.

## Step 2 — Check content fit (every citation)

For each key, read the bib entry (authors, title, year, venue). For each occurrence:

- Determine what the cited work actually shows/argues. Use existing knowledge of the paper; if not confident, use WebSearch (title + authors) and read the abstract. Do not guess.
- Judge whether the work supports the specific claim in the sentence. Watch for these common failure modes:
  - **Mechanism mismatch**: the paper is about a different mechanism than the clause implies (e.g., a beliefs-based paper cited for probability weighting, or vice versa).
  - **Application vs. source theory**: a short application paper cited where the foundational theory paper is the right cite (or the reverse — a general theory cited for a specific empirical claim).
  - **Overclaim**: the citation is used for a stronger or broader claim than the paper establishes.
  - **Taxonomy leakage**: in a paper that classifies mechanisms/literatures into branches, a cite placed under the wrong branch.
- Verdict per occurrence: **Good fit** / **Questionable** / **Misfit**, with one- or two-sentence reasoning. For Questionable/Misfit, suggest a better placement or replacement cite if one is apparent.

## Step 3 — Check publication status (unpublished items only)

An entry counts as **not yet published in an academic journal** if any of:
- `year = {forthcoming}` or the journal/note field contains "forthcoming", "accepted", "in press", "R&R", "revise";
- entry type `@unpublished`, `@techreport`, `@misc`, or a working-paper series (NBER, SSRN, CEPR, IZA, BREAD, arXiv, university WP series) in any field;
- no `journal` field on an `@article`, or `journal` names a working-paper series;
- `volume`/`pages` missing on an entry claiming journal publication (flag as possibly-published-but-incomplete — verify anyway).

Books, book chapters, and published conference proceedings (e.g., AER P&P) count as published.

For each such entry, check in this order and record what each source said:
1. **WebSearch** for the exact title + authors — look for a journal landing page (publisher site, DOI) with volume/issue/pages.
2. **Google Scholar / journal site / RePEc-IDEAS** results surfaced by the search.
3. **Each author's personal website** — search `"<author name>" economics homepage` (adapt field), then WebFetch their publications or CV page and look for the paper's current status. Do this for **every author** of the entry, not just the first, until a definitive status is found; note authors whose sites could not be found or fetched.

Outcome per entry: **Now published** (give full updated reference: journal, year, volume, issue, pages, DOI), **Still unpublished** (best current status, e.g., "NBER WP, no journal version found as of <date>"), or **Unclear** (conflicting or missing information — say what was checked).

Do **not** edit the `.bib` file as part of this skill — the report is the output. (The bib may be managed by Zotero or another tool; hand edits can be silently overwritten.) Include the corrected BibTeX fields in the report so the user can update the source of truth.

## Step 4 — Write the report

Write `citation_audit.md` in the paper's directory (ask before overwriting an existing one from a previous run — or write `citation_audit_YYYY-MM-DD.md`). Structure:

```markdown
# Citation audit: <main file> (<date>)

Summary: N unique citations, M occurrences. X misfits, Y questionable, Z unpublished items now published, W still unpublished.

## Action items

### Content-fit issues
- **<bibkey>** at [file:line] — verdict; one-line reason; one-line suggested fix (§ link to full section).

### Now published — update the bib
- **<bibkey>** — full updated reference: journal, year, volume(issue), pages, DOI (+ any title/author corrections).

## <bibkey> — Author(s) (Year), "Title"
**Bib entry:** venue and status as currently recorded.
**Occurrences:**
1. [file:line] "…quoted claim…" — **Good fit / Questionable / Misfit**: reasoning.
2. [file:line] "…" — …
**Publication status** (only if it was unpublished): Now published / Still unpublished / Unclear — details, updated reference fields, sources checked (including which author websites).

## <next bibkey> — …
```

- The **Action items** section is a compact digest of only the findings that require action, so the user can act without reading the full audit: (i) every occurrence with a **Misfit** or **Questionable** verdict, and (ii) every entry recorded as unpublished in the bib that has since been published (including advance-access entries that now have final volume/issue/pages). Omit good fits, still-unpublished items, and cosmetic bib fixes — those stay in the per-key sections and loose ends. Since the report is written incrementally in batches, write this section last (once all verdicts are in) and insert it directly under the summary line.
- One section per unique key, ordered by first appearance; all occurrences of a key in that one section.
- Use markdown links with relative paths for every file:line reference.
- End with a short list of loose ends: bib keys cited but missing from the loaded `.bib`, entries in the `.bib` never cited (optional, only if quick), and anything that needs the user's judgment.

## Practical notes

- Papers can have 50–150 unique citations; this is a long task. Work in batches (e.g., 10–15 keys at a time), appending to the report as you go so progress is not lost. Use TodoWrite to track batches.
- Web checks are parallelizable: consider batching WebSearch calls or delegating batches of publication-status checks to subagents, but keep content-fit judgments in the main context where the paper's claims are visible.
- If a claim's sentence spans a paragraph of context needed to judge fit, quote only the clause but read the surrounding paragraph before judging.
- Consult project memory (if any) for previously settled editorial calls about specific citations, and do not re-litigate them — report the settled call and its reasoning instead.
