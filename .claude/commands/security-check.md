---
description: Scan project for security issues — exposed secrets, missing .gitignore entries, unsafe patterns
scope: project
allowed-tools: Read, Grep, Glob, Bash(git:*), Bash(grep:*)
---

# Security Check

Scan this project for security vulnerabilities.

## Checks to Perform

### 1. Secrets in Code

```bash
# Search tracked files for common secret patterns
git grep -n -E '(api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*["\x27][A-Za-z0-9+/=_-]{8,}' -- ':!*.lock' 2>/dev/null || echo "No secrets found in code"

# Search for AWS access keys
git grep -n 'AKIA[0-9A-Z]\{16\}' 2>/dev/null || echo "No AWS keys found"

# Search for URLs with embedded credentials
git grep -n -E '(https?://[^:]+:[^@]+@)' 2>/dev/null || echo "No credential URLs found"
```

### 2. .gitignore Coverage

Verify these entries exist in `.gitignore`:
- [ ] `.env`
- [ ] `.env.*`
- [ ] `.env.local`
- [ ] `CLAUDE.local.md`
- [ ] `*.log`

Note any stack-specific entries that should also be present (e.g., `node_modules/`, `__pycache__/`, `target/`, `dist/`).

### 3. Sensitive Files Tracked by Git

```bash
for f in .env .env.local .env.production secrets.json credentials.json service-account.json id_rsa .npmrc .pypirc; do
  git ls-files --error-unmatch "$f" 2>/dev/null && echo "WARNING: $f is tracked by git!"
done
echo "Sensitive file check complete."
```

### 4. .env File Verification

- [ ] `.env` exists but is NOT in git
- [ ] `.env.example` exists and IS in git
- [ ] `.env.example` has NO real values (only placeholders like `YOUR_KEY_HERE`)

### 5. Dependency Audit

Detect project type and run the appropriate audit:

```bash
[ -f "package.json" ] && npm audit --production 2>/dev/null | head -20
[ -f "Pipfile" ] || [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] && pip-audit 2>/dev/null | head -20
[ -f "Cargo.toml" ] && cargo audit 2>/dev/null | head -20
[ -f "go.mod" ] && govulncheck ./... 2>/dev/null | head -20
```

If no audit tool is available for the detected stack, note it.

## Output Format

| Check | Status | Details |
|-------|--------|---------|
| Secrets in code | Pass/Fail | ... |
| .gitignore coverage | Pass/Fail | ... |
| Sensitive files tracked | Pass/Fail | ... |
| .env handling | Pass/Fail | ... |
| Dependency audit | Pass/Fail/N/A | ... |

**Overall: PASS / FAIL**

List specific remediation steps for any failures.
