---
name: check-input-numbers
description: Check that every "input number" fragment (a script-generated .tex file containing a single number, pulled into the paper via \input) ends with a `%` immediately after the number, so LaTeX spacing is correct. Scans the given or currently-opened tex file plus all tex files it \inputs recursively. Produces a markdown report listing only the fragments that are missing the trailing `%`. Use when the user asks to check input numbers, number fragments, or trailing percent signs in \input files.
---

# Input-number `%` audit

Every number our scripts compute is printed into a small `.tex` fragment ("input number") and pulled into the paper with `\input{...}`. Each fragment must end with a `%` **immediately after the number** — otherwise the end-of-file newline becomes a space in the typeset text. This skill finds fragments missing that `%`.

The argument (if given) is the tex file to start from; otherwise use the file currently open in the IDE if it is a plausible entry point (has `\documentclass` or is clearly a paper/appendix file). If neither is clear, ask the user which tex file to check.

## Step 1: Collect all \input references recursively

1. Starting from the entry tex file, find every `\input{...}`, `\include{...}`, and `\ExpandableInput{...}` on non-comment text (skip anything after a non-escaped `%` on each line, and skip commented-out lines — a fragment referenced only in dead text is not compiled).
2. Resolve each argument relative to the entry file's directory (LaTeX resolves paths from the compile root). If the argument has no extension, append `.tex`.
3. Recurse into every referenced file that is itself hand-written tex (section files, appendix text, response documents) to collect further `\input`s. Do not recurse into script-generated fragments.
4. If a referenced file does not exist, note it for the report's end section (it would break compilation) and continue.

## Step 2: Classify each referenced file

Only **input numbers** are in scope: files whose content — after ignoring full-line comments (files often have a comment line above the number) — is a single short value on one line: a number, possibly with a sign, decimals, thousands separators, or adjacent characters like `\$`, `\%`, or a unit.

Out of scope (do not check, do not report): table fragments (contain `&`, `\\`, `\midrule`, `\multicolumn`, ...), figure includes, and whole-document parts like sections or appendices.

If a file is ambiguous (e.g., a short phrase rather than a number), treat it as an input number if it is clearly a script-generated inline fragment; mention it in the report's end section if unsure.

## Step 3: Check the trailing `%`

For each input number, the value must be followed **immediately** by `%` — no space, tab, or newline between the value and the `%`. A newline after the `%` is fine. Flag the file when:

- the value is followed by end-of-file or a newline with no `%`, or
- there is whitespace between the value and the `%` (the whitespace still gets typeset).

Do not flag correct files.

## Step 4: Write the report

Write `input_numbers_YYYY-MM-DD.md` (using today's date) in the project's `.claude/` directory. If a report with today's date already exists, overwrite it. Structure:

```markdown
# Input-number `%` audit: <entry file> (<date>)

Summary: N fragments missing the trailing `%`, out of K input numbers checked across the files reachable from <entry file>. Correct fragments are not listed.

## Missing trailing `%`

1. [path/to/fragment.tex](path/to/fragment.tex) — content: `6.8` — referenced from [file.tex:123](file.tex#L123)
2. ...
```

- List **only** the failing fragments. If none fail, say so in one line.
- For each failing fragment, show its content (the value as it appears) and at least one place it is `\input` from, as markdown links with relative paths.
- End with a short note listing any referenced files that do not exist and any files you were unsure how to classify. Omit this section if empty.

## Practical notes

- These fragments are produced by scripts (Stata/R/Python). **Never edit a fragment to fix it** — the fix belongs in the generating script. The report is for the user to update their scripts.
- A fast first pass: check whether each candidate file's last non-whitespace character is `%`; then verify flagged cases by reading the file, and confirm borderline content classifications by reading how the fragment is used in the paper.
