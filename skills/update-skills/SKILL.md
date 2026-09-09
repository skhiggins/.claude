---
name: update-skills
description: Reconcile duplicated skills between the project's .claude/skills folder (Dropbox-synced across machines) and the user-level ~/.claude/skills folder (shared across projects on this machine). Finds skills present in both, diffs them, infers which copy is newer, asks the user to confirm, then copies the confirmed newer copy over the older one so both locations match. Skills present in only one location are copied to the other so every skill lives in both places. Use when the user runs /update-skills or asks to sync/reconcile their skills.
---

# Update duplicated skills

The user keeps user-created skills in two places on purpose:

- **Project-level**: `<project>/.claude/skills/<name>/` — travels across machines via Dropbox, but only applies to that project.
- **User-level**: `~/.claude/skills/<name>/` — applies to every project on this machine, but does not sync across machines.

Edits sometimes land in only one copy. This skill reconciles them.

## Step 1 — Enumerate and match

List skill directories (those containing a `SKILL.md`) under both locations. Match by directory name. Skills present in only one location are handled in Step 5b.

## Step 2 — Compare each matched pair

For each skill present in both locations, compare the full directory trees (every file, not just SKILL.md): same set of relative paths, and same content per file (e.g., `Get-FileHash -Algorithm SHA256`). If identical, report the skill as in sync and move on.

## Step 3 — For pairs that differ, infer which is more recent

Gather evidence, in rough order of reliability:

1. **File timestamps**: `LastWriteTime` of each differing file. `Copy-Item` and Dropbox both preserve modification times, so after a sync the two copies have equal mtimes; a strictly later mtime usually indicates a later manual edit. Be suspicious if timestamps and content evidence disagree.
2. **Content structure**: is one version a superset of the other (extra sections, extra files, extra rules)? Additions usually indicate the newer copy; but a deliberate trim is also possible, so treat this as suggestive, not decisive.
3. **Internal clues**: dates, references to tools/paths/features that only existed later, version notes.
4. **Git history**: if either location is inside a git repo, `git log` on the skill path is authoritative for that copy.

## Step 4 — Explain to the user, then confirm

In a standalone message with no tool calls attached, for each differing skill explain:

- **How the copies differ** — a concise, human-readable description of the substantive differences (not a raw dump unless the user asks).
- **Which copy you think is more recent and why**, citing the evidence from Step 3. If you have no view, say so, but still walk through the evidence you considered and why it was inconclusive.

Then ask the user to confirm which copy is most recent, using AskUserQuestion with **one question per duplicated skill** (never bundle multiple skills into one multi-select). Options per skill: project copy is newer / user copy is newer / skip this skill.

## Step 5 — Copy the confirmed newer copy over the other

For each confirmed skill, copy the newer skill directory over the older location so the two are identical (e.g., `Copy-Item -Recurse -Force <newer>\* <older>\`). If the older copy contains files that do not exist in the newer copy, do not silently delete them — tell the user which files would be removed and confirm before deleting.

## Step 5b — Copy one-location skills to the other location

Skills that exist in only one of the two locations should end up in both. List them (noting which location each currently lives in), then confirm with the user in a single AskUserQuestion (multi-select over the skills — one decision), in case a skill is deliberately kept in one place. Copy each confirmed skill directory to the missing location, preserving modification times (e.g., `Copy-Item -Recurse`, or `cp -rp` in bash), so future timestamp comparisons in Step 3 remain meaningful.

## Step 6 — Report

Summarize: which skills were in sync, which were updated and in which direction, and which were copied to the other location (plus any the user chose to keep in one place).
