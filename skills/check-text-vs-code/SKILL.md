---
name: check-text-vs-code
description: Verify that what a LaTeX paper says was done matches what the code repository actually does. Covers figure and table notes and captions, and main-text passages that describe data, sample, variable and shock definitions, specifications, inference, and results (data section, empirical strategy, robustness paragraphs, appendix text). Checks sample, time unit and window, geographic unit, definitions, transformations, winsorizing, fixed effects, clustering, weights, excluded periods, significance stars, and the number fragments pulled into the text, by tracing each exhibit or \input number to the script that produces it and reading that script and its upstream prep scripts. Takes exhibit labels, section names, files, line ranges, or the IDE selection as the argument; with no argument, checks every exhibit and every methods passage in the paper. Never edits; writes a timestamped markdown report to the project's .claude folder. Use when the user calls /check-text-vs-code or asks whether the paper's description of the analysis matches the code.
---

# Check the paper's text against the code

Descriptions of what was done drift away from the code: an RA writes a note from memory, a definition is changed in a script but not in the data section, a robustness paragraph describes a specification that was later replaced. This skill reads the paper's methods-type claims one by one, in exhibit notes and in the main text alike, and checks each claim the code can settle against the scripts that produce the results. It reports; it never edits the paper or the code.

Examples of what it catches: "quarter to month" for a quarter-over-quarter change; "subdelegación" where the code merges on municipality; "clustered at the individual level" where the code clusters on branch; a data section saying transactions run through August 2015 when the data end in July; a main-text sentence defining a shock as a 15% fall "compared to the local area's baseline" when the code uses the 2009 mean; a control-mean row computed over all accounts.

## Step 1: Determine the scope

Accepted argument forms, in any combination:

- **Exhibit labels or numbers**: `tab:shocks`, `f:holiday_withdraw`, "Table A5", "Figure 3". Resolve numbers by counting floats in document order within each series (main figures, main tables, appendix figures, appendix tables). The unit is the float: caption, notes, and the `\input`/`\includegraphics` files inside it.
- **Main-text passages**: a section or subsection name or label ("Section 4", "Data", `s:data`, "the robustness subsection"), a paragraph identified by its first words, or a line range ("main.tex L780-L800"). Resolve a heading to the span up to the next heading of the same or higher level.
- **Files**: a `.tex` path means every float and every prose passage in that file.
- **IDE selection**: if no argument is given and text is selected, check the selection, extended to whole paragraphs or to the enclosing float.
- **No argument, no selection**: check the whole paper: every figure and table, plus every main-text and appendix passage that describes data, sample, definitions, specifications, or inference. Confirm with the user first, since a whole paper means reading most of the code.

When a main-text passage is in scope, the exhibits it references (`\ref` to tables and figures) are in scope too, because the passage's claims are usually settled by the same scripts.

## Step 2: Locate the code repository

The scripts live in a git clone, not in the paper's Dropbox/Overleaf folder, and copies of scripts inside the paper folder may be stale. Find the repo in this order:

1. The project's memory (`MEMORY.md` in the project's `.claude/memory/`; look for a "scripts repo" or "code repo" entry) or `CLAUDE.md`.
2. A sibling clone whose name matches the paper folder under `C:/GitHub/` (Windows) or `~/GitHub/`.
3. Otherwise ask the user for the path.

Then run `git pull` in the repo (read-only otherwise) and record the commit hash (`git log --oneline -1`) for the report. If the pull fails, say so and check against the local state.

Learn the repo's conventions before tracing: the run file (`00_run.do`, `master.do`, `Makefile`, `run_all.R`, or similar) gives the script order; each script's header typically lists "Files used" and "Files created" and a "Purpose" line; a `README.md` may map outputs to scripts. Results are usually written under `results/tables/`, `results/graphs/`, `results/numbers/`.

## Step 3: Extract the claims

**From an exhibit**: split the caption and note into atomic claims (see the checklist in Step 5).

**From a main-text passage**: extract every sentence that states what was done or what the data are, as opposed to interpretation. Typical claim-bearing sentences:

- data description: source, unit of observation, period covered, how variables are constructed, what is dropped or winsorized, how treatment and control are defined, how randomization or matching was done;
- definitions in prose: "we define a local shock as ...", "active accounts are accounts that ...", "the stock of savings is computed as ...";
- specification statements: "we estimate equation (3) with branch and month fixed effects", "standard errors are clustered at the branch level", "we winsorize at the 95th percentile", "the event window runs from 12 months before to 36 months after";
- result statements that embed a procedure: "the joint test across the six post-lottery coefficients", "averaging over the four years after the incentive", "in the 110 experimental branches";
- numbers in prose that come from the data, whether pulled in with `\input{results/numbers/...}` or typed. For an `\input` fragment, the claim is that the fragment measures what the sentence says it measures (e.g., the sentence says "control-group mean in the lottery months" and the script computes it that way). For a typed number, check it against the code's output if the output exists, and note that typed numbers belong to `/check-hardcoded`.

Interpretation, motivation, literature, and framing sentences are out of scope. Do not check prose quality or typos (`/check-for-typos`, `/check-ra-text`), and do not re-litigate settled editorial calls recorded in project memory.

## Step 4: Trace each claim to its code

For each exhibit, and for each main-text claim:

1. **Start from generated files.** List every `\input{...}`, `\ExpandableInput`, and `\includegraphics{...}` in the float or passage; strip `_cropped`, `-eps-converted-to`, and extension variants to get base names. For a main-text passage without any generated file, use the exhibits it references, then the variable or concept names (grep the scripts for `shock`, `winsor`, `cluster(`, `asinh`, `keep if`, the outcome names).
2. **Find the writing script**: `grep -rn "<base name>" <repo>/scripts` (and other script folders). The writer is the script that passes the name to `latexify`, `esttab`/`outreg2`, `graph export`, `ggsave`, `write.table`, `print_asis`, `file open`, etc.; prefer writers over readers when several scripts match.
3. **Read the writing script in full**: estimation or tabulation commands, sample restrictions (`keep if`, `drop if`, `if` conditions on the estimation command), winsorizing or trimming, `absorb()`/`i.` fixed effects, `cluster()`/`vce()`, weights, transformations (`asinh`, `log`), the loop that maps specifications to columns or panels, and the code that writes each number fragment (what is summed, over which observations, with which `if`).
4. **Walk upstream** through "Files used" until every variable the claim depends on is traced to its construction: the dataset the writer loads, the prep script that creates it, and so on. Upstream is where definitions of shocks and treatment indicators, geographic and time units, panel collapses (day, month, two-month period, quarter), sample windows and excluded periods, and outcome constructions live.
5. **Record the exact file and line** for every fact you rely on, so the report can cite `script.do:123`.

Do not stop at the first script if the claim concerns something defined upstream: clustering is settled in the regression script; "quarter to quarter" is settled in the prep script that computes the change; "transactions through July 2015" is settled where the raw data are read or trimmed.

If a file has no writing script in the repo (hand-made table, external figure, a number typed from an outside source), say "not generated by the repo" and check only what the code can settle.

## Step 5: Check claim by claim

The checklist; skip items the text does not mention:

- **Sample**: which accounts/branches/units, opening dates or cohorts, treatment status, balanced or unbalanced panel, any `keep if`/`drop if` the text omits or contradicts, the number of units.
- **Unit of observation and time unit**: account, branch, municipality; day, week, month, two-month period, quarter; "account × quarter" must match the collapse.
- **Time window and excluded periods**: start and end dates (and whether the last period is partial), lottery or incentive months dropped, event windows and endpoint binning.
- **Geographic unit**: municipality, locality, subdelegación, state; the merge key.
- **Variable definitions**: outcomes (count vs amount vs stock; IHS or log; pesos or dollars; winsorized or not, at what percentile, within what cells), regressors, indicators (what equals one and when), thresholds (15% of what baseline, computed how), "active" or "new" account definitions.
- **Specification**: equation in the text vs the estimation command: fixed effects and their level, interactions, controls, weights, reference period, stacked or pooled designs, which coefficients a joint test covers.
- **Inference**: clustering level, bootstrap unit and repetitions, robust SEs, star thresholds, confidence-interval level, marker conventions for significance.
- **Numbers**: N, clusters, means, dates, percentages: which fragment they come from and that the fragment's script computes what the sentence says (e.g., "control mean" with a `tratamiento == 0` restriction; "pre-period" with the right `if`).
- **Panels and columns** (exhibits): the note's mapping matches the loop in the script; the caption names the outcome and transformation of the file actually included.

Verdicts: **Match**, **Mismatch** (the text says X, the code does Y), **Imprecise** (not wrong, but the code allows a more exact statement), **Not verifiable** (the code does not settle it). Report Mismatch and Imprecise rows in detail; give Match counts in the summary.

Do not flag differences between the note and the main text as such; each is compared with the code, and if they disagree with each other the report will show it through their separate verdicts.

## Step 6: Parallelize when the scope is large

For more than about five exhibits or passages, spawn one general-purpose agent per exhibit, per section, or per group that shares a writing script, giving each the repo path, the source lines, and Steps 3 to 5 verbatim, and asking for the per-item table in the report format below. Merge the returned tables into one report in document order. Do not have agents edit anything.

## Step 7: Write the report

Write `.claude/text_vs_code_{YYYYMMDD_HHMMSS}.md` in the project's `.claude/` folder (never overwrite):

```markdown
# Paper text vs code

- Paper root: main.tex
- Code repo: C:/GitHub/SavingsLotteries-repl @ 46553f9b (pulled YYYY-MM-DD)
- Scope: Section 4 (Data), Table A7 (tab:shocks)
- Date: YYYY-MM-DD
- Items checked: 2; claims checked: 31; mismatches: 5; imprecise: 3; not verifiable: 2

## Section 4: Data ([main.tex:784-800](../main.tex#L784-L800))

- Generated files used: results/numbers/n_branches.tex, results/numbers/n_accounts_lottery.tex
- Scripts: scripts/01_movimientos_dataprep.do (raw transactions), scripts/03_branches_dataprep.do, scripts/40_summary_numbers.do
- Claims checked: 9 (match 7, mismatch 1, imprecise 1)

| Claim | Text says | Code does | Verdict | Code location | Suggested wording |
|---|---|---|---|---|---|
| End of transaction data | `through August 2015` | last transaction date kept is 2015-07-31 | Mismatch | 01_movimientos_dataprep.do:88 | `through July 2015` |

## Table A7: Effect of Local Unemployment Shocks (`tab:shocks`)

- Note: [SavingsLotteries_tables_apdx.tex:339](../SavingsLotteries_tables_apdx.tex#L339)
- Generated files: results/tables/ENOE_15_postshock.tex, results/tables/ENOE_15_did.tex, results/numbers/ENOE_obs.tex, results/numbers/c_mean_deposit.tex, ...
- Writing script: scripts/134_unemployment_regs.do; upstream: scripts/133_unemployment_accounts_prep.do, scripts/132_unemployment_shocks_prep.do
- Claims checked: 12 (match 7, mismatch 4, imprecise 1)

| Claim | Text says | Code does | Verdict | Code location | Suggested wording |
|---|---|---|---|---|---|
| Shock definition | `negative change in employment quarter to month` | quarter-over-quarter change vs previous quarter in the same municipality, negative only, exceeding 15% of mean 2009 employment | Mismatch | 132_unemployment_shocks_prep.do:90-107 | `a quarter-to-quarter fall in employment ... exceeding 15\% of the municipality's average quarterly employment in 2009` |
| Clustering | `clustered at the individual level` | `cluster(sucursal)`: branch | Mismatch | 134_unemployment_regs.do:75, 105 | `clustered at the branch level` |
| Control mean row | row label `Mean (control, level)` | `sum <var> if lottery_quarter == 0 & post_shock == 0`, no treatment restriction: pre-shock mean over all accounts | Mismatch (code) | 134_unemployment_regs.do:147 | fix in script (add `tratamiento == 0`) or relabel the row |

## Possible code issues

- 134_unemployment_regs.do:147: "control mean" computed over treatment and control accounts.

## Untraced files

- (none)
```

- `Text says` quotes the source verbatim (a substring of one source line, in backticks) so the user can find and edit it; `Code does` states the fact in words with the key command or variable name; `Code location` is `script:line` (plain text; the repo is outside the paper folder so links do not resolve). Line links for the paper follow the `/check-for-typos` convention (`../main.tex#L123` from the report in `.claude/`).
- `Suggested wording` replaces the quoted phrase with what the code does, in the paper's own terminology (match the main text's terms: "lottery months", "treatment branches", "account holders"); leave it blank for Not verifiable rows.
- If a claim fails because the **code** departs from the intended design that the text describes, mark the verdict "Mismatch (code)", say so in the row, and list it under `## Possible code issues`; the fix belongs in the script, not the text.
- If a generated table's own row labels or headers conflict with the code, the label fix belongs in the generating script; say so.
- Generated files or claims that could not be traced go under `## Untraced files` with the grep you ran.

## Step 8: Report back

Tell the user: the report filename, the repo and commit checked, the exhibits and passages covered, the counts of mismatches and imprecise claims, and the two or three most consequential mismatches in one line each (inference and sample claims first, then definitions). Do not edit the paper or the code; the user decides which text to rewrite and which scripts to change, and can then ask for the rewrites or run `/check-ra-text` on the corrected passages.
