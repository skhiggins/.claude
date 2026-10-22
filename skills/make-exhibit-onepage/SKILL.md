---
name: make-exhibit-onepage
description: Shrink an exhibit (table or figure) until the exhibit and its full note fit together on one PDF page, by iteratively reducing its adjustbox/includegraphics width and recompiling. Takes a label, caption, or the IDE selection as the target; with no target, checks and fixes every exhibit in the paper (the main tex file plus all tex files it \inputs recursively). Use when the user calls /make-exhibit-onepage or asks to downsize or resize an exhibit so its note fits on the same page as the exhibit.
---

# Make an exhibit fit on one page with its note

A table or figure can be taller than the space its note needs, so the note spills onto the next page. The fix is to scale the exhibit down — reduce the `max width` of the `\adjustbox` wrapping the table, or the `width` of the `\includegraphics` — until the float and its complete note render on the same PDF page. Scaling the width scales the height proportionally, so a width reduction frees vertical space.

## Target and scope

- **Target exhibit**: the label or caption named in the argument, or the exhibit containing the IDE selection. **No target → all-exhibits mode**: process every `\begin{table}`/`\begin{figure}` in the paper.
- **Root tex file**: the file open in the IDE if it has `\documentclass`; if the open file is an `\input` fragment, find the root by searching the project's tex files for an uncommented `\input` of it. In iZettle_fee the root is `paper/BehavioralFirmsProfitableOpportunities.tex`.
- **Paper = root + every uncommented `\input{...}.tex`, recursively.** Exhibits usually live in dedicated appendix files.
- **Never edit the auto-generated files in `results/`** (`results/tables/`, `results/figures/`, `results/numbers/`) — the width knob is always in the paper-side wrapper around the `\input`/`\includegraphics`.
- **Only shrink, never grow.** An exhibit that already fits is left untouched (report it as fine). Honor any deliberate-width notes in project memory.
- **[iZettle_fee]** Fix widths on the paper side only. The response doc's copies keep their own `max width=1\textwidth` convention and their own pagination; do not tune them unless the user asks.

## Compile strategy

- Compile in the root file's directory with `pdflatex -synctex=1 -interaction=nonstopmode <root>.tex`.
- If `<root>.aux` and `<root>.bbl` already exist, **iterate with single pdflatex passes** — the bibliography stays warm and pagination is accurate. If they do not exist, run the full sequence once first.
- After the last width change, run the **full sequence** per the document's backend (biblatex/biber: `pdflatex → biber → pdflatex`; classic bibtex: `pdflatex → bibtex → pdflatex → pdflatex`) so the delivered PDF is clean.

## Detecting whether a note spills (the fiddly part)

Work from the **rendered PDF text**, not the tex, using `pdftotext`. For the target exhibit, derive plain-text search strings as pdftotext will render them:

- the **caption title** (the text inside `\caption{...}`, without any `Table~X:` prefix);
- a **distinctive phrase from the last sentence of the note** before the significance line (e.g. "prior to taking logs");
- the **note's final line**, usually the stars line, rendered as `* p < 0.1, ** p < 0.05, *** p < 0.01.` (sometimes followed by a Romano-Wolf plus-signs sentence — then that is the final line).

Rules for choosing phrases: strip macros and math (`$p$-value` renders as `p-value`, `\makequote{X}` as `"X`, `~` as a space); avoid `\inputnumber` output, numbers that scripts may change, and long words that pdftotext may merge across a line-break hyphen (e.g. "Heteroskedasticity-robust" can render as "Heteroskedasticityrobust"); 3–8 words is right.

Find each string's page with the helper script in this skill's directory:

```
bash <skill-dir>/find_pages.sh <root>.pdf "prior to taking logs"
```

The stars line and similar phrases appear in **many** notes, so never trust a global match: first find the caption's page N (the caption title is usually unique), then extract that page alone (`pdftotext -q -f N -l N <root>.pdf -`) and check the note-end strings occur **on page N**. The exhibit fits iff caption, note-start, and note-end are all on the same page. Checking the top of page N+1 confirms what spilled.

## Fix loop for one exhibit

1. Locate the width knob: `\adjustbox{max width=X\textwidth, ...}` / `\begin{adjustbox}{max width=X\textwidth}` / `\resizebox` for tables, `\includegraphics[width = X\textwidth]` for figures. If the exhibit has no scaling wrapper, add an `\adjustbox{max width=X\textwidth, center}{...}` matching the style of neighboring exhibits in the same file.
2. Reduce in coarse steps first (e.g. 1.2 → 1.0), recompile (single pass), re-check the pagination.
3. Once it fits, refine in **0.01 steps** to the **largest width that still fits** (bisect between the last failing and first fitting value). Example (2026-10-15): `tab:survey_balance_sample` went 1.2 → 0.97; 0.98 still spilled the last line and a half.
4. **Floor at 0.5\textwidth**: if it still spills there, restore the original width and report the exhibit as unfixable by scaling (the note is too long — needs a `\clearpage`, note cuts, or restructuring; that is the user's call).
5. Caveat for the minipage style (`\adjustbox{...}{\begin{minipage}...table + note...\end{minipage}}`, used by some balance tables): the note scales **with** the table, so the note cannot split off — instead check that the whole float fits on one page, and shrink the same way if it overflows.

## All-exhibits mode

Pagination interacts: shrinking an exhibit shifts every later page, which can fix or break later exhibits. So work in document order:

1. Baseline compile; list every exhibit with its caption page and note-fit status.
2. Fix the **first** spilling exhibit completely (fix loop above), then re-check all later exhibits against the fresh PDF before touching the next one.
3. Repeat until a full pass finds no spilling exhibit. Exhibits already followed by a `\clearpage` comment noting a deliberate page break are still checked — the `\clearpage` protects the *next* exhibit, not this one's note.

## Report and aftermath

- Write a timestamped report to the project's `.claude/` folder (`make_exhibit_onepage_YYYY-MM-DD_HHMM.md`): one row per exhibit — label, file:line of the width knob, old → new width (or "unchanged — already fits" / "unfixable at 0.5"), caption page, and note-fit status before and after.
- In chat, summarize the widths changed with file:line links.
- If a changed width deviates from the project's convention for that file (e.g. the iZettle_fee paper-side default of `max width=1.2\textwidth`), record the deviation and its reason in project memory so a later exhibit sync does not restore the convention width.
- Delete any temporary `pdftotext` output files; leave the final compiled PDF in place.
