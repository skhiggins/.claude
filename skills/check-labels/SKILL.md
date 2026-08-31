---
name: check-labels
description: Check that every \label in the paper (main tex file plus all recursively \input'ed files) and in the response doc uses the correct type prefix (e.g. e: for equations, fig: for figures), that references use \eqref for equations and \ref for everything else, and that no refs point to undefined labels. Proposes renames and applies them on user approval. Use when the user asks to check, audit, or fix labels or references in the paper.
---

# Check label prefixes and reference commands

Labels in the paper must carry a prefix identifying what they label, and the prefix must be consistent between where the `\label` is defined and where it is `\ref`'ed or `\eqref`'ed. This skill audits every label and reference in the paper (and the response doc, if one exists), reports violations with proposed renames, and applies the renames after the user approves.

## Scanner script

Run the bundled scanner (report-only; it never edits files):

```
python "<skill-dir>/check_labels.py" [MAIN_TEX] [RESPONSE_TEX]
```

Both arguments default to this paper's main file and response doc. The script builds the recursive input closure, classifies each label by context, and prints: duplicate definitions, prefix violations, refs to undefined labels, `\eqref` discipline violations, and unreferenced labels. It is `\cut{...}`/`\cutrr{...}`-aware: those macros discard their argument, so labels/refs inside them never render — they are reported informationally, not as broken refs. Spot-check its classifications against the source before proposing fixes — the classifier is heuristic (environment stack + nearest sectioning command + footnote spans), so verify anything surprising by reading the tex. If the audit rules change, update the script rather than doing one-off manual scans.

To apply approved renames, use the bundled applier (renames `\label` and all ref commands together — including `\hyperref[label]`'s bracket-delimited argument — exact matches only, commented occurrences included so restorable blocks stay consistent):

```
python "<skill-dir>/apply_renames.py" SPEC.json
```

where SPEC.json is `{"files": [...], "renames": {"old": "new", ...}}`. Write the spec to a temp file (it is per-run input, unlike the scripts, which are permanent skill assets). Include the paper closure files *and* the response doc in `files`. Re-run the scanner afterward to confirm zero broken refs.

## Files

- **Main paper file**: if the user names one, use it. Otherwise default to `paper/BehavioralFirmsProfitableOpportunities.tex`. Do not guess among the `_long` / `_short` / `_um*` / conflicted-copy variants in the same folder — those are old drafts. If genuinely ambiguous, ask.
- **Paper = main file + all recursively `\input`/`\include`'d tex files**, followed transitively (files those files input, etc.). Only follow *uncommented* input commands. Do not confuse `\inputnumber{...}` (a stats macro) with `\input`.
- **Auto-generated results files** (`results/tables/*.tex`, `results/figures/*.tex`, `results/numbers/*.tex`) that enter via `\input`: scan them for labels and refs, but **never edit them** — they are script output and manual edits will be overwritten. If a violation originates in one, either fix it at the inclusion site in the paper or flag that the generating script must change.
- **Response doc**: if an `r_*.tex` referee-response document exists (default `paper/RR_Response_ECMA/r_BehavioralFirmsProfitableOpportunities.tex`), run all the same checks on it (plus its own recursive inputs). The response doc references paper labels via `\externaldocument` (xr package), so any label rename in the paper must also be applied to the response doc's refs, and vice versa.
- **Never edit files outside this closure.** Old drafts in the same folder share label names; touching them creates noise and merge pain.

## Prefix map (current paper)

| Prefix | Labels |
|--------|--------|
| `e:`   | equations (`equation`, `align`, `gather`, `multline`, and similar math environments) |
| `p:`   | predictions, propositions, corollaries, and lemmas (`prediction`, `proposition`, `corollary`, `lemma` environments) |
| `s:`   | sections (`\section`) in the main text |
| `a:`   | appendix sections (`\section` after `\appendix` or inside appendix files) |
| `ss:`  | subsections (`\subsection`) |
| `fig:` | figures (`figure` environment) |
| `tab:` | tables (`table` environment) |
| `fn:`  | footnotes (`\footnote`) |
| `alg:` | algorithms (`algorithm` environment) |

**Response-doc-only prefixes**: the response doc labels its own sections `ec:` (editor comment replies) and `rc:N_M` (referee N, comment M — e.g. `rc:1_1`). These are accepted alongside `s:`/`ss:` in the response doc only, never in the paper.

The exact prefixes may differ in another paper. If this skill is used on a different paper, first infer the dominant prefix per label type from the existing labels and confirm the map with the user before flagging anything. If a label type appears that has no prefix in the map (e.g., a `\subsubsection`, lemma, or assumption gets labeled for the first time), ask the user what prefix to use rather than inventing one.

## Checks

For every *uncommented* `\label{...}` in the closure (skip labels behind `%` — a `%` comment runs to end of line):

1. **Classify** the label by its context: the innermost environment (`equation`, `figure`, `table`, `prediction`, `proposition`, `corollary`, `algorithm`, ...) or the nearest preceding sectioning/footnote command (`\section`, `\subsection`, `\footnote`). For sections, determine whether the label is in the appendix (`a:`) or main text (`s:`).
2. **Prefix check**: the label must start with the mapped prefix followed by `:`. Violations include wrong prefix (`eqn:` on an equation), wrong separator (`fn_beta_hat`), and no prefix at all (`results`, `tau_hat`).
3. **Duplicate check**: the same label defined more than once in the closure (uncommented) is an error.

For every *uncommented* reference (`\ref`, `\eqref`, any `\autoref`/`\cref`/`\Cref`/`\pageref` if present, and `\hyperref[label]{text}` — note its label is bracket-delimited, not brace-delimited):

4. **Existence check**: the referenced label must be defined somewhere in the closure (for the response doc, "the closure" includes the paper via `\externaldocument`).
5. **\eqref discipline**: references to equation labels must use `\eqref`, never `\ref`; references to anything that is not an equation must use `\ref` (or the other non-eqref commands), never `\eqref`. `\hyperref` and `\pageref` are exempt (they carry their own link text or page number).

Also report (informational, not errors): labels that are never referenced anywhere in the closure.

## Fix procedure

1. Produce the full violation report first (see Reporting), including a proposed rename for each nonconforming label (e.g., `eqn:sign_interest` → `e:sign_interest`, `fn_beta_hat` → `fn:beta_hat`, `design` → `s:design`, `tau_hat` → `e:tau_hat`) and each `\ref`↔`\eqref` swap.
2. If a proposed new name would collide with an existing label, flag it and ask instead of renaming.
3. Ask the user once for approval of the batch (they may exclude items).
4. Apply approved renames **atomically per label**: change the `\label` and every reference to it in the same pass, across the paper closure *and* the response doc. A label renamed in one place but not the other breaks compilation silently (`??` refs).
5. After edits, re-run the existence check (check 4) to confirm no ref was orphaned.

## Reporting

End with a concise summary, grouped by check, with file:line links for every item:

- Prefix violations: label, location, classification, proposed rename → applied / skipped by user / flagged (collision or in auto-generated file).
- `\ref`/`\eqref` misuse: each occurrence → applied / skipped.
- Refs to undefined labels, duplicate definitions: flagged for the user.
- Unreferenced labels: informational list.
- Totals: N labels checked, N references checked, N edits made.

If the closure is large, the scan (not the edits) can be parallelized across subagents by file batch, but the label↔ref cross-checks must be done on the merged results.
