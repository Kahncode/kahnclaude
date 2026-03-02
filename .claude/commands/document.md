---
description: Build or update project documentation. No args: high-level ARCHITECTURE.md index only. With args: deep-dive into the named subsystem and link it from ARCHITECTURE.md.
scope: project
argument-hint: [subsystem or topic]
---

# Document

Build or update project documentation for the current codebase.

**Target:** $ARGUMENTS

## Behavior

### No arguments — High-Level Pass

Delegate to the `documenter` agent via the Agent tool with this context:

> High-level pass only. Write or update `docs/ARCHITECTURE.md` as the system index: system overview diagram, component map with one-line responsibilities, technology choices and rationale, and links to any existing subsystem docs. Do not create subsystem files. Do not recurse.

### With arguments — Deep-Dive Pass

Delegate to the `documenter` agent via the Agent tool with this context:

> Deep-dive into the `$ARGUMENTS` subsystem. Write `docs/<subsystem>.md` covering key concepts, entry points, data flow, Does/Does NOT table, and key file references. Generate Mermaid diagrams appropriate to what exists in the code — no speculation. Then update `docs/ARCHITECTURE.md` to link to the new or updated subsystem file.

The agent reads the code and decides which diagram types apply. No magic keywords are needed.
