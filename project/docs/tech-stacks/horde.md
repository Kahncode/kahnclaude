# Horde — Reference

> Generic Horde behaviour (API, link shapes, scheduler, storage, gotchas). Read by the `horde` skill and the `horde-guide` agent. Add newly verified generic Horde facts HERE, not to memory.
> Project facts (server, streams, schedules, Slack, agents, workspaces): {{HORDE_DOC}}.

---

## Versions & Layout

| Item | Value |
|------|-------|
| Server source | `Engine/Source/Programs/Horde/` (plugin `Plugins/Build/HordeServer.Build/`, dashboard `HordeDashboard/src/`) |
| Engine-shipped docs | `Engine/Source/Programs/Horde/Docs/` (Config/, Config/Schema/, Deployment/, Internals/, Tutorials/, `ReleaseNotes.md`) |

### Machine-readable sources
- Template dry run: `$KC_PROJECT_ROOT/.claude/skills/horde/scripts/listonly_templates.py <stream.json> <id,id,...> [extra args]` runs RunUAT BuildGraph `-ListOnly` per template; logs go to `{{TEMP_BASE}}\horde-scratch\listonly\`.
- What Horde receives from BuildGraph: `-HordeExport` (not `-Export`).

---

## API Cheat Sheet

**Auth**
- Anonymous requests get 401. Today the only auth is the user's logged-in Chrome (`fetch(..., {credentials:'include'})` from a tab on the Horde origin, via Claude in Chrome `javascript_tool`).
- Engine docs say bearer tokens come from the `/account` page (`Docs/Config/Permissions.md:31`); admins also have `/admin/token`. Unverified for non-admin users.

| Need | Endpoint |
|---|---|
| Job (steps, batches, agent, outcome) | `GET /api/v1/jobs/<jobId>` → `batches[].steps[]` (`name`, `outcome`, `state`, `logId`), `batches[].agentId` |
| Step-saved artifacts for a CL | `GET /api/v2/artifacts?streamId={{HORDE_STREAM_ID}}&minChange=<cl>&maxChange=<cl>&type=step-saved` (keys contain `job:<jobId>/step:<stepId>`) |
| Download artifact zip | `GET /api/v2/artifacts/<id>/zip` |
| Agent history | `GET /api/v1/agents/<agentId>/history` |
| Server version | `GET /api/v1/server/info` |
| Full REST reference | `Engine/Source/Programs/Horde/Docs/Internals/RestApi.md` |

- The browser session gets **403** on the horde-logs blobs endpoint, so blob sizes need server file access.
- streamId = depot stream lowercased, `/` → `-`, leading `//` dropped (`//MyGame/dev` → `mygame-dev`).

---

## Link Shapes

Full table with endpoints: `.claude/skills/horde/references/link-shapes.md`. Routes come from `HordeDashboard/src/App.tsx:143-178`.

| URL | What it is |
|---|---|
| `/job/<jobId>` (`?step=<stepId>`, `&batch=`) | job / step |
| `/log/<logId>` | a step log |
| `/testreport/<testdataId>` | test report |
| `/stream/<streamId>` (`?tab=`) | stream page / template tab |
| `/agents?agentId=<id>` | agent |
| `/audit/{job,issue,agent,template}/...` | audit log |
| `/artifact/<artifactId>` | artifact redirect |
| `/automation`, `/buildhealth` | test automation hub / build health |
| `?issue=<id>` on any page | issue panel |

---

## Scheduling & Triggers (short form; project details in {{HORDE_CI_CONFIG_DOC}})

- `requireSubmittedChange` defaults to **true**. A slot with no new submit to the stream is skipped and never caught up (`ScheduleConfig.cs:42`; log line "no candidate changes after CL").
- `maxActive: 1` skips a slot while the previous scheduled run is still active ("already have maximum number of jobs running", `ScheduleService.cs:374-376`).
- `templateParameters` in a schedule are **ignored**: scheduled jobs start with `GetDefaultParameters` (`ScheduleService.cs:551-555`). For non-default values, make a separate template with the args baked in.
- A pattern with no `interval` fires once a day at `minTime`. `maxTime` is inclusive.
- `chainedJobs` fire when the trigger target reaches Success **or Warnings**. An aggregate trigger needs **every** step of the aggregate to pass, so trigger on a node instead.
- `schedule.gate` runs only at a CL where another template's target already passed.
- Queue score = job priority × 10 + node priority + 1 (`JobCollection.cs:2598`).
- Horde skips a step whose `After=` dependency failed (fail-fast).

---

## Notifications & Escalation

- `escalateAlias` must be a Slack **ID**: `S…` (group) → `<!subteam^S…>`, `U…` (user) → `<@U…>`. A handle like `my-team` pings nobody (`FormatUserOrGroupMention`, `SlackNotificationSink.cs` ~2040).
- `escalateTimes` are minutes added one after another from issue creation, and the last value repeats until the issue resolves. Horde has no stop option, so a huge last value acts as a stop.
- Stock Horde also pings the owner plus the alias on owned issues ("for vis", `SlackNotificationSink.cs` ~3313).
- Existing issues pick up a config change only on their next update.

---

## Agents & Workspaces

Compare a slow or odd step by agent history (`/api/v1/agents/<id>/history`) before blaming a CL range.

Workspace lifetime (from the engine's Horde source):
- An `incremental: true` workspace type: batch-start sync and end-of-batch clean skip untracked files, so `Sync/GauntletTemp/...` survives from job to job on the same agent (`WorkspaceInfo.cs:442-450`, `PerforceExecutor.cs:239-248`).
- Only a **full conform** (dashboard), `incremental: false` or Gauntlet `-Clean` / `UE_GauntletCleanTempDir=true` wipes it. The daily automatic conform is not full and keeps it (`ConformTaskSource.cs:176`).
- A job batch gets an exclusive lease on an agent with no other leases (`JobTaskSource.cs:626`, `:881`), so two jobs never write the same workspace at once.
- `$(UE_HORDE_SHARED_DIR)` = `<data dir>\Saved`: shared by every workspace on the agent, wiped by a full conform, so it is no more durable than the workspace.

---

## Storage Failures (temp storage and logs)

- `ArgumentOutOfRangeException (Parameter 'start')` in `BatchBlobReader.ReadPacketsAsync` (`bundleResponse.Data.Memory.Slice(...)`, BatchBlobReader.cs ~355 in 5.8) means the server returned fewer bundle bytes than requested.
  - FileSystem backend: `MemoryMappedFileCache.Read` returns EMPTY data for a 0-byte blob and clamps a short file with `Math.Min`, without raising an error.
  - A missing file throws FileNotFound instead, which shows up as a different error.
  - `HttpStorageBackend.ReadBlobAsync` never checks the length it received.
- Log variant: the dashboard shows "Unable to read `<logId>/<bundle>_N#pkt=off,len` … (Parameter 'start')" from `FlushedPacketHandle.ReadExportAsync` (PacketHandle.cs:185) via `LogCollection.ReadLinesAsync`.
  - The log root ref is bad, so every line fails.
  - `pkt=0` means the bundle file is about 0 bytes.
- What to do:
  1. Rerun only the failed step.
  2. If it fails again at the same point, the stored blob is bad: rerun the node that produced the block.
  3. Check free space on the Horde server's Storage volume.

---

## Gotchas

- Run `p4` with a depot path from **PowerShell**. Git Bash turns `//<depot>/...` into `C:/...`; `MSYS_NO_PATHCONV=1` then breaks `.p4config`.
- `p4 change -i` piped from PowerShell fails because of the BOM. Write the spec to a file and run `cmd /c "p4 change -i < file"`.
- A stream json may have `//` comments and trailing commas. Horde accepts them; strict parsers don't.
- A stream json submit goes live immediately; there is no staging.
- Step artifact zips can have paths longer than 260 characters. `Expand-Archive` silently drops files such as `EditorOutput.log`, so use python `zipfile`.
- PowerShell 5.1 splits `-Script=...MyGameBuild.xml` at the dot. Run RunUAT through python `subprocess`.
- The Horde Tests tab shows only the last iteration of an `iterations=N` run; per-pass counts are in the step log.

---

## Sources

| Source | Version last read |
|---|---|
| `Engine/Source/Programs/Horde/Docs/ReleaseNotes.md` | top entry = the version your engine ships |
| `Engine/Source/Programs/Horde/Docs/**` | synced engine |
| Epic online docs | `https://dev.epicgames.com/documentation/en-us/unreal-engine/horde-in-unreal-engine` (check against ReleaseNotes before trusting) |

`/horde learn` updates this table after it reads new documentation.
