---
name: read-pdf-from-zotero
description: Read a cited paper's PDF in full by resolving a citation key (or author/year/title) to a PDF in the local Zotero storage, then running the read-pdf skill on it. Use when the user passes a citation key or paper reference to /read-pdf-from-zotero, or asks to read or verify a cited paper without providing a PDF path.
---

# Read a cited paper's PDF from Zotero storage

This skill is a wrapper around the `read-pdf` skill: it first locates the paper's PDF in the local Zotero storage at `C:\Users\skh2820\Zotero\storage\`, then hands off to `read-pdf` for the conversion and full chunked read. The argument is typically a citation key from the project's bibliography (e.g., `babina_customer_2025`), optionally followed by a question to answer about the paper. Author/year/title may be given instead of a key.

## Step 1: Resolve the citation key to bibliographic details

1. Find the project's bibliography file(s): the `.bib` file(s) loaded by the paper's main tex file (via `\addbibresource{...}` or `\bibliography{...}`). Grep them for the citation key.
2. From the entry, extract the first author's last name, the year, and the title.
3. Check the entry's `file` field first: Zotero-exported entries usually contain one or more attachment paths under `C:\Users\skh2820\Zotero\storage\<hash>\<name>.pdf`, separated by `;` and sometimes with escaped characters (`C\:\\Users\\...`). If a listed path exists on disk, use it and skip Step 2. If several PDFs are listed (e.g., working paper and published version), prefer the one matching the bib entry's venue/year; if the choice is unclear, ask the user (AskUserQuestion) rather than guessing.

If the argument is not a citation key (the user gave author/year/title directly), skip the bib lookup and go to Step 2 with those details.

## Step 2: Search Zotero storage

If there is no usable `file` field, or the listed file does not exist:

1. Zotero storage consists of folders named by 8-character hashes, each typically holding one attachment. Filenames usually follow `Author et al. - Year - Title.pdf` or `Author - Year - Title.pdf`, with long titles truncated.
2. Search with Glob under `C:\Users\skh2820\Zotero\storage\`, choosing whichever combination of first author name, year, and distinctive title words best discriminates (e.g., `*/*Babina*Customer*.pdf`). Try several patterns before concluding the paper is absent; prefer words from early in the title (truncation), and allow for punctuation differences.
3. If multiple distinct PDFs match (different versions of the paper), list them and ask the user which to use, unless the bib entry's year/venue makes the choice unambiguous.
4. If nothing matches, report the patterns tried and ask the user for the path; do not fall back to a different paper.

## Step 3: Hand off to read-pdf

Invoke the `read-pdf` skill (Skill tool) with the resolved PDF path plus the remainder of the user's request (the question to answer), and follow it exactly: convert with its script, read the entire text file in sequential 800-line chunks, and only then answer, citing page markers. One adjustment: when a citation key was given, name the converted text file after the citation key (e.g., `<project>/.claude/references/babina_customer_2025.txt`) so the reference folder stays organized by bib key.
