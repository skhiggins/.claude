---
name: assess-report
description: Assess the user's draft referee report against the paper under review, point by point, checking accuracy, mistakes, and fairness. Use when the user invokes /assess-report, optionally passing the report file and/or paper PDF as arguments.
---

# Assess a draft referee report against the paper

Goal: verify every claim in the user's draft referee report against the full text of the paper, and write the assessment to a markdown file.

Two modes:
- **Full mode**: assess the entire report (Steps 1-4). Use when no prior assessment exists, or when the user asks for a fresh full assessment.
- **Incremental mode**: if `assess_report.md` already exists in the report's folder AND the user has highlighted part of the report (an `ide_selection` of lines from the report file) or otherwise pointed to specific points, assess only that part and update `assess_report.md` in place (see "Incremental mode" below).

## Step 1: Identify the inputs

- **Report**: the file passed as an argument, or else the open/most recently discussed report file in the paper's folder (typically `comments.txt` or a `*.md` report draft). If ambiguous, ask the user which file is the report.
- **Paper**: the PDF passed as an argument, or else the manuscript PDF in the same folder as the report. If ambiguous, ask.

## Step 2: Read the paper in full (if not already read)

If the full paper has NOT already been read in this conversation (verified by whether specific tables/pages can be cited from context), invoke the `read-pdf` skill on the paper PDF and follow it completely: convert to `.txt`, then read every chunk sequentially. If a converted `.txt` already exists next to the PDF, skip conversion but still read it in full.

If a preregistration / pre-analysis plan file exists in the same folder (e.g., `AEARCTR-*.txt`), read it too, since report claims about prespecification cannot be assessed without it. If the report makes prespecification claims and no registration file is present, note this in the assessment rather than guessing.

## Step 3: Assess the report point by point

Read the report file in full. Then go through it point by point (each numbered comment, including sub-points like 2a, 2b, and each distinct claim in the introduction paragraph). For each point, assess:

1. **(i) Accuracy**: Is everything the user says accurate? Check every factual claim against the paper: numbers, table/figure references, sample sizes, coefficient values, significance levels, what the paper does or does not report, quotes. Cite the specific PDF page / table / figure that confirms or contradicts each claim.
2. **(ii) Mistakes**: Are there any mistakes? Flag anything wrong or imprecise: wrong numbers, wrong exhibit references, claims the paper actually addresses somewhere (cite where), overstatements ("never reports X" when X appears in an appendix), or garbled details. Distinguish clear errors from defensible simplifications.
3. **(iii) Fairness**: Is it a fair critique? Judge whether the criticism is warranted given what the paper does: Is the request proportionate and actionable for the authors? Does the paper have a defense the report ignores? Would the editor find the point persuasive, and on what grounds? Where relevant, note if the critique could be strengthened (e.g., if the paper's own text supports a stronger version) or should be softened.

The authors do not get to reply to the report; the editor reads it and decides. So do not frame fairness objections as "the authors could reply X" or "the authors will say the point is already covered," and do not treat a possible author nitpick as a defect in the point. Evaluate each point on whether it is fair and accurate on the merits and on how the editor is likely to weigh it. If the paper does address something the report raises (e.g., a caveat in a footnote or a robustness table), state where, and judge whether the report's point still stands given that passage; that is an accuracy question, not a prediction of the authors' response.

Be direct: the user wants errors caught before the report goes to the editor, not reassurance. If a point cannot be verified from the available materials, say so explicitly rather than guessing.

## Step 4: Write the assessment to a markdown file

Save the assessment as `assess_report.md` in the same folder as the report file (e.g., `2026/JFQA/assess_report.md`), overwriting any previous assessment there.

Structure:

```markdown
# Assessment of referee report: <manuscript id / paper title>

_Report file: <path> (assessed <YYYY-MM-DD>)_

## Summary
<2-4 sentences: overall verdict, count of errors found, points needing attention before submission.>

## Point-by-point assessment

### <Point number and short label>
- **Accuracy:** <verified / issues, with page/table citations>
- **Mistakes:** <none, or each mistake with the correction>
- **Fairness:** <fair / needs strengthening / needs softening, with reasoning>
```

Do not modify the report file itself. After writing the file, give the user a brief summary in dialog, most importantly any outright errors that must be fixed, and link to the assessment file.

## Incremental mode: re-assessing part of the report

Trigger: `assess_report.md` already exists next to the report file, and the user runs the skill with part of the report highlighted (or names specific points). The highlighted text defines the scope; do not re-assess the rest of the report.

1. Read the current `assess_report.md` and the current report file in full (the report may have changed since the last assessment, and surrounding context is needed to interpret the selection).
2. Ensure the paper (and registration, if prespecification is at issue) is in context, per Step 2. Reading the full paper text is still required if it is not already in context — a partial assessment must be held to the same evidence standard as a full one.
3. Assess only the selected part, using the same (i) accuracy / (ii) mistakes / (iii) fairness criteria from Step 3. Compare against the existing assessment of that point, if any: note where the change resolves a previously flagged issue, where a previous note still applies, and any new issues introduced.
4. Update `assess_report.md` in place:
   - Replace the point sections covered by the selection; add new sections (in report order) for points that did not exist before; delete sections for points the user has removed from the report.
   - Update the Summary and any "Items to fix before submission" list so they reflect the current state of the whole report — remove fixed items, add new ones. Do not leave stale claims about points that changed.
   - Update the assessed date line, e.g. `_Report file: <path> (assessed <original date>; points X, Y re-assessed <YYYY-MM-DD>)_`.
   - Leave all sections outside the selection untouched.
5. In dialog, summarize only the re-assessed part: whether the change resolves prior flags, and any new errors.
