---
name: read-pdf
description: Read a PDF in full by converting it to a text file with a Python script, then reading the entire text file in sequential chunks so no content is skipped. Use when the user asks to read, summarize, referee, or analyze a PDF (papers, reports, referee packets), or passes a .pdf path to /read-pdf.
---

# Read a PDF in full

Goal: read the *entire* PDF, not just the parts that fit in one Read call. Never read the `.pdf` directly with the Read tool; always go through the text conversion below.

## Step 1 — Convert the PDF to a text file

Run the conversion script that lives in this skill's `scripts/` directory (same directory as this SKILL.md):

```
python <path-to-this-skill>/scripts/pdf_to_txt.py "<file>.pdf" "<project>/.claude/references/<file>.txt"
```

- Always pass the second argument: save the `.txt` in the current project's `.claude/references/` folder (the script creates the folder if it doesn't exist). Saving inside the project avoids per-chunk Read permission prompts, which occur when reading files outside the project directory. The script prints the page, line, and character counts.
- It uses PyMuPDF, falling back to pypdf if PyMuPDF is not installed. If both are missing, run `pip install pymupdf` and retry.
- Page boundaries are marked in the output as `===== [page N of M] =====`; use these markers when citing page numbers.

## Step 2 — Read the text file in full, in sequential chunks

Use the line count printed by the script to plan the chunks, then read the `.txt` file with the Read tool in consecutive chunks of 800 lines each (`offset=1, limit=800`, then `offset=801, limit=800`, and so on) until the end of the file. Do not use larger chunks: 1000 lines of dense academic text can exceed the Read tool's 25,000-token cap.

Rules:

1. Read every chunk, in order. Do not skip chunks, do not stop early because you think you have "enough," and do not sample only sections that look relevant.
2. After each chunk, before moving on, mentally register the key content you just read (main claims, methods, results, numbers, page locations). The point of chunking is retention: each chunk must be processed, not just loaded.
3. Continue until a Read call returns fewer lines than requested (end of file).
4. Only after the final chunk, produce the requested output (summary, referee notes, answer to the user's question), citing page numbers from the `===== [page N of M] =====` markers.

If the resulting `.txt` is near-empty or garbled while the PDF has many pages, the PDF is likely scanned images without a text layer; tell the user OCR would be needed instead of proceeding silently.
