---
name: answer
description: Research and answer questions using general knowledge, codebase exploration, library docs (Context7), web search, or a user-provided URL. Different from /explain which analyzes specific code.
scope: project
---

# Answer

Answer research questions by pulling from all available knowledge sources. Invoke as `/answer <question>`.

## When to Use

- Conceptual questions: "How does X work?", "What's the difference between X and Y?"
- Library/framework questions: "How do I use X for Y?"
- Architectural, tooling, or best-practice questions
- Current events in tech: release notes, new APIs, CVEs

## Research Sources

Use the minimum sources needed. Prefer faster/cheaper sources first.

| Source | When to use | Tool |
|--------|-------------|------|
| General knowledge | Stable concepts, algorithms, language features | (no tool) |
| Codebase search | "How is X used in this repo?" or to ground the answer in real usage | `Grep`, `Glob`, `Read` |
| External docs | Precise, version-specific library API questions | `mcp__claude_ai_Context7__resolve-library-id` → `mcp__claude_ai_Context7__query-docs` |
| Web search | Recent releases, current best practices, CVEs, anything post-training | `WebSearch` |
| Direct URL | User provides a link, or a doc URL is known | `WebFetch` |

## File Context (Adaptive)

Check whether the active file (visible in the conversation or IDE context) is relevant to the question:

- **File-relevant question** (mentions the current language, a library used in the file, or asks about behavior in context): read and include the full file as context
- **Unrelated question**: only note the file name and language as ambient context; don't dump the full content

If file relevance is unclear and including it might help, ask: *"Should I look at your current file for context?"*

## Process

1. **Classify** — simple factual or multi-source research?
2. **Check file relevance** — read the active file if it aids the answer
3. **Select sources** — pick the minimum set needed
4. **Research in parallel** — fire independent lookups simultaneously
5. **Synthesize** — combine findings into a single coherent answer

## Output Style (Adaptive)

### Simple question

Answer directly in 1–3 paragraphs. No headers. Include a code snippet if it clarifies.

### Complex / multi-source research

```
## Answer
[Core answer — the thing the user needs to know]

## Background
[Why this is the case, trade-offs, caveats, alternatives]

## Examples
[Code snippets or concrete illustrations]

## Sources
[Links, doc pages, or file paths from this repo]
```

Don't pad short answers into the complex format. Match the depth to the question.
