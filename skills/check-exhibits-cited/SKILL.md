---
name: check-exhibits-cited
description: Check that every figure and table (exhibit) in the paper and its appendix is cited somewhere (main text, appendix text, or another exhibit's notes) and that exhibits are first cited in numbering order; write a timestamped markdown report to the project's .claude folder. Use when the user calls /check-exhibits-cited or asks whether exhibits are all cited or cited in order.
---

# Check that exhibits are cited, and cited in order

## Step 1: Determine the root tex file

This must be the file that is actually compiled (the one containing `\documentclass`), since exhibit numbering follows document order. Priority: skill argument; else the tex file open in the IDE (if it lacks `\documentclass`, find the compiled file that `\input`s it); else ask.

## Step 2: Scan the document

```
python <path-to-this-skill>/scripts/scan_exhibits.py "<root>.tex"
```

The script flattens the document by following `\input`/`\include`/`\subfile` in document order and prints, in that order:

- `LABEL <label> <figure|table|none> <file>:<line> appendix=<yes|no>` for every `\label` (type is the innermost float environment; `none` means it is a section/equation label, not an exhibit);
- `REF <label> <file>:<line> in_float=<yes|no> appendix=<yes|no>` for every `\ref`/`\cref`/`\Cref`/`\autoref`/`\vref` (multi-label `\cref`s are split into one line each);
- `WARNING` lines for includes that could not be found or circular includes.

## Step 3: Analyze

1. **Exhibits** are the `LABEL` lines with type `figure` or `table`. Their document order within each series defines the numbering. There are up to four series, each numbered separately: main figures, main tables, appendix figures, appendix tables (`appendix=yes/no` gives the split).
2. **Subfigure/panel labels**: several labels can belong to one float (same file, adjacent lines, no intervening float). Group them: the float counts as cited if *any* of its labels is referenced. List the panel labels in the report row of the parent exhibit rather than as separate exhibits.
3. **Citations**: match `REF` lines to exhibit labels (ignore refs to `none`-type labels). Classify each citation by where it occurs: main text, appendix text, or inside another float (`in_float=yes`, i.e., a table/figure note). All three count as "cited."
4. **Flags**:
   - `NOT CITED`: an exhibit with zero references.
   - `OUT OF ORDER`: within each series, the order of *first* citations (by document order of the `REF` lines) should match the exhibits' numbering order. Flag any exhibit whose first citation comes after the first citation of a higher-numbered exhibit in the same series, and say which exhibit overtook it.
   - **Multiple appendices**: if the document numbers appendix exhibits per section (e.g., `\Alph{section}.\arabic{figure}`, giving A.1, B.1, ...), check appendix ordering only *within* each appendix section. Citation order across sections is unconstrained: a first-citation order of Figure A.1, A.2, B.1, A.3 is *not* a problem, but A.2 cited before A.1 is.

## Step 4: Write the report

Write to the project's `.claude/` folder as `exhibits_cited_{YYYYMMDD_HHMMSS}.md` (timestamped; never overwrite previous reports). Structure:

```markdown
# Exhibit citation report

- Root file: paper/PriceComparisonTools.tex
- Date: YYYY-MM-DD

## Summary of problems

- NOT CITED: Appendix Figure A3 (`fig:xyz`) — defined at paper/draft_figures_appendix.tex:120, never referenced.
- OUT OF ORDER: Figure 4 (`fig:abc`) first cited at paper/PriceComparisonTools.tex:210, after Figure 5's first citation (paper/PriceComparisonTools.tex:180).
- (or "None." if all exhibits are cited and in order)

## Main figures

| # | Label | Defined at | First cited | All citations | Flags |
|---|---|---|---|---|---|
| 1 | fig:abc | paper/x.tex:50 | paper/x.tex:30 (main text) | paper/x.tex:30 (main text); paper/y.tex:12 (table note) | |

## Main tables
...
## Appendix figures
...
## Appendix tables
...
```

- Number exhibits by their position within their series (1, 2, ... and A1/B1-style for the appendix if the document uses per-section numbering).
- Paths relative to the project root.
- Never edit any tex files as part of this skill; it is report-only.

## Step 5: Report back

Give the user the report filename and repeat the "Summary of problems" section in chat (or state that all exhibits are cited and in order).
