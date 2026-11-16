---
name: task-user-story
description: "Requirements discovery before planning: pressure-tests a raw idea with skeptical agents and grills the user until WHAT and WHY are settled — 'help me think through X', 'pressure-test this idea', 'should we build', 'write a user story'. Produces an alignment brief. Not for tasks whose scope is already clear (task-planning)."
allowed-tools: Read, Glob, Agent, SendMessage, AskUserQuestion
---

# Task Discovery & Alignment

Turns a raw, half-formed request into a **shared understanding** of what to build and why — *before* a single line of planning or code. The deliverable is an alignment brief and a recommended direction, which then feeds `task-planning` to produce the actual implementation plan.

## Why this skill exists

Most wasted engineering effort isn't bad code — it's building the wrong thing, rebuilding something that already exists, or two people picturing different things behind the same sentence. A request like "add a cooldown to grenades" hides a dozen unstated decisions and at least one question worth asking out loud: *should this even be a cooldown, or is the real problem something else?*

So this skill does the unglamorous front work: it restates the need in the team's own vocabulary so everyone means the same thing, it sends skeptics to look for reasons *not* to proceed (or cheaper ways to), and then it interrogates the user with the sharpest questions those skeptics surfaced. Only once the dust settles does it write down what was agreed.

The current conversation's main context is precious — it's shared by everything downstream. So **you orchestrate; agents explore.** You don't grep the codebase yourself (you don't even have the tools to); you dispatch read-only agents and synthesize what they bring back.

## The flow

### Phase 0 — Reformulate in the domain's ubiquitous language

A shared understanding starts with shared words. Before anything else, restate the request using the project's canonical terminology so latent disagreements surface immediately instead of three steps later.

Read the local context that defines that vocabulary (don't search the codebase — just read these):

```
CLAUDE.md and CLAUDE.local.md          (project + personal rules, domain-language pointers)
{{ARCHITECTURE_DOC}}                    (system overview, component map)
```

Then follow any **Domain Language** pointers those files contain to the relevant ubiquitous-language glossary, and read it. For example, subsystem terms often live in `{{SUBSYSTEM_DOCS_DIR}}\<subsystem>*.md`. Use the glossary that matches the request's domain; if none fits, work from the architecture doc's terms.

Produce two things and show them to the user right away:

1. **A user-story statement** — the need in one crisp sentence, using canonical terms (replace aliases with the glossary's term, e.g. "spawn point"→**Spawner**):
   > **As a** [role] **I want** [goal in domain terms] **so that** [benefit].
2. **A one-paragraph restatement** that names the specific Entities, Behaviors, and Managers the request actually touches.

Lead with: *"Here's how I'm reading this in our terms — correct me before we go further:"* This is the first alignment checkpoint. If the user corrects the framing, fold it in before spawning agents — you don't want four agents investigating a misread request.

### Phase 1 — Fan out the skeptics (parallel)

Spawn **all** of the perspective agents in a single message so they run concurrently. Each gets a distinct lens and is read-only — they investigate and report; they do not change anything. Give every agent the reformulated user-story statement and restatement as shared context.

Use the agent types that fit the lens (suggested defaults below; adjust to what the request needs):

| Lens | What it's for | Suggested agent |
|------|---------------|-----------------|
| **Counter-idea** | Argue *against* doing this. Steelman the "do nothing" and "do something simpler" cases. Propose 1-2 alternative framings of the underlying need. | `general-purpose` |
| **Prior art** | Does this already exist, fully or partly, in the codebase? Find reusable systems, patterns, near-duplicates we'd be reinventing. | `Explore` or `code-planner` |
| **Feasibility** | Technical cost and risk: complexity, dependencies, engine/replication/GAS constraints, what makes it hard. | `code-planner` |
| **Rightness** | Is this the *right* thing to build? Does it serve the real underlying goal, fit the architecture and project direction, and not paint us into a corner? | `general-purpose` |

Give each a prompt shaped like this (vary the lens):

```
You are the <LENS> reviewer for a proposed piece of work. Investigate read-only and
report back — do not change anything.

PROPOSED NEED (in our domain terms):
<user-story statement + restatement>

YOUR LENS: <one-paragraph description of this lens from the table>

Return concisely:
1. Findings — what you discovered, with file paths / concrete evidence where relevant.
2. The strongest case from your lens — your sharpest point (the alternative, the
   existing system, the blocking constraint, the "are we sure?").
3. Questions only the user can answer — decisions your lens exposes that you could
   NOT resolve from the code or docs. Be specific; these become the grilling.
```

Two cheaper variants, scale to the request:
- **Trivial / well-trodden requests:** skip the fan-out or run just Prior-art + Rightness. Don't ceremony-bomb a one-liner.
- **Large or contested requests:** add lenses (e.g. a "user/player experience" lens, or a second counter-idea from a different angle) — diversity of attack beats redundancy.

If you reach for a heavyweight multi-agent fan-out across many sub-questions, that's the moment to consider whether the user wants a full Workflow — but for the standard 3-4 lenses, parallel `Agent` calls are the right tool.

### Phase 2 — Grill until aligned

This is the heart of it, and the part the old version was missing. The agents handed you real tensions — disagreements between lenses, a near-duplicate system, a blocking constraint, an unanswered "is this even the right goal." **Your questions come from those findings, not from a generic checklist.** That's what makes the interrogation worth the user's time.

Synthesize first, then ask:
- Collapse the agents' returns into the **genuine decision points**: where lenses conflict, where prior-art changes the calculus, where feasibility forces a tradeoff, where rightness questions the premise.
- Lead with the load-bearing ones — the answers that would most change the direction.
- Batch tightly-related questions into a single `AskUserQuestion` call (2-4 at once); don't drip them one at a time and waste the user's attention. When you have a recommendation, say so and put it first.

Then **loop**. After each round, you'll know more — and the answers usually expose the next layer. Keep going until the genuine ambiguities and cross-lens disagreements are resolved or the user explicitly waives them. Don't stop at the first round just because you asked something; don't manufacture rounds once alignment is real. If new answers materially shift scope, you can re-engage a perspective agent via `SendMessage` (it still holds its context) to re-check feasibility or prior art against the new direction.

The bar to clear before Phase 3: *you could explain back to the user what you're building, why, what you're explicitly not building, and what you considered and rejected — and they'd nod.*

### Phase 3 — Write the alignment brief

Once aligned, write the brief directly in the conversation. This is the record of what was agreed and the springboard into planning. Keep the reformulated user story at its spine.

```markdown
# Alignment Brief: [Short Title]

## The need (user story)
**As a** [role] **I want** [goal in domain terms] **so that** [benefit].

[One-paragraph restatement in ubiquitous language — the Entities/Behaviors/Managers
this touches.]

## Shared understanding
- **What we're building:** [the agreed direction, in 2-4 bullets]
- **What we're explicitly NOT building:** [scope cuts the grilling produced]
- **Why this and not the alternatives:** [the counter-ideas considered and the
  reason we're not taking them — this is the value of the skeptic pass, captured]

## What already exists
[From the prior-art agent — systems/patterns to reuse or extend, with paths. Or
"Nothing relevant found — this is genuinely new."]

## Key risks & constraints
[From feasibility/rightness — only genuine ones, each with why it matters.]

## Open decisions deferred to planning
[Anything intentionally left for task-planning to resolve against the actual code.
Empty is fine — say so.]

## Recommended direction
[2-4 sentences: the path forward and the rough shape of the work.]
```

Rules of thumb:
- The "Why this and not the alternatives" section is the point — if it's empty, the skeptic pass didn't earn its keep; revisit.
- Don't pad risks or invent open decisions. An honest "no major risks; this is well-trodden" is more useful than boilerplate.

### Phase 4 — Hand off

The brief defines *what* and *why*; `task-planning` turns it into *how*. Offer the next step:

> "Aligned. Next step?
> - `/task-planning` — explore the code and turn this brief into an implementation plan
> - `/to-jira-issue` — capture this brief as a Jira ticket first
> - Keep refining — re-open any decision above"

When the user picks `task-planning`, pass the whole brief as the task input so the planner starts from the agreed direction, not the raw request.
