---
name: fix-typos
description: Apply the corrections listed in the "To fix" section of the latest /check-for-typos report (.claude/typos_*.md) to the LaTeX source files, using each row's verbatim Original → Fix substrings. Use when the user calls /fix-typos after reviewing a typo report.
---

# Apply typo fixes from the report

## Step 1: Locate and re-read the report

Reports live in the project's `.claude/` folder as `typos_{YYYYMMDD_HHMMSS}.md`. Use the report passed as the skill argument if given; otherwise the one with the latest timestamp in its filename (confirm with the user if it looks stale, e.g., older than the source files' last edits).

**Always re-read the report now, even if you wrote it earlier in this session**: the user may have moved rows between `## To fix` and `## Unsure`, or edited a `Fix`. Act only on the current contents. Rows under `## Unsure` are not applied unless the user moved them into `## To fix`.

## Step 2: Apply each fix

For every row in `## To fix` (paths relative to the project root):

1. **Generated files**: if the file is script-produced (anything under `results/`, or other generated tables/numbers), do NOT edit it — the fix belongs in the generating script. Collect these to report.
2. Read the target file around the listed line (the `Line` cell is usually a markdown link such as `[123](../main.tex#L123)`; the number is the line). Line numbers may have shifted since the report was written: if `Original` is not on that line, search nearby lines, then the whole file, using the listed line as the anchor to choose among multiple occurrences.
3. Apply the edit with the Edit tool, `old_string` = the row's `Original` (verbatim, backticks removed), `new_string` = the row's `Fix`. If `Original` matches more than once in the file, extend it with adjacent text from the source line until it is unique; never use replace-all.
4. If `Original` cannot be found (likely already fixed by hand), skip the row and note it.
5. Fix only the listed occurrence; other occurrences of the same slip are separate rows.
6. **If an Edit call fails for any reason, stop immediately**: do not retry; show the user the intended change (file, old text, new text) and let them make it.

Text inside a `%<*tag>`…`%</tag>` region that another document pulls in (`\quotepaper`/`\quotenotes`) needs fixing in the source document only; do not hand-edit the pulling document. Hand-duplicated text (captions, hand-copied quotes) has its own row per file in the report — apply each.

## Step 3: Update the report

Edit the report: delete the rows that were applied, and annotate the rows that remain (Notes column: "not found; already fixed?" or "generated file; fix in script") so the report shows only the outstanding state. Leave `## Unsure` untouched.

## Step 4: Report back

Summarize: fixes applied (with file:line links), rows skipped and why, and generated-file findings that need script changes. If any fix touched LaTeX structure (braces, quote marks, `\ref` targets), recommend recompiling with the full pdflatex/biber/pdflatex sequence — and, for documents that pull tagged regions from another document, compiling the source document first. Suggest re-running `/check-for-typos` on the edited file to confirm a clean result.
