---
name: cut-abstract
description: Reduce a paper's abstract to a specified word count. Use when the user asks to shorten, trim, or cut an abstract to N words.
argument-hint: <target word count> [file]
---

# Cut abstract to a target word count

Reduce the paper's abstract to the word count the user specifies, preserving as much substantive content as possible.

## Locating the abstract

1. If the user highlighted text in the IDE (an `ide_selection` block is present), treat that selection as the abstract.
2. Otherwise, find the abstract inside the `\begin{abstract}...\end{abstract}` environment of the tex file the user names (or the main paper tex file in `paper/` if none is named).

## Counting words

- Count words in the compiled prose, not tex tokens. An `\input{...}` of a number file (e.g., a sample size) counts as one word; citations and inline math count as they would read.
- Report the before and after word counts with the suggested revision.

## Rules

- **Never edit the tex file directly.** Respond in dialog with the suggested revised abstract (and word counts). The user will paste it in themselves.
- Cut in this order of preference: redundant phrasing and filler; details already implied by context; methodological detail not needed to understand the contribution; substantive findings only as a last resort.
- **If reaching the target requires cutting anything substantive (a finding, a design element, a magnitude) or involves a real tradeoff, stop and ask the user for their opinion before settling on a version.** Use AskUserQuestion when the choice is discrete.
- If multiple defensible versions exist, present each option with its word count and state the tradeoffs (what each version cuts and why one might prefer it).
- Preserve the paper's terminology and any project style conventions (e.g., spell out abbreviations at first use).
