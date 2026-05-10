# Reference: Perforce Sync Workflow

Extracted from `helix_perforce.md` for the `get-latest` skill.

---

## Sync Commands

| Action | Command |
|--------|---------|
| Sync to latest | `p4 sync` |
| Sync to specific CL | `p4 sync @<CL>` |
| Sync specific path | `p4 sync //depot/path/...` |
| Dry-run (preview only) | `p4 sync -n ...` |
| Check opened files | `p4 opened` |

## Conflict Resolution by File Type

### Binary Files (.uasset, .umap, .ubulk, .pak, images, audio)

- **Never merge binary files** -- only accept theirs or accept yours
- `p4 resolve -at <file>` -- accept theirs (server version)
- `p4 resolve -ay <file>` -- accept yours (local version)
- Always ask the user which version to keep

### Text Files (.h, .cpp, .cs, .ini, .md)

- `p4 resolve -am <file>` -- auto-merge (safe merges only)
- `p4 resolve -at <file>` -- accept theirs
- `p4 resolve -ay <file>` -- accept yours
- For complex conflicts, show both versions and ask the user

## Check What Needs Resolving

```bash
p4 resolve -n
```

Lists files that have pending resolve actions without executing them.

## Authentication

If `p4` commands fail: check P4PORT/P4USER/P4CLIENT are set (via `.p4config` or env vars), run `p4 login` to refresh the ticket, verify network connectivity.

## Shelving (User Reference)

If the user wants to shelve before syncing:
- `p4 shelve -c <CL>` -- shelve files in a changelist
- `p4 unshelve -s <CL>` -- restore shelved files after sync

## Scope

Only sync files under the project's allowed directories (typically `Source/` for UE projects). Do not sync Plugins, Config, Content, or Build files without explicit user approval.
