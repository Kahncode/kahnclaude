# Horde link shapes → API

Base: `{{HORDE_URL}}`. Dashboard routes come from `Engine/Source/Programs/Horde/HordeDashboard/src/App.tsx:143-178`. API routes come from the `[Route(...)]` attributes in the server controllers (paths below). **GET only**: this skill never calls PUT, POST or DELETE.

| Pasted URL | Ids | Fetch (GET) | Controller |
|---|---|---|---|
| `/job/<jobId>` | jobId | `/api/v1/jobs/<jobId>` (has `batches[].steps[]`, `batches[].agentId`, `templateId`, `change`, `createTime`) | `HordeServer.Build/Jobs/JobsController.cs:370` |
| `/job/<jobId>?step=<stepId>` | jobId, stepId | the job above, then find the step in `batches[].steps[]`. If needed: `/api/v1/jobs/<jobId>/batches/<batchId>/steps/<stepId>` | `JobsController.cs:1767` |
| `/job/<jobId>?batch=<batchId>` | jobId, batchId | the job above, then `batches[]` where `id == batchId` (agent, lease, error) | — |
| `...&issue=<id>` or `?issue=<id>` on any page | issueId | `/api/v1/issues/<id>`, `/api/v1/issues/<id>/events`, `/api/v1/issues/<id>/streams` | `HordeServer.Build/Issues/IssuesController.cs:385`, `:698`, `:584` |
| `/log/<logId>` | logId | `/api/v1/logs/<logId>` (metadata), `/api/v1/logs/<logId>/lines?index=<n>&count=<m>` | `HordeServer.Compute/Logs/LogsController.cs:74`, `:217` |
| `/testreport/<testdataId>` | testDataId | `/api/v1/testdata/<testDataId>` | `HordeServer.Build/Jobs/TestData/TestDataController.cs:451` |
| `/stream/<streamId>` (`?tab=<tab>`) | streamId, tab = template tab | `/api/v1/streams/<streamId>` (templates, schedules) | `HordeServer.Build/Streams/StreamsController.cs:115` |
| template in a stream | streamId, templateId | `/api/v1/streams/<streamId>/templates/<templateId>` | `StreamsController.cs:552` |
| `/agents?agentId=<id>` | agentId | `/api/v1/agents/<agentId>/history` | `HordeServer.Compute/Agents/AgentsController.cs:368` |
| `/lease/<leaseId>` | leaseId | `/api/v1/leases/<leaseId>` | `HordeServer.Compute/Agents/Leases/LeasesController.cs:117` |
| `/artifact/<artifactId>` | artifactId | red triage, so hand to `horde-artifact` | — |
| `/audit/{job,issue,agent,template}/...` | as named | the matching object above | — |
| `/automation`, `/buildhealth`, `/dashboard`, `/serverstatus` | none | answer from docs and config; fetch only if the question needs live data | — |
| Server version question | none | `/api/v1/server/info` | `HordeServer/Server/ServerController.cs:66` |
| Slack `:x: {{P4_STREAM}} - CL <n> - <Template> …` | CL, template, step | red triage, so hand to `horde-artifact` | — |

Controller paths are relative to `Engine/Source/Programs/Horde/Plugins/Build/` or `Plugins/Compute/` (ServerController sits under `Engine/Source/Programs/Horde/HordeServer/`). Line numbers drift between engine versions; re-grep `[Route("/api/v1/...` if one has drifted.

## Fetch snippet (Chrome tab on the Horde origin, `javascript_tool`)
```js
const r = await fetch('/api/v1/jobs/<jobId>', {credentials:'include'});
r.status + ' ' + (await r.text()).length
```
Fetch the whole body and save it with a second call that returns the text. If the body is large, return only the fields you need with the `filter` query param, e.g. `?filter=id,name,change,templateId,batches.agentId,batches.steps.id,batches.steps.name,batches.steps.outcome,batches.steps.state` (`Docs/Internals/RestApi.md:29`).

**401/403:** the user is not logged in, or the endpoint needs a bearer token. Stop and ask; don't retry.
