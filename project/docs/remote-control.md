# Claude Code — Remote Control & Sessions

## What is `claude remote-control`?

Starts a persistent server on your local machine that lets you connect to and control Claude Code from the Claude.ai app (browser or mobile). The PC does **not** expose inbound ports — it makes outbound HTTPS connections only.

```bash
claude remote-control
claude remote-control --name "MyPC"
claude remote-control --name "MyPC" --spawn worktree --capacity 10
```

Keep the terminal open. When it closes, the session goes offline.

---

## How Sessions Appear in the Claude.ai App

- Open `claude.ai/code` or the Claude mobile app
- Sessions are listed with a **computer icon** and **green dot** when online
- Session name is what you passed to `--name` (defaults to a random slug)
- Tap a session to connect; tap **New session** to spawn a fresh agent on the same server

---

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--name <label>` | random slug | Display name in the app |
| `--capacity <N>` | 32 | Max concurrent sessions on this server |
| `--spawn <mode>` | `same-dir` | How new sessions are created (see below) |
| `--verbose` | off | Show detailed connection logs |

---

## `--spawn` Modes

| Mode | Behavior | When to use |
|------|----------|-------------|
| `same-dir` | All sessions share the working directory | Switching devices, single-user handoff |
| `worktree` | Each new session gets its own git worktree | Parallel independent agents; **requires git repo** |

Press **`w`** at runtime to toggle between modes while the server is running.

---

## Capacity

`Capacity: 1/32` means 1 session connected out of a max of 32. This is **per-server** — each `claude remote-control` process has its own counter. Reduce it to cap resource usage; increase it for shared/team servers.

---

## Parallel Agents

With `--spawn worktree`, each time someone taps **New session** in the app, a fresh Claude agent spawns in its own isolated git worktree. Multiple agents can work in parallel on the same project without file conflicts. Each shows up as a separate session in the app.

---

## Naming Pattern

Useful convention for identifiable sessions:

```bash
FOLDER=$(basename "$PWD") && TS=$(date +%Y%m%d_%H%M%S)
claude remote-control --name "${FOLDER}_${TS}"
# e.g. MyProject_20250101_120000
```

---

## Startup Automation

To launch on Windows login, add to your startup bat:

```bat
start "" cmd /k "cd /d C:\your\project && claude remote-control --name %COMPUTERNAME%"
```

`%COMPUTERNAME%` expands correctly in `cmd.exe` but NOT in bash — use it in `.bat` files only.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| PC not in session list | Terminal must be running `claude remote-control` |
| Auth error | Must use `claude /login` (claude.ai OAuth) — API keys don't work |
| `ANTHROPIC_API_KEY` set | Unset it; remote control requires claude.ai login |
| Old version | Needs Claude Code v2.1.51+. Check: `claude --version` |
| Team/Enterprise | Admin must enable Remote Control at `claude.ai/admin-settings/claude-code` |
| `%COMPUTERNAME%` shows literally | You ran from bash, not cmd. Use `$COMPUTERNAME` in bash or run via cmd |
| Session disappeared | Network drop >10 min times out — re-run `claude remote-control` |
