# Tech Stack Guide: Astro

Used by `/kc:generate-claude-md` when an Astro project is detected, and by `/kc:create-project astro` to scaffold a new one.

---

## Detection Pattern

**Files:** `astro.config.mjs` / `astro.config.ts` (root) or `astro` in `package.json` dependencies.

When detected, this guide is loaded and the user is asked all questions below (optional to skip any).

---

## Create Project

Read by `/kc:create-project`. Values are literal; `<target>` is the project directory.

- **Init command (npm):** `npm create astro@latest <target> -- --template minimal --no-install --no-git --yes`
- **Init command (pnpm):** `pnpm create astro@latest <target> --template minimal --no-install --no-git --yes`
- **Init command (yarn):** `yarn create astro <target> --template minimal --no-install --no-git --yes`
- **Template repo:** `https://github.com/kahncode/astro-template` (placeholder until the repo exists)
- **Template ref:** `main`
- **Default package manager:** `npm` (the Node default; offer only managers detected on PATH, never assume pnpm)
- **Post-init:** `<pm> install`, then `<pm> run build` as a smoke test

Notes:

- The init flags were checked against the Astro docs; re-verify with `npm create astro@latest -- --help` if the init fails.
- The `--typescript` flag no longer exists (strict TS is the default since Astro 5).
- The template repo is a normal functional Astro project. Its files overwrite the init output, so init flags need not match user preferences.

---

## Questions & Mappings

### 1. Project Description

**Question:** What will this site contain? (purpose, main pages, content types)

**Expected Answer:** Free text. Asked by `/kc:create-project` if no description was passed.

**CLAUDE.md Mapping:** Project Overview → Description; seeds Key Patterns & Conventions.

**Rationale:** Drives every later suggestion (rendering mode, content model, integrations).

### 2. Rendering Mode

**Question:** Static (SSG), server-rendered (SSR), or hybrid?

**Expected Answer:** `static`, `server`, or hybrid (per-page `prerender`).

**Auto-detection:** `output` in `astro.config.*` and presence of an `adapter`.

**CLAUDE.md Mapping:** Tech Stack Details → `Rendering` row; Project-Specific Rules (adapter, prerender rules).

### 3. Content Source

**Question:** Where does content come from? (Markdown/MDX content collections, headless CMS, database, none)

**Auto-detection:** `src/content/`, `src/content.config.ts`, CMS SDKs in dependencies.

**CLAUDE.md Mapping:** Tech Stack Details → `Content` row; Key Patterns (collection schemas, content location).

### 4. UI Framework Islands

**Question:** Do you need interactive islands? Which framework? (none, React, Svelte, Vue, Solid, Preact)

**Auto-detection:** `@astrojs/*` integrations in `package.json`.

**CLAUDE.md Mapping:** Tech Stack Details → `UI islands` row; Key Patterns (client directive conventions: prefer `client:visible`/`client:idle`).

### 5. Styling

**Question:** Styling approach? (Tailwind, plain CSS/scoped styles, CSS modules, other)

**Auto-detection:** `tailwindcss` / `@tailwindcss/vite` in dependencies.

**CLAUDE.md Mapping:** Code Style → styling row.

### 6. Deployment Target

**Question:** Where will it be deployed? (Netlify, Vercel, Cloudflare, static host, Node server, other)

**Auto-detection:** `@astrojs/{netlify,vercel,cloudflare,node}` adapter.

**CLAUDE.md Mapping:** Tech Stack Details → `Hosting` row; Critical Rule 1 (never auto-deploy) names the target.

### 7. Package Manager & Node Version

**Question:** Package manager and Node version?

**Auto-detection:** lockfile (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`), `engines`, `.nvmrc`.

**CLAUDE.md Mapping:** Development Commands (all rows) and Prerequisites.

### 8. Testing & Quality

**Question:** Testing and checks? (Vitest, Playwright, `astro check`, ESLint, Prettier)

**Auto-detection:** devDependencies and `package.json` scripts.

**CLAUDE.md Mapping:** Development Commands → test/lint/format/type-check rows; Code Style table.

### 9. SEO & Performance

**Question:** SEO needs? (sitemap, RSS, i18n, image optimization)

**Auto-detection:** `@astrojs/sitemap`, `@astrojs/rss`, `i18n` in config.

**CLAUDE.md Mapping:** Project-Specific Rules (use `astro:assets` for images, page metadata conventions).
