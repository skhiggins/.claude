---
name: read-pdf
description: Read a PDF in full by converting it to a text file with a Python script (the conversion is skipped when a previous run already converted the same PDF), then reading the entire text file in sequential chunks so no content is skipped. Use when the user asks to read, summarize, referee, or analyze a PDF (papers, reports, referee packets), or passes a .pdf path to /read-pdf.
---

# Read a PDF in full

Goal: read the *entire* PDF, not just the parts that fit in one Read call. Never read the `.pdf` directly with the Read tool; always go through the text conversion below.

## Step 1: Convert the PDF to a text file (reusing an earlier conversion when one exists)

Run the conversion script that lives in this skill's `scripts/` directory (same directory as this SKILL.md). Run it even when the PDF was probably converted in an earlier session: the script itself checks for an earlier conversion and does not convert the same PDF twice.

```
python <path-to-this-skill>/scripts/pdf_to_txt.py "<file>.pdf"
```

- **Output path and name (chosen by the script; do not choose your own).** The script saves the `.txt` in the project's `.claude/references/` folder (created if needed) and derives the name from the PDF's location, so the same PDF always maps to the same file:
  - Project root: the nearest folder above the PDF that contains a `.claude` folder (the user's home folder does not count); if there is none, the current working directory.
  - Name: the PDF's path relative to the project root, with folder separators and any character other than letters, digits, `.`, `-`, and `_` replaced by `_`, and the extension replaced by `.txt`. So `2026/AEJApplied/PDF_Proof.pdf` becomes `2026_AEJApplied_PDF_Proof.txt` and `2024/AEJApplied/2/PDF_Proof.PDF` becomes `2024_AEJApplied_2_PDF_Proof.txt`; same-named PDFs in different folders never collide. A PDF outside the project (e.g., in the Zotero library) is named after its file name alone.
  - Saving inside the project avoids per-chunk Read permission prompts, which occur when reading files outside the project directory.
  - Pass a second argument only when the calling skill prescribes a name (e.g., `read-pdf-from-zotero` names files by citation key): `python <path-to-this-skill>/scripts/pdf_to_txt.py "<file>.pdf" "<project>/.claude/references/<citation_key>.txt"`.
- **Check for a previous conversion (done by the script).** Before converting, the script hashes the PDF and looks in the output folder for a `.txt` written by a previous run of this skill from the same PDF (each converted file records the source path and the SHA-256 hash of the PDF on its first line). If it finds one, it prints `Already converted by a previous run; skipping conversion`, then the path of the existing file and its page, line, and character counts. In that case do not convert again and do not delete or rewrite the file: go to Step 2 and read the file whose path the script printed (it can differ from the default name when the file was converted by a skill that names files by citation key). A `.txt` at the output path that predates this check (it has no source line) is also reused, provided it is non-empty and newer than the PDF. If the PDF has changed since it was converted, its hash no longer matches and the script converts it afresh. Add `--force` only when the existing `.txt` is visibly truncated or garbled.
- The script prints the page, line, and character counts whether it converted the PDF or reused an existing file.
- It uses PyMuPDF, falling back to pypdf if PyMuPDF is not installed. If both are missing, run `pip install pymupdf` and retry.
- Page boundaries are marked in the output as `===== [page N of M] =====`; use these markers when citing page numbers. Line 1 of the file is the source line (`===== [source: <pdf path>; sha256: <hash>] =====`) and is not part of the PDF.

## Step 2: Read the text file in full, in sequential chunks

Use the line count printed by the script to plan the chunks, then read the `.txt` file at the path the script printed with the Read tool in consecutive chunks of 800 lines each (`offset=1, limit=800`, then `offset=801, limit=800`, and so on) until the end of the file. Do not use larger chunks: 1000 lines of dense academic text can exceed the Read tool's 25,000-token cap.

Rules:

1. Read every chunk, in order. Do not skip chunks, do not stop early because you think you have "enough," and do not sample only sections that look relevant.
2. After each chunk, before moving on, mentally register the key content you just read (main claims, methods, results, numbers, page locations). The point of chunking is retention: each chunk must be processed, not just loaded.
3. Continue until a Read call returns fewer lines than requested (end of file).
4. Only after the final chunk, produce the requested output (summary, referee notes, answer to the user's question), citing page numbers from the `===== [page N of M] =====` markers.

If the resulting `.txt` is near-empty or garbled while the PDF has many pages, the PDF is likely scanned images without a text layer; tell the user OCR would be needed instead of proceeding silently.
