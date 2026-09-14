---
name: check-for-typos
description: Read the full text of a LaTeX file (the one open in the IDE, or the path passed as the argument) plus every tex file it \input/\includes recursively, and write a timestamped markdown report of typos — misspellings, wrong-word errors (though/through, and/as), missing or doubled words, agreement slips, and punctuation/bracket glitches — that a dictionary spellchecker misses. Use when the user calls /check-for-typos or asks to proofread a tex file for typos. Complements /spellcheck (LTeX dictionary check); the companion /fix-typos applies the report.
---

# Check a LaTeX document for typos

This is a full read-through by Claude, not a dictionary check: it catches errors that are real words in the wrong place ("though" for "through", "and" for "as", "then" for "than"), dropped or doubled words, and punctuation slips that LTeX+ (/spellcheck) does not flag. It reports; it never edits. The companion `/fix-typos` applies the report.

## Step 1: Determine the root tex file

Priority order:
1. A `.tex` path passed as the skill argument.
2. The `.tex` file currently open in the IDE (`ide_opened_file` context).
3. Otherwise, ask the user which file to check.

The root need not be the document's main file: if the open file is itself an `\input` section or appendix file, check it and whatever *it* inputs. Say in the report which file was the root.

## Step 2: Collect the compiled prose

Run the helper script from the skill directory (never a temp copy):

```
python <path-to-this-skill>/scripts/collect_tex.py "<root>.tex" --project-root "<project root>"
```

It writes `.claude/typos_source_<timestamp>.txt`: the root file with every `\input`/`\include`/`\subfile` expanded in place (document order), comment text stripped but the `%` that starts each comment kept (see Step 4 on line-break spacing), blank lines dropped, and each remaining line prefixed `path:line:` with the *original* line number. It also:

- drops the argument of macros the document defines as empty (`--drop-macros`, default `cut,cutrr`) — check the preamble of the project's main file and adjust if other no-op macros exist;
- skips includes under `results/`, `tables/`, `figures/`, `numbers/` as script-generated and lists them (`--include-generated` to read them anyway — only useful for spotting typos to fix in the generating scripts);
- warns about includes it could not find.

Read the script's summary: note the file list, line count, skipped generated files, and missing includes for the report.

## Step 3: Read the entire collected text

Read the collected file with the Read tool in sequential chunks of at most 800 lines (`offset`/`limit`), from the first line to the last. Do not sample, skim, or stop early; do not grep for suspected patterns instead of reading. For long documents, keep a checklist of chunks (e.g., with TodoWrite) and append findings to a draft of the report after each chunk so nothing is lost if the context is summarized.

Read the LaTeX as a copyeditor would read the rendered text: mentally drop markup wrappers (`\new{}`, `\added{}`, `\um{}`, `\sh{}`, `\short{}`, `\emph{}`, `\textbf{}`), treat `\citet`/`\citep`/`\ref` as names and numbers, and read math only for surrounding prose (do not proofread formulas).

## Step 4: What counts as a typo

**Flag (To fix)** — errors any careful copyeditor would mark as mistakes:

- Misspellings and dropped/transposed letters ("aleviated", "heterogneity", "wnat"), including ones inside comments-turned-live text.
- Wrong-word substitutions that pass a spellchecker: though/through, and/as, then/than, affect/effect, its/it's, form/from, to/too, of/or, lose/loose, principal/principle, complimentary/complementary, and the like.
- Missing words ("we find the effect is", "in line deciding"), doubled words ("the the", "of of", "that that" when not grammatical), and duplicated phrases left by editing ("in in the").
- Grammar slips that are unambiguous errors: subject–verb agreement, a/an before vowel sounds, plural/singular mismatch ("this results"), wrong verb form after a citation ("\citet{x} shows" for a multi-author paper when the document's convention is plural — check the document's convention first), dangling fragments left by partial edits.
  - For subject–verb (and other number) disagreements, do not assume the subject is correct as written and the verb must change. Consider both repairs: fix the verb to match the subject, or fix the subject's number to match the verb. Pick the one that makes the sentence say what the author evidently meant, given the surrounding text (what is being counted or measured, whether the same noun is singular or plural nearby, and what the rest of the paragraph refers to). Example: in "The magnitude of the interest rate increases in these studies are even larger", the better fix is usually "The magnitudes of the interest rate increases ... are even larger" (several studies, several magnitudes), not "is even larger". When both repairs are defensible, put the row under **Unsure** and give both alternatives in the `Fix`/note columns rather than silently choosing the verb change.
- Wrong or missing prepositions only when unambiguously wrong ("focused in monitoring" → "focused on").
- Punctuation and typesetting glitches visible in the output: double periods or commas, missing space after sentence punctuation, space before a period/comma, unbalanced parentheses/brackets/braces in prose, wrong LaTeX quote marks (`"word"` or `''word``` instead of ``` ``word'' ```), a period inside vs outside a parenthesis inconsistently, stray characters, a sentence starting lowercase after a period, capitalization errors in proper nouns.
- Cross-reference text errors: "Table" where the `\ref` is a figure, "Section" for an appendix, an `\eqref` referred to as a table, a footnote sentence that does not end with a period.
- Line-break spacing errors. A newline in the source is a space in the output unless the line ends with `%`, and the collected text keeps every `%` for exactly this check. Flag a line that does **not** end in `%` when the next non-blank line starts with `,`, `;`, `.`, `)`, `\footnote`, or `\cite`: the output will show a space before that punctuation or footnote mark. The fix is a trailing `%` on the first line (or moving the punctuation up), not stripping the `%`. Conversely, a line that ends in `%` followed by a line starting with punctuation renders correctly; do not flag it. Look at the `%`, not at the raw line break, before deciding either way.

**Unsure** — list separately, with a one-line reason, when it could be deliberate:

- Inconsistent forms within the document (take-up vs takeup, FinTech vs fintech, e-mail vs email, "percent" vs `\%`), British vs American spelling mixed.
- Possible missing article or awkward preposition where the sentence is still grammatical.
- Text inside `\new{}`/`\added{}` that reads like an unfinished edit.
- A `%` in the middle of a prose line that hides the rest of the line (the collected text ends at that `%`). This may be a deliberate comment-out, but it may also be a `%` meant for the end of the line that now silently drops a clause or a citation; give the hidden text's location so the user can decide.
- Hardcoded numbers or dates that look mistyped (these belong to /check-hardcoded, but flag an obvious digit slip).

**Do not flag** — out of scope, even if you would write it differently: word choice, sentence structure, hedging, redundancy, tone, Oxford commas, hyphenation preferences that are consistent, en/em-dash style, house-style choices such as colon capitalization (see project memory for settled conventions and do not re-litigate them), and anything inside formulas, `\label`/`\ref` keys, URLs, file paths, or bib keys.

## Step 5: Write the report

Write `.claude/typos_{YYYYMMDD_HHMMSS}.md` in the project's `.claude/` folder (timestamp of the run, never overwrite). Use exactly this structure (`/fix-typos` parses it, and the user may move rows between sections or edit fixes before running it):

```markdown
# Typo report

- Root file: paper/BehavioralFirmsProfitableOpportunities.tex
- Date: YYYY-MM-DD
- Files read: N (list)
- Skipped as generated: (list, or none)
- Includes not found: (list, or none)

## To fix

| File | Line | Original | Fix | Notes |
|---|---|---|---|---|
| paper/appendix.tex | [123](../paper/appendix.tex#L123) | `can be aleviated though email` | `can be alleviated through email` | two errors in one span |

## Unsure

| File | Line | Original | Suggested | Why unsure |
|---|---|---|---|---|
| paper/main.tex | [456](../paper/main.tex#L456) | `take-up` / `takeup` | pick one | both forms used; 14 vs 3 occurrences |
```

- `Line` is a markdown link so the user can click straight to the line: `[123](<path from the report file to the source file>#L123)`. The report lives in `.claude/`, so a source file at the project root is `../main.tex#L123` and one in `paper/` is `../paper/main.tex#L123`. When a row covers several lines, link each number separately (`[400](../main.tex#L400), [997](../main.tex#L997)`), and link line numbers mentioned in Notes the same way (`[L855](../main.tex#L855)`). Keep `File` as plain text.
- `Original` is a **verbatim substring of the source line**, in backticks, long enough to be unique on that line and to include every character the fix changes (keep surrounding LaTeX such as braces and `\%` exactly). `Fix` is the replacement for exactly that substring. `/fix-typos` applies `Original` → `Fix` with an exact-match edit, so both must be copyable as-is.
- One row per occurrence; sort rows by file (document order) then line.
- If a typo is in a **generated** file (`results/` etc.), never propose editing it: put "fix in generating script" in Notes.
- If the typo sits inside a `%<*tag>`…`%</tag>` region that another document pulls in (the response doc's `\quotepaper`/`\quotenotes`), note "shared tagged region; edit here only" — fixing the paper fixes both. If instead the same text is hand-duplicated in another document (captions, hand-copied quotes), add a second row for the other file so both get fixed.

## Step 6: Report back

Tell the user: the report filename, counts for To fix and Unsure, files read and skipped, any includes not found, and that they can edit the report (move Unsure rows into To fix, change a Fix) and then run `/fix-typos` to apply it. Do not apply any fix yourself.
