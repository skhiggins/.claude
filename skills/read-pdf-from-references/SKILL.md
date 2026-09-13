---
name: read-pdf-from-references
description: Locate a paper's PDF in the user's Dropbox reference library (C:\Dropbox\FinancialInclusion\References) by author, year, or title, then read it in full with the read-pdf skill. Use when the user asks to read a paper "from References" or names a paper that is not in Zotero.
---

# Read a paper's PDF from the Dropbox reference library

This skill is a wrapper around the `read-pdf` skill: it first locates the paper's PDF in the user's reference library at `C:\Dropbox\FinancialInclusion\References\`, then hands off to `read-pdf` for the conversion and full chunked read. The argument is typically author names and a year (e.g., `Bruhn and Love 2014`), a citation key from a `.bib` file (e.g., `bruhn_real_2014`), or a title fragment, optionally followed by a question to answer about the paper.

## How the library is organized

- About 1,800 PDFs. Most are inside topical subfolders (e.g., `Bank Accounts and Savings Products`, `Business Training`, `ATMs and Debit Cards`, `Behavioral`), and some subfolders have further subfolders (replication packages, appendices). A minority of PDFs sit in the top-level folder. Always search recursively (`**/`).
- The usual filename convention is `Author1 Author2 ... Year (Journal) Title.pdf`, e.g., `Bruhn and Love 2014 (J Finance) The Real Impact of Improved Access to Finance Evidence from Mexico.pdf`. Variants: no journal in parentheses; "and" between two authors; `et al`; `f` or `forthcoming` in place of the year; punctuation stripped from titles. Working-paper versions and published versions may both be present.
- Online appendices are stored as separate files, often `... APPENDIX.pdf` or `... Online Appendix.pdf` next to the main file. Some PDFs already have a converted `.txt` next to them; ignore those and convert fresh into the project's `.claude/references/` folder as `read-pdf` requires.

## Step 1: Resolve the argument to search terms

1. If the argument is a citation key, find the project's `.bib` file(s) (loaded by the main tex file via `\addbibresource{...}` or `\bibliography{...}`) and grep for the key to get the first author's last name, year, and title. If the entry's `file` field points to a path under `C:\Dropbox\FinancialInclusion\References\` that exists, use it directly and skip Step 2.
2. If the argument is author/year/title text, use it as is.

## Step 2: Search the library

1. Search with Glob under `C:\Dropbox\FinancialInclusion\References\` using `**/*<pattern>*.pdf`. Start with the first author's last name plus the year (e.g., `**/*Bruhn*2014*.pdf`), then add a distinctive title word if there are too many hits, or drop the year if there are none (the file may say `f` or `forthcoming`).
2. Try at least three patterns before concluding the paper is absent: author + year; author + title word; title words alone. Allow for a second author's name appearing before the year, `et al`, and punctuation differences.
3. Exclude appendix files, `.txt` companions, and files inside replication-package folders when picking the main text, unless the user asked for the appendix. If both a working-paper and a published version match, prefer the published one (the filename with a journal in parentheses) unless the user's request or the bib entry's year points to the other; if the choice is unclear, ask the user (AskUserQuestion).
4. If several distinct papers match, list them and ask which one to read. If nothing matches, report the patterns tried and ask the user for the path; do not fall back to a different paper and do not search Zotero unless asked (the `read-pdf-from-zotero` skill covers that library).

## Step 3: Hand off to read-pdf

Invoke the `read-pdf` skill (Skill tool) with the resolved PDF path plus the remainder of the user's request (the question to answer), and follow it exactly: convert with its script into `<project>/.claude/references/`, read the entire text file in sequential 800-line chunks, and only then answer, citing page markers. Name the converted text file after the citation key when one was given (e.g., `bruhn_real_2014.txt`); otherwise use `<firstauthor>_<year>.txt` (e.g., `bruhn_love_2014.txt`). If the user also asked for the appendix, locate and convert it as a separate file with an `_appendix` suffix.
