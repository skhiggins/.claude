---
name: transfer-exhibit
description: Transfer a highlighted figure/table between the referee-response document and the paper (direction depends on which document the highlighted exhibit lives in), applying the required formatting differences between the two versions (commented-out \label, Table~\ref{}/Figure~\ref{} caption prefix, and \singlespacing/\onehalfspacing bracketing around floats in the response doc; adjustbox max width 1.2 in the paper vs 1 in the response doc; notes text single-sourced in the paper via %<*notes-...> tags pulled into the response doc with \quotenotes). Also handles updating an exhibit that already exists in the destination, e.g. bringing a newer modified version from the response doc into the paper. With no exhibit highlighted, check all exhibits common to both documents for consistency. Use when the user asks to transfer, copy, sync, port, or update an exhibit between the response doc and the paper.
---

# Transfer an exhibit between the response doc and the paper

The referee-response document reproduces some of the paper's figures and tables, and new exhibits are sometimes drafted in one document and later added to the other. This skill copies an exhibit from one document to the other — in whichever direction is needed — while applying the deliberate formatting differences the two versions must have.

## Files

- **Response document**: if the user names one, use it. Otherwise default to `paper/RR_Response_ECMA/r_BehavioralFirmsProfitableOpportunities.tex`. If other `r_*.tex` response docs exist and the user was ambiguous, ask which one.
- **Main paper file**: read the response doc's preamble and use the file named in `\externaldocument{...}` (e.g., `\externaldocument{../BehavioralFirmsProfitableOpportunities}` → `paper/BehavioralFirmsProfitableOpportunities.tex`). Do not guess among the `_long` / `_short` / conflicted-copy variants.
- **Paper = main file + all recursively `\input` tex files** (follow every uncommented `\input{...}`). Appendix exhibits typically live in dedicated files (e.g., `appendix_tables_notonline.tex`, `appendix_figures_notonline.tex`, `appendix_tables_supplemental.tex`, `appendix_figures_supplemental.tex`).
- **Never edit the auto-generated `.tex` files in `results/`** (`results/tables/`, `results/figures/`, `results/numbers/`) — they are script output and manual edits will be overwritten.

## Determining the direction

The user highlights (IDE selection) an exhibit, or names one. Determine which document the highlighted exhibit is in:

- Highlighted in the **response doc** → transfer response doc → paper.
- Highlighted in the **paper** (main file or any `\input` file) → transfer paper → response doc.

If the exhibit already exists in the destination document (matched by `\label`, or by the `\ref` in the response doc's caption prefix, or by the underlying `results/` filename), the transfer is an **update**: overwrite the destination version's content (results filename, caption title, notes) to match the source, preserving the destination-side formatting conventions below. If it does not exist in the destination, it is an **insertion** (see placement rules below).

To determine whether a response-doc exhibit is already in the paper, compare its label against the `\label`s of the paper's exhibits: collect the exhibit's label from the response-doc version (whether it appears as a commented-out `%\label{...}`, a live local `\label{...}`, or only inside the caption prefix's `Table~\ref{...}`/`Figure~\ref{...}`) and search for that label text among the `\label`s inside `\begin{table}`/`\begin{figure}` environments across all paper files (main file plus every recursively `\input` tex file, including the appendix exhibit files). A match means the exhibit exists in the paper (→ update); no match means it does not (→ insertion) — fall back to the `results/` filename check before concluding it is absent.

If the transfer direction implies overwriting content that looks newer or deliberately different in the destination (not just the sanctioned formatting differences), ask the user which version is ground truth before overwriting — in either direction.

## Updating an existing paper exhibit from a newer response-doc version

A common case: the exhibit already exists in both documents, the response-doc copy was modified during drafting (new columns or panels, a different `results/` filename, revised caption or notes), and the user wants the paper brought up to date. When the user highlights the response-doc version (or says the response-doc version is the newer one):

1. Locate the paper counterpart via the `\ref` in the response doc's caption prefix, or failing that by label text or the underlying `results/` filename.
2. For this transfer the response doc is ground truth for **content**: overwrite the paper version's `\input` results filename, caption title, notes text, and panel/column structure to match the response-doc version. (This inverts the usual rule — outside an explicit transfer, the paper is ground truth, as in check-response-paper-text. The user's instruction to transfer establishes the direction, so do not re-ask which side wins.) If the response version carries revised literal notes text (i.e., it was drafted before conversion to `\quotenotes`), write that text into the paper's tagged notes region, then replace the response-doc notes text with the `\quotenotes` call.
   - Exception: if the paper version also contains content edits that the response-doc version lacks (both sides were edited since they diverged), stop and ask before overwriting, listing the differences in each direction.
3. Keep the paper version **in place**: its position among the paper's exhibits, float placement specifier, and surrounding text do not change during an update.
4. Apply the paper-side conventions while transferring: live `\label` (keep the paper's existing label text), `\caption{Title}` with no `Table~\ref{}:`/`Figure~\ref{}:` prefix, `max width=1.2\textwidth` (iZettle_fee), no `\singlespacing`/`\onehalfspacing` spacing commands around or inside the float, and paths shortened one level (`../../results/...` → `../results/...`).
5. Afterward, verify the response-doc version still follows its own conventions (commented `\label`, caption prefix `\ref` pointing at the paper's label, `max width=1\textwidth`, `\singlespacing` before the float and `\onehalfspacing` after the float + notes); if it had drifted onto a local live label during drafting, fix it.

## Shared notes system (single-sourced notes text)

For exhibits that appear in **both** documents, the notes *text* is not duplicated: it lives only in the paper, wrapped in `catchfilebetweentags` tag pairs, and the response doc pulls it live at compile time.

- **Paper side**: the notes text is enclosed in `%<*notes-tab-foo-bar>` / `%</notes-tab-foo-bar>` comment lines (tag name = `notes-` + the exhibit's label with `:` and `_` turned into `-`, e.g. label `tab:het_all_ctrl_busy` → tag `notes-tab-het-all-ctrl-busy`; figures use `notes-fig-...`). The open tag goes on its own line immediately after the paper's notes wrapper (`\begin{justify}` plus any `\emergencystretch=3em`/`\singlespacing` lines for tables; the `\footnotesize`/`\singlespacing` lines inside the figure environment for figures); the close tag goes immediately after the last notes line, before `\end{justify}`/`\end{figure}`. Only the text is tagged — wrappers stay outside the tags and remain per-document. No `\label` inside a tagged region.
- **Response side**: the notes block keeps its own wrappers (`\footnotesize`, `\vspace`, `\begin{justify}` [+ `\emergencystretch=3em`], `\end{justify}`, `\normalsize` for tables; `\footnotesize \singlespacing` inside the figure env for figures), but the text itself is replaced by a single line: `\quotenotes{<paper-file-basename>}{<tag>}` — e.g. `\quotenotes{appendix_tables_notonline}{notes-tab-het-all-ctrl-busy}`. `\quotenotes` is defined in the response preamble as `\ExecuteMetaData[../#1.tex]{#2}`; the first argument is the paper-side file (without `.tex`) that physically contains the tagged notes (`appendix_tables_notonline`, `appendix_figures_notonline`, `appendix_tables_supplemental`, ...), not necessarily the main paper file.
- **Editing notes**: edit the paper's tagged text only; the response doc updates on recompile. Never re-introduce literal notes text in the response doc for a shared exhibit. `\inputnumber` inside tagged notes works in both docs (each defines it with its own path prefix), and `\ref`/`\eqref` to paper labels resolve in the response doc via `\externaldocument`.
- **Captions are not shared**: caption titles are still duplicated (paper `\caption{Title}` vs response `\caption*{Table~\ref{...}: Title}`) and must match verbatim.

## Required differences between the two versions

The two versions must be identical in content, **except** for exactly these differences, which must be applied (not merely tolerated) when transferring:

1. **`\label`**: commented out in the response doc version (e.g., `%\label{tab:foo}`); live (uncommented) in the paper version. The label text itself must be identical.
2. **Caption title prefix**: the response doc version uses `\caption*{Table~\ref{tab:foo}: Title}` (or `Figure~\ref{fig:foo}:`), where the `\ref` points to the paper's label via `\externaldocument`; the paper version uses `\caption{Title}` with no prefix. The Title after the prefix must be identical. (Response-only exhibits that are *not* being transferred to the paper keep a local live label instead — but once transferred, the response doc version switches to the commented-label + `\ref`-prefix convention.)
3. **[iZettle_fee project only] adjustbox width**: when `\adjustbox{max width=...}` (or `resizebox` equivalent) wraps the exhibit, the paper version uses `max width=1.2\textwidth` (the paper has 1.25" margins and tables may spill into them) and the response doc version uses `max width=1\textwidth`. In other projects, keep the widths identical unless the user says otherwise.
4. **Spacing commands bracketing tables**: the response doc's body text is `\onehalfspacing`, so each table (or contiguous block of exhibits) is bracketed by a `\singlespacing` line just *before* `\begin{table}[H]` and an `\onehalfspacing` line after the float + notes block ends (figure notes instead carry `\footnotesize \singlespacing` at the start of the notes, and table-notes `justify` blocks open with `\begin{justify}\singlespacing`). The paper version has none of these (its tables all sit in an appendix that already follows a global `\singlespacing`). When transferring to the paper, drop the spacing commands; when transferring to the response doc, add the bracketing pair — and make sure the trailing `\onehalfspacing` is present, otherwise the rest of the response doc silently becomes single-spaced.

Additionally, adjust relative paths mechanically: the response doc lives one directory deeper, so `../results/...` in the paper ↔ `../../results/...` in the response doc (applies to `\input`, `\inputnumber`, `\includegraphics`).

Other acceptable, do-not-touch differences: float placement specifiers (`[H]` vs `[!ht]`), `\centering`/`nscenter`/spacing wrappers, `\clearpage` and comment-divider lines, and the response doc's notes appearing after the float in `\footnotesize ... \begin{justify}...\end{justify}` blocks vs inside the float or in a notes macro in the paper. The notes *text* is single-sourced via the shared notes system above (paper tags + `\quotenotes` in the response doc), so it cannot diverge; if a shared exhibit's response version still carries literal notes text, migrate it to the tag system as part of the transfer.

## Placement when inserting a new exhibit into the paper

When transferring an exhibit from the response doc that does not yet exist in the paper:

1. Find where the result is **discussed** in the paper's prose (search for the topic, the results filename, or key phrases from the caption/notes).
2. Place the exhibit relative to the exhibits already in the paper that are discussed **before and after** that point — i.e., its position in the exhibit ordering should mirror the order of first discussion in the text.
3. **Tables and figures are grouped separately**, not interspersed: Table 1..N all come before Figure 1, and in each appendix, Table A.1..A.N all come before Figure A.1. So a new table goes among the tables (ordered by discussion point relative to the other tables), and a new figure among the figures — even if a figure is discussed between two tables.
   - Exception: if main-paper exhibits are interspersed with the text (as in the iZettle_fee main paper), place the new main-paper exhibit near its discussion point instead. The grouping rule still applies to iZettle_fee **appendix** tables and figures.
4. Decide main paper vs appendix by where the result is discussed and how the surrounding exhibits are housed; if ambiguous, ask the user.
   - **[iZettle_fee project only]** Unless the user specifies otherwise, a new exhibit goes in **Appendix E** ("Additional Tables and Figures", `\label{a:notonline}` — the `appendix_tables_notonline.tex` / `appendix_figures_notonline.tex` files). Appendix E exhibits are **not** explicitly `\ref`'ed in the paper's text (any `\ref`s to them sit inside `\cut{...}` or comments), so you cannot locate the discussion point by searching for a `\ref` to the exhibit's label. Instead, find where the *result* is discussed in the prose (topic keywords, results filename, caption/notes phrases), do the same for the exhibits already in Appendix E, and order the new exhibit accordingly (tables among tables, figures among figures).
5. Give the paper version a live `\label`; then update the response doc version to the commented-label + `Table~\ref{}:`/`Figure~\ref{}:` prefix convention pointing at that label.
6. Wire up the shared notes: wrap the notes text just inserted in the paper in a `%<*notes-...>` / `%</notes-...>` tag pair (naming and placement per the shared notes system above), then replace the response-doc version's literal notes text with the corresponding `\quotenotes{<paper-file-basename>}{<tag>}` call, keeping the response's notes wrappers in place.

When inserting into the response doc, place the exhibit after the response passage that discusses it (response-doc floats typically use `[H]` and sit inline with the discussion).

## No-highlight mode: consistency check of shared exhibits

When invoked with no exhibit highlighted or named:

1. Enumerate every uncommented `\begin{table}`/`\begin{figure}` in the response doc; match each to the paper via the `\ref` in its caption prefix (or the results filename). Skip response-only exhibits (no `\ref` to a paper label) but list them in the report.
2. For each shared exhibit, verify:
   - Content matches: same `results/` filename (modulo `../` vs `../../`), same caption title (after stripping the prefix).
   - Notes use the shared system: the response version's notes are a `\quotenotes{file}{tag}` call, the named file contains that tag pair, and the tag encloses the paper version's notes text (wrappers outside the tags).
   - The required differences above are correctly in place on each side (commented vs live label; prefix vs no prefix; adjustbox 1 vs 1.2 in iZettle_fee).
3. On a content mismatch, do not assume a direction: ask the user which version is ground truth, then update the other side (the user's standing preference is full convergence — no tolerated divergences). On a formatting-convention violation (e.g., response doc using `max width=1.2`), fix it to the convention directly; no need to ask. If a shared exhibit still carries literal notes text in the response doc: when the text matches the paper's verbatim (comments aside), migrate it to the tag system directly; when it differs, ask which side is ground truth first, then migrate.
4. Report: N shared exhibits → consistent / fixed (with file:line links) / asked-and-resolved; response-only exhibits listed; any caption `\ref` pointing to a label missing from the paper flagged.
