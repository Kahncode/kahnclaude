---
name: horde-artifact
description: "Downloads and triages a Horde step's saved artifact: unzips it, writes DIGEST.md (failing tests, first errors, crash lines), checks the project's Horde runbook and says rerun (infra) or hand off (code/test). ALWAYS invoke for a pasted Horde or Slack job-failure message, a Horde job URL, a step-saved folder or zip, or 'triage the horde logs for CL N'."
---

# Horde artifact: download + triage

Horde: `{{HORDE_URL}}` (API needs login; anonymous = 401).
Auth = the user's logged-in Chrome (Claude in Chrome tools). No token.
This skill never quarantines, edits code, ini or tests. Quarantining a test is a separate, explicit change the user makes.
Server, API, link shapes and agent facts: `{{HORDE_DOC}}` (generic Horde: `docs/tech-stacks/horde.md`). A Horde question that isn't about a red (schedule, ping, skipped step, config how-to) goes to the `horde` skill.

## 1. Parse the message
- Stream: `{{P4_STREAM}}` → streamId `{{HORDE_STREAM_ID}}` (lowercase, `/` → `-`, drop leading `//`).
- CL: `CL 12345`.
- Template: text after the CL (`Full Editor test`, `Smoke test`); ignore the `N step failed` suffix.
- Step: the line `<Step> — N errors` (`Smoke Test`). Slug = lowercase, spaces → `-` (`smoke-test`).
- A pasted Horde URL `/job/<jobId>?step=<stepId>` beats parsing.
- Already on disk? A zip in `{{DOWNLOADS}}` or a folder in `{{DOWNLOADS}}\h\` for that CL+step → skip to step 5 or 6.

## 2. Open Chrome
One ToolSearch for `tabs_context_mcp, tabs_create_mcp, tabs_close_mcp, navigate, javascript_tool, computer, read_page`.
`tabs_context_mcp` → `tabs_create_mcp` → navigate to `{{HORDE_URL}}/`.
If the extension isn't connected, stop and ask the user to open Chrome with the extension.

## 3. Find the artifact (javascript_tool in that tab)
```js
const r = await fetch('/api/v2/artifacts?streamId={{HORDE_STREAM_ID}}&minChange=123456&maxChange=123456&type=step-saved', {credentials:'include'});
r.status + ' ' + JSON.stringify((await r.json()).artifacts?.map(a => ({id:a.id, name:a.name, keys:a.keys, desc:a.description})))
```
- Keep artifacts whose keys contain `job:<jobId>/step:<stepId>`; match the step via `/api/v1/jobs/<jobId>` (step names in `batches[].steps[]`, `outcome: "Failure"`). Note the agent name from the batch: the runbook keys some verdicts on it.
- Several jobs at that CL → pick the one whose template matches and whose step failed; else newest. Say which one.
- If fetch returns 401/403 (dashboard uses a bearer, not cookies): open the job page, click the step, Artifacts → step-saved → Download.

## 4. Download
- Expected name: `step-saved_<streamId>_<CL>_<step-slug>_<hex>.zip`. If `{{DOWNLOADS}}\<that>.zip` exists, skip.
- Else navigate the tab to `{{HORDE_URL}}/api/v2/artifacts/<id>/zip`; Chrome saves it to `{{DOWNLOADS}}`.
- Wait (Bash `run_in_background` until-loop) for the `.zip` to exist with no `*.crdownload` left. Close the tab.

## 5. Unzip (python zipfile, short folder)
Never `Expand-Archive`: some test zips hold 260+ char paths and it silently drops `EditorOutput.log`.
Destination `{{DOWNLOADS}}\h\<CL>-<step-slug>`; if that folder already holds a different artifact, append `-<first 8 chars of artifact id>`. Skip if the folder exists with the same zip.
```powershell
python -I -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "<zip>" "{{DOWNLOADS}}\h\<CL>-<step-slug>"
```
For editor test steps, check an `EditorOutput.log` exists in the result (missing = crash before the editor started, or a bad extract).

## 6. Digest
```powershell
python -I -X utf8 "$KC_PROJECT_ROOT/.claude/skills/horde-artifact/scripts/digest.py" "{{DOWNLOADS}}\h\<CL>-<step-slug>"
```
- Writes `DIGEST.md` in that folder: result summary, failing tests with first error and event time, crash/ensure/fatal/compile lines with the test they hit in, runbook signature hits, headlines (the project's `HORDE_DIGEST_HEADLINES` patterns, AssetRegistryGather, frames >= 60 s), and a Files list (`E1` = EditorOutput.log, `S1` = step log, `R1` = report index.json).
- Also takes a single step log (the Horde "Download log" file, named `{{P4_STREAM}}` with every `/` → `+`, then `-CL <n>-<step>.log`, e.g. `++Project+dev-CL <n>-<step>.log`) → `<name>-DIGEST.md` next to it. Covers `iterations=N` runs (one `E` per `Pass_N_of_M` / `Retry_N`).
- Read `DIGEST.md` first, not the raw logs. Open raw logs only at the line refs it gives (`E3:9258` → Read EditorOutput.log with an offset near 9258).
- The digest redacts lines that may hold credentials (editor logs carry a plain-text ClientLogin token). Never print those lines yourself.

## 7. Triage against the runbook
Read `{{HORDE_RUNBOOK}}`, then:
- Take each "Runbook signature hits" row. It counts only if it falls in the failing test or crash window (same test name in the crash list, timestamps near "Failed at"). `noise` rows never count.
- Check threshold rows against Headlines: AssetRegistryGather wall time / AssetDataDiscovery, `system commit free` near 1-2 GB, long frames before a `Client not ready after`.
- Rows that say "fixed by CL X": if this run's CL is at or after X, the red is NEW, not known.
- Give a one-line verdict first: `Verdict: <infra-agent | engine | test race | code | unknown> — <evidence> (runbook row, memory ref)`.
- **infra-agent / known engine** → say so, name the agent to avoid if known, suggest rerunning the step, and stop. No investigation.
- **test race / code / unknown** → hand off with the digest path, CL, job/step, agent and failing test names:
  - `investigate` (default): ranked causes.
  - `diagnose`: when the user wants it proven, or the runbook row says hand to diagnose (known open red).
- If the user asks to quarantine, say it is a separate change; don't edit DefaultEngine.ini here.

## 8. Report
1. Verdict line.
2. `DIGEST.md` path and the artifact folder.
3. Failing tests with their first error (from the digest table).
4. Next action: rerun step / handed to investigate or diagnose.
After a hand-off proves a new recurring signature, offer to add a runbook row. Add one only when a memory file backs it, and cite that memory in the Ref column.
