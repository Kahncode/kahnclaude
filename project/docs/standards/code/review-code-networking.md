# Review Code: Networking — Reference

## Property Replication

### Replication Checklist
1. Mark property `UPROPERTY(Replicated)` or `ReplicatedUsing=OnRep_X`
2. Override `GetLifetimeReplicatedProps` with `DOREPLIFETIME` macro
3. Set `bReplicates = true` in Actor constructor
4. `OnRep_` callbacks handle only cosmetic/UI updates — no gameplay logic
5. Test with `net.PktLag` and multiple PIE clients

### Replication Conditions

| Condition | Use when |
|-----------|---------|
| `COND_None` | Replicate to all connections (default) |
| `COND_OwnerOnly` | Player-specific data (ammo, UI state) |
| `COND_SkipOwner` | Third-person cosmetic state |
| `COND_SimulatedOnly` | Cosmetic state for non-owning clients |
| `COND_AutonomousOnly` | Local player only |
| `COND_InitialOnly` | Replicate once on spawn |
| `COND_Custom` | `PreReplication` for per-connection control |

## RPC Patterns

### Server RPC (Client to Server)
- **Always `WithValidation`** — validate input to prevent cheating
- Never call Server RPCs from the server — check `HasAuthority()` first
- Function: `Server_X`, impl: `Server_X_Implementation`, validate: `Server_X_Validate`

### Client RPC (Server to Owning Client)
- Function: `Client_X`, impl: `Client_X_Implementation`

### NetMulticast (Server to All Clients)
- Function: `Multicast_X`, impl: `Multicast_X_Implementation`

### Reliability Rules
| Use | For |
|-----|-----|
| `Reliable` | Gameplay-critical RPCs (fire, use ability) |
| `Unreliable` | Cosmetic/high-frequency RPCs (effects, footsteps) |

**Never `Reliable` for high-frequency RPCs** — reliable buffer overflow disconnects clients.

## Authority and Role Checks

```cpp
if (HasAuthority())
    ProcessDamage(Instigator, Damage);  // Server-only gameplay

if (!IsRunningDedicatedServer())
    SpawnParticleEffect();  // Never render on dedicated server
```

- `ROLE_Authority` — server
- `ROLE_AutonomousProxy` — local player on their client
- `ROLE_SimulatedProxy` — remote player on another client
- Never call `Destroy()` on replicated actors from clients — only server destroys

## Net Dormancy

Sleep actors that change rarely to save bandwidth:
```cpp
SetNetDormancy(DORM_DormantAll);  // Constructor

void AMyPickup::OnPickedUp()
{
    FlushNetDormancy();       // Wake briefly
    bIsPickedUp = true;
    SetNetDormancy(DORM_DormantAll);  // Sleep again
}
```

## Bandwidth Optimization

1. **Replication conditions**: `COND_OwnerOnly` for player-specific data
2. **Net dormancy**: sleep infrequently-changing actors
3. **Minimize RPCs**: prefer property replication; batch updates
4. **Quantize values**: reduce bits for positions/rotations
5. **Net priority/frequency**: `NetPriority` for importance, `NetUpdateFrequency` for rate
6. **Replication Graph**: spatial nodes for large-scale multiplayer (100+ actors)

## What NOT to Do

- Never replicate cosmetic state — use `NetMulticast Unreliable` RPCs
- Never trust client input — always validate Server RPCs
- Never replicate large frequently-changing arrays — use delta/custom serialization
- Never `Destroy()` replicated actors from clients
- Never put gameplay logic in `OnRep_` callbacks

## Client-Side Prediction

Apply effect locally for responsiveness, then let server confirm or correct:
- `IsLocallyControlled()` → apply local prediction immediately
- `!HasAuthority()` → send Server RPC for validation
- `HasAuthority()` → apply authoritatively

## Replication Graph

Replace default replication driver for large-scale multiplayer (100+ actors):
- Derive from `UReplicationGraph` with custom nodes
- `UReplicationGraphNode_GridSpatialization2D` for distance-based relevancy
- Always-relevant nodes for game state / player states
- Per-connection nodes for player-specific actors
- Set `NetCullDistanceSquared` to reduce consideration range

## Network Debugging

| Command | Effect |
|---------|--------|
| `stat net` | Network stats overlay |
| `net.PktLag=100` | Simulate 100ms latency |
| `net.PktLoss=5` | Simulate 5% packet loss |

Always test multiplayer features with simulated latency and packet loss before shipping.

---

## Review Guidelines

### What to IGNORE
- General correctness not related to networking (other dimension)
- Style details (other dimension)
- Client-only rendering/audio code

### Severity Classification
- **CRITICAL**: Missing DOREPLIFETIME, Server RPC without WithValidation, Reliable on high-frequency RPC, gameplay logic in OnRep
- **WARNING**: Missing replication conditions, missing authority checks, over-replication, missing dormancy
- **INFO**: Bandwidth optimization, Push Model suggestions, net priority tuning
