---
description: Display or create system architecture documentation
scope: project
---

# System Architecture

Display and maintain the current system architecture.

## Instructions

1. Read `docs/ARCHITECTURE.md` (if it exists)
2. Read `docs/INFRASTRUCTURE.md` (if it exists)
3. Display the architecture overview, data flow, and component map

## If Documentation Exists

Display:

- System overview diagram
- Service/component responsibility table
- Data flow description
- Technology choices and rationale

## If Documentation Doesn't Exist Yet

Create `docs/ARCHITECTURE.md` with:

1. **System Overview** — Mermaid diagram showing components and connections
2. **Component Responsibilities** — "Does / Does NOT" table for each service
3. **Data Flow** — how data moves through the system
4. **Technology Choices** — what was chosen and WHY (this is the most valuable part)

Use `/diagram architecture` to auto-generate the overview from code, then fill in the rationale manually.

## Architecture Doc Standards

Good architecture documentation is AUTHORITATIVE:

- States what the system IS, not what it might be
- Uses "Does / Does NOT" tables to prevent scope creep
- Includes "If you are about to [X], STOP — [reason]" warnings for common mistakes
- Documents the non-obvious: why MongoDB instead of Postgres, why a monolith instead of microservices

Template for a "Does / Does NOT" table:

```markdown
## API Service — Does / Does NOT

| Does                 | Does NOT                     |
| -------------------- | ---------------------------- |
| Handle HTTP requests | Access the database directly |
| Validate input       | Contain business logic       |
| Call service layer   | Make external HTTP calls     |
```
