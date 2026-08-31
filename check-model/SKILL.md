---
name: check-model
description: Two-pass review of a LaTeX file containing an economic model (intuitive explanation plus formal proofs). Pass 1 reads as a theorist checking math correctness; pass 2 reads as a non-theorist PhD economist checking clarity. Produces a markdown report. Use when the user asks to check, verify, or review a model, proof, or theory section in a .tex file.
---

# check-model

Review a specified `.tex` file that contains both an intuitive explanation and formal proofs for an economic model, in two independent passes, then write a markdown report.

## Input

The argument is the path to the `.tex` file. If no file is specified, ask the user which file to check. Read the entire file (and any files it `\input`s or `\include`s that contain model content or proofs — but not auto-generated table files).

## Pass 1: Theorist read

Read the file as a careful economic theorist refereeing the paper. Check that all of the math is correct and that there are no typos or inconsistencies. Specifically:

- Re-derive every derivation and verify every step of every proof. Do the algebra yourself; do not assume a step is correct because it looks plausible. Check signs, inequality directions, limits of integration/summation, and boundary/corner cases.
- Verify that each proposition/lemma/theorem statement matches what its proof actually establishes (no stronger claim than proved, all stated assumptions actually used, no unstated assumptions silently invoked).
- Check notational consistency throughout: the same symbol means the same thing everywhere, subscripts/superscripts are consistent, function arguments are not silently dropped or changed.
- Check consistency between the intuitive explanation and the formal results: the intuition must not claim more (or the opposite of) what the math shows.
- Check for typos in math and text (dropped primes, swapped indices, wrong equation references, etc.).
- If unsure whether something is an error — e.g., a step you cannot verify, an assumption that may or may not be needed, a possible but not certain sign error — explicitly flag it as "unsure" and explain why you are unsure. Do not silently pass over it, and do not overclaim that it is wrong.

## Pass 2: Non-theorist PhD economist read

Now re-read the file from scratch as a different reader: a PhD economist who has taken the prerequisite math classes and the first-year PhD microeconomics sequence and has read Mas-Colell, Whinston, and Green (MWG), but who is *not* a theorist. This reader can follow standard tools (constrained optimization, envelope theorem, basic fixed-point and comparative-statics arguments, expected utility) but does not have specialist knowledge beyond that. Check whether everything is explained sufficiently clearly for this reader to understand:

- Is all notation defined before (or where) it is used?
- Are non-standard concepts, solution techniques, or results beyond MWG explained or cited, rather than assumed known?
- Are proof steps that a non-theorist could not readily fill in themselves either spelled out or accompanied by a pointer/explanation? Flag "it is easy to show" / "it follows that" steps that are not in fact easy for this reader.
- Does the intuitive explanation actually convey the economics of each result, or does it just restate the math in words?
- Is the mapping between the intuition section and the formal section clear (which proposition formalizes which claim)?
- Flag any place where this reader would get stuck, and say what additional sentence(s) or steps would unstick them.

Keep the two passes separate: an issue can appear in both, but judge pass 2 by clarity for the non-theorist reader, not by correctness.

## Report

Write a markdown report to the project's `.claude/` directory, named `check_model_<texfilename>_<YYYY-MM-DD_HHMM>.md`, so that repeated runs on the same file save as different files rather than overwriting each other (e.g., `.claude/check_model_model_appendix_2026-08-11_1435.md`). Take the timestamp from the system clock (e.g., `Get-Date -Format "yyyy-MM-dd_HHmm"` on Windows, `date +%F_%H%M` otherwise); do not guess the time. Do not put the report in the project root. The report should contain:

1. **Header**: file checked, date, one-paragraph overall assessment.
2. **Pass 1: Correctness (theorist read)** — each issue as its own item with:
   - severity: **error** / **likely error** / **unsure** / **typo/minor**;
   - a markdown link to the specific line(s) in the tex file, in the format `[file.tex:LINE](relative/path/file.tex#LLINE)`;
   - what is wrong (or why you are unsure), showing the relevant math;
   - the suggested fix where you have one.
3. **Pass 2: Clarity (non-theorist read)** — each issue as its own item with:
   - severity: **would get stuck** / **hard to follow** / **could be clearer**;
   - a line link as above;
   - what the reader is missing and what addition would fix it.
4. **Things checked and found fine** — a brief list of the main derivations/proofs verified as correct, so the user knows the coverage of the check.

If either pass finds no issues, say so explicitly rather than omitting the section. After writing the report, summarize the most important findings (a few sentences) in the conversation and link to the report file.
