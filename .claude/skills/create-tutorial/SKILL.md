---
name: create-tutorial
description: "Subsystem tutorial generator. ALWAYS invoke when the user asks for a tutorial, guide, onboarding doc or walkthrough of a system or module: 'tutorial for X', 'how do I use X', 'guide to the X system', 'walk through the X subsystem'. Writes <tutorials dir>/<system>.md covering architecture, key variables and a usage walkthrough."
allowed-tools: Read, Grep, Glob, Write, Edit, Agent
---

# Create a Subsystem Tutorial

Produce a learning-oriented tutorial for a **code subsystem or feature** in this repo — something a teammate can read to understand how the thing is shaped, find the knobs that matter, and make their first change with confidence.

A good tutorial is not an API dump and not a vague overview. It answers, in order: *What is this and how is it shaped? What do I touch to change its behavior? How do I actually use, debug, and extend it?* Keep that arc in mind — every section earns its place by moving the reader along it.

## Division of labor

Tracing the code — following entry points and data flow, pulling out real type and variable names with line numbers — is best done by a **general-purpose research agent** (spawn one via the Agent tool, `subagent_type: general-purpose`). It runs read-only, gathers a findings brief, and hands it back. This skill owns the **shape and the teaching**: it resolves the target, gets the brief, then writes the tutorial.

This split matters. If you let an agent freestyle the whole document, the structure and teaching quality drift between runs. If you trace everything inline yourself, you burn context on grep output and lose the thread. So: delegate the archaeology, own the writing. For a small, well-contained feature you may find it faster to trace inline — that's fine; the brief is a means, not a ritual.

## Flow

### 1. Resolve the target

Figure out what the user means and where it lives. Targets come in two shapes:

- **A whole subsystem** — a directory under `{{UE_PROJECT_DIR}}\Source\<Module>\<Subsystem>\` (e.g. `{{UE_GAME_MODULE}}/AI/`, `{{UE_GAME_MODULE}}/AbilitySystem/`).
- **A feature** — a capability that lives in *scattered* files, not its own folder (e.g. "weapon reloading" spans a component, a config struct, input wiring, and a few animation notifies). Here the real work is figuring out which files implement the feature. Grep for the obvious symbols (`Reload`, `Ammo`, `Magazine`) and follow the references.

Confirm in one line before you invest in research: *"Tutorial for weapon reloading — the weapon component + ammo data + input wiring under `{{UE_GAME_MODULE}}/Weapons/` — go?"* If the target is ambiguous, list candidates and ask. If it plainly doesn't exist, say so and offer the closest matches rather than guessing. A wrong target wastes the whole research pass.

### 2. Check for existing context

Before researching, look for material that already exists so the tutorial aligns with it instead of contradicting it:

- `{{ARCHITECTURE_DOC}}` — system-level map; the subsystem may already be summarized there.
- A `UBIQUITOUS_LANGUAGE.md` inside the subsystem folder — **authoritative** for terminology. If present, the tutorial must use these exact terms.
- Any existing `{{TUTORIALS_DIR}}\<system>.md` — if it exists, this is an **update**: read it, and ask whether to refresh in place or rewrite.

### 3. Get a findings brief

Spawn a **general-purpose research agent** (Agent tool, `subagent_type: general-purpose`) with a prompt that asks for a structured **findings brief**, not a finished document. Give it the target and the files you found in step 1, and ask it to return:

- **Purpose** — what the thing does, in 2-3 sentences, grounded in the code.
- **Architecture** — the main components (classes/structs), their responsibilities, and how data/control flows between them. Ask for a **Mermaid diagram** of the relationships.
- **Entry points** — where execution enters (e.g. `BeginPlay`, an ability activation, a subsystem `Initialize`, a registration call). This is where a reader starts tracing.
- **Key types & files** — the handful of types/files a newcomer must understand, with paths (`file_path:line`).
- **Configuration** — the tunable knobs: `UPROPERTY` fields, config structs, defaults, and **what each one actually affects** (a variable name without its effect is useless in a tutorial). Note whether each knob is per-instance or global, and flag any value that's secretly a mode switch.
- **Runtime behavior** — the lifecycle/state machine over time, not just static structure: what fires when, what advances state.
- **Extension points** — how it's meant to be customized (subclassing, data assets, registering a handler, a Blueprint-overridable function).
- **Gotchas** — replication/authority caveats, init order, lifetime/GC, threading, surprising defaults — anything that bites newcomers.

Tell it to ground every claim in real symbols and `file:line` — invented APIs are the main failure mode of generated tutorials. If the agent stalls or you're tracing a small feature, just gather this yourself with Read/Grep; the brief is the input to your writing, however you get it.

### 4. Write the tutorial

Write `{{TUTORIALS_DIR}}\<system>.md` from the findings. If that folder is under a local-only path (`{{LOCAL_ONLY_PATHS}}`), **never `p4 add` it**; just write the file.

The single most important thing: **you are teaching, not cataloguing.** A reference doc lists what exists; a tutorial builds a mental model so the reader can act. The difference shows up in three habits that are easy to lose if you treat this as filling in a template:

- **Show real code, don't just tabulate it.** When a small config struct, a key function body, or a telling class comment explains something better than prose, paste the actual lines (kept short — the illustrative part) and cite `file:line`. A 6-line struct shown is clearer than a 6-row table describing it. Tables are great for *comparing many things* (a dozen variables, a list of types); code excerpts are better for *understanding one thing deeply*. Use whichever teaches.
- **Explain the why, and anticipate the reader's questions.** Don't just say what happens — say why it's built that way and answer the question a newcomer will actually ask next ("so where does the enemy actually *move*?"). The reader's confusion is the thing you're removing.
- **Include a Debugging section.** This is what separates a tutorial someone *uses* from one they skim. How do you see the system working (gameplay debugger category, log categories, CVars, PIE)? When it misbehaves, what are the common symptoms and where do you look? A symptom → likely-cause → where-to-check table is gold here.

Use the section guide below for shape, but flex it: a small subsystem gets a tight version; a large one gets fuller architecture and walkthrough. Cut a section with a one-line note if it genuinely doesn't apply, and add one the system needs. Match the surrounding docs' tone — explanatory and direct, not breathless.

### 5. Verify and report

Confirm the file wrote, then report per the project's after-task format:
- **What I did** — one sentence.
- **What to check** — point them at the file and the riskiest claim to verify (usually the variable effects or the walkthrough steps).
- **Next step** — offer to publish to Confluence via `to-confluence-page` if they want it shared.

## The moves a good tutorial makes

Below is the menu of sections that, together, teach a system well. Think of them as *moves*, not a checklist — each one does a specific job for the reader. Use the ones the system needs, in roughly this order; a small feature might fold several together, a large one might split them. The litmus test for including a section: does it move the reader along the arc (*what → how shaped → what do I touch → how do I use/debug/extend*)? If yes, keep it; if it's there to fill a template, cut it.

What makes these *teach* rather than catalogue:

- **Show real code, don't just tabulate it.** A 6-line config struct pasted in (with the key fields commented) teaches more than a 6-row table describing it. Use a short code excerpt at the moment a reader needs to see the actual mechanism; use tables when *comparing many things* (a dozen knobs, a list of files). Cite `file:line` either way so they can jump to source.
- **Explain the why and answer the next question.** Don't just state what happens — say why it's built that way and pre-empt the question a newcomer will ask next ("so where does the enemy actually *move*?"). Their confusion is what you're removing.
- **Make it usable, not just readable.** The Debugging and Worked-example sections are what turn a doc someone skims into one they keep open while working. Don't skimp on them.

```markdown
# <System/Feature Name> — Tutorial

> Path: `Source/<...>` · Audience: engineers new to this · Last updated: <date>
One-paragraph intro: "By the end you'll be able to <author/tune/debug X>." Plus a one-line
terminology note pointing at UBIQUITOUS_LANGUAGE.md if the subsystem has one.

## The big picture
What it is, why it exists, and the mental model. State up front any fact that reframes how
the reader should think ("this component holds no state — it writes the Blackboard; the
Behavior Tree moves the pawn"). When there's a data/ownership hierarchy, show it as a small
tree or Mermaid diagram (e.g. `UMyEnemyDef → FMyEnemyConfig → FMyEnemyCombatConfig`). Call out
distinct layers — e.g. per-instance config vs global settings.

## Concepts
A short glossary of the domain terms this tutorial uses, defined in context. Honor the
UBIQUITOUS_LANGUAGE.md spelling and meaning. This lets the rest of the doc speak the
team's language without stopping to define terms inline.

## Quickstart: making your first change
A fast on-ramp placed early on purpose — once the reader has the mental model and the
vocabulary, give them a win before the deep reference. A realistic first task ("add a
patrol route", "create a new enemy definition asset") as numbered steps with real paths and
what to build/test afterward. Concrete enough to follow without guessing. (This is "author
a new one yourself"; the later Worked example traces an existing one at runtime.)

## Key files
A table mapping the load-bearing files to their role: `file | what lives here`. This is the
"where do I look" map — keep it to the files that matter, not every file in the folder.

## Configuration in detail
The tunable knobs, grouped *by concern* (e.g. "who it fights", "how it moves", "timing")
rather than dumped in one flat list. For each group, show the relevant struct/fields as a
short commented code excerpt, then a table giving each field's default and — the part that
matters — its **effect** (what changes when you change it). Flag any value that's secretly
a mode switch, and separate global settings from per-instance ones.

## Runtime lifecycle
How the system behaves over time, not just its static shape. A Mermaid flowchart of the
state machine / lifecycle, then a step-by-step trace of the main path naming the real
functions, with a short code excerpt at the pivotal step. This is where the diagram turns
into understanding.

## Worked example
A concrete, configured instance — show its values in a small table — then narrate what
actually happens at runtime, step by step, referencing the rules from the sections above.
This is "read an example and watch it run"; it cements the mental model.

## Debugging
How to see it working — gameplay debugger category, relevant log categories, CVars, PIE
steps. Then a symptom → likely cause → where-to-check table for the common failures.

## Extending the system
The intended customization points (subclass, data asset, register a handler, BP override),
with a snippet or concrete step where it helps.

## Gotchas
Bulleted pitfalls a newcomer will actually hit: replication/authority, init order,
lifetimes/GC, threading, Blueprint boundaries, surprising defaults.

## See also
Links to UBIQUITOUS_LANGUAGE.md, ARCHITECTURE.md, related tutorials, relevant Confluence.
```

## Rules

- **Teach, don't just catalogue.** The win condition is a reader who understands and can act. Narrative, real code excerpts, a worked example, and a usable debugging section beat an exhaustive table dump every time. If it reads like an API reference, it's not done.
- **Ground every symbol in real code, with `file:line`.** A tutorial that references a class or variable that doesn't exist is worse than none — it teaches wrong mental models. Citations also let the reader jump straight to source, which is half the value.
- **Honor the ubiquitous language.** If the subsystem has a `UBIQUITOUS_LANGUAGE.md`, its terms win over any synonym you might prefer.
- **Effects over inventories.** Every variable and type gets a "so what" — what it controls or owns. Drop entries you can't explain.
- **One subsystem/feature per invocation.** Tutorials are focused; if asked for several, do them one at a time.
- **Don't `p4 add` the output** when its folder is local-only (`{{LOCAL_ONLY_PATHS}}`).
