---
name: web-search
description: "Web-first research answerer. ALWAYS invoke for questions whose best answer is online: current events, latest releases, version-specific APIs, prices, CVEs, news, 'look up X', 'search the web for X', or any fact your training may have outdated. Searches the live web first and uses built-in knowledge only when the web adds nothing. Never answer 'latest version' from memory."
allowed-tools: WebSearch, WebFetch, Read
---

# Web-First Search & Answer

Answer the user's question by searching the live web first, then synthesizing a sourced report. This skill exists because built-in knowledge has a cutoff and goes stale — for anything time-sensitive, version-specific, or fast-moving, the web is the source of truth.

## When the web is essential vs optional

Search the web when freshness or precision matters: current events, "latest"/"newest" anything, release notes, version numbers, prices, CVEs, library API specifics, recent changes, or any claim you'd otherwise hedge on. When in doubt, search — a cheap query beats a confidently wrong answer from stale memory.

You may answer from built-in knowledge **only** when the question is about stable, timeless concepts (a sorting algorithm, a language feature that hasn't changed) AND a quick search would add nothing. Even then, prefer one confirming search over assuming.

## Process

1. **Decompose the question.** Identify the specific facts you need. A vague question ("how's the new framework?") needs reframing into searchable sub-questions (release date, key features, reception).

2. **Search.** Issue focused `WebSearch` queries — one per distinct sub-question rather than one giant query. Use specific terms (names, versions, dates) over generic phrasing. Run independent searches in parallel.

3. **Fetch when snippets aren't enough.** Search snippets are often too shallow to answer precisely. When a result looks authoritative (official docs, a primary source, a detailed article), `WebFetch` the page to read it properly. Prefer primary sources over aggregators.

4. **Cross-check.** For contested or surprising claims, confirm against a second independent source before stating it as fact. Note disagreement rather than papering over it.

5. **Fall back only if needed.** If the web genuinely adds nothing beyond what you already know with confidence, say so and answer from knowledge — but make clear which parts are unverified.

6. **Synthesize** into the report format below.

## Output format

Use this structure. Keep each section as long as it needs to be and no longer — a simple question gets a short Answer and Sources, skipping the rest.

```
## Answer
[The direct answer — the thing the user actually asked for, stated up front.]

## Background
[Why this is the case, context, trade-offs, caveats, disagreement between sources, what's uncertain.]

## Examples
[Concrete illustrations, code snippets, numbers, or specifics — only if they clarify.]

## Sources
- [Title or description](URL) — one-line note on what this source supports
- ...
```

Rules that keep the report trustworthy:
- **Cite specifically.** Every non-obvious factual claim should trace to a source in the list. Link the actual page you used, not a homepage.
- **Date-stamp volatile facts.** Prices, versions, "as of" claims — say when they were true, since they drift.
- **Flag uncertainty honestly.** If sources conflict or coverage is thin, say so. Don't manufacture confidence.
- **Don't pad.** If the answer is one paragraph, the report is one paragraph plus sources. The structure serves the answer, not the reverse.

## Example

**Input:** "what's the latest stable Node.js LTS version?"

**Process:** Search `Node.js current LTS version 2026` → fetch nodejs.org/en/about/releases if the snippet is ambiguous → confirm the version and its support window.

**Output:**
```
## Answer
Node.js 22 ("Jod") is the active LTS as of June 2026, with Node.js 24 in current/soon-to-be-LTS status.

## Background
Node promotes even-numbered releases to LTS; each gets ~30 months of support. Check the release schedule before pinning, since the active line rotates roughly yearly.

## Sources
- [Node.js Releases](https://nodejs.org/en/about/previous-releases) — official release/LTS schedule
```
