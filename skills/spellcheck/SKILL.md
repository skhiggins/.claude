---
name: spellcheck
description: Run the LTeX+ spellchecker on a LaTeX file and all tex files it \input/\includes (recursively), classify each flagged word as needing a fix or safely ignorable, and write a two-section timestamped report to the project's .claude folder. Use when the user calls /spellcheck (optionally passing a .tex path) or asks to spellcheck the paper.
---

# Spellcheck a LaTeX paper with LTeX+

## Step 1: Determine the root tex file

Priority order:
1. A `.tex` path passed as the skill argument.
2. The `.tex` file currently open in the IDE (from the `ide_opened_file` context).
3. Otherwise, ask the user which file to check.

## Step 2: Run the checker

```
python <path-to-this-skill>/scripts/run_ltex.py "<root>.tex"
```

Use a 10-minute timeout. Notes on the script:

- It recursively collects every tex file reached via `\input`, `\include`, or `\subfile` from the root file (resolved relative to the root file's directory, falling back to the including file's directory), skips included files that contain no words (e.g., generated number snippets), and runs the LTeX+ CLI bundled with the VSCode extension on all of them in as few invocations as possible (each invocation has ~40s of JVM startup).
- It reads the existing LTeX+ dictionary from `.vscode/settings.json` (`ltex.dictionary.*` keys), so words already added via /spellcheck-define are not re-flagged.
- Exit code conventions: 0 or 3 (issues found) are both success; anything else is a real error, and the script prints the CLI's stderr.
- Output format per issue: `path:line:col: info: 'word': ... [RULE_ID]`, followed by the source line and `Use 'suggestion'` lines.

## Step 3: Classify the spelling issues

Only lines with rule `[MORFOLOGIK_RULE_*]` are spelling errors; ignore other rules (grammar/punctuation) unless the user asks for them.

For each flagged word, use the context line to classify it:

- **To fix**: real typos and misspellings (e.g., "inflations expectations", "teh"). When unsure, put it here with a note rather than silently ignoring it.
- **Safe to ignore**: proper nouns (author names, places, institutions, e.g., "Attanasio", "CMF"), field terminology and intentional variant spellings (e.g., "heteroskedasticity"), non-English words used deliberately, acronyms, and package/command artifacts that leak through.

## Step 4: Write the report

Write the report to the project's `.claude/` folder as `spellcheck_{YYYYMMDD_HHMMSS}.md` (timestamp of the run, so previous reports are never overwritten). Use exactly this structure (the helper skills /spellcheck-define and /spellcheck-fix parse the most recent report, and the user may move rows between sections before running them):

```markdown
# Spellcheck report

- Root file: paper/PriceComparisonTools.tex
- Date: YYYY-MM-DD
- Files checked: N

## To fix

| File | Line | Word | Fix | Notes |
|---|---|---|---|---|
| paper/appendix.tex | 123 | teh | the | |

## Safe to ignore

| File | Line | Word | Reason |
|---|---|---|---|
| paper/PriceComparisonTools.tex | 365 | Attanasio | author name |
```

- File paths relative to the project root; sort rows by file then line.
- The same word may appear on multiple lines; list every occurrence in "To fix" (each needs its own edit), but only once per word in "Safe to ignore" (the dictionary is word-level; use the first occurrence's file/line).
- If a flagged word is in a **generated** tex file (anything under `results/`, or other script-produced tables/numbers), never propose editing that file: note in the Notes column that the fix belongs in the generating script.

## Step 5: Report back

Tell the user: the report filename, counts per section, any includes that could not be found, and that they can edit the report (move rows between sections, change fixes) and then run `/spellcheck-define` to add the ignorable words to the LTeX+ dictionary and/or `/spellcheck-fix` to apply the fixes.
