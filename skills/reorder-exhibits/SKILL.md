---
name: reorder-exhibits
description: Reorder the figure/table floats in the source files so that, within each series (main figures, main tables, appendix figures, appendix tables), exhibits appear in the order they are first discussed in the paper. Always reruns check-exhibits-cited first to get a fresh report. Use when the user calls /reorder-exhibits or asks to reorder exhibits to match the discussion order.
---

# Reorder exhibits to match the order of first citation

## Step 1: Rerun check-exhibits-cited

**Always rerun the full check-exhibits-cited skill first** (its Steps 1-4: determine the root file, run the scanner, analyze, write a new timestamped report to `.claude/`). Never act on an older report, even one produced earlier in this session: the user may have edited the tex files since it was written. The fresh report is the sole input to the steps below.

## Step 2: Compute the target order

Within each of the four series (main figures, main tables, appendix figures, appendix tables), the target order of exhibits is the document-order position of each exhibit's *first* citation. Constraints:

- **Never change which series an exhibit belongs to**: do not move exhibits between main and appendix, and do not intermingle figures and tables. Keep the paper's existing convention for which block comes first (in this project, the figures file is `\input` before the tables file; preserve whatever the current convention is).
- **Per-section appendix numbering**: if the appendix numbers exhibits per section (e.g., `B.3`, `I.1`), floats can only be reordered *within* their section (in practice, within their source file). If an OUT OF ORDER flag involves exhibits in *different* appendix sections, do not fix it by moving a float across sections/files; instead list it in the final report as requiring either a change to the citation order in the text or a deliberate decision to move the exhibit to another section.
- **Uncited exhibits** have no citation anchor: leave them in their current position relative to their neighbors, and repeat their NOT CITED flag in the final summary.
- A float with several panel labels counts once, positioned by the first citation of *any* of its labels; its panels move with it.

## Step 3: Apply the reordering

Reorder by moving entire float environments (`\begin{figure}...\end{figure}`, `\begin{table}...\end{table}`, including sideways/starred/longtable variants) within their file:

- Preserve each float block exactly as-is (byte-for-byte), including its caption, labels, notes, and any `\input` of generated table files.
- Leave commented-out floats and interstitial material (`\clearpage`, comments, stray text) where they are; move only the active float blocks around them, keeping the file's blank-line/`\clearpage` rhythm sensible.
- Never edit files under `results/` or other script-generated files; the floats live in the hand-written `draft_*.tex` wrappers, and moving a whole float (with its `\input{results/...}`) is fine.
- Exhibit numbers and `\ref`s update themselves on recompilation since numbering follows document order; no reference text needs editing.

## Step 4: Verify

Rerun the scanner and re-do the analysis to confirm: (a) the set of exhibit labels is unchanged; (b) no OUT OF ORDER flags remain, except the cross-section cases excluded in Step 2. If something is still out of order, fix it before reporting (or explain why it cannot be fixed by reordering).

## Step 5: Report back

Summarize in chat:

- which floats were moved, with from/to positions (file and old/new neighbor exhibits);
- which flagged issues were *not* fixable by reordering (cross-section citation order, uncited exhibits) and what would fix them;
- the filename of the fresh check-exhibits-cited report from Step 1;
- a reminder to recompile the paper to refresh numbering.
