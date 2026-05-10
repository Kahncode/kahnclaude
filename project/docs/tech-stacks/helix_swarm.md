# Tech Stack Guide: Helix Swarm

<!-- detection: opt-in | signal: Swarm URL in config or README | prerequisite: helix_perforce -->
<!-- prompt: "Do you use Helix Swarm for code reviews?" -->

---

## Setup — Environment Variables

Store in `CLAUDE.local.md` (never committed).

### Required

> **Tip:** Just paste any Swarm review URL (e.g., `https://swarm.company.com/reviews/12345`) and Claude will auto-extract the base URL.

| Variable | How to Obtain |
|----------|---------------|
| `SWARM_URL` | Paste any Swarm URL — base URL is extracted automatically. Or auto-detected via `p4 property -l -n P4.Swarm.URL`. |

### Authentication

Swarm uses your active Perforce login ticket as the API password. No additional credentials needed if `p4 login` is active.

- **Ticket location:** `%USERPROFILE%\p4tickets.txt` (Windows) or `~/.p4tickets` (Linux/macOS)
- **Ticket format:** `<server-ip>:<port>=<username>:<ticket-hex>`
- If API calls fail with `401`, run `p4 login` to refresh the ticket.

---

## Setup — Auto-Detection

No manual questions required. The Swarm URL is auto-detected; ask only if detection fails.

| Step | Method | CLAUDE.md Section |
|------|--------|-------------------|
| 1. Detect Swarm URL | `p4 property -l -n P4.Swarm.URL` or check Swarm triggers via `p4 triggers -o`. Ask user only if both fail. | Service Ports |

### Defaults (no question needed)

- Workflow: Shelve CL > Swarm auto-creates review > Reviewer approves > Submit
- Comment handling: auto-fix own comments, ask before fixing others', always post reply
- Always reply when addressing comments, never archive others' comments, re-shelve after fixes

---

## Operational Reference — Helix Swarm

### Finding the Swarm Review for a Local CL

When you have a local changelist number `CLXXXX`, the Swarm review ID is typically
the same number (or very close). Confirm via the API:

```bash
curl -s -u "$P4USER:$P4TICKET" \
  "$SWARM_URL/api/v9/reviews?change=CLXXXX"
```

Or navigate directly in a browser:

```
$SWARM_URL/reviews/CLXXXX
```

### Getting the Bearer Token (P4 Ticket)

Swarm uses your active Perforce login ticket as the API password.

#### Option 1 — Read cached ticket (no interaction needed)

The P4 client caches your session ticket after login in:

```
%USERPROFILE%\p4tickets.txt
```

Format of the file:

```
<server-ip>:<port>=<username>:<ticket>
```

Example:

```
192.168.1.100:1666=jdoe:A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4
```

Extract the ticket value (the hex string after the colon following your username).

#### Option 2 — Generate a fresh ticket interactively

Run in a terminal (requires your Perforce password):

```bash
p4 login -p
```

This prints a ticket you can copy directly.

### Making API Calls

Use HTTP Basic Auth with your P4 username and ticket:

```bash
P4USER=<your-p4-username>
P4TICKET=<hex-ticket-from-p4tickets.txt>

# Get review details
curl -s -u "$P4USER:$P4TICKET" \
  "$SWARM_URL/api/v9/reviews/CLXXXX"

# Get comments on a review
curl -s -u "$P4USER:$P4TICKET" \
  "$SWARM_URL/api/v9/comments?topic=reviews/CLXXXX"
```

### Updating a Swarm Review via Shelving

Shelving a changelist automatically updates its associated Swarm review. Reviewers will see the new diff without a new review being created.

```bash
p4 shelve -c <CL>
```

- Use the **same CL number** as the original review — Swarm links reviews to CLs, so shelving the same CL pushes updated files to the existing review.
- Review URL stays the same: `$SWARM_URL/reviews/<CL>`
- If files were already shelved, `p4 shelve -c <CL>` replaces the previous shelf.

### Key API Endpoints

| Purpose              | Endpoint                                              | Method |
|----------------------|-------------------------------------------------------|--------|
| Review details       | `/api/v9/reviews/{id}`                                | GET    |
| Review comments      | `/api/v9/comments?topic=reviews/{id}`                 | GET    |
| Reviews for a CL     | `/api/v9/reviews?change={cl}`                         | GET    |
| Files in a review    | `/api/v9/reviews/{id}/files`                          | GET    |
| Post a comment       | `/api/v9/comments`                                    | POST   |
| Update comment state | `/api/v9/comments/{id}`                               | PATCH  |

### Comment API Details

#### Posting a Review-Level Comment

```bash
curl -s -u "$P4USER:$P4TICKET" -X POST \
  "$SWARM_URL/api/v9/comments" \
  -d "topic=reviews/$REVIEW_ID" \
  -d "body=Your comment text"
```

#### Replying to an Existing Comment (Threaded)

Use the **v11 API** with the topic in the URL path and `context.comment` as the parent ID:

```bash
curl -s -u "$P4USER:$P4TICKET" -X POST \
  "$SWARM_URL/api/v11/comments/reviews/$REVIEW_ID" \
  -H "Content-Type: application/json" \
  -d '{"body":"Reply text","context":{"comment":PARENT_COMMENT_ID}}'
```

- The v9 API does **not** support threaded replies — `context[comment]` on v9 fails with "File path is required".
- The v11 endpoint returns data in `{"error":null,"data":{"comments":[...]}}` format.

#### Changing Comment Task State

```bash
curl -s -u "$P4USER:$P4TICKET" -X PATCH \
  "$SWARM_URL/api/v9/comments/{id}" \
  -d "taskState=open"
```

Valid `taskState` transitions follow a strict state machine:

```
comment -> open -> addressed
                -> verified
open -> addressed -> verified
```

- A comment in `comment` state **cannot** jump directly to `addressed` — it must first transition to `open`, then to `addressed`.
- To mark a comment as addressed, always do two PATCH calls: `open` then `addressed`.

#### Deleting Comments

- `DELETE /api/v9/comments/{id}` returns `405 Method Not Allowed` — comments cannot be deleted via the API.

### Fixing Review Comments — Workflow

When processing Swarm review comments after applying fixes:

1. **Auto-apply rules:**
   - **Comments by the current P4USER**: apply the fix directly without asking for confirmation.
   - **Comments by anyone else**: show the proposed fix and ask for confirmation before applying.

2. **After each addressed comment:**
   - Post a reply on the review: `[ClaudeCode] Comment Addressed`
   - Transition the comment taskState: `comment` -> `open` -> `addressed` (two PATCH calls)
   - Archive the comment: `POST /api/v11/comments/{id}/archive` (collapses it in the UI; replies are archived with it)

### Swarm Notes

- The cached ticket in `p4tickets.txt` may use the server's **IP** rather than its hostname. This is normal — the ticket is still valid for Swarm auth regardless of which form is in the file.
- Tickets expire after your configured P4 ticket timeout. If you get a `401`, run `p4 login` to refresh, then re-read `p4tickets.txt`.

### External Documentation

- **Swarm REST API reference**: https://help.perforce.com/helix-core/helix-swarm/swarm/2025.1/Content/Swarm/swarm-api-endpoint-comments.html
  - Use WebFetch to look up endpoints, parameters, and response formats when the info above is insufficient.
