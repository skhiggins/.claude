---
name: check-files-used
description: Find every file the paper uses (a given tex entry file plus everything it references recursively) and report, folder by folder, which files in the project could be removed, flagging files not modified in over a year. Use when the user asks which files are used/unused by the paper, wants to clean up the project folder, or runs /check-files-used.
---

# Files-used audit

The paper's directory accumulates files (old figure versions, superseded tables, stale PDFs) that are no longer referenced by any compiled tex file. This skill maps everything the paper actually uses and reports the rest as removal candidates.

The argument (if given) is the tex file to start from; otherwise use the file currently open in the IDE if it is a plausible entry point (has `\documentclass` or is clearly a paper/appendix/response file). If neither is clear, ask the user which tex file to check.

**Other compiled documents:** the project may contain additional root documents (response letters, slides — any tex file with `\documentclass` that is not reached from the entry file). Run Step 1 on each of them too. Files used only by these documents get their own report section and are never removal candidates.

## Step 1: Collect all files used by the paper

1. Starting from the entry tex file, scan its live (non-dead) text for file references. Dead text is: anything after a non-escaped `%` on a line, anything inside `\begin{comment}...\end{comment}`, and anything inside `\iffalse...\fi`. Track references that appear *only* in dead text separately — the referenced file is not used by the compiled paper, but note it in the report (see Step 3).
2. Reference commands to catch: `\input{...}`, `\include{...}`, `\ExpandableInput{...}`, `\includegraphics[...]{...}`, `\overpic`, `\includepdf[...]{...}`, `\bibliography{...}` (append `.bib`), `\addbibresource{...}`, `\import{dir}{file}` / `\subimport`, `\subfile{...}`, `\lstinputlisting`, `\verbatiminput`, `\InputIfFileExists`. **Brace-less forms count too:** `\input` and `\ExpandableInput` (a `\@@input` alias) also accept a bare path terminated by whitespace, e.g. `\input results/tables/foo_panelA` — grep for `\\(input|ExpandableInput|@@input)\s+[^\s{]` in addition to the braced patterns (a 2026-08-23 audit missed such references and used table files were deleted as a result). Also honor any `\graphicspath{...}` declarations when resolving graphics. If `\documentclass` or `\usepackage` names a class/style that exists as a local `.cls`/`.sty` file in the project, count it as used.
   **Custom wrapper macros:** projects often define their own file-reading commands, e.g. `\newcommand{\inputnumber}[1]{\input{results/numbers/#1}}`. Before scanning, collect all macro definitions (`\newcommand`, `\renewcommand`, `\providecommand`, `\def`, `\NewDocumentCommand`, `\let`) in the entry file and everything it inputs (including local `.sty`/`.cls` files) whose body contains any reference command from the list above (or `\@@input`). Treat each such macro as an additional reference command, and resolve its argument through the definition's path template (prefixes, appended extensions, `#1` placement). Recurse: a wrapper of a wrapper also counts.
3. Resolve each path relative to the entry file's directory (LaTeX resolves from the compile root, even for references inside nested files). If an `\input`/`\include` argument has no extension, append `.tex`. For extensionless graphics, treat every existing candidate (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.eps`) as used — conservative, since which one the compiler picks depends on settings.
4. Recurse into every referenced `.tex` file (hand-written or script-generated) to collect further references, and so on until closure.
5. If a referenced file does not exist, note it for the report's end section (it would break compilation) and continue.
6. **epstopdf byproducts:** for every used `<name>.eps`, also mark `<name>-eps-converted-to.pdf` (and the variant spelling `<name>-converted-to-eps.pdf`) as used/auto-generated. These must never appear as removal candidates when their `.eps` is used. If the `.eps` itself is *unused*, both the `.eps` and its converted pdf are candidates; note the pairing.

## Step 2: Inventory the directory tree

1. List all files under the entry file's directory recursively (PowerShell `Get-ChildItem -Recurse -File`), recording each file's `LastWriteTime`.
2. Exclude from the analysis entirely: `.git/`, `.claude/`, `.vscode/`, `.texpadtmp/` (and similar editor/build temp folders), and compile artifacts of any tex file (`.aux`, `.log`, `.out`, `.toc`, `.lof`, `.lot`, `.bbl`, `.blg`, `.synctex`, `.synctex.gz`, `.fls`, `.fdb_latexmk`, `.nav`, `.snm`, `.vrb`). These are regenerable or out of scope; mention in one line of the report that they were skipped.
3. Classify every remaining file: **used** (directly or transitively, per Step 1), **dead-reference only** (referenced only in commented-out text), or **unused**.
4. **Safety net:** before finalizing, grep each unused file's basename (without extension) across all tex files in the project. If it appears in live text, the file was reached by a reference form Step 1 did not anticipate: reclassify it as used and note the unrecognized form in the report. If it appears only in dead text, keep it a candidate but flag it in the Notes column.
5. A file is **>1 year old** if its `LastWriteTime` is more than 365 days before today.

## Step 3: Write the report

Write `files_used_YYYY-MM-DD.md` (today's date) in the project's `.claude/` directory. If a report with that name already exists, ask before overwriting, or append `_HHMM`. Structure:

```markdown
# Files-used audit: <entry file> (<date>)

Summary: N files used by the paper; M unused files are removal candidates, of which K have not been modified in over a year. Build artifacts and .git/.claude/.vscode folders were skipped.

## Files used by the paper

### (root)
- main.tex, references.bib, ...

### results/tables
- ...

## Removal candidates

### (root)
| File | Last modified | >1 year old | Notes |
|---|---|---|---|
| old_draft.pdf | 2024-03-02 | yes | |
| fig3.tex | 2026-05-11 | no | referenced only in commented-out text (main.tex L123) |

### results/figures
| ... |
```

- Subsections are folders relative to the entry file's directory, in path order; root-level files go under "(root)". Omit folders with nothing to show in that section.
- The used-files sections are compact bullet lists (no tables). The removal-candidates sections are tables with columns: File, Last modified (date), >1 year old (yes/no), Notes.
- Notes column: flag dead-reference-only files (with the location of the commented-out reference), epstopdf byproducts of unused `.eps` files, and anything else that argues for caution before deleting.
- **Wholly-unused folders:** if an entire folder (or folder subtree) is unused and contains more than ~20 files — typical for code, logs, or data directories that are simply not paper assets — do not list every file. Replace the table with one summary line: folder, file count, last-modified range, and whether all files are >1 year old. The user can ask for the full listing of a specific folder afterward.
- End with a short section listing referenced files that do not exist (would break compilation) and any references the skill could not resolve (e.g., paths built from macros). Omit if empty.

## Practical notes

- **Never delete anything.** The report is advice; the user decides what to remove.
- **If later asked to carry out deletions based on a report:** do not trust the report blindly — it may be stale or wrong (on 2026-08-23, 11 used table files were deleted from a report that had misclassified them). Re-run the Step 2 safety-net grep on each file at deletion time, and after deleting, recompile every compiled document in the project (paper and response docs) and confirm zero "can't find file" errors before considering the cleanup done.
- Age is supporting evidence, not proof: a script-generated table can be regenerated any time (so its timestamp is recent even if obsolete), and an old file may still be the canonical source of something. The used/unused classification is the primary signal; the age flag is secondary.
- Fast approach: one `Get-ChildItem -Recurse` pass for the inventory and timestamps; Grep across `*.tex` for the reference commands; then resolve and recurse only through files actually referenced.
