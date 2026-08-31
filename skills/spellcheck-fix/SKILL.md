---
name: spellcheck-fix
description: Apply the corrections listed in the "To fix" section of the latest spellcheck report (.claude/spellcheck_*.md) to the LaTeX source files. Use when the user calls /spellcheck-fix after reviewing a /spellcheck report.
---

# Apply spelling fixes from the report

## Step 1: Locate and re-read the spellcheck report

Reports live in the project's `.claude/` folder as `spellcheck_{YYYYMMDD_HHMMSS}.md`. Use the report passed as the skill argument if given; otherwise use the one with the latest timestamp in its filename (confirm with the user if that seems stale).

**Always re-read the file now, even if you generated it earlier in this session**: the user may have moved rows between sections or edited the proposed fixes after /spellcheck ran. Act only on the current contents.

## Step 2: Apply each fix

For every row in the `## To fix` section (paths are relative to the project root):

1. **Generated files**: if the file is script-produced (anything under `results/`, or other generated tables/numbers), do NOT edit it; the fix must be made in the generating script. Collect these to report to the user.
2. Read the target file around the listed line. Line numbers may have shifted since the report was written: if the word is not on that line, search nearby lines, then the whole file, using the listed line as the anchor to pick among multiple occurrences.
3. Apply the `Fix` column value with the Edit tool, preserving surrounding LaTeX exactly. If the word cannot be found (likely already fixed manually), skip it and note that.
4. Fix only the listed occurrence, not all occurrences of the word, unless rows list each occurrence.

## Step 3: Update the report

Edit the report: remove the rows that were applied, and annotate skipped rows (e.g., "not found; already fixed?" or "generated file; fix in script") in the Notes column so the report reflects the remaining state.

## Step 4: Report back

Summarize: fixes applied, rows skipped and why, and any generated-file findings that need changes in the generating scripts. Suggest re-running /spellcheck to verify a clean result.
