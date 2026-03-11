---
name: pr
description: Generate a pull request title and description from the current branch diff, push the branch, and create the PR with gh pr create.
scope: project
---

# Generate PR Description

Create a comprehensive pull request description based on the current branch diff.

## Process

### 1. Gather Context

```bash
# Get current branch name
git branch --show-current

# Find base branch
git remote show origin | grep 'HEAD branch'

# Get all commits on this branch vs base
git log main..HEAD --oneline

# Get the diff summary and full diff
git diff main...HEAD --stat
git diff main...HEAD
```

### 2. Analyze Changes

Categorize the changes:

- **Features**: New functionality
- **Fixes**: Bug fixes
- **Refactors**: Code improvements without behavior change
- **Docs**: Documentation updates
- **Tests**: Test additions/changes
- **Chores**: Dependencies, configs, tooling

### 3. Generate PR Description

Use this format:

```markdown
## Summary

[2-3 sentences describing what this PR does and why]

## Changes

- [Bullet point for each logical change]
- [Group related file changes together]
- [Focus on what changed, not how]

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Refactor (no functional changes)
- [ ] Documentation update

## Testing

[How was this tested? What should reviewers verify?]

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)

[Add screenshots for UI changes]

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged

---

Generated with Claude Code
```

### 4. Determine Title

PR title format: `type(scope): description`

Examples:

- `feat(auth): add OAuth2 login support`
- `fix(api): handle null response from payment service`
- `refactor(db): extract query builder into separate module`

### 5. Create PR

Always create the PR without asking for confirmation. Derive the target repo from the `origin` remote:

```bash
# Get the GitHub repo slug from origin
REPO=$(git remote get-url origin | sed 's|.*github.com[:/]\(.*\)\.git|\1|')

# Push branch if not already on remote
git push -u origin HEAD

# Create PR targeting origin explicitly
gh pr create --repo "$REPO" --title "..." --body "..."
```

Return the PR URL when done.

## Guidelines

- Focus on **why** over **what** (the diff shows what)
- Link to related issues: `Fixes #123` or `Relates to #456`
- Call out breaking changes prominently
- Mention any manual steps required post-merge
- Keep bullet points scannable (one line each)
