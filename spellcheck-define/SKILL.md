---
name: spellcheck-define
description: Add every word in the "Safe to ignore" section of the latest spellcheck report (.claude/spellcheck_*.md) to the LTeX+ dictionary in .vscode/settings.json. Use when the user calls /spellcheck-define after reviewing a /spellcheck report.
---

# Add ignorable words to the LTeX+ dictionary

## Step 1: Locate and re-read the spellcheck report

Reports live in the project's `.claude/` folder as `spellcheck_{YYYYMMDD_HHMMSS}.md`. Use the report passed as the skill argument if given; otherwise use the one with the latest timestamp in its filename (confirm with the user if that seems stale).

**Always re-read the file now, even if you generated it earlier in this session**: the user may have moved rows between sections or edited words after /spellcheck ran. Act only on the current contents.

## Step 2: Extract the words

Take the `Word` column of every row in the `## Safe to ignore` section. Deduplicate, preserving the capitalization shown (the LTeX dictionary is case-sensitive; a lowercase entry also covers capitalized uses, but not vice versa).

## Step 3: Merge into .vscode/settings.json

At the project root, read `.vscode/settings.json` (create it if missing) and merge the words into the `"ltex.dictionary.en-US"` array (use the matching language key if the project checks a different language):

- Preserve all other keys and any existing dictionary entries.
- Add only words not already present; keep the array sorted case-insensitively.

## Step 4: Report back

Tell the user how many words were added and how many were already present. Note that the LTeX+ extension usually picks up the settings change immediately, but a window reload ("Developer: Reload Window") may be needed; subsequent /spellcheck runs read this same setting, so these words will no longer be flagged.
