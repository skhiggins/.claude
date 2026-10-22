---
name: clean-tex-build
description: Delete the build artifacts of one LaTeX root file (every `<jobname>.*` file next to it except `<jobname>.tex`: .aux, .log, .pdf, .synctex.gz, .bbl, .bcf, .nav, .out, .snm, .toc, .fls, .fdb_latexmk, and so on). The tex file is taken from the argument (an @-mention or a path) or from the file open in the IDE. Use when the user calls /clean-tex-build, or asks to clean, clear, or remove the build/auxiliary/compilation files of a tex file.
argument-hint: [path/to/file.tex]
---

# Clean the build artifacts of a tex file

Remove every file in the same folder whose name is `<jobname>.<something>`, where `<jobname>` is the tex file's name without `.tex`, except the tex file itself. Nothing else is touched: no files in other folders, no files with a different base name (so `<jobname>_old.tex` or `<jobname>-figure.pdf` are not matched), and never the `.tex` file.

## Step 1: Determine the tex file

Priority:

1. The skill argument, if given. It may arrive as an IDE @-mention (`@NUdevlunch_60m_8Oct2026.tex`); strip a leading `@`. A relative path is relative to the working directory.
2. Otherwise, the tex file currently open in the IDE.
3. Otherwise, ask the user which file to clean (AskUserQuestion with the `.tex` files in the working directory as options).

The file must end in `.tex` and exist. If it does not, stop and say so.

## Step 2: Make sure no build is running

A running compile would recreate files mid-deletion or fail when its `.aux` disappears. Check first:

```
tasklist | findstr /i "latexmk pdflatex xelatex lualatex biber bibtex"
```

(PowerShell: `Get-Process latexmk, pdflatex, xelatex, lualatex, biber, bibtex -ErrorAction SilentlyContinue`.) If any is running, tell the user and wait for it to finish before continuing; do not kill it.

## Step 3: List what would be deleted

```
python <path-to-this-skill>/scripts/clean_tex_build.py "<file>.tex"
```

Without `--delete` the script only lists. It prints one line per match:

- `DELETE <path> <size> known` for recognized LaTeX build extensions.
- `REVIEW <path> <size> unknown` for a `<jobname>.*` file whose extension is not a recognized build artifact (for example `.docx`, `.xlsx`, `.bib`, `.zip`, `.bak`). These are not deleted unless the user confirms.
- `NONE` if nothing matches.

## Step 4: Delete

- If the list has only `DELETE` lines, run the deletion without asking; invoking the skill is the instruction to delete.

  ```
  python <path-to-this-skill>/scripts/clean_tex_build.py "<file>.tex" --delete
  ```

- If the list has `REVIEW` lines, delete the `DELETE` lines right away (same command), then ask the user about the `REVIEW` files with one AskUserQuestion (multi-select over those files is fine: they are parts of the same decision). Delete the confirmed ones by name:

  ```
  python <path-to-this-skill>/scripts/clean_tex_build.py "<file>.tex" --delete --only <name1> <name2>
  ```

The script prints `DELETED <path>` or `FAILED <path> <reason>` per file. A `FAILED` on the `.pdf` usually means a viewer has it open; report it and do not retry in a loop.

## Step 5: Report

One short message: the jobname, how many files were deleted (list them by extension, e.g. `.aux .bbl .bcf .blg .log .nav .out .pdf .run.xml .snm .synctex.gz .toc`), any `FAILED` files with the reason, and any `REVIEW` files that were kept. Mention that the next compile must run the full sequence (pdflatex, biber or bibtex, pdflatex, pdflatex) since the bibliography files are gone.
