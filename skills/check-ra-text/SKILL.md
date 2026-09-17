---
name: check-ra-text
description: Review text written by a research assistant (typically appendix sections, data appendices, or figure/table notes in a LaTeX paper) for typos and, above all, for sentences that read as non-native or awkward English. Takes the subsections, exhibits, files, or line ranges to check as the argument (or the IDE selection). Never edits; writes a timestamped markdown report of suggested fixes and rewrites to the project's .claude folder. Use when the user calls /check-ra-text or asks to review, polish, or check RA-written text.
---

# Check RA-written text for typos and non-native English

The RAs who draft appendix text and exhibit notes are often not native English speakers. This skill reads the specified passages the way a native-speaking coauthor would before submission: it catches ordinary typos (as `/check-for-typos` does) **and** sentences that are grammatical but read as translated, awkward, or unclear. It reports; it never edits. The user reviews the report and either applies rows with `/fix-typos <report path>` or asks for the rewrites to be applied afterwards.

## Step 1: Determine the scope

The user will usually name the passages in the argument. Accepted forms, in any combination:

- **Section headings or labels**: "Appendix B", "the data appendix", "Section 8.2", `a:pls_us`, "Robustness". Resolve a heading to the span from its `\section`/`\subsection`/`\subsubsection`/`\paragraph` line to the next heading of the same or higher level (or `\end{document}`). Number-only references ("Appendix C", "Section 5.1") are resolved by counting headings in document order, with appendix letters counted from `\appendix` (or the file's first appendix `\section`); say in the report which heading you matched.
- **Exhibits**: "Figure A5 notes", "Table AII", `fig:branch_ihs_dep`. The scope is the whole float: caption, notes, and any `\input` text in it (generated tables and numbers are skipped, but their surrounding notes are checked).
- **Files**: a `.tex` path means the whole file.
- **Line ranges**: "main.tex L1600-1700".
- **IDE selection**: if no argument is given and text is selected in the editor, check the selection (extended to whole sentences/paragraphs).

If nothing is given and nothing is selected, ask which passages to check. Do not check the whole paper by default: the main text is the user's own writing, and the point of this skill is RA-drafted passages.

## Step 2: Collect the text

Run the collector shared with `/check-for-typos` from the skills directory (never a temp copy):

```
python <skills-root>/check-for-typos/scripts/collect_tex.py "<root main tex>.tex" --project-root "<project root>"
```

It writes `.claude/typos_source_<timestamp>.txt` with every `\input`/`\include` expanded in document order, comment text stripped (the `%` that starts each comment is kept), and each line prefixed `path:line:` with the original line number. Locate the requested spans in that file by their headings, labels, or line numbers, and read exactly those spans. If the collector is unavailable, read the source files directly with the Read tool.

Then read for context, not for review:

- the main-text paragraph(s) that discuss each exhibit or refer to each appendix section, so you know what the RA text is meant to say and which terms the paper uses for the same objects ("lottery months", "treatment branches", "stock of savings", "account holders"); check the project's memory index for settled terminology and editorial calls and do not re-litigate them;
- a page or two of the user's own main text, to match its register (first-person plural, present tense for results, sentence length).

## Step 3: Read every sentence of the scope

Read the whole scope sequentially, sentence by sentence; do not sample. For each sentence ask two questions: *Is anything wrong?* (Step 4a) and *Would a native-speaking economist have written it this way?* (Step 4b). Read the LaTeX as rendered text: drop markup wrappers, treat `\citet`/`\ref` as names and numbers, and read math only for the prose around it (do not proofread formulas, but do check that variables named in prose match the equation).

## Step 4a: Typos and mechanical errors (To fix)

Apply the same criteria as `/check-for-typos` Step 4: misspellings, wrong-word substitutions, missing or doubled words, unambiguous agreement errors (consider whether the subject or the verb is the one to change), a/an, wrong or missing prepositions that are outright errors, punctuation and quote-mark glitches, cross-reference wording ("Table" for a figure), line-break spacing before punctuation when a line does not end in `%`, and an unescaped `%` after a number. A `%` in the middle of a prose line is a deliberate comment-out; do not flag it.

## Step 4b: Non-native and awkward phrasing (Rewrites)

Flag a sentence when a careful native reader would pause, even if it is grammatical. Typical patterns, many of them Spanish-influenced:

- **Articles**: missing "the"/"a" before singular count nouns ("in Bansefi Survey", "at branch level"), and extra "the" before general plurals or abstract nouns ("the account holders save more", "the data of the accounts").
- **Prepositions and verb complements**: "allows to + verb" (needs an object or "allows for"), "permit to", "consists in", "depend of", "different to", "in the last years" (over the past few years), "since 2010 until 2015" (from ... to), "according to the results" used as a hedge, "at the end" for "in the end".
- **False friends and calques**: "realize" for carry out, "actual" for current, "assist to" for attend, "eventually" for possibly, "pretend" for intend, "comprehend" for comprise, "in function of" for as a function of, "the same than", "the 15\% of", "one of the most important ones", "economical" for economic, "informations".
- **Tense and aspect**: present perfect where simple past is idiomatic for a dated event, past tense for what the figure "shows", future tense for a fixed procedure, "is being" for a state.
- **Countable/uncountable and number**: "evidences", "researches", "a data", "informations", "the data is/are" inconsistent with the paper's convention.
- **Word order and sentence shape**: adverb placement ("we estimate also", "only" misplaced), very long sentences chained with "and"/"which"/"where", a subject separated from its verb by a long modifier, topic-comment sentences that start with the qualifier ("For the accounts opened in the lottery months, in treatment branches, the effect ...").
- **Register and hedging**: "it is worth to mention", "as we can see", "it is important to note that", "we can observe", "in order to" (to), "with the aim of", "as well as" for "and", "on the other side", "in this sense", "that is to say", ", being X the ..." (absolute clause), "respectively" without a clear pairing.
- **Referent and clarity**: "this"/"it"/"the same" with no clear antecedent; "the former/the latter" across sentences; a definition given after the term is used; a caption or note that describes a different figure (copied from a sibling exhibit).
- **Terminology consistency**: a term that differs from the main text's ("incentive months" vs "lottery months", "clients" vs "account holders", "branch office" vs "branch"), or a variable described in words that do not match the equation.
- **Redundancy and padding**: "each and every", "period of time", "in the month of October", "a total of 110 branches", "the results of the estimates".

For each flagged sentence, propose one rewrite that keeps the author's meaning and numbers and reads as the user's own prose. Rewrites must follow the user's writing rules (global CLAUDE.md): no filler intensifiers, no figurative language about what words or sentences "do", no "Not X. Just Y." constructions, future tense for future events, keep subject and verb close, em-dashes only where correct. Do not restyle for taste: if the sentence is idiomatic native English and clear, leave it alone even if you would phrase it differently.

## Step 4c: Unsure

List separately, with a one-line reason, anything that may be deliberate: inconsistent forms within the document, a possibly missing article where the sentence is still fine, a number or date that looks slipped (belongs to `/check-hardcoded`), a sentence you would only change on taste, and cases where a fix requires knowing the data (e.g., whether "each branch" or "each account" is meant).

## Step 5: Write the report

Write `.claude/ra_text_{YYYYMMDD_HHMMSS}.md` in the project's `.claude/` folder (never overwrite). Use this structure; the `## To fix` and `## Unsure` tables are the `/fix-typos` format so the user can apply them with `/fix-typos .claude/ra_text_<timestamp>.md` after review, and `## Rewrites` uses the same verbatim `Original` → `Suggested` convention so rows moved into `## To fix` also apply cleanly.

```markdown
# RA text review

- Scope: Appendix B (SavingsLotteries_tables_apdx.tex L140-L200), notes to Figure A5 (SavingsLotteries_figures_apdx.tex L1010-L1020)
- Root file: main.tex
- Date: YYYY-MM-DD
- Sentences read: N
- Skipped as generated: (list, or none)

## To fix

| File | Line | Original | Fix | Notes |
|---|---|---|---|---|
| SavingsLotteries_tables_apdx.tex | [151](../SavingsLotteries_tables_apdx.tex#L151) | `households in Bansefi Survey` | `households in the Bansefi Survey` | missing article before a named survey |

## Rewrites

| File | Line | Original | Suggested | Why |
|---|---|---|---|---|
| SavingsLotteries_tables_apdx.tex | [179](../SavingsLotteries_tables_apdx.tex#L179) | `Column 4 to 6 test if the differences are statistically significant between the groups` | `Columns 4 to 6 test whether the differences between the groups are statistically significant` | plural "Columns"; "whether" for an indirect question; keep "between the groups" next to "differences" |

## Unsure

| File | Line | Original | Suggested | Why unsure |
|---|---|---|---|---|
| paper/sl_geo_data_appendix_text.tex | [120](../paper/sl_geo_data_appendix_text.tex#L120) | `(i.e. not grouped` | `(i.e., not grouped` | comma after i.e. used elsewhere; may be deliberate |

## Recurring patterns

- Missing "the" before named surveys and datasets (6 rows).
- "Column N to M" for plural subjects (4 rows).
```

- `Line` is a markdown link relative to the report file: a source file at the project root is `../main.tex#L123`, one in `paper/` is `../paper/main.tex#L123`. Link every line number mentioned in Notes/Why the same way (`[L855](../main.tex#L855)`). Keep `File` as plain text.
- `Original` is a **verbatim substring of the source line**, in backticks, unique on that line, including every character the change touches (keep braces, `\%`, `~`, `\ref{}` exactly). `Suggested`/`Fix` replaces exactly that substring. A rewrite may span a whole sentence but not a line break; if a sentence spans lines, give one row per line or quote the part on one line and describe the rest in Why.
- One row per sentence in `## Rewrites`; if a sentence has both a typo and a phrasing problem, put the typo in `## To fix` and the rewrite in `## Rewrites` with the typo already corrected in `Suggested`, and note the overlap so the user applies one or the other.
- `Why` states the grammar or usage point in a few words, so the RA can learn the pattern; do not write essays.
- Sort rows by file (document order) then line. Never propose edits to generated files (`results/`, `tables/` produced by scripts): say "fix in generating script" in Notes.
- `## Recurring patterns` lists the three to six most frequent issue types with row counts; it is feedback the user can pass to the RA. Omit the section if nothing recurs.

## Step 6: Report back

Tell the user: the report filename, the scope actually checked (with line ranges), counts for To fix, Rewrites, and Unsure, the recurring patterns in one or two lines, and that after reviewing they can run `/fix-typos <report path>` to apply the To fix rows (and any Rewrites rows they move there), or ask for specific rewrites to be applied. Do not apply anything yourself.
