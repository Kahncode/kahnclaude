# Where to Look: Reuse Map (UE5 / Lyra / project test framework)

These are starting points, not answers. **Verify the signature in this engine version before recommending anything.** Open the header and read the function.

## Contents
1–2. Project test framework and game code: project notes
3. Engine: Gameplay Ability System
4. Engine: containers, algorithms, strings
5. Engine: actors, components, world
6. Common re-implementations to look for

---

## 1–2. Project test framework and game code

Project specifics: read {{PROJECT_NOTES_DIR}}\reuse-finder.md if it exists.

## 3. Engine: Gameplay Ability System

Headers: `Engine/Plugins/Runtime/GameplayAbilities/Source/GameplayAbilities/Public/`

- `AbilitySystemComponent.h`: `GetOwnedGameplayTags()`, `HasMatchingGameplayTag`, `HasAnyMatchingGameplayTags`, `GetBlockedAbilityTags()`, `AreAbilityTagsBlocked`, `FindAbilitySpecFromHandle`, `FindAbilitySpecFromClass`, `GetActivatableAbilities()`, `GetActiveEffects`/`GetActiveEffectsWithAllTags`, `GetGameplayTagCount`
- `Abilities/GameplayAbility.h`: `DoesAbilitySatisfyTagRequirements` (public; the base version appends the blocking tags via `AppendMatchingTags`), `GetAssetTags()`, `CanActivateAbility`, `GetInstancingPolicy`
- `AbilitySystemBlueprintLibrary.h`: actor-to-ASC lookups (`GetAbilitySystemComponent`), event sends
- `GameplayEffectTypes.h` / `GameplayTagContainer.h` (`Engine/Source/Runtime/GameplayTags/Classes/`): `Filter`, `FilterExact`, `HasAny`, `HasAll`, `AppendMatchingTags`, `ToStringSimple`, `GetGameplayTagParents`, `MatchesTag`

## 4. Engine: containers, algorithms, strings

- `TArray`: `FindByPredicate`, `ContainsByPredicate`, `FilterByPredicate`, `IndexOfByPredicate`, `RemoveAll`, `RemoveAllSwap`, `AddUnique`, `Append`, `Sort`, `StableSort`
- `Algo/` (`Engine/Source/Runtime/Core/Public/Algo/`): `Transform`, `TransformIf`, `CountIf`, `AllOf`, `AnyOf`, `NoneOf`, `MinElementBy`, `MaxElementBy`, `Accumulate`, `Find`, `Reverse`
- `FString`: `Join`, `Printf`, `Split`, `ParseIntoArray`, `StartsWith`, `Contains`, `LexToString`, `FString::SanitizeFloat`
- Enum text: `UEnum::GetValueAsString`, `StaticEnum<E>()->GetNameStringByValue`. In tests, prefer the test framework's enum-text helper (project notes).
- Math: `FMath::IsNearlyEqual`, `IsNearlyZero`, `Clamp`, `FVector::Dist`/`Dist2D`/`DistSquared`, `FBox::IsInside`, `FMath::Lerp`
- Time: `FPlatformTime::Seconds`, `UWorld::GetTimeSeconds`, `FTimerManager`

## 5. Engine: actors, components, world

- `TActorIterator<T>`, `UGameplayStatics::GetAllActorsOfClass`, `GetAllActorsWithTag`
- `AActor::FindComponentByClass`, `GetComponents<T>`, `GetComponentsByTag`
- `APawn::GetController`, `AController::GetPawn`, `APlayerState::GetPawn`, `GetPlayerController`
- `UKismetSystemLibrary` traces, `UWorld::LineTraceSingleByChannel`
- Reflection (outside tests): `FindFProperty<T>`, `TFieldIterator`. In tests, use the test framework's reflection helper (project notes).

## 6. Common re-implementations to look for

| Smell | Usually replaced by |
|-------|---------------------|
| Loop over `GetActivatableAbilities()` to find one by handle or class | `FindAbilitySpecFromHandle` / `FindAbilitySpecFromClass` |
| Manual "owned tags ∩ set" loop | `Owned.Filter(Set)` / `HasAny` |
| `FindFProperty` + `ContainerPtrToValuePtr` in a test file | The test framework's reflection helper (project notes) |
| Loop building a `TArray<FString>`, then manual comma join | `FString::Join` |
| Loop with a counter for "how many match" | `Algo::CountIf` |
| Loop with a bool flag for "any match" | `ContainsByPredicate` / `Algo::AnyOf` |
| Hand-written enum switch to string | `UEnum::GetValueAsString` / the test framework's enum-text helper |
| Two `Describe*` helpers printing the same fields | Keep the one in the system's TestUtility |
| A wrapper that only forwards one call with no added null-safety or meaning | Inline it (only if it has 1–2 callers and the wrapper adds no meaning) |
| A project override that recomputes what the base engine function already returns | Call `Super::` or the base public function |
