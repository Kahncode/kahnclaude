# Tech Stack Guide: Next.js

Used by `/kc:generate-claude-md` when a Next.js project is detected, and by `/kc:create-project nextjs` to scaffold a new one.

---

## Detection Pattern

**Files:** `next.config.js` / `next.config.mjs` / `next.config.ts` (root) or `next` in `package.json` dependencies.

When detected, this guide is loaded and the user is asked all questions below (optional to skip any).

---

## Create Project

Read by `/kc:create-project`. Values are literal; `<target>` is the project directory.

- **Init command:** `npx create-next-app@latest <target> --ts --app --src-dir --tailwind --eslint --import-alias "@/*" --use-<pm> --skip-install --disable-git --yes`
- **Template repo:** `https://github.com/kahncode/nextjs-template` (placeholder until the repo exists)
- **Template ref:** `main`
- **Default package manager:** `npm` (the Node default; offer only managers detected on PATH, never assume pnpm)
- **Post-init:** `<pm> install`, then `<pm> run build` as a smoke test

Notes:

- Flags were checked against the `create-next-app` reference. The user's answers (TypeScript, Tailwind, `src/`, linter) replace the corresponding flags; `--no-tailwind`, `--no-src-dir`, `--biome` or `--no-eslint` are the negations.
- `--yes` uses defaults for anything not given. Recent versions also add `AGENTS.md`; pass `--no-agents-md` since KahnClaude generates `CLAUDE.md`.
- The template repo is a normal functional Next.js project. Its files overwrite the init output.

---

## Questions & Mappings

### 1. Project Description

**Question:** What will this app contain? (purpose, main screens, users)

**Expected Answer:** Free text. Asked by `/kc:create-project` if no description was passed.

**CLAUDE.md Mapping:** Project Overview → Description; seeds Key Patterns & Conventions.

**Rationale:** Drives every later suggestion (data layer, auth, rendering strategy).

### 2. Router & Rendering

**Question:** App Router or Pages Router? Mostly server components, static, or heavily client-side?

**Auto-detection:** `app/` vs `pages/` (or under `src/`); `next` version in `package.json`.

**CLAUDE.md Mapping:** Tech Stack Details → `Router` row; Project-Specific Rules (server vs client component rules, `"use client"` boundaries).

### 3. Data & Backend

**Question:** Data layer? (none, Postgres/Prisma/Drizzle, Supabase, external API, CMS)

**Auto-detection:** `prisma/`, `drizzle.config.*`, `@supabase/*`, ORM dependencies.

**CLAUDE.md Mapping:** Tech Stack Details → `Database` row; Key Patterns (where queries live, server actions vs route handlers).

### 4. Authentication

**Question:** Authentication needed? (none, Auth.js, Supabase Auth, Clerk, custom)

**Auto-detection:** `next-auth`, `@clerk/*`, `@supabase/ssr` in dependencies.

**CLAUDE.md Mapping:** Tech Stack Details → `Auth` row; Project-Specific Rules (protect routes in middleware/proxy and server actions).

### 5. Styling & UI

**Question:** Styling and component library? (Tailwind, shadcn/ui, CSS modules, other)

**Auto-detection:** `tailwindcss`, `components.json` (shadcn), `*.module.css`.

**CLAUDE.md Mapping:** Code Style → styling row.

### 6. Deployment Target

**Question:** Where will it be deployed? (Vercel, Docker/Node server, static export, Cloudflare, other)

**Auto-detection:** `vercel.json`, `Dockerfile`, `output` in `next.config.*`.

**CLAUDE.md Mapping:** Tech Stack Details → `Hosting` row; Critical Rule 1 (never auto-deploy) names the target.

### 7. Package Manager & Node Version

**Question:** Package manager and Node version?

**Auto-detection:** lockfile, `engines`, `.nvmrc`.

**CLAUDE.md Mapping:** Development Commands (all rows) and Prerequisites.

### 8. Testing & Quality

**Question:** Testing and checks? (Vitest/Jest, Playwright, ESLint/Biome, Prettier, `tsc`)

**Auto-detection:** devDependencies and `package.json` scripts.

**CLAUDE.md Mapping:** Development Commands → test/lint/format/type-check rows; Code Style table.

### 9. Environment & Secrets

**Question:** Which environment variables are needed? (names only, never values)

**Auto-detection:** `.env.example`, `process.env.*` usage.

**CLAUDE.md Mapping:** Service Ports & Configuration → env var column; reinforces Critical Rule 0.
