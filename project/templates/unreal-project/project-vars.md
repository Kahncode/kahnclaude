# Project Variables — <ProjectName>

> Copy to `<project>/.claude/rules/project-vars.md` and fill the values. User-level skills, agents and docs (`~/.claude`) write these as `{{NAME}}`; scripts read them with `.claude/scripts/lib/project_vars.py` / `ProjectVars.ps1` (a non-empty env var wins).
> Values may reference other vars (`{{PROJECT_ROOT}}\docs`). Leave a var empty when the project doesn't have that service; the skill that needs it then stops and says so.
> No secrets here: tokens and passwords go in `.env`. Examples use a project called MyGame at `C:\p4\MyGame`.
> Project-only rules for a user-level skill/agent/standard `X` go in `{{PROJECT_NOTES_DIR}}\X.md` (overlay, read after the generic file).

## Paths

```ini
# Workspace root (also a real env var via .claude/settings.local.json env). e.g. C:\p4\MyGame
PROJECT_ROOT=
# Engine folder (env var too). e.g. C:\p4\MyGame\Engine
UE_ENGINE=
# .uproject path (env var too). e.g. {{PROJECT_ROOT}}\MyGame\MyGame.uproject
UE_PROJECT=
# Solution file (env var too). e.g. {{PROJECT_ROOT}}\UE5.sln
UE_SOLUTION=
# Scratch root for Claude temp files. e.g. {{PROJECT_ROOT}}\.temp
TEMP_BASE=
# Per-agent temp folder pattern.
TEMP_ROOT={{TEMP_BASE}}\<agent>-<CL>\
# Browser downloads folder (Horde zips, logs). e.g. C:\Users\<you>\Downloads
DOWNLOADS=
# Second P4 workspace root for CI config (empty if none). e.g. C:\p4\dev-tools
DEVTOOLS_WORKSPACE_ROOT=
# Engine-bundled dotnet + UBT dll. e.g. {{UE_ENGINE}}\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe
UBT_DOTNET=
UBT_DLL={{UE_ENGINE}}\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll
# Editor exe name as it appears in Task Manager. e.g. MyGameEditor-Win64-DebugGame.exe or UnrealEditor.exe
EDITOR_PROCESS=
# Machine-state checker (editor, Live Coding, UBT, test runs).
EDITOR_STATUS_SCRIPT=C:\Users\<you>\.claude\scripts\unreal\editor_status.ps1
# Folder of per-item overlays (project-only rules). e.g. {{PROJECT_ROOT}}\docs\project-notes
PROJECT_NOTES_DIR=
# This project's Claude memory folder. e.g. C:\Users\<you>\.claude\projects\C--p4-MyGame\memory
CLAUDE_MEMORY_DIR=
# Workspace paths that are never added to version control (comma list).
LOCAL_ONLY_PATHS=.claude/,docs/,scripts/,.temp/,CLAUDE.local.md,.env
```

## Unreal project

```ini
# Project name (stem of the .uproject). e.g. MyGame
UE_PROJECT_NAME=
# Folder holding the .uproject (Source/, Config/, Saved/, Content/). e.g. {{PROJECT_ROOT}}\MyGame
UE_PROJECT_DIR=
# Main runtime game module. e.g. MyGameGame
UE_GAME_MODULE=
# Editor-only module. e.g. MyGameEditor
UE_EDITOR_MODULE=
# Regex of Source/ module folders that are tooling, not game code. e.g. MyGameEditor|Developer|Programs
UE_TOOLING_MODULES_REGEX=
# Default UBT target line. e.g. MyGameEditor Win64 DebugGame
UE_DEFAULT_TARGET=
```

## Automation tests

```ini
# Test module and its rules README (empty if the project has none).
UE_TEST_MODULE=
UE_TEST_README=
# Automation test name prefix. e.g. MyGame.
UE_TEST_PREFIX=
# Project test-class macro and log-watch helper (empty if stock UE).
UE_TEST_CLASS_MACRO=
UE_TEST_LOG_WATCH_CLASS=
# Log category for temporary diagnostic logs. e.g. LogMyGameDiag
UE_DIAG_LOG_CATEGORY=
# Map the automation tests boot into. e.g. LV_Automation_Empty
UE_TEST_MAP=
# Script that runs one automation test group (Horde-equivalent runner).
TEST_RUNNER_SCRIPT=
```

## Perforce

```ini
P4PORT=
P4USER=
P4CLIENT=
# Optional second workspace (CI config stream). e.g. <user>_devtools
P4CLIENT_DEVTOOLS=
# Depot root, main stream, CI config stream. e.g. //MyGame, //MyGame/dev, //MyGame/dev-tools
P4_DEPOT_ROOT=
P4_STREAM=
P4_DEVTOOLS_STREAM=
# Submitters / client-name regex to skip as automation in change sweeps.
P4_BOT_USERS=
P4_BOT_CLIENT_REGEX=robomerge|horde|BUILD_
```

## Services (leave empty when not used)

```ini
SWARM_URL=
HORDE_URL=
# Studio game-server admin panel and its API (<env> = environment name).
ADMIN_PANEL_URL=
ADMIN_API_URL=
# Person to ask about admin panel access.
ADMIN_PANEL_CONTACT=
JIRA_URL=
CONFLUENCE_URL=
SENTRY_ORG=
SENTRY_PROJECT=
# Studio time zone for schedules. e.g. Europe/Berlin
STUDIO_TZ=
```

## Horde / CI

```ini
# Horde stream id (the stream name lower-cased with dashes). e.g. mygame-dev
HORDE_STREAM_ID=
# Depot path of the stream's Horde config. e.g. //MyGame/dev-tools/Horde/Config/mygame-dev.stream.json
HORDE_STREAM_CONFIG=
# Project Horde facts, red-step runbook, CI config notes, local CI runner notes.
HORDE_DOC=
HORDE_RUNBOOK=
HORDE_CI_CONFIG_DOC=
LOCAL_CI_TESTS_DOC=
# BuildGraph scripts, ;-separated, relative to PROJECT_ROOT.
BUILDGRAPH_SCRIPTS=
# Slack channel for CI results, and the Slack group ID to escalate to (S…).
SLACK_CI_CHANNEL=
SLACK_ESCALATE_GROUP_ID=
# Docker registry for the Horde server image.
DOCKER_REGISTRY=
# Extra horde-artifact digest headlines from project log lines: name=regex:cap, ;-separated (optional).
HORDE_DIGEST_HEADLINES=
```

## Jira / Confluence

```ini
JIRA_CLOUD_ID=
JIRA_PROJECT_KEY=
JIRA_ASSIGNEE_ACCOUNT_ID=
# Default parent epic for new tickets (optional).
JIRA_ACTIVE_EPIC=
JIRA_DEFAULT_ISSUE_TYPE=Task
JIRA_LABELS=["claude_generated"]
JIRA_COMPONENTS=[]
JIRA_CONTENT_FORMAT=markdown
# Estimate labels if the project uses labels instead of story points (empty = story points).
JIRA_ESTIMATE_LABELS=
CONFLUENCE_CLOUD_ID=
CONFLUENCE_SPACE_KEY=
# Numeric space id (REST v2) and root page id.
CONFLUENCE_SPACE_ID=
CONFLUENCE_ROOT_PAGE_ID=
# Registry of published pages (id, parent, source file).
CONFLUENCE_PAGE_REGISTRY=
# Forge extension key of the "HTML File (Attachment)" macro app on this site.
CONFLUENCE_HTML_MACRO_EXT_KEY=
```

## Docs

```ini
ARCHITECTURE_DOC={{PROJECT_ROOT}}\docs\ARCHITECTURE.md
SUBSYSTEM_DOCS_DIR={{PROJECT_ROOT}}\docs\subsystems
TUTORIALS_DIR={{PROJECT_ROOT}}\docs\tutorials
```

## Community

```ini
# Player-facing game name and Discord server (empty if none).
GAME_NAME=
DISCORD_GUILD_ID=
```

## Presentation skill

```ini
# Private claude.ai artifact links: the design system the decks use, and a reference deck built with it.
PRESENTATION_DS_ARTIFACT_URL=
PRESENTATION_REFERENCE_DECK_URL=
```

## Claude Docs

```ini
# Daily digest doc id (scheduled jobs; optional).
DAILY_DIGEST_DOC_ID=
```
