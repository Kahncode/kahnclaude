---
name: create-project
description: Create a new project from a stack template (astro, nextjs, fastapi) - interview, official init CLI, template repo overlay, KahnClaude install, and a tailored CLAUDE.md
scope: framework
argument-hint: <stack> <target-path> [description]
---

# /kc:create-project

Create a new project: official init CLI, then a template repo overlay, then KahnClaude install and a generated `CLAUDE.md`. Each phase is its own git commit so the overlay and install diffs stay reviewable.

**Usage:** `/kc:create-project <stack> <target-path> [description]`

- `<stack>` must match a guide in `project/tech-stacks/<stack>.md` that has a `## Create Project` section (currently `astro`, `nextjs`, `fastapi`). If omitted or unknown, list the available stacks and ask.
- `<target-path>` is the new project directory. If omitted, ask.
- `[description]` is what the project will contain. If omitted, ask in step 3.

All guides, templates and scripts are read from the KahnClaude source directory, never copied to the target.

## Steps

1. **Preflight**
   - Run `git --version`. If it fails, abort: "git is required."
   - Resolve `<target>`. If it exists and is non-empty (ignoring `.git/`), stop and ask the user; never overwrite without confirmation.
   - If `<target>` is not a git repo, create the directory if needed and run `git init`.

2. **Load the stack guide**: read `project/tech-stacks/<stack>.md`. Parse the `## Create Project` section: init command per package manager, template repo, template ref, default package manager, post-init steps.

3. **Interview the user (critical step)**. Do this before touching any files.
   - Description: use the argument, otherwise ask "What will this project contain? (purpose, main features, users)". Do not continue without one.
   - Ask every question in the guide's `## Questions & Mappings` (all optional; skip those the description already answers). Use `AskUserQuestion` (max 4 options per question) where choices are discrete.
   - Detect which package managers are installed by running `<pm> --version` for the ones the guide lists (for Node: npm, pnpm, yarn, bun). Offer only the detected ones. The default is the guide's `Default package manager` (npm for Node stacks); never assume pnpm or any other manager the guide does not name. Follow the guide's `Package manager detection` bullet if present (for example uv).
   - Ask for the project name (default: target folder name).
   - Keep the description and all answers; they are reused in step 8. Never ask the same thing twice.

4. **Run the init command** from the guide for the chosen package manager. If the guide says `Init command: none`, skip this step entirely (no init commit); the template overlay in step 5 is then the first commit. Apply the user's answers by adjusting flags (for example Tailwind, `src/`, linter in Next.js). Always skip install and git inside the init.
   - If the init refuses the directory because of `.git/`, run it in a temp sibling directory and move the contents into `<target>`.
   - Commit: `chore: initial <stack> scaffold`.

5. **Apply the template repo**:
   ```
   python <kahnclaude>/scripts/apply_template.py <template-repo> <template-ref> <target>
   ```
   - Template files overwrite init output (including `package.json`). Show the user the `OVERWROTE` and `ADDED` lists.
   - If the template repo is unreachable (placeholder URL, no network), report it and ask: skip the overlay, or abort. Do not fail silently.
   - Commit: `chore: apply <stack> template`.

6. **Install KahnClaude**: run `/kc:install <target>`, passing the detected stack, so the stack question is not repeated. In its manifest step, add:
   ```json
   "scaffold": { "stack": "<stack>", "template_repo": "<url>", "template_ref": "<ref>" }
   ```
   Commit: `chore: install KahnClaude`.

7. **Install dependencies and smoke test**: run the guide's post-init steps (install, then build). Report failures; do not hide them. Commit lockfile changes if any (`chore: add lockfile`).

8. **Generate CLAUDE.md**: run `/kc:generate-claude-md <target>` with the description and all interview answers pre-supplied so it asks nothing already answered.
   - If the template repo shipped a `CLAUDE.md`, treat it as the existing file and run enhance mode (append missing sections, fill project name, description and tech rows from the answers; never overwrite template rules).
   - Otherwise generate from `project/CLAUDE.md` as usual.
   - Commit: `docs: add project CLAUDE.md`.

9. **Report**: commit list (`git log --oneline`), files overwritten by the template, any failed steps, and next steps (`<pm> run dev`, review `CLAUDE.md`).

## Notes

- Never push or create remotes.
- Never commit secrets; verify `.env` is gitignored before the first commit (install adds it, but check when the init created none).
- Created projects are one-shot: `/kc:update` updates Claude components only, not template files.
- If any phase fails, stop, report the failing command and output, and leave the commits made so far in place.
