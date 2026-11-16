# Reference: Shelve & Swarm Changelist

Merged from `shelve-checkpoint.md` and `create-swarm-review.md` for the `swarm-review-shelve` skill.

---

## Shelve Commands

```bash
# Shelve all files in a changelist
p4 shelve -c <CL#>

# Force-update an existing shelf
p4 shelve -f -c <CL#>

# Unshelve (restore) files
p4 unshelve -s <CL#>

# Unshelve to a different CL
p4 unshelve -s <CL#> -c <target-CL#>
```

## Resolving the Active CL

```bash
# List pending CLs for the current user/workspace ($P4USER/$P4CLIENT are empty in the shell)
p4 changes -s pending --me -c "$(p4 -ztag -F %clientName% info)"

# List exactly what a CL will shelve (always before shelving)
p4 opened -c <CL#>
```

Files in the `default` changelist cannot be shelved until moved to a numbered CL. The default CL holds the user's unrelated work in this shared workspace: move only files you name, never a wildcard.

```bash
# Create a new, empty numbered CL (strip Files: or it swallows the whole default CL)
p4 change -o | sed -e 's/<enter description here>/Checkpoint/' -e '/^Files:/,$d' | p4 change -i

# Move named files from default to the new CL
p4 reopen -c <new-CL#> <file> [<file> ...]
```

## Swarm URL Patterns

- Change page: `$SWARM_URL/changes/<CL#>` (links its review). Review IDs differ from CL numbers (e.g. CL 12000 → review 12042), so never build `/reviews/<CL#>`
- Shelving a CL with `#review` in its description auto-creates a Swarm review
- Subsequent shelves to the same CL update the existing review (URL stays the same)

## Detecting Swarm URL

1. Check `SWARM_URL` environment variable
2. Run `p4 property -l -n P4.Swarm.URL`
3. Check Swarm triggers: `p4 triggers -o`
4. Ask the user as a last resort

## Authentication

Swarm uses the active Perforce login ticket. No additional credentials needed.

- Ticket location: `%USERPROFILE%\p4tickets.txt` (Windows) or `~/.p4tickets` (Linux/macOS)
- If API calls fail with `401`, run `p4 login` to refresh
- If `p4` commands fail, ensure P4PORT/P4USER/P4CLIENT are set and `p4 login` has been run

## Shelving Checklist

1. Finalize the CL description (must have `[TICKET]`, `[summary]`, `#review`)
2. Run `p4 shelve -c <CL#>`
3. Share the CL number or Swarm URL with reviewers
4. After review comments, fix locally then `p4 shelve -f -c <CL#>` to update

## Shelving Behavior

- Shelved files stay in the changelist (not submitted)
- Shelving the same CL replaces the previous shelf
- Multiple shelves to the same CL act as versioned snapshots
- Shelving does not affect the Swarm review unless the CL has `#review` in its description

## What NOT to Shelve

- `.claude/` directory contents
- `CLAUDE.local.md`
- `.env` files or any credentials
- Large binary assets already in the depot (wastes server space)

## Finding the Review for a CL

```bash
curl -s -u "$P4USER:$P4TICKET" \
  "$SWARM_URL/api/v9/reviews?change=<CL#>"
```

Or open `$SWARM_URL/changes/<CL#>`, which links the review.
