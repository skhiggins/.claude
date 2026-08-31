---
name: check-response-paper-text
description: Check that text quoted inside `paper` environments in a referee-response document matches the paper verbatim, and that figures/tables appearing in both the response doc and the paper match in content (allowing formatting differences). The paper is ground truth; mismatches are fixed by updating the response doc. Use when the user asks to check, sync, or verify the response document against the paper.
---

# Check response-document text against the paper

The referee-response document quotes passages from the paper inside `\begin{paper}...\end{paper}` blocks and reproduces some of the paper's figures and tables. After rounds of editing, the paper and the response doc can drift apart. This skill verifies they match and fixes drift, **always treating the paper as ground truth and editing only the response document**.

## Files

- **Response document**: if the user names one, use it. Otherwise default to `paper/RR_Response_ECMA/r_BehavioralFirmsProfitableOpportunities.tex`. If other `r_*.tex` response docs exist and the user was ambiguous, ask which one.
- **Main paper file**: read the response doc's preamble and use the file named in `\externaldocument{...}` (e.g., `\externaldocument{../BehavioralFirmsProfitableOpportunities}` → `paper/BehavioralFirmsProfitableOpportunities.tex`). Do not guess among the `_long` / `_short` / conflicted-copy variants.
- **Paper = main file + all recursively `\input` tex files.** Build the file list by following every uncommented `\input{...}` in the main file, then in those files, etc. **Exclude** auto-generated results files (`results/tables/*.tex`, `results/figures/*.tex`, `results/numbers/*.tex`) from the *text-search* list — they are script output, not paper prose — but note them: they matter for the figure/table content check.

## Part 1 — verbatim text check

1. Extract every `\begin{paper}...\end{paper}` block from the response doc, **skipping** the `\newenvironment{paper}` definition in the preamble. Record the line range of each block.
2. For each block, locate the corresponding passage in the paper files. Grep for a distinctive literal anchor phrase (a long run of plain words with no LaTeX markup) from near the start of the block; if needed, use a second anchor from the end of the block to find the passage boundaries. Search all paper files, not just the main one.
3. Compare **verbatim** — character for character, *including* LaTeX markup (`\new{}`, `\added{}`, `\cut{}`, `\note{}`), `%` comments, and `\inputnumber{...}` / `\input{...}` references. The response doc's preamble defines no-op versions of the paper's markup commands precisely so that paper text can be pasted unmodified; preserving the markup verbatim is the point.
   - The only tolerated differences are leading indentation per line, and the paths inside `\input`/`\inputnumber`/`\includegraphics` (the response doc lives one directory deeper, so `../results/...` in the paper becomes `../../results/...` in the response doc — this path adjustment is correct and must be preserved, not "fixed").
   - Do **not** normalize line breaks casually: a `%` comment runs to end of line, so re-wrapped lines can change what is commented out. If line-wrapping differs, verify the rendered text (with comment semantics) is identical; if in doubt, treat it as a mismatch.
   - **Partial quotes are OK.** A block may quote only the relevant part of a paper paragraph — starting and/or ending mid-paragraph (even mid-line). This is fine as long as the quoted part matches the paper verbatim; do not "complete" the block with the rest of the paragraph.
   - **`\dots` elisions are OK.** A block may intentionally omit an irrelevant *middle* part (never the beginning or end) of the quoted passage, replacing it with `\dots` in the response doc. This is fine as long as the text before and after the `\dots` each match the paper verbatim, in order and from the same passage.
4. On mismatch: replace the block's contents in the response doc with the paper's text exactly (adjusting relative paths as above). Never edit the paper.
   - **Exception — ask first if the response doc may be the ground truth.** If the response-doc version looks newer or deliberate rather than stale — e.g., filled-in `\inputnumber` values where the paper still has empty placeholders or a `%!` todo, recently edited comments, or added text that reads like an edit intended for the paper — do not overwrite it silently. Always ask the user which version is ground truth before transferring edits from one tex file to the other, in either direction.
5. If a block's text cannot be found in the paper at all (it may have been cut or heavily rewritten), do **not** guess or delete — flag it in the report for the user to decide.
6. **Hardcoded numbers vs `\inputnumber`.** A verbatim match does not settle this: if a passage hardcodes a numeric value (e.g., "137") where an auto-generated number file exists for the same quantity — evidenced by an `\inputnumber{...}` reference to that quantity elsewhere (in the response doc's own prose, in the surrounding sentence, or in the other document) — flag it and ask the user whether the hardcoded value should be replaced by the `\inputnumber` reference (usually in both documents). Do not decide silently in either direction.

## Part 2 — figure/table content check

1. Enumerate every *uncommented* `\begin{table}` / `\begin{figure}` environment in the response doc (some floats are fully commented out — skip those).
2. Determine whether each float also appears in the paper:
   - If the caption contains `Table~\ref{tab:...}` or `Figure~\ref{fig:...}`, that label identifies the paper counterpart. Find `\label{tab:...}` / `\label{fig:...}` in the paper files (including the appendix table/figure files) to locate it.
   - Floats whose caption has **no** `\ref` to a paper label are response-only; skip them (note them in the report as "response-only, not checked").
   - If the caption has a `\ref` but the label does not exist anywhere in the paper, flag it — the response doc claims the table is in the paper but it is not.
3. Compare **content**, allowing formatting differences:
   - **Underlying content file**: the `\input{...results/tables/....tex}` filename (for tables) or `\includegraphics{...results/figures/...}` filename (for figures) must be identical apart from the `../` vs `../../` path prefix. A different results filename is a content mismatch.
   - **Caption title**: must match after stripping the response doc's `Table~\ref{...}:` / `Figure~\ref{...}:` prefix, and ignoring `\caption*` vs `\caption`.
   - **Notes text**: the table/figure notes (in the response doc these follow the float in `\footnotesize ... \begin{justify}...\end{justify}` blocks; in the paper they may sit inside the float or in a notes macro) must match verbatim under the same rules as Part 1.
   - **Expected, acceptable differences** (never flag these): `\caption*` + `Table~\ref{...}:` prefix in the response doc vs `\caption` + `\label` in the paper; the `\label` commented out in the response doc; float placement specifiers (`[H]` vs `[!ht]` etc.); size/positioning wrappers (`adjustbox`, `resizebox`, `\centering`, `nscenter`, spacing commands); `\clearpage` and comment-divider lines.
4. On content mismatch: update the response doc to match the paper (caption title, notes text, or results filename). **Never edit the auto-generated `.tex` files in `results/`** — they are produced by scripts and any manual edit will be overwritten. The same exception as in Part 1 applies: if the response-doc version may be the ground truth, ask the user before overwriting.

## Reporting

End with a concise summary:

- Text blocks: N checked → matched / updated (with line refs) / not found in paper (flagged).
- Floats: N in response doc → matched / updated / response-only (skipped) / label missing from paper (flagged).
- List every edit made to the response doc with file:line links.

If the response doc is long, Parts 1 and 2 can be run via parallel subagents (one per part, or one per batch of blocks), but all edits should be verified against the paper text before reporting.
