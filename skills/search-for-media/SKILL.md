---
name: search-for-media
description: Search online for media/news articles (NYT, WSJ, FT, local outlets, trade press) about a particular topic, e.g., to support a claim on a slide, provide background for a discussion, or find citable journalism. Use when the user calls /search-for-media or asks to find news articles, press coverage, or media reporting on a topic.
---

# Search for media articles on a topic

Goal: find news/media articles on a topic and report what each one actually says, with enough sourcing detail (outlet, author, date, link) that the user can cite it on a slide or in a document.

## Step 0: Pin down the ask

Before searching, state (and if ambiguous, ask):

1. **The claim or question the article needs to address** — be precise. "Coverage of BNPL" is too loose; "reporting that BNPL is increasingly used for essentials like rent and utilities" is searchable and checkable.
2. **Purpose**: slide citation, background reading, a quotable line, or evidence for/against a claim. This determines how deeply each candidate must be read.
3. **Geography and language**: if the topic concerns a specific country, plan to search its local language and outlets too (same principle as the search-for-photo skill) — domestic press covers domestic phenomena far more densely than the international press.

## Step 1: Search in English

- WebSearch with topic keywords plus outlet names or `site:` terms for quality control (e.g., "nytimes.com BNPL rent utilities", "site:ft.com ...").
- Use the `allowed_domains` parameter to restrict to specific outlets when the user asked for a particular source.
- For recent phenomena, anchor the query to the news event most likely to have generated coverage; event-anchored queries beat topic queries.
- Cast wider than the big brands: trade press (industry outlets), wire services (Reuters, AP, ANI, PTI), and regional papers often have the substantive piece the national outlets summarize.

## Step 2: Search in the local language (when the topic is country-specific)

Translate the query into the local language, native script, using terms a local journalist would use (program names, product names, agency names). Run several phrasings. Local outlets frequently carry detail (statistics, regulator statements, on-the-ground reporting) absent from English coverage.

## Step 3: Read before characterizing — and route around paywalls by searching more, not by asking the user

The searching is this skill's job. Do not hand the search back to the user; exhaust the routes below first.

- **Never characterize an article's substance from its headline, URL, or search snippet alone.** Fetch and read the article before saying what it argues or whether it supports a claim; if the full text cannot be read, say so explicitly and mark any characterization as unverified speculation based on the headline/snippet. (An article whose headline looks off-point may state the needed claim directly in its body.)
- Paywalled outlets (NYT, WSJ, FT, Bloomberg, The Ken, The Information) usually block automated fetching. When the on-point piece is paywalled, keep searching rather than stopping:
  - The same story is usually reported by wire services (Reuters, AP, AFP, ANI, PTI) and syndicated or matched by non-paywalled outlets — search the story's key facts (names, numbers, dates) to find readable parallel coverage.
  - The underlying source (a regulator's rule, an agency report, a survey, a court filing) is often public and citable directly — often a stronger slide citation than the newspaper story about it.
  - Secondary coverage that quotes the paywalled piece can verify its key claims.
- Only after those routes are exhausted: report the paywalled piece as a candidate (clearly marked unread/unverified), give the link, and note the user can supply the text if they happen to have access — as a last resort, never as the plan.
- **Copyright**: never reproduce an article's full text or long excerpts, even if accessible or supplied. Summarize in your own words; direct quotes should be brief (a sentence or two) and attributed.

## Step 4: Deliver

For each candidate article report: outlet, author (if known), date, headline, link; a summary of what it actually says relevant to the user's claim (in your own words); whether it was read in full or only partially (and mark unread ones as unverified); and paywall status. Rank by usefulness for the stated purpose, not by outlet prestige. If nothing directly on-point exists, say so and report the nearest coverage found, being explicit about the gap between what the user wanted and what the articles establish.

Slide citation format: Outlet, "Headline," date (author optional).

## Example

**BNPL for essentials (from a discussion of a BNPL/merchants paper)**: the user wanted press coverage of consumer-protection concerns about BNPL. The on-point piece was Stacy Cowley, "'Buy Now, Pay Later' Lenders Pitch Loans for Needs Like Electricity and Rent," New York Times, Aug 17, 2026: BNPL expanding into rent/utilities/medical financing, half of users in a LendingTree survey unable to make ends meet otherwise, loan stacking, "phantom debt" invisible to credit bureaus, shadow-banking concerns. NYT blocks fetching, so the Step 3 routes apply: the piece's key facts (the Fed economists' $160B spending estimate, the LendingTree survey) are independently reported by non-paywalled outlets and traceable to their public sources, which can be read, verified, and cited directly.
