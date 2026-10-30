---
name: diagnose-latex
description: Diagnose a LaTeX compilation error and report its cause and fix, without editing any tex file. Reads the existing .log (and .blg) first, using a parser that handles both "! Message" and -file-line-error formats; only if the log shows no error, is missing, or is stale does it reproduce the build in a scratch output directory. Takes a tex file path (or @-mention) as the argument, or uses the file open in the IDE. Use when the user calls /diagnose-latex or asks why a tex file does not compile, what a LaTeX error means, or what is causing a compilation error.
argument-hint: [path/to/file.tex]
---

# Diagnose a LaTeX compilation error

Goal: tell the user what caused the error and exactly how to fix it. **Never edit the tex files** (nor any auto-generated file under `results/`); the deliverable is a diagnosis in chat. Do not write a report file.

The order matters: **the existing log comes first.** It records the build the user actually ran, with the user's flags and their buffer contents at that moment. Recompiling overwrites it and can make a transient error disappear. Recompile only under the conditions in Step 5, and then only into a scratch directory.

## Step 1: Identify the tex file and its root document

1. The skill argument, if given. It may arrive as an IDE @-mention (`@paper/foo.tex`); strip a leading `@`. A relative path is relative to the working directory.
2. Otherwise, the tex file currently open in the IDE.
3. Otherwise, ask the user which file (AskUserQuestion listing the `.tex` files that have a `\documentclass`).

Find the **root document**, which is the file whose log matters:

- If the file has a `% !TEX root = ...` magic comment in its first lines, that names the root.
- Else, if the file contains `\documentclass`, it is the root.
- Else it is an `\input`/`\include`d fragment: search the project's `.tex` files for an uncommented `\input{...}`, `\include{...}`, or `\subfile{...}` of it (match the path with and without `.tex`, relative to the including file's folder). Skip conflicted copies (`(... conflicted copy ...)`), `archive/`, and obviously stale variants. If several roots include it, ask which one the user compiled.

In a referee-response setup (a response document that pulls text from the paper via `\externaldocument`, `catchfilebetweentags`, `\ExecuteMetaData`, etc.), an error in the response document can originate in the paper's files. Keep both in mind.

## Step 2: Locate the log and check that it is the right one

1. Log location: `<root folder>/<jobname>.log` by default. If LaTeX Workshop uses an output directory, the log is there instead: check `latex-workshop.latex.outDir` in the workspace `.vscode/settings.json` and in the user settings (`%APPDATA%\Code\User\settings.json` on Windows), and any `-outdir=`/`-output-directory=` in `latex-workshop.latex.tools`. Note the flags the user's tools pass (for example `-file-line-error`, `-shell-escape`), since Step 5 must reproduce them.
2. Make sure no build is running, because a log being written is incomplete:
   `tasklist | findstr /i "latexmk pdflatex xelatex lualatex biber bibtex"`. If one is running, wait for it and say so.
3. Freshness: compare the log's modification time with the root `.tex` and with every file it inputs that changed recently (`ls -l --time-style=+%H:%M:%S` on the root, the open file, and the bibliography). A source file saved **after** the log means the log may describe an error that is already fixed, or miss a new one. Note this explicitly in the report.
4. Unsaved editor changes are invisible to every check here. If the user's description does not match what the files show, say that the error may come from unsaved edits.
5. If available, also call the IDE diagnostics tool (`mcp__claude-vscode__getDiagnostics` with the root's and the open file's URIs) and keep entries with severity `Error` and source `LaTeX`. LaTeX Workshop puts the last build's parsed errors there, which can survive after the log has been overwritten. The output can be large; filter it with grep for `"severity": "Error"`.

## Step 3: Parse the log

```
python <path-to-this-skill>/scripts/parse_latex_log.py "<log>" --blg "<root folder>/<jobname>.blg"
```

The script unwraps TeX's 79-character line breaks (so labels and file names split across lines are still matched), lists every error in order with its file and line, gives the `l.<n>` context TeX printed, and summarizes the warnings that matter: missing files, undefined references and citations, multiply defined labels, and rerun requests. It also reports the run status (output written, emergency stop, fatal error, interrupted run) and the biber/bibtex log's errors and warnings. A missing `.blg` means the bibliography tool has not run since the build files were last cleaned.

How to read it:

- **Do not trust "Errors: 0" blindly.** If the script prints a WARNING about unparsed `file:line: message` lines, read those log lines directly; they are usually errors in a format the parser does not recognize. When the IDE diagnostics (Step 2) show errors the script missed, confirm with `grep -nE "^!|:[0-9]+: " <log>`.
- **Focus on the first error.** Later errors are usually consequences of it (one missing `}` can produce a dozen).
- **File attribution:** with `-file-line-error` output the file is exact; otherwise it comes from TeX's open-file stack, which is a heuristic. When it is marked heuristic, confirm it by searching the candidate files for the context text (the part of the `l.<n>` line before the break).
- **The TeX context:** in `l.<n> <before>` followed by `<after>` on the next line, TeX had read up to the end of `<before>` when the error occurred. The culprit is usually the last token of `<before>`.
- A log with zero errors but the run status "interrupted" (no memory-usage block at the end) means the previous build was stopped partway. The error the user saw may have been the interruption itself or a truncated `.aux` on the next run.

## Step 4: Inspect the source

1. Read the attributed file around the reported line (about 10 lines on each side) and quote the offending line in the report.
2. If the error is inside an auto-generated file (`results/tables/`, `results/numbers/`, figures), the fix belongs in the wrapper that includes it or in the generating script. Never propose editing the generated file itself.
3. If the project is a git repository, `git diff -- <file>` (or `git log -p -1 -- <file>`) shows whether the line was just changed, which is usually where the error came from. In Dropbox-only projects, use file modification times instead.
4. For errors in macros defined by the project (`\new`, `\quotepaper`, `\inputnumber`, etc.), read their definitions in the preamble before diagnosing.

## Step 5: Reproduce only if the log does not explain the error

Recompile **only** when the log has no error, is missing, or is stale (sources saved after it), or when the log and the user's report disagree. Never compile in place: that overwrites the user's PDF, `.aux`, `.synctex.gz`, and the evidence.

From the root's folder (so relative paths resolve as in the user's build):

```
mkdir -p <scratch>/diag
cp <jobname>.bbl <jobname>.aux <scratch>/diag/ 2>/dev/null
pdflatex -interaction=nonstopmode -file-line-error <user's extra flags, e.g. -shell-escape> -output-directory=<scratch>/diag <jobname>.tex
python <path-to-this-skill>/scripts/parse_latex_log.py <scratch>/diag/<jobname>.log
```

- Use the scratchpad directory from the system prompt for `<scratch>`.
- Use the engine the user uses (pdflatex, xelatex, lualatex), from the LaTeX Workshop recipe or the document's requirements.
- With `\include`, `-output-directory` needs the included files' subfolders to exist under `<scratch>/diag`; create them.
- If the problem is in the bibliography, run biber in the scratch directory as well (`biber --input-directory <scratch>/diag --output-directory <scratch>/diag <jobname>`) and parse its `.blg`.
- If the scratch build compiles cleanly, say so: the saved files compile, so the error came from unsaved changes, an interrupted or concurrent build, or stale build files (for example a truncated `.aux` from an interrupted run, which the next full run repairs).

## Step 6: Report (chat only; no edits)

Lead with the cause in one sentence. Then:

- **Which log** was read, its time, and whether it is older than the sources (and whether Step 5 was needed).
- **The error**: the message verbatim, the location as a clickable `file:line` link, and the offending source line quoted.
- **Cause**: what in that line (or upstream of it) triggers the error, with a confidence level if the diagnosis is inferred.
- **Fix**: the exact change, as old text → new text, or the exact command to run (for example a full `pdflatex → biber → pdflatex` sequence with `-synctex=1`). Do not apply it. If the fix is a build action that deletes or overwrites files (deleting a truncated `.aux`, a clean rebuild), describe it and let the user decide.
- **Cascades**: say which later errors are consequences of the first and will disappear with it.
- **Other warnings** worth knowing, briefly: undefined references or citations (shown as ?? or bold keys), multiply defined labels. These are not errors, but LaTeX Workshop and the user may report them as "the error".

## Common causes

| Message | Usual cause | Usual fix |
|---|---|---|
| `Undefined control sequence` | Typo in a macro name; macro from a package not loaded; macro defined only in another document's preamble (e.g. a paper macro used in the response doc) | Fix the name, load the package, or define the macro in this preamble |
| `Missing $ inserted` | `_`, `^`, or a math-only symbol in text mode (often an underscore in a file name or label printed as text) | Escape it (`\_`) or wrap the math in `$...$` |
| `File 'x' not found` / `LaTeX Error: File ... not found` | Path relative to the wrong folder (e.g. `../results` in one document, `../../results` in the other); a results file the scripts have not produced yet | Fix the path relative to the root's folder; or have the generating script run |
| `Runaway argument?` / `File ended while scanning use of \X` | Unbalanced braces in the argument of `\X`; or a truncated `.aux` from an interrupted run (e.g. `\abx@aux@segm`, `\@newl@bel`) | Balance the braces; for a truncated `.aux`, rerun the full sequence (or delete the `.aux` and rerun) |
| `Paragraph ended before \X was complete` | Blank line inside the argument of a short macro (e.g. a highlighting macro like `\new{...}` spanning paragraphs) | Remove the blank line, or use `%` on an empty line, or split the macro |
| `Extra }, or forgotten \endgroup` / `Missing } inserted` | Brace mismatch, often from an edit that split a `{...}` group across environments | Re-pair the braces; check the lines just edited |
| `Misplaced alignment tab character &` | `&` in text, or a table whose column count changed when regenerated | `\&` in text; adjust the `tabular` spec in the wrapper (never the generated table) |
| `Text line contains an invalid character` | Control characters (CR, TAB, ^^M, etc.) written into the source, e.g. by a shell heredoc that interpreted backslash escapes | Find them with `python <path-to-this-skill>/scripts/parse_latex_log.py --scan-ctrl <file.tex> ...` and retype the line |
| `\pdfendlink ended up in different nesting level` | A hyperlink (citation, `\ref`) split across a page break inside a footnote or float | Rephrase, `\mbox{}` the link, or move it |
| `Dimension too large` / `TeX capacity exceeded` | Runaway recursion, an enormous table, or a plotting package fed bad data | Find the macro or exhibit at the reported line |
| biber `ERROR` / bibtex `---line N of file` | Syntax error in the `.bib` entry named in the `.blg`; `.bcf` from a different biblatex version | Fix the entry at that line; rerun the full sequence |
| Empty quote / text missing in a document using `catchfilebetweentags` (`\ExecuteMetaData`) | Tag name mismatch, or the tag pair is missing or unbalanced in the source file | Check that `%<*tag>` and `%</tag>` both exist in the named file and match exactly |
| References print as `??` in a document with `\externaldocument` | The external document was not compiled (its `.aux` is missing or stale) | Compile the external document first, then this one |
