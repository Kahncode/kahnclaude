---
name: reuse-finder
description: "Finds code that re-implements something the engine, Lyra or the codebase already provides, and says what to call instead. ALWAYS invoke for 'does this already exist', 'reuse an existing function', 'find duplicate logic', 'can the engine do this', 'dedupe', or a file, CL or plan to shrink. Also use before writing a helper over ~10 lines. Not for style cleanups (/simplify)."
allowed-tools: Read, Grep, Glob, Bash
---

# Reuse Finder: Delete Code by Calling What Already Exists

Given a file, folder, pending CL, or proposed snippet, find logic that duplicates something that already exists in one of these places:
- the Unreal Engine (including the GameplayAbilities plugin and other engine plugins)
- the Lyra base classes in `{{UE_GAME_MODULE}}` (Lyra-based projects)
- the project test framework (`{{UE_TEST_MODULE}}`)
- elsewhere in the same module

Project specifics: read {{PROJECT_NOTES_DIR}}\reuse-finder.md if it exists.

Report each duplicate with the exact function to call instead, proof that it is equivalent, and the net lines saved. Then offer to apply the changes.

Why this matters: in this codebase the cheapest line is the one never written. One-off helpers multiply, diverge, and each grows its own bugs. The project rule is *one way per concept*: a concept lives in its owning file and everyone calls it there.

## Required variables

| Variable | Purpose |
|----------|---------|
| `PROJECT_ROOT` | Workspace root (`{{PROJECT_ROOT}}`) |
| `UE_ENGINE` | Engine source root (`{{UE_ENGINE}}`) |

Set in the process env by `.claude/settings.local.json` `env` (values also listed in .claude/rules/project-vars.md).

## Inputs

| Input | How to get the code units |
|-------|---------------------------|
| File or folder path | Read it. For a folder, list the `.cpp` files and start with the largest and most helper-heavy ones (anonymous helpers, `Private` namespaces, `static` functions, `Describe*`/`Find*`/`Get*`/`Is*` utilities). |
| Pending CL / opened files | `p4 opened -c <CL>`, then `p4 diff -du` for each file. Scan only added or changed lines and the functions that contain them. |
| Proposed snippet or plan (often Claude's own earlier proposal in the conversation) | Use the snippet as written. Treat every new function in it as a candidate. |

## Workflow

### 1. Break the code into candidate units
For each function, or each block of more than ~5 lines inside a function, write a one-line **intent** in plain words, plus the **types it touches**. Example:

> `DescribeTagsBlocked`: "list the ASC's owned tags that are in the ability's blocked set, plus which active abilities block it". Touches `UAbilitySystemComponent`, `UGameplayAbility`, `FGameplayTagContainer`.

Writing the intent is what makes searching possible. You search for the *intent* and the *types*, not the local function name, which was invented here and won't match anything.

Skip trivial units (one-liners, pure plumbing) unless the same one-liner appears in three or more places.

### 2. Search, cheapest and likeliest first
Stop searching for a unit once you have a verified hit.

1. **The public API of the types the code already touches.** This is the most common win. Open the header of each type the unit calls into and scan its public methods. If code loops over an ASC's internals, the ASC probably already has a getter for what it wants. Use Glob for the header, then Grep within that file only.
2. **The engine base implementation of anything the project overrides.** When the unit works around missing information, check whether the engine's base function already produces it and a project override drops it. (In the example below, Lyra's `DoesAbilitySatisfyTagRequirements` drops the blocking tags that the engine's version appends.)
3. **Same module.** Grep the module's `Private` tree for the intent's key calls, for example `GetOwnedGameplayTags`, `FindFProperty`, or `Filter(`. Two helpers calling the same engine functions in the same order are near-duplicates.
4. **The test framework index** (when the code is in `{{UE_TEST_MODULE}}`). The project notes hold the map of its helpers. Some concepts have a declared single home, and a local copy of one is always a finding.
5. **Game code** (`{{UE_GAME_MODULE}}`): Lyra components and project subsystems that already expose the query.
6. **Engine utility libraries:** `Algo::`, TArray and TMap methods, `FString`, `FMath`, `UGameplayStatics`, `UKismet*Library`, `FGameplayTagContainer`. See the reference file for common re-implementations.

Search hygiene, because the tree is huge:
- **Never content-search `Content/`, `*.uasset`, `*.umap`, or a whole `Plugins` tree.** A hook blocks it, and it freezes the disk.
- Scope Engine greps to one module's `Public` folder, for example `Engine/Plugins/Runtime/GameplayAbilities/Source/GameplayAbilities/Public`. Never grep all of `Engine/`.
- Prefer Glob plus a targeted Grep over reading whole files. Read only the function you plan to recommend.
- For a folder input with many units, you may fan out to Explore agents, one per area (engine API, test framework, game code). Give each the intents and types. Merge their hits, then verify them yourself.

### 3. Verify every candidate
An unverified suggestion costs the user more than it saves. Read the existing function's body and confirm each of these:
- **Same semantics:** null handling, empty input, return on failure, side effects (logging, RPCs, dirtying), server vs. client, ordering, exact vs. partial tag match.
- **Callable from here:** public, or protected but reachable; exported (`*_API` or a module dependency that already exists). A runtime module (tests included) must never depend on an editor module such as `{{UE_EDITOR_MODULE}}`, because that crashes `-game` boots. Not deprecated in this engine version.
- **Not slower in a hot path:** a per-frame poll, a per-actor loop, or `Tick`.
- **Note any difference** and whether it matters for this caller. A near-match with a harmless difference is still a finding. Say what differs.

If you can't verify a candidate, drop it, or list it under "Unverified" with what you would need to check.

### 4. Estimate net lines saved
Count lines removed minus lines added, including call-site changes and includes. Don't round up. A 2-line saving that removes a whole concept (a second reflection path, for example) is worth reporting. Say why.

### 5. Respect project rules when shaping the fix
- **Game code (`{{UE_GAME_MODULE}}`) and `Engine/`:** propose changes there only as an option that needs explicit approval. Prefer a fix in the calling code.
- **Consolidating two project helpers:** keep the one in the concept's owning file (the system's `TestUtility`, or the core utility) and delete the other.
- **Style in sketches:** East const (`FFoo const&`), no anonymous namespaces (tests: `<Owner>::Private`; game code: a private member in the header, never a file-scope `static`), max 2-line comments.
- **Precision-preserving:** change the call, not the surrounding code.

## Report format

Use this template. Keep it scannable, with the status first.

```
# Reuse findings — <target>

**In short:** <N> findings, ~<X> net lines removable; top win: <one line>.

| # | Current (file:line) | Reuse instead | Net lines | Confidence | Risk |
|---|---------------------|---------------|-----------|------------|------|
| 1 | `Foo.cpp:128` GetAbilityTags | `MyTestReflection::TryRead<FGameplayTagContainer>` (`MyTestReflection.h:68`) | -6 | High | None |

## 1. <short title>
- **Current:** `path:line`, a ≤5-line excerpt or a one-line description
- **Existing:** `path:line`, the signature
- **Equivalence:** what you checked; any difference and why it doesn't matter here
- **Change:** a 1-5 line sketch of the new call site
- **Saves:** -N lines (removed X, added Y)

## Checked, not worth it
- `<unit>`: <why: existing version differs in X / not exported / hot path>

## Unverified
- `<unit>` → `<candidate>`: needs <what>
```

Rank by net lines times confidence, and put concept-removals high. If nothing qualifies, say so plainly and list what you checked. An honest "no duplicates found" is a valid result.

End with a single offer: "Apply findings 1–N via code-dev in a pending CL?" Don't edit files yourself. The fix goes through `code-dev` with changelist discipline, followed by a build.

## Worked example (proposed snippet)

The user asked for a diagnostic naming which tag blocked an ability. The first proposal was a new 25-line `DescribeTagsBlocked` that reflected on `ActivationBlockedTags`, called `GetAdditionalActivationTagRequirements`, and looped over the active abilities. The reuse pass found:
1. The public `UAbilitySystemComponent::GetOwnedGameplayTags()` and `GetBlockedAbilityTags()` (`AbilitySystemComponent.h`) already cover every blocking source. Printing both replaces the whole function: about 3 lines instead of about 25.
2. The engine's `UGameplayAbility::DoesAbilitySatisfyTagRequirements` already appends the exact blocking tags (`AppendMatchingTags`), and Lyra's override drops them. This went into the report as a game-code option needing approval, not as the default.
3. Precedent: `MyRegressionTests.cpp:160` already prints owned tags in a failure message, so the pattern is established.
4. The local reflection helper `GetAbilityTags` (`MyTestActions.cpp:128`) duplicates the test framework's `MyTestReflection::TryRead<FGameplayTagContainer>`. That's a separate finding, because it is a second way to do a one-way concept.

The pattern to copy: look at the public API of the types the code already touches before writing anything, then check whether a project override threw away what the engine computes.
