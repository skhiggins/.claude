---
name: succinct
description: Answer the user's question or request within a hard word limit (default 100 words) to avoid verbose responses padded with superfluous information. Use when the user invokes /succinct, optionally followed by a word count and/or the question itself.
argument-hint: [word limit] [question]
---

# Answer within a word limit

Answer the request in at most N words, where N is the first integer in the arguments if one is given, and 100 otherwise. The rest of the arguments, if any, is the question; if there is no question in the arguments, answer the most recent user question in the conversation.

## Rules

- The limit is a hard cap on the visible response, including any headers, list labels, and code. Count words before printing; if over, cut and recount rather than printing and apologizing.
- Lead with the answer. No preamble ("Great question", "Here is a summary"), no restating the question, no closing offers ("Let me know if...").
- Include only what changes the reader's understanding or decision: the conclusion, the key reason or evidence, and any necessary caveat. Omit background the user already has, alternative options not being recommended, and explanations of how the answer was obtained.
- Prefer plain sentences over bullet lists and headers unless the content is a list. Formatting counts against the budget and rarely adds information at this length.
- Do not compensate for the cap by making tool calls that dump long output; the cap applies to the response the user reads.
- If the question cannot be answered adequately within the limit, give the best answer that fits and state in a few words what was omitted (e.g., "Details on X omitted."), so the user can ask for more.
- All other standing preferences (no filler intensifiers, no figurative language about rhetoric, link file references) still apply.
