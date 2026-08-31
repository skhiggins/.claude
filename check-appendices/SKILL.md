---
name: check-appendices
description: Check that the order of appendix sections matches the order in which the appendices are first cited in the paper (citing any exhibit or label inside an appendix counts as citing that appendix), write a timestamped report to the project's .claude folder, then automatically reorder the appendix sections to fix any violations. Use when the user calls /check-appendices or asks whether appendices are in citation order.
---

# Check and fix appendix ordering

## Step 1: Determine the root tex file

This must be the file that is actually compiled (the one containing `\documentclass`). Priority: skill argument; else the tex file open in the IDE (if it lacks `\documentclass`, find the compiled file that `\input`s it); else ask.

## Step 2: Scan the document

```
python <path-to-this-skill>/scripts/scan_appendix_order.py "<root>.tex"
```

The script flattens the document by following `\input`/`\include`/`\subfile` in document order and prints:

- `APPENDIX <idx> <file>:<line> <title>` for each `\section` after `\appendix`/`\begin{appendices}` (idx = current position: 1 = Appendix A, etc.);
- `LABEL <label> in=<idx|main> <file>:<line>` for every `\label`, attributed to the appendix section containing it;
- `REF <label> loc=<idx|main> <file>:<line>` for every reference, with the location of the reference itself;
- `WARNING` lines for unresolved or circular includes.

## Step 3: Analyze

1. **Attribution**: an appendix section owns every label defined inside it — the section's own label, plus labels of exhibits, subsections, equations, and propositions. Citing *any* of these counts as citing the appendix (per the user's rule, citing an exhibit from an appendix counts as the first citation of that appendix).
2. **Anchor**: each appendix's anchor is the document-order position of the first `REF` to any of its labels that occurs *outside the appendix itself* (`loc` differs from the appendix's idx). Main-text citations come before all appendix-located citations in document order, so using flat document order handles both.
3. **Flags**:
   - `OUT OF ORDER`: the sequence of anchors should be non-decreasing in appendix order (A's anchor before B's, etc.). Flag each appendix whose anchor precedes the anchor of an earlier-lettered appendix, and say which appendix it should precede.
   - `NOT CITED`: an appendix none of whose labels is ever referenced from outside it. These have no anchor: leave them in place (keep their relative position) and flag them.

## Step 4: Write the report

Write to the project's `.claude/` folder as `check_appendices_{YYYYMMDD_HHMMSS}.md` (timestamped; never overwrite previous reports). Include: current order (letter, title, source file, defining `\section` location), each appendix's anchor (label cited, file:line of the citation), the flags, and the target order. Then state which moves will be made.

## Step 5: Fix the ordering

Reorder the appendix sections to match the anchor order:

- Identify the movable unit for each appendix: the contiguous block that brings it into the document. In this project that is either an inline block in the root file (e.g., `\startanappendix` + `\section{...}\label{...}` + `\input{...}` and any attached lines like `\setcounter{prop}{0}`) or a `\startanappendix` + `\input{draft_appendix_*.tex}` group in `draft_sections_appendix.tex`. Move whole units byte-for-byte; do not edit inside the appendix content files.
- Preserve interstitial comments and commented-out blocks in place where reasonable; keep each unit's `\startanappendix`/`\clearpage` rhythm intact.
- Uncited appendices keep their current position relative to their neighbors.
- Appendix letters and all `\ref`s update themselves on recompilation; no reference text needs editing.
- Never edit files under `results/` or other script-generated files.

## Step 6: Verify and report back

Rerun the scanner and confirm: (a) the set of appendix titles and labels is unchanged; (b) anchors are now non-decreasing (except uncited appendices). Then summarize in chat: the old and new appendix order (with old and new letters), which units were moved in which file, any NOT CITED appendices, the report filename, and a reminder to recompile so letters and cross-references refresh.
