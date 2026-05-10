# Resolve Diff — Reference

## P4 Commands

| Command | Purpose |
|---------|---------|
| `p4 describe -du <CL>` | Get changelist description and unified diff |
| `p4 diff -du <path>` | Diff pending changes for a file or folder |
| `p4 diff -du <path>/...` | Diff all pending changes under a folder recursively |
| `p4 opened` | List currently opened files in the workspace |
| `p4 changes -s pending -u $P4USER -c $P4CLIENT -m 1` | Latest pending changelist |
| `p4 client -o` | Client spec (extract Stream field) |

## Resolution Priority

1. **CL number** (all digits) — `p4 describe -du`
2. **Swarm URL/ID** (`reviews/NNNN` or `rNNNN`) — extract CL, then `p4 describe -du`
3. **File path** (existing file) — `p4 diff -du <file>`
4. **Folder path** (existing directory) — `p4 diff -du <folder>/...`
5. **System name** (free text) — Grep/Glob to find files, then `p4 diff -du` filtered
6. **Auto-detect** (no args) — `p4 opened` then `p4 changes -s pending`

## Swarm URL Parsing

Swarm URLs follow patterns like:
- `https://<server>/reviews/<id>`
- `https://<server>/reviews/<id>/v<version>`

Extract the numeric review ID and look up the associated changelist.

## Mainline Warning

If the resolved stream path contains `/main` or `/mainline`, emit a prominent warning:
```
WARNING: You are on a mainline stream. Changes here affect all downstream streams.
```
