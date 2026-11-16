# Regression

Does this change break something that already worked?

Correctness asks "is the new code right on its own?" Regression asks a different
question: even if the new code is internally correct, does it silently break
existing callers, saved assets, Blueprints, network compatibility, or behavior
that other systems already depend on? A change can be flawless in isolation and
still be a regression because of its ripple effects.

To find regressions you MUST read code the diff did *not* touch — callers,
subclasses, referencing Blueprints, serialized assets. The finding is still
anchored to the changed line (it is the cause), but the evidence lives in the
things that break downstream.

## Criteria

### API & Signature Changes
- **Changed signatures** — added/removed/reordered params, changed return type
  or return semantics (e.g. now returns null where it never did before)
- **Removed or renamed public symbols** — deleted/renamed function, property, or
  type that callers still reference
- **Narrowed contracts** — stricter preconditions, new early-returns, an event
  that now fires twice or in a different order than callers assume

### Serialization & Data Compatibility (UE5's biggest silent regression source)
- **Removed/renamed `UPROPERTY`** without a `CoreRedirect` → existing assets,
  DataAssets, DataTables, and saved games load with that data lost
- **Retyped `UPROPERTY`** (e.g. `int32`→`FName`, enum→struct) → existing
  serialized values deserialize wrong or drop to defaults
- **Reordered/inserted `UENUM` values** → byte-serialized enum fields on existing
  assets now resolve to the wrong entry
- **Changed `USTRUCT` layout** used in saved data or replicated as a whole
- **Missing redirect/migration** for any of the above (`[CoreRedirects]`,
  `StructRedirects`, or a PostLoad/migration path)

### Replication & Network Compatibility
- **Changed `DOREPLIFETIME` conditions** or added/removed `ReplicatedUsing` →
  desync, missed RepNotify side effects
- **Changed RPC signatures or reliability** → mismatch with clients on the old
  build; mixed-version desync
- **Authority/relevancy changes** that alter what an existing client sees

### Default & Config Changes
- **Changed default member initializer or config/`.ini` default** → existing
  content that relied on the old default silently changes behavior
- **Renamed/removed CVar or config key** referenced by content, scripts, or
  launch options

### UE5-Specific
- **GAS** — renamed GameplayTag string, changed AttributeSet member, altered
  ability activation tags → existing abilities/effects/Blueprints break
- **Blueprint-exposed API** — a `BlueprintCallable`/`BlueprintPure`/exposed
  `UPROPERTY` that Blueprints call; removing/renaming it breaks those graphs
  silently (no C++ compile error)
- **Removed code paths** — deleting a branch, delegate binding, or function that
  another subsystem quietly depended on
- **Changed subsystem/init ordering** — moving work between `BeginPlay`,
  `OnWorldBeginPlay`, `PostLoad`, or a readiness gate that others wait on

## Review Process

For each symbol the diff changes or removes:

1. **Find who depends on it** — Grep `Source/` for callers and referencers; for
   `UPROPERTY`/`UFUNCTION`/tags, remember Blueprints and assets reference these
   by name with no compile-time check.
2. **Ask what old state exists** — is there serialized data, saved content, or a
   shipped client that assumed the pre-change shape/behavior?
3. **Check for a migration** — if data/format changed, is there a redirect or
   PostLoad path? If not, that's the regression.
4. **Confirm behavior parity** — for same-signature changes, does every existing
   caller still get the behavior it was written against?

## What to Look For in Diffs

- Deleted or renamed public functions/properties (especially `UPROPERTY`,
  `UFUNCTION`, GameplayTags, AttributeSet members)
- Changed signatures, return types, or parameter defaults
- Retyped or removed `UPROPERTY` with no accompanying `CoreRedirect`
- Reordered `UENUM` entries
- Changed `DOREPLIFETIME` conditions, added/removed `RepNotify`, changed RPCs
- Changed default initializers or `Config/*.ini` defaults
- Removed branches, delegate bindings, or "unused" helpers that weren't dead

---

## Severity Classification

- **CRITICAL**: Silent data loss or corruption on load (removed/retyped
  `UPROPERTY` or reordered enum with no redirect), replication/RPC break with
  existing clients, breaking a shipped save/asset format
- **WARNING**: Broken caller or Blueprint/asset reference the compiler won't
  catch, behavior change an existing system relies on, default/config change that
  alters existing content
- **INFO**: Compatibility concern worth a redirect or migration note, low-risk
  ordering change worth confirming
