---
name: check-citations
description: Audit every citation in a LaTeX paper, in order of appearance, for (1) content fit — does the cited work support the claim it is attached to — and (2) publication status — for works not yet published in an academic journal (forthcoming, working papers, SSRN/NBER, preprints), check whether they have since been published, including each author's website. Every content-fit flag is then verified by reading the flagged paper in full from the local Zotero storage, using a parallel agent workflow. Produces a markdown report with one section per citation. Use when the user asks to check, audit, or verify citations in a paper.
---

# Citation audit

Audit citations in a LaTeX paper one by one, in order of appearance. The argument (if given) is the main `.tex` file; otherwise find the paper's main file (the one with `\documentclass` and a bibliography command) and confirm with the user if ambiguous.

## Step 1: Collect citations

1. Identify the bibliography file(s) actually loaded: `\addbibresource{...}` or `\bibliography{...}` in the main file. Ignore `.bib` files present in the folder but not loaded.
2. Extract every citation command from the main file **and any `\input`/`\include`d tex files that are part of the compiled document** (not script-generated table fragments). Match: `\cite`, `\citep`, `\citet`, `\citealt`, `\citeauthor`, `\citeyear`, `\textcite`, `\parencite`, `\autocite`, `\footcite`, `\fullcite` — with optional `*` and optional `[...]` arguments, possibly multiple comma-separated keys per command.
3. **Skip commented-out lines** (`%`-prefixed text) — do not audit citations in dead text, but if a commented cite of the same key exists, it may be noted as context.
4. Record for each occurrence: file, line number, and the full sentence (or clause) containing the citation — this is the *claim* the citation supports.
5. Group occurrences by citation key: multiple cites of the same key go in one report section. Order sections by the key's **first** appearance in the document.

## Step 2: Check content fit (every citation)

For each key, read the bib entry (authors, title, year, venue). For each occurrence:

- Determine what the cited work actually shows/argues. Use existing knowledge of the paper; if not confident, use WebSearch (title + authors) and read the abstract. Do not guess.
- Judge whether the work supports the specific claim in the sentence. Watch for these common failure modes:
  - **Mechanism mismatch**: the paper is about a different mechanism than the clause implies (e.g., a beliefs-based paper cited for probability weighting, or vice versa).
  - **Application vs. source theory**: a short application paper cited where the foundational theory paper is the right cite (or the reverse — a general theory cited for a specific empirical claim).
  - **Overclaim**: the citation is used for a stronger or broader claim than the paper establishes.
  - **Taxonomy leakage**: in a paper that classifies mechanisms/literatures into branches, a cite placed under the wrong branch.
- Verdict per occurrence: **Good fit** / **Questionable** / **Misfit**, with one- or two-sentence reasoning. For Questionable/Misfit, suggest a better placement or replacement cite if one is apparent. Verdicts of Questionable or Misfit at this stage are **preliminary**: they must be verified against the full text in Step 4 before the report is finalized.

## Step 3: Check publication status (unpublished items only)

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

## Step 4: Verify content-fit flags by reading the flagged papers in full (agent workflow)

Every preliminary **Misfit** or **Questionable** verdict from Step 2 must be verified against the full text of the cited work before the report is finalized. Do this with a multi-agent workflow; invoking this skill is the user's opt-in to that orchestration.

1. **Collect the flagged citation keys** (deduplicated). Skip keys where: (a) project memory records the flag as already settled by the user; (b) the entry is grey literature, press, or a report with no academic PDF expected in Zotero; or (c) the flag does not depend on the paper's content (e.g., a date inconsistency between the claim and the entry's year). Skipped flags keep their preliminary verdict, annotated with why they were not full-read verified.
2. **Launch the workflow.** Load the `workflow-authoring` skill, then call the Workflow tool with a script that fans out one `agent()` per flagged key in parallel, each returning a result against a schema like `{ key, pdf_found, verdict: "CONFIRMED" | "OVERTURNED" | "REVISED", evidence, suggested_fix }`. Respect the session's workflow size guideline: if more than ~15 keys are flagged, run the verification in batches. If the Workflow tool is not available in the session, launch the same per-key agents in parallel with the Agent tool (general-purpose) instead.
3. **Each agent's prompt** must contain the citation key; the bib entry (authors, year, title, venue, and any `file` field verbatim); the flagged claim sentence(s) with file:line; the preliminary verdict and its reasoning; and these instructions (the `read-pdf-from-zotero` procedure, inlined because agents do not load skills):
   - Locate the PDF: try the bib `file` field paths first. They may be another machine's absolute paths (e.g., `/Users/<name>/Zotero/storage/<hash>/...`); in that case try the same `<hash>` folder under the local storage `C:\Users\skh2820\Zotero\storage\`. Failing that, Glob the storage folder by author and distinctive title words (e.g., `*/*<Author>*<TitleWord>*.pdf`), trying several patterns; filenames follow `Author et al. - Year - Title.pdf` with long titles truncated. If several versions match, prefer the one matching the bib entry's venue and year.
   - Convert with `python C:\Users\skh2820\.claude\skills\read-pdf\scripts\pdf_to_txt.py "<pdf>" "<project>/.claude/references/<citation_key>.txt"`, then read the ENTIRE `.txt` with the Read tool in sequential 800-line chunks until end of file. No skipping, no sampling, no stopping early.
   - Only after the final chunk, judge whether the preliminary verdict is accurate for the specific claim. Return the verdict with page-cited evidence: quote the decisive passages and cite their `===== [page N of M] =====` markers, and state explicitly when a term or fact central to the claim appears nowhere in the paper. If the flag stands, return a concrete suggested fix (rewording or replacement cite).
   - If no PDF can be found, return `pdf_found: false` with the patterns tried. Never verify from the abstract alone and never substitute a different paper.
4. **Fold the results into the report.** For each flagged entry: record the final verdict and mark it "verified by full read <date>", include the agents' page-cited evidence, note the converted text's path (`.claude/references/<key>.txt`) so later sessions can re-check without re-reading, and upgrade or downgrade the verdict where the full read overturned or revised the preliminary call (a Questionable that the full read confirms as unsupported becomes Misfit; a flag the full read overturns becomes Good fit, with the evidence). Entries whose PDF was not found stay flagged, marked "unverified — judged from abstract/summary only."

## Step 5: Write the report

Write `citation_audit.md` in the paper's directory (ask before overwriting an existing one from a previous run — or write `citation_audit_YYYY-MM-DD.md`). Structure:

```markdown
# Citation audit: <main file> (<date>)

Summary: N unique citations, M occurrences. X misfits, Y questionable (of which V verified by full read), Z unpublished items now published, W still unpublished.

## Action items

### Content-fit issues
- **<bibkey>** at [file:line] — verdict (verified by full read / unverified); one-line reason; one-line suggested fix (§ link to full section).

### Now published — update the bib
- **<bibkey>** — full updated reference: journal, year, volume(issue), pages, DOI (+ any title/author corrections).

## <bibkey> — Author(s) (Year), "Title"
**Bib entry:** venue and status as currently recorded.
**Occurrences:**
1. [file:line] "…quoted claim…" — **Good fit / Questionable / Misfit**: reasoning. For flagged occurrences: verification outcome, page-cited evidence, and the converted text's path.
2. [file:line] "…" — …
**Publication status** (only if it was unpublished): Now published / Still unpublished / Unclear — details, updated reference fields, sources checked (including which author websites).

## <next bibkey> — …
```

- The **Action items** section is a compact digest of only the findings that require action, so the user can act without reading the full audit: (i) every occurrence with a **Misfit** or **Questionable** verdict, and (ii) every entry recorded as unpublished in the bib that has since been published (including advance-access entries that now have final volume/issue/pages). Omit good fits, still-unpublished items, and cosmetic bib fixes — those stay in the per-key sections and loose ends. Since the report is written incrementally in batches, write this section last (once all verdicts, including Step 4 verifications, are in) and insert it directly under the summary line.
- One section per unique key, ordered by first appearance; all occurrences of a key in that one section.
- Use markdown links with relative paths for every file:line reference.
- End with a short list of loose ends: bib keys cited but missing from the loaded `.bib`, entries in the `.bib` never cited (optional, only if quick), and anything that needs the user's judgment.

## Practical notes

- Papers can have 50–150 unique citations; this is a long task. Work in batches (e.g., 10–15 keys at a time), appending to the report as you go so progress is not lost. Use TodoWrite to track batches.
- Web checks are parallelizable: consider batching WebSearch calls or delegating batches of publication-status checks to subagents, but keep preliminary content-fit judgments in the main context where the paper's claims are visible; only the Step 4 full-read verification is delegated to agents.
- If a claim's sentence spans a paragraph of context needed to judge fit, quote only the clause but read the surrounding paragraph before judging.
- Consult project memory (if any) for previously settled editorial calls about specific citations, and do not re-litigate them — report the settled call and its reasoning instead, and exclude them from Step 4 verification.
