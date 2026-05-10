# Tech Stack Guide: Helix Perforce

<!-- detection: auto | signal: .p4ignore, .p4config, .p4enviro, or P4PORT/P4USER/P4CLIENT env vars | prerequisite: none -->
<!-- prompt: "Perforce configuration detected. Do you want to set up Perforce integration?" -->

---

## Setup — Environment Configuration

A `.p4config` file in the workspace root is required so all `p4` commands (including those run by Claude via Bash) automatically pick up the correct server, user, and workspace. Without this file, `p4` may default to the wrong hostname or fail to connect.

### Required Variables

| Variable | How to Obtain |
|----------|---------------|
| `P4PORT` | autodetect, then ask user |
| `P4USER` | autodetect, then ask user |
| `P4CLIENT` | autodetect, then ask user |

### Autodetection — Try Before Asking

Before prompting the user, attempt to detect the active Perforce connection automatically. Run all three steps in parallel:

**Step 1 — Read configured values:**

```bash
p4 set 2>/dev/null
```

This returns P4PORT, P4USER, P4CLIENT, P4CHARSET, etc. as currently configured (env vars, registry, `.p4config`).

**Step 2 — Check Windows registry for additional server references:**

```bash
reg query "HKCU\Software\Perforce\Environment" 2>/dev/null
```

Registry keys like `P4_<server:port>_CHARSET` reveal servers the user has connected to, even if P4PORT currently points to an unresolvable alias. Extract the `<server:port>` from these key names.

**Step 3 — Check for running Perforce processes:**

```bash
tasklist 2>/dev/null | grep -i -E "p4|perforce|helix"
```

If P4V or p4d is running, the user has an active Perforce session.

**Step 4 — Validate the connection:**

Try `p4 info` with the detected P4PORT:

```bash
p4 -p <detected_port> -u <detected_user> info 2>&1 | head -20
```

- If the configured P4PORT fails (e.g. `perforce:1666` doesn't resolve), check the registry for charset keys matching the pattern `P4_<host:port>_CHARSET` — the `<host:port>` in those key names is the real server address.
- If `p4 info` succeeds, extract `Server address`, `User name`, and `Client name` from the output.

**Step 5 — Confirm with the user:**

Present the autodetected values and ask the user to confirm or correct them before writing `.p4config`. Example:

> Detected Perforce connection:
> - **P4PORT:** `p4-server.example.com:1666`
> - **P4USER:** `jsmith`
> - **P4CLIENT:** `WORKSTATION-01`
>
> Are these correct?

Only ask the user to provide values manually if autodetection fails entirely (no `p4 set` output, no registry keys, no running processes).

### Create .p4config

Once values are confirmed (autodetected or user-provided), **create the file** at the workspace root using the Write tool:

```ini
# .p4config — Perforce connection settings
P4PORT=ssl:perforce.company.com:1666
P4USER=username
P4CLIENT=username_workspace
```

After writing the file, also set the `P4CONFIG` environment variable so `p4` discovers the file:

```bash
# Windows (persistent)
setx P4CONFIG .p4config

# Linux/macOS
export P4CONFIG=.p4config  # add to ~/.bashrc or ~/.zshrc
```

Finally, ensure `.p4config` is listed in `.p4ignore` so it is not submitted to the depot.

### Verification

Run `p4 info`. If it fails: check P4PORT/P4USER/P4CLIENT are set (via `.p4config` or env vars), run `p4 login`, verify network connectivity.

---

### Defaults (no question needed)

- Create CL before editing any file
- Never revert without asking
- Never submit without user approval

---

## Operational Reference — Perforce

### Connection

- **Depot**: Configure in `.p4config` or environment variables
- **Stream**: Set via `P4CLIENT` workspace mapping
- **Local workspace root**: Your project root directory
- Large binary assets (Content folder) require Perforce — not optional.

### Authentication — Cached Login Tickets

Perforce CLI commands work without interactive login because of cached session tickets:

1. **Cached login tickets** — When you run `p4 login` in your terminal, Perforce stores a session ticket (typically in `%USERPROFILE%\p4tickets.txt`). All subsequent `p4` commands reuse that ticket silently.
2. **Environment variables** — `P4USER`, `P4PORT`, `P4CLIENT` are set (via `.p4config`, `.p4enviro`, or system env vars), so `p4` knows which server and workspace to target without prompting.

#### If authentication breaks

- **Expired ticket** — run `p4 login` in a terminal to refresh.
- **Missing env vars** — ensure `P4USER`, `P4PORT`, and `P4CLIENT` are set (preferably via `.p4config`).
- **Wrong user context** — if Claude's shell runs under a different OS account it won't see your ticket; run `p4 login` under that account.

### CLI Commands — Use p4 Directly via Bash

Use the `p4` CLI directly through the Bash tool for all Perforce operations:

| Action | Command |
|--------|---------|
| Open file for edit | `p4 edit <file>` |
| Add new file | `p4 add <file>` |
| Create changelist | `p4 change -o \| sed 's/<enter description here>/Description/' \| p4 change -i` |
| Move file to CL | `p4 reopen -c <CL#> <file>` |
| Revert file | `p4 revert <file>` |
| Check status | `p4 status` |
| Diff file | `p4 diff <file>` |

### File Workflow — Follow This Order

1. **Create a changelist first** — always before touching any file.
2. **Existing file** → run `p4 edit <file>` before writing to it.
3. **New file** → create it, then run `p4 add <file>`.
4. **Move all files** into the changelist with `p4 reopen -c <CL#> <file>`.

#### p4 edit vs p4 add

- `p4 edit` — file already exists in the depot. Opens it for modification.
- `p4 add` — file is new and not yet in the depot. Marks it for addition.
- If unsure, run `p4 status` first — if the file shows as tracked, use `p4 edit`.

### Changelist Descriptions

- If no description is given, **generate one from context** (affected file, system, or purpose).
- Only ask the user if there is genuinely not enough context.
- Always append `#review` to every description.
  - `Fix AI patrol logic #review`
  - `Add BotCharacter dodge ability #review`

### Submit Policy

**Never run `p4 submit`.** Submitting is exclusively the user's responsibility.
If asked to submit, explain the restriction and stop.

### Shelving

- Shelving is used to back up in-progress work or share for review without submitting.
- Run `p4 shelve -c <CL>` via Bash if shelving is needed.
- Shelved files stay in the changelist — they are not submitted.
- To unshelve: `p4 unshelve -s <CL> -c <target-CL>`.

### Local-Only Files — Never p4 add

These are covered by `.p4ignore` and must never be registered in Perforce:

- `.claude/` and all its contents
- `CLAUDE.local.md`
- `docs/` folder (`ARCHITECTURE.md`, `coding-standard.md`, etc.)
- Memory files

### Scope

Only modify files under the project's `Source/` directory.
Do not touch Plugins, Config, Content, Build files, or other Source modules without explicit user approval.

### External Documentation

- **P4 Command Reference**: https://help.perforce.com/helix-core/server-apps/cmdref/current/Content/CmdRef/commands.html
  - Use WebFetch to look up command syntax, flags, and usage when the info above is insufficient.
