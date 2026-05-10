# Reference: Swarm Comment Workflow

Extracted from `helix_swarm.md` for the `swarm-review-comments` skill.

---

## Authentication

Use HTTP Basic Auth with P4 username and cached ticket:

- Ticket file: `%USERPROFILE%\p4tickets.txt` (Windows) or `~/.p4tickets` (Linux/macOS)
- Format: `<server-ip>:<port>=<username>:<ticket-hex>`
- If `401` error, run `p4 login` to refresh

## Key API Endpoints

| Purpose | Endpoint | Method |
|---------|----------|--------|
| Review details | `/api/v9/reviews/{id}` | GET |
| Review comments | `/api/v9/comments?topic=reviews/{id}` | GET |
| Reviews for a CL | `/api/v9/reviews?change={cl}` | GET |
| Post a comment | `/api/v9/comments` | POST |
| Update comment state | `/api/v9/comments/{id}` | PATCH |

## Fetching Comments

```bash
curl -s -u "$P4USER:$P4TICKET" \
  "$SWARM_URL/api/v9/comments?topic=reviews/$REVIEW_ID"
```

Each comment has: `id`, `user`, `body`, `context.file` (depot path), `context.rightLine` (line number), `context.content` (diff lines), `taskState`.

## Posting a Threaded Reply

Use the **v11 API** -- v9 does NOT support threaded replies:

```bash
curl -s -u "$P4USER:$P4TICKET" -X POST \
  "$SWARM_URL/api/v11/comments/reviews/$REVIEW_ID" \
  -H "Content-Type: application/json" \
  -d '{"body":"[ClaudeCode] Comment Addressed","context":{"comment":PARENT_COMMENT_ID}}'
```

## Task State Transitions

State machine is strict -- cannot skip steps:

```
comment -> open -> addressed -> verified
```

To mark as addressed, always do TWO PATCH calls:

```bash
# Step 1: comment -> open
curl -s -u "$P4USER:$P4TICKET" -X PATCH \
  "$SWARM_URL/api/v9/comments/COMMENT_ID" -d "taskState=open"

# Step 2: open -> addressed
curl -s -u "$P4USER:$P4TICKET" -X PATCH \
  "$SWARM_URL/api/v9/comments/COMMENT_ID" -d "taskState=addressed"
```

## Archiving Comments

Collapses the comment in the Swarm UI (replies archived with it):

```bash
curl -s -u "$P4USER:$P4TICKET" -X POST \
  "$SWARM_URL/api/v11/comments/COMMENT_ID/archive"
```

Comments cannot be deleted (`DELETE` returns `405`).

## Auto-Apply Rules

- **Comments by current P4USER**: apply fix directly without asking
- **Comments by anyone else**: show proposed fix, ask for confirmation before applying

## Updating the Review After Fixes

Shelving the same CL updates the associated Swarm review automatically:

```bash
p4 shelve -f -c <CL#>
```

Review URL stays the same: `$SWARM_URL/reviews/<CL#>`
