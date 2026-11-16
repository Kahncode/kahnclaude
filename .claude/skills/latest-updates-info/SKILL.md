---
name: latest-updates-info
description: "Latest-capabilities briefer for a named tool. ALWAYS invoke when the user asks what's new in a tool, library, framework, app or service: 'what's new in X', 'latest features of X', 'catch me up on X', 'X release notes'. Searches official release notes first and returns a digest of the current version and newest capabilities with sources. Never answer from memory."
allowed-tools: WebSearch, WebFetch, Read
---

# Latest Updates Briefer

Tell the user what's newest in a specific tool: its current version and the capabilities that have landed recently. This exists because built-in knowledge has a training cutoff, and release cadences for active software outrun it — so for "what's new in X", the live web (especially the project's own changelog) is the source of truth, not memory.

The job is narrower than open-ended research: the user has named a tool and wants to be caught up on it. Anchor everything to that tool's own primary sources and return a predictable, skimmable digest.

## What counts as "the tool"

The user names a target — a product (Claude Code, Unreal Engine, VS Code), a library/framework (React, FastAPI), a language (Python), a service (GitHub Actions, AWS Lambda), or a CLI. If the name is ambiguous (e.g. "Claude" could mean the models, the API, or Claude Code), pick the most likely reading from context and say which one you chose; offer to redo it for the other reading rather than stalling to ask.

The user is *not* giving you their installed version here — don't ask for it or try to detect it. "Latest" means latest released, full stop. If they later want "what changed since version N," that's a follow-up you can handle by filtering, but the default is simply the newest state of the tool.

## Process

1. **Identify the primary source.** Every actively maintained tool publishes its own truth: a `CHANGELOG`, a release-notes page, a GitHub Releases tab, a "what's new" doc, or a release blog. Find that first — it's more authoritative and more current than any third-party summary. A good opening query is the tool name plus "release notes", "changelog", or "what's new", optionally with the current year.

2. **Pin the current version and date.** Establish what the latest release actually is (version number or named release) and when it shipped. This frames everything else and tells the user how fresh the picture is.

3. **Read the source, don't skim snippets.** Search snippets are too shallow to enumerate features reliably. When you find the official changelog or release-notes page, `WebFetch` it and read the recent entries properly. Prefer primary sources over roundup articles; use secondary sources to add color or confirm, not as the backbone.

4. **Scope "recent" sensibly.** For fast-moving tools, the last few releases or a few months is the right window. For slow ones, the latest major/minor is enough. Aim to capture what a regular user would experience as "new since I last paid attention" — not an exhaustive line-by-line of every patch.

5. **Sort by what matters to a user.** Headline the capabilities people would actually care about. Separate genuinely new features from breaking changes and deprecations — those last two are what bite people, so never bury them.

6. **Synthesize** into the digest below.

## Output format

Use this structure. Keep each section as long as it needs to be and drop any that don't apply — a quiet release might be just the version line, a few features, and sources.

```
## <Tool> — what's new
**Latest:** <version / release name> (released <date>). <One line on how big a deal this release is.>

## New & notable
- <Feature or capability> — <what it lets you do, one line>
- ...

## Breaking changes
- <What changed and what it breaks> — only if any; omit the section otherwise

## Deprecations
- <What's on the way out and the replacement> — only if any; omit otherwise

## Fixes & smaller stuff
- <Worth-mentioning fixes or minor improvements> — keep brief, omit if nothing stands out

## Sources
- [Title](URL) — what this source backs up (link the actual changelog/release page, not a homepage)
```

What keeps this digest trustworthy and worth reading:
- **Lead with the version and date.** "Latest" is a moving target; stamping it tells the user how stale this will get and which release the rest describes.
- **Surface breaking changes and deprecations prominently.** A "what's new" that hides what will break someone's setup has failed at its main job.
- **Cite the primary source.** Each non-obvious claim should trace to a real release-notes or changelog page in Sources — not a vendor homepage or a blog that's merely repeating the changelog.
- **Translate, don't transcribe.** Don't paste raw changelog lines; say what each change *lets the user do*. A changelog entry is for maintainers; this digest is for someone deciding whether to care.
- **Be honest about gaps.** If the official changelog is thin, behind a login, or you can only find third-party coverage, say so rather than implying you read the source of record.

## Example

**Input:** "what's new in Claude Code lately?"

**Process:** Search `Claude Code changelog 2026` and `Claude Code release notes` → fetch the official changelog/release-notes page → identify the most recent version and the features added across the last several releases → separate new features from any breaking changes.

**Output:**
```
## Claude Code — what's new
**Latest:** v1.4x (released June 2026). Steady stream of agent and workflow features since the last time most people looked.

## New & notable
- Background tasks — long-running commands keep running across turns and notify you on completion, so you don't block the session waiting.
- Workflow orchestration — deterministic multi-agent scripts (fan-out, pipelines) for large review/migration jobs.
- ...

## Breaking changes
- <only if the release notes list one>

## Sources
- [Claude Code changelog](https://...) — official release notes for the versions above
```

This is a worked shape, not a script — match the real sections to whatever the tool's changelog actually contains.
