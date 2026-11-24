---
name: create-project
description: Create a new project from a stack template (astro, nextjs, fastapi) - init CLI, template overlay, targeted interview during KahnClaude install, and a tailored CLAUDE.md
scope: framework
argument-hint: <stack> <target-path> [description]
---

# /kc:create-project

Create a new project: official init CLI, then the template repo overlay, then an interview limited to what the template leaves open (run during the KahnClaude install), a generated `CLAUDE.md`, and an updated `README.md`. Each phase is its own git commit so the overlay and install diffs stay reviewable.

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

2. **Load the stack guide**: read `project/tech-stacks/<stack>.md`. Parse the `## Create Project` section: init command per package manager, template repo, template ref, default package manager, post-init steps. Ask nothing yet.

3. **Run the init command** (skip entirely if the guide says `Init command: none`; then step 4 is the first commit).
   - Use the guide's default package manager (check `<pm> --version`; if missing, follow the guide's `Package manager detection` bullet or pick the first installed manager the guide lists; never assume one it does not name).
   - Run the guide's init command for that manager with its literal flags. Always skip install and git. The template overwrites the result, so do not tailor flags to preferences.
   - If the init refuses the directory because of `.git/`, run it in a temp sibling directory and move the contents into `<target>`.
   - Commit: `chore: initial <stack> scaffold`.

4. **Apply the template repo**:
   ```
   python <kahnclaude>/scripts/apply_template.py <template-repo> <template-ref> <target>
   ```
   - Template files overwrite init output (including `package.json`). Show the user the `OVERWROTE` and `ADDED` lists.
   - If the template repo is unreachable (placeholder URL, no network), report it and ask: continue with the init output only (the interview then runs in full), or abort. Do not fail silently.
   - Commit: `chore: apply <stack> template`.

5. **Interview and install KahnClaude** (critical step; the interview happens here, not earlier).
   - **Resolve from the files first**: for each question in the guide's `## Questions & Mappings`, apply its `Auto-detection` rule to `<target>` (config, manifests, lockfiles, `.nvmrc`, `engines`, scripts). A detected answer is final: do not ask it. Print a short "Resolved by template" list (question: value).
   - Description: use the argument, otherwise ask "What will this project contain? (purpose, main features, users)". Do not continue without one.
   - Ask only the remaining questions (all optional; skip those the description already answers). Use `AskUserQuestion` (max 4 options per question) where choices are discrete. Do not ask questions whose answer would contradict what the template ships.
   - Package manager: the template lockfile wins over the one used for init; if they differ, tell the user and use the lockfile's. Ask for the project name (default: target folder name) and set it in the manifest if the template carries a placeholder.
   - Keep the description and all answers (asked and detected); they are reused in step 7. Never ask the same thing twice.
   - Run `/kc:install <target>`, passing the detected stack so the stack question is not repeated. In its manifest step, add:
     ```json
     "scaffold": { "stack": "<stack>", "template_repo": "<url>", "template_ref": "<ref>" }
     ```
   - Commit: `chore: install KahnClaude`.

6. **Install dependencies and smoke test**: run the guide's post-init steps (install, then build) with the resolved package manager. Report failures; do not hide them. Commit lockfile changes if any (`chore: add lockfile`).

7. **Generate CLAUDE.md**: run `/kc:generate-claude-md <target>` with the description and all answers (asked and template-detected) pre-supplied so it asks nothing already answered.
   - If the template repo shipped a `CLAUDE.md`, treat it as the existing file and run enhance mode (append missing sections, fill project name, description and tech rows from the answers; never overwrite template rules).
   - Otherwise generate from `project/CLAUDE.md` as usual.
   - Commit: `docs: add project CLAUDE.md`.

8. **Update README.md**: the template's `README.md` still describes the template, so rewrite it for this project.
   - Replace the title with the project name and the template blurb with the project description plus a one-line stack summary from the answers.
   - Replace template-usage instructions ("create a repo from this template", "follow the checklist") with project setup: prerequisites (runtime version, package manager from the lockfile) and install steps.
   - Keep sections that stay accurate (commands table, structure); correct any that no longer match `package.json`/`pyproject.toml` scripts. Link to `CLAUDE.md` and `docs/ARCHITECTURE.md` rather than duplicating them.
   - If the template shipped no `README.md` (or only the init stub), generate a short one: title, description, stack, prerequisites, install, commands, links.
   - Show the user a summary of changes; never invent features or URLs not present in the description or answers.
   - Commit: `docs: update README`.

9. **Report**: commit list (`git log --oneline`), files overwritten by the template, what the template resolved vs what was asked, any failed steps, and next steps (`<pm> run dev`, review `CLAUDE.md`).

## Notes

- Never push or create remotes.
- Never commit secrets; verify `.env` is gitignored before the first commit (install adds it, but check when the template has none).
- Created projects are one-shot: `/kc:update` updates Claude components only, not template files.
- If any phase fails, stop, report the failing command and output, and leave the commits made so far in place.
