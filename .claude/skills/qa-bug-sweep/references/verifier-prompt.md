# Verifier prompt (one per batch with findings)

Send this as a `code-reviewer` agent prompt.

---

A reviewer found the bugs below in CLs submitted to {{P4_STREAM}} between
{since} and {until}. Your job is to **disprove** each one. Reviewers
over-report, and every false bug sent to QA costs the team trust in this list.

{paste the BUG blocks}

Every CL in the window, so you can check whether a later CL already fixed it:
{one line each: "<n> <user> <first line of description>"}

For each bug, read the diff (`p4 describe -du <CL>`) and the real source around
`Where`, then try to break the claim:
- Is it guarded somewhere the reviewer didn't look (caller, `IsValid` upstream,
  authority check, BP-side check)?
- Does that path actually run in a client or dedicated-server build, or only in
  editor, tests, or a cheat?
- Is it already fixed by a later CL in the window?
- Can a player really see it? Would the repro steps get there?
- Is the severity honest?

Return one line per bug:

```
<id>: confirmed | likely | rejected — <reason ≤20 words>   [severity: <keep or new>]
```

`confirmed` means you traced the path end to end. `likely` means it's plausible
and you found no guard, but you couldn't trace everything. `rejected` means you
found the guard or reason. If the repro steps are wrong but the bug is real, give
corrected steps under the line.
