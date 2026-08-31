---
name: check-eps
description: For every figure included in the paper (recursively through all tex files the paper inputs), check whether a non-EPS figure has an EPS version of the same file and whether that EPS is newer than the included version; write a timestamped markdown report to the project's .claude folder. Use when the user calls /check-eps or asks whether figures have (up-to-date) EPS versions.
---

# Check for EPS versions of included figures

## Step 1: Determine the root tex file

This must be the file that is actually compiled (the one containing `\documentclass`), since `\graphicspath` is set there. Priority: skill argument; else the tex file open in the IDE (if it lacks `\documentclass`, find the compiled file that `\input`s it); else ask.

## Step 2: Scan the document

```
python <path-to-this-skill>/scripts/scan_figures.py "<root>.tex"
```

The script flattens the document by following `\input`/`\include`/`\subfile` in document order, honors `\graphicspath`, and prints one line per `\includegraphics`:

- `FIG <texfile>:<line> <as-written> resolved=<path|NOT-FOUND> ext=<ext> eps=<path|none> fig_mtime=<iso|na> eps_mtime=<iso|na> eps_newer=<yes|no|na>`
- `WARNING` lines for tex includes that could not be found or circular includes.

Extensionless `\includegraphics` arguments are resolved using pdflatex's search order (.pdf, .png, .jpg, .jpeg, .eps). For each resolved non-EPS figure, the script looks for a same-name `.eps` in the same directory and compares modification times.

## Step 3: Analyze

The paper's policy is that whenever an .eps version of a figure exists, the tex should `\includegraphics` the .eps. So every non-EPS figure that has an .eps version is an action item for an RA. Classify each `FIG` line:

1. **Already EPS** (`ext=.eps`): nothing to check.
2. **Non-EPS with EPS version** (`eps=<path>`): needs RA review — the include should be switched to the .eps. Sub-classify by mtime gap:
   - **Same run** (eps mtime within a few seconds of the included file, or newer): the .eps was written by the same script run, so switching the extension should suffice.
   - **Stale** (eps meaningfully older than the included file): the .eps may show an older version of the figure; the generating script should be rerun (or the figure confirmed unchanged) before switching. Note the gap size — mtimes are a heuristic and cannot distinguish a no-change rerun from a real edit.
3. **Non-EPS without EPS version** (`ext` not `.eps`, `eps=none`): no EPS exists (often screenshots, where EPS may not be needed).
4. **Not found** (`resolved=NOT-FOUND`): the included figure file itself is missing.

If the same figure file is included more than once (e.g., main text and appendix), report it once and list all include locations.

## Step 4: Write the report

Write to the project's `.claude/` folder as `check_eps_{YYYYMMDD_HHMMSS}.md` (timestamped; never overwrite previous reports). Structure:

```markdown
# EPS figure report

- Root file: paper/PriceComparisonTools.tex
- Date: YYYY-MM-DD

## Summary

- N figures included; A already .eps; B included as .pdf/.png even though an .eps exists; C non-eps with no .eps; D not found.
- **Action needed: all B figures in the table below need to be checked by an RA.** Each include should be switched to the .eps; for rows marked "stale," the generating script should be rerun (or the figure confirmed unchanged) first.
- No edits have been made to any tex files; this report is the RA's checklist.

## Non-EPS figures with an EPS version — all need RA review

| Included file | Included at | Fig mtime | EPS mtime | EPS newer? | Note |
|---|---|---|---|---|---|
| results/graphs/analysis/x.pdf | paper/draft_figures.tex:74 | 2026-05-01 10:00 | 2026-06-01 09:00 | no | stale (~30 days) |

## Non-EPS figures with no EPS version
...
## Figures included as EPS
...
## Missing figure files / warnings
...
```

- Paths relative to the project root.
- Never edit any tex files or figure files as part of this skill; it is report-only.

## Step 5: Report back

Give the user the report filename and repeat the Summary section in chat, stating how many includes need to be switched to .eps and which of those have a stale .eps. Never make the switches yourself — the report is a checklist for an RA.
