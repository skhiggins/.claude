---
name: search-for-photo
description: Search online for a photo that illustrates a specific concept (typically for discussant or presentation slides), searching in both English and the local language of the country where the phenomenon occurs. Use when the user calls /search-for-photo or asks to find a photo/image for a slide or to illustrate a point.
---

# Search for a photo illustrating a concept

Goal: find a photo the user can put on a slide (usually a discussant slide), with a usable license or a citable source, that actually demonstrates the concept — not something adjacent to it.

## Step 0: Pin down what the photo must show

Before searching, state (and if ambiguous, ask):

1. **The evidentiary content**: what must be visible in the frame for the photo to make the point. Be precise — a photo that shows something adjacent does not work. (Example: for merchant multi-homing in India, a counter with QR codes from *different* providers, with distinguishable branding, demonstrates the point; a counter with several QR codes all from the same provider does not, and an audience member who can read the branding will notice.)
2. **The country and its language(s)**: the phenomenon usually occurs in a specific country, and that country's press photographs it far more often than the international press does.

## Step 1: Search in English

Try open-license repositories first, since those can go straight onto a slide:

- Wikimedia Commons: fetch `https://commons.wikimedia.org/w/index.php?title=Special:Search&search=<terms>&ns6=1` (the `ns6=1` restricts to files).
- Flickr (filter by license), Unsplash, Pexels, Openverse.

Then general WebSearch for news articles and photo essays containing the image.

## Step 2: Search again in the local language

Translate the query into the local language (native script, colloquial terms — e.g., Hindi "दुकान पर पेटीएम फोनपे क्यूआर कोड", Hebrew "רפורמת מחירים עגולים תג מחיר") and rerun WebSearch. Local-language queries surface local news photo galleries that English queries miss entirely; these galleries are often the richest source because domestic outlets photograph everyday commerce. Use several phrasings, including ones a local journalist would use (product names, program names, and slang in the local language).

## Step 3: Stock and editorial agencies

Shutterstock, Alamy, Getty Images (editorial), and iStock reliably have this kind of photo but block automated fetching. Do not fight the 403s: hand the user direct search URLs and suggested query strings, and note that licensing a single image is usually cheap. Getty/AFP/Reuters editorial photos spike around news events involving the phenomenon — name the relevant event if there is one, since searching the event finds the photo.

## Step 4: Deliver, with caveats

- **Never describe a photo's content as verified unless it was actually seen** (by reading the image or a reliable description of that specific image). WebFetch page summaries are secondhand: present them as "reported to show," not "shows."
- News sites lazy-load images, so WebFetch often cannot extract image URLs even when the gallery is right. In that case give the user the page URL to open in a browser and screenshot, with the outlet credited on the slide (standard discussant-slide practice).
- State the license or reuse basis for every candidate (public domain / CC / stock license needed / screenshot-with-credit).
- Ask whether the user has their own photos: if they have visited the country, their own photo needs no license and is more credible on a slide. But apply the Step 0 test to their photo too — check that it shows the evidentiary content, not something adjacent.
- If no photo materializes, say so and offer the fallback: make the point with citable text evidence (a regulator's rule, a survey statistic, a quoted news description) found during the search.

## Examples from past discussions

1. **UPI multi-homing (India)** — discussion of a BNPL/merchants paper. Concept: Indian shop counters displaying payment QR codes or soundboxes from multiple competing providers (Paytm, PhonePe, Google Pay, BharatPe). English searches of Commons/Flickr/Unsplash/Pexels found nothing usable. A Hindi query ("दुकान पर पेटीएम फोनपे गूगल पे क्यूआर कोड स्टिकर फोटो दुकानदार") surfaced an Amar Ujala photo gallery about NPCI's "one soundbox" rule — a rule whose existence is itself citable evidence that multi-provider counters are the norm. The user's own photos from India showed multiple QR codes all from Paytm: adjacent, but not the concept (Step 0 test).
2. **Israeli round-price reform** — discussion of a heuristic-pricing paper. Concept: price tags after Israel's reform prohibiting posted prices ending in non-0 digits (the 1- and 5-agora coins had long been out of circulation, but stores still posted .99-style prices to exploit left-digit bias); ideally a tag or shelf showing both the old .99-style price and the new round price. Search in English ("Israel round prices reform agorot price tags") and Hebrew (e.g., "רפורמת מחירים עגולים תג מחיר סופרמרקט", "עיגול מחירים 99 אגורות").
