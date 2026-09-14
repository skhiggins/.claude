---
name: check-notes-vs-code
description: Verify that the notes (and captions) of figures and tables in a LaTeX paper describe what the generating code actually does — sample, time unit and window, geographic unit, variable and shock definitions, transformations, winsorizing, fixed effects, clustering, weights, excluded periods, significance stars — by tracing each exhibit's \input/\includegraphics file back to the script that writes it in the code repository and reading that script and its upstream prep scripts. Takes exhibit labels, numbers, files, or the IDE selection as the argument; with no argument, checks every exhibit in the paper. Never edits; writes a timestamped markdown report to the project's .claude folder. Use when the user calls /check-notes-vs-code or asks whether exhibit notes match the code.
---

# Check exhibit notes against the code

Notes under figures and tables are often written by an RA from memory or copied from a sibling exhibit, and then the code changes. This skill reads each note claim by claim and checks every claim that the code can settle against the script that produces the exhibit. It reports; it never edits the paper or the code.

Examples of what it catches (all from one real note): "quarter to month" for a quarter-over-quarter change; "subdelegación" where the code merges on municipality; "clustered at the individual level" where the code clusters on branch; "month-year fixed effects" where the regression absorbs quarter-year.

## Step 1: Determine the scope

Accepted argument forms, in any combination:

- **Exhibit labels or numbers**: `tab:shocks`, `f:holiday_withdraw`, "Table A5", "Figure 3", "Appendix Table AII". Resolve numbers by counting floats in document order within each series (main figures, main tables, appendix figures, appendix tables; `\appendix` or the appendix files start the appendix series). Say in the report which float you matched.
- **Files**: a `.tex` path means every float in that file.
- **IDE selection**: if no argument is given and the selection lies inside a float, check that float.
- **No argument, no selection**: check every figure and table in the paper (main text and appendix). Confirm with the user first if there are more than about 30 exhibits, since each one requires reading code.

The unit of work is one float environment: caption, notes, and the `\input`/`\includegraphics` files inside it.

## Step 2: Locate the code repository

The scripts live in a git clone, not in the paper's Dropbox/Overleaf folder, and copies of scripts inside the paper folder may be stale. Find the repo in this order:

1. The project's memory (`MEMORY.md` in the project's `.claude/memory/`; look for a "scripts repo" or "code repo" entry) or `CLAUDE.md`.
2. A sibling clone whose name matches the paper folder under `C:/GitHub/` (Windows) or `~/GitHub/`.
3. Otherwise ask the user for the path.

Then run `git pull` in the repo (read-only otherwise) and record the commit hash (`git log --oneline -1`) for the report. If the pull fails, say so and check against the local state.

Learn the repo's conventions before tracing: the run file (`00_run.do`, `master.do`, `Makefile`, `run_all.R`, or similar) gives the script order; each script's header typically lists "Files used" and "Files created" and a "Purpose" line; a `README.md` may map outputs to scripts. Results are usually written under `results/tables/`, `results/graphs/`, `results/numbers/`.

## Step 3: Trace each exhibit to its code

For each float:

1. List the generated files it uses: every `\input{...}` (tables, number fragments in the notes), `\ExpandableInput`, and `\includegraphics{...}` inside the float. Strip `_cropped`, `-eps-converted-to`, and extension variants to get the base name.
2. Find the writing script: `grep -rn "<base name>" <repo>/scripts` (and other script folders). The script that writes the file is the one that passes the name to `latexify`, `esttab`/`outreg2`, `graph export`, `ggsave`, `write.table`, `print_asis`, `file open`, etc. If several scripts match, prefer the one that writes rather than reads.
3. Read the writing script in full: the regression or tabulation commands, the sample restrictions (`keep if`, `drop if`, `if` conditions on the estimation command), winsorizing or trimming calls, `absorb()`/`i.` fixed effects, `cluster()`/`vce()`, weights, transformations (`asinh`, `log`), the loop that defines which specification lands in which column or panel, and the code that writes the notes' number fragments (N, means).
4. Walk upstream through "Files used" until every variable the note defines is traced to its construction: the dataset the writing script loads, the prep script that creates it, and so on. Typical things that live upstream: how a shock or treatment indicator is defined and at what geographic and time unit, how the panel is collapsed (day, month, two-month period, quarter), how the sample window and excluded periods are set, and how outcomes are constructed (counts, amounts, stocks, indicators).
5. Note the exact file and line for every fact you rely on, so the report can cite `script.do:123`.

Do not stop at the first script if the note's claim concerns something defined upstream. A clustering claim is settled in the regression script; a "quarter to quarter" claim is settled in the prep script that computes the change.

If a file has no writing script in the repo (hand-made table, external figure), say "not generated by the repo" and check only what the note claims about sources.

## Step 4: Check the note claim by claim

Split the note (and the caption) into atomic claims and check each one the code can settle. The standard checklist; skip items the note does not mention:

- **Sample**: which accounts/branches/units, opening dates or cohorts, treatment status, balanced or unbalanced panel, any `keep if`/`drop if` the note omits or contradicts.
- **Unit of observation and time unit**: account, branch, municipality; day, week, month, two-month period, quarter; "account × quarter" must match the collapse.
- **Time window and excluded periods**: start and end dates, lottery or incentive months dropped, event windows and binning of endpoints.
- **Geographic unit**: municipality, locality, subdelegación, state; what the merge key is.
- **Variable definitions**: outcomes (count vs amount vs stock; IHS or log; in pesos or dollars; winsorized or not, at what percentile, within what cells), regressors, indicators (what equals one and when, e.g., post = strictly after the first shock quarter), thresholds (15% of what baseline, computed how).
- **Specification**: equation in the note vs the estimation command: fixed effects (which, at what level), interactions, controls, weights, event-time reference period, stacked or pooled designs.
- **Inference**: clustering level, bootstrap and its resampling unit and repetitions, robust SEs, significance-star thresholds, confidence-interval level of whiskers, marker conventions for significance.
- **Numbers in the note**: N, number of clusters, control means, dates: confirm which fragment file they come from and that its script computes what the note says it is (e.g., "control mean in the pre-period" vs the code's `sum ... if post == 0`).
- **Panels and columns**: the note's mapping of panels/columns to specifications matches the loop in the script.
- **Caption**: the caption names the right outcome and transformation for the file actually included.

Verdicts: **Match**, **Mismatch** (the note says X, the code does Y), **Imprecise** (not wrong but the code allows a more exact statement, e.g., "periods after the shock" for "quarters strictly after the first shock quarter"), **Not verifiable** (the code does not settle it, e.g., a claim about data provenance). Only report Mismatch and Imprecise rows in detail; list Match counts in the summary.

Do not check prose quality, typos, or style here (`/check-for-typos`, `/check-ra-text`), and do not re-litigate settled editorial calls recorded in project memory. Do not flag differences between the note and the main text; the comparison is note vs code.

## Step 5: Parallelize when the scope is large

For more than about five exhibits, spawn one general-purpose agent per exhibit (or per group of exhibits that share a writing script), giving each the repo path, the float's source lines, and Steps 3 and 4 verbatim, and asking for the per-exhibit table in the report format below. Merge the returned tables into one report; keep the exhibits in document order. Do not have agents edit anything.

## Step 6: Write the report

Write `.claude/notes_vs_code_{YYYYMMDD_HHMMSS}.md` in the project's `.claude/` folder (never overwrite):

```markdown
# Exhibit notes vs code

- Paper root: main.tex
- Code repo: C:/GitHub/SavingsLotteries-repl @ 46553f9b (pulled YYYY-MM-DD)
- Scope: Table A7 (tab:shocks), Figure A5 (f:holiday_withdraw)
- Date: YYYY-MM-DD
- Exhibits checked: 2; claims checked: 23; mismatches: 4; imprecise: 2; not verifiable: 1

## Table A7: Response to Local Unemployment Shocks (`tab:shocks`)

- Note: [SavingsLotteries_tables_apdx.tex:339](../SavingsLotteries_tables_apdx.tex#L339)
- Generated files: results/tables/ENOE_15_postshock.tex, results/tables/ENOE_15_did.tex, results/numbers/ENOE_obs.tex, ...
- Writing script: scripts/134_unemployment_regs.do; upstream: scripts/133_unemployment_accounts_prep.do, scripts/132_unemployment_shocks_prep.do
- Claims checked: 12 (match 7, mismatch 4, imprecise 1)

| Claim in note | Note says | Code does | Verdict | Code location | Suggested wording |
|---|---|---|---|---|---|
| Shock definition | `negative change in employment quarter to month` | quarter-over-quarter change vs previous quarter of the same municipality, negative only, exceeding 15% of mean 2009 employment | Mismatch | 132_unemployment_shocks_prep.do:90-107 | `a quarter-to-quarter fall in employment ... exceeding 15\% of the municipality's average quarterly employment in 2009` |
| Clustering | `clustered at the individual level` | `cluster(sucursal)`: branch | Mismatch | 134_unemployment_regs.do:75, 105 | `clustered at the branch level` |
| Post-shock indicator | `equals 1 for the periods after the unemployment shock` | `post = quarter_id > shock_qdate`: quarters strictly after the first shock quarter | Imprecise | 134_unemployment_regs.do:59 | `equals one in the quarters after the first shock quarter` |

## Figure A5: ...
```

- `Note says` quotes the note verbatim (a substring of the source line, in backticks) so the user can find and edit it; `Code does` states the fact in words with the key command or variable name; `Code location` is `script:line` (plain text; the repo is outside the paper folder so links do not resolve).
- `Suggested wording` is a replacement for the quoted phrase that states what the code does, in the paper's own terminology (match the main text's terms: "lottery months", "treatment branches", "account holders"); leave it blank for Not verifiable rows.
- If a claim is wrong because the **code** is wrong (the note describes the intended design and the script departs from it), say so in the row and add it to a final `## Possible code issues` section; the fix belongs in the script, not the note.
- If a generated table's own row labels or headers conflict with the note, note that the label fix belongs in the generating script.
- Generated files that could not be traced go in a `## Untraced files` section with the grep you ran.

## Step 7: Report back

Tell the user: the report filename, the repo and commit checked, the exhibits covered, the counts of mismatches and imprecise claims, and the two or three most consequential mismatches in one line each (inference and sample claims first). Do not edit the paper or the code; the user decides which notes to rewrite and can then ask for the rewrites or use `/check-ra-text` on the corrected notes.
