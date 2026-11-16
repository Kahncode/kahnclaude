---
name: processes-cleanup
description: "Dev tool process cleaner. ALWAYS invoke when the user asks about stuck processes, zombie processes, or cleaning up hung tools. Do not run tasklist/taskkill directly — this skill checks for suspicious duplicates and confirms before killing."
disable-model-invocation: true
allowed-tools: Bash(tasklist *), Bash(taskkill *)
---

# Processes Cleanup

Clean up stuck or duplicate instances of tech stack tools.

## Target Processes

| Tool | Executable | Suspicious if |
|------|------------|---------------|
| P4V | p4v.exe | > 2 instances |
| P4Merge | p4merge.exe | > 1 instance |
| Perforce CLI | p4.exe | > 5 instances |
| Visual Studio | devenv.exe | > 2 instances |

## Instructions

1. **List processes** — run: `tasklist | grep -iE "p4v|p4merge|p4\.exe|devenv"`

2. **Analyze counts** — count instances of each executable

3. **Report findings** — show the user:
   - Process name, count, total memory
   - Flag any that exceed thresholds above

4. **If suspicious counts found:**
   - Ask user which to kill (specific PIDs or all of a type)
   - Never kill without confirmation

5. **Kill selected processes:**
   ```bash
   taskkill //PID <pid> //F          # specific PID
   taskkill //IM <name>.exe //F      # all of a type
   ```

6. **Verify** — re-run tasklist to confirm cleanup
