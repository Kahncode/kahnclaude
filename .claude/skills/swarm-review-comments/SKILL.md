---
name: swarm-review-comments
description: "Swarm comment handler. ALWAYS invoke when the user asks to fetch, address, or fix Swarm review comments. Do not read Swarm API directly — this skill fetches comments, fixes one-by-one, replies, marks addressed, and re-shelves."
---

# Fetch and Address Swarm Comments

Use PROACTIVELY when user says `fetch swarm comments`, `address review comments`, `swarm comments`, or asks to fix review feedback.

**Input:** $ARGUMENTS (CL number -- bare digits or `CL` prefix)

## Reference

- @docs/standards/swarm/swarm-review-comments.md -- Swarm API, comment workflow
- @project/docs/tech-stacks/helix_swarm.md -- full Swarm API guide

## allowed-tools

Read, Write, Edit, Grep, Glob, Bash(p4 *), WebFetch

## Step 1 -- Parse CL and Get Auth

Extract CL number from $ARGUMENTS. Get P4USER and P4TICKET:

```bash
p4 set -q P4USER
cat "$USERPROFILE/p4tickets.txt"
```

Parse ticket file (`<server>=<user>:<ticket>`) to extract the hex ticket string.

## Step 2 -- Fetch Review and Comments

```bash
curl -s -u "$P4USER:$P4TICKET" "$SWARM_URL/api/v9/reviews?change=$CL"
curl -s -u "$P4USER:$P4TICKET" "$SWARM_URL/api/v9/comments?topic=reviews/$REVIEW_ID"
```

Display numbered summary of unaddressed comments with: author, file, line, body, taskState.

## Step 3 -- Fix Comments One-by-One

For each unaddressed comment (`taskState` is `comment` or `open`):

1. Show the diff context and comment body
2. Map depot path to local path (strip depot prefix, prepend project root)
3. Read the relevant code section
4. Delegate to the `code-dev` agent via the Agent tool, passing: the comment text, file path, line number, and surrounding code context. The agent proposes a fix.
5. Present the proposed fix. **Auto-apply** if comment is by current P4USER; **ask approval** if by someone else.
6. On approval: `p4 edit <file>`, apply fix with Edit tool
7. **Reply** via v11 API (threaded):
   ```bash
   curl -s -u "$P4USER:$P4TICKET" -X POST \
     "$SWARM_URL/api/v11/comments/reviews/$REVIEW_ID" \
     -H "Content-Type: application/json" \
     -d '{"body":"[ClaudeCode] Comment Addressed","context":{"comment":COMMENT_ID}}'
   ```
8. **Mark addressed** -- two PATCH calls (`comment` -> `open` -> `addressed`)
9. **Archive** the comment

## Step 4 -- Re-Shelve

If any files were modified:

```bash
p4 shelve -f -c $CL
```

Report: fixed count, skipped count, modified files, Swarm review URL.

## Rules

- Never run `p4 submit`
- Always reply to comments before marking addressed
- Task state transitions: `comment` -> `open` -> `addressed` (cannot skip)
