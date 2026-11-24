# Tech Stack Guide: FastAPI

Used by `/kc-generate-agents-md` when a FastAPI project is detected, and by `/kc-create-project fastapi` to scaffold a new one.

---

## Detection Pattern

**Files:** `pyproject.toml` or `requirements*.txt` containing `fastapi`, or a `FastAPI(` call in `main.py` / `api/main.py` / `app/main.py`.

When detected, this guide is loaded and the user is asked all questions below (optional to skip any).

---

## Create Project

Read by `/kc-create-project`. Values are literal; `<target>` is the project directory.

- **Init command:** none (FastAPI has no official scaffolder; the template repo is the whole project)
- **Template repo:** `https://github.com/Kahncode/py-fastapi-template.git`
- **Template ref:** `main`
- **Default package manager:** `uv` (the template is built on it: `pyproject.toml` + `uv.lock`)
- **Package manager detection:** run `uv --version`. If missing, install it with `python -m pip install --upgrade uv` (same bootstrap as the template's `scripts/setup_dev_env.sh`) after asking the user.
- **Post-init:** `uv sync`, then `uv run pre-commit install --install-hooks`, then smoke test `uv run python -c "import api.main"`

Notes:

- With no init command, `/kc-create-project` skips the init phase and the template is the first commit.
- The template requires Python 3.14+ (`requires-python`). Check `python --version` before `uv sync`; uv can fetch a matching interpreter.
- The template ships no `AGENTS.md`, so one is generated from `project/AGENTS.md` using the interview answers.
- `uv run pytest` needs PostgreSQL (pytest-postgresql); do not use it as the smoke test.
- After scaffolding, rename the project in `pyproject.toml` (`name`, `description`) and in `tests/config.yaml` (`app_name`).
- The template README still shows `uvicorn src.main:app`; the real entry point is `api.main:app`.

---

## Questions & Mappings

### 1. Project Description

**Question:** What will this API do? (purpose, main resources, consumers)

**Expected Answer:** Free text. Asked by `/kc-create-project` if no description was passed.

**Instructions Mapping:** Project Overview → Description; seeds Key Patterns & Conventions.

### 2. Database

**Question:** Which database? (PostgreSQL via SQLAlchemy/asyncpg, none, other)

**Auto-detection:** `sqlalchemy`, `asyncpg`, `alembic` in `pyproject.toml`; `SQLDatabaseService` in config YAML.

**Instructions Mapping:** Tech Stack Details → `Database` row; Project-Specific Rules (async sessions, migrations location).

### 3. Authentication

**Question:** How is the API authenticated? (none, bearer/JWT, API key, GCP identity, external provider)

**Auto-detection:** `api/core/auth.py`, `fastapi.security` imports, `google-auth` dependency.

**Instructions Mapping:** Tech Stack Details → `Auth` row; Project-Specific Rules (every non-public route depends on the auth dependency).

### 4. File Storage

**Question:** Do you need file storage? (none, local, GCS, S3, SFTP)

**Auto-detection:** `*FileStorageService` entries under `services:` in `api/config/*.yaml`; `aioboto3`, `google-cloud-storage`, `paramiko`.

**Instructions Mapping:** Tech Stack Details → `Storage` row; Key Patterns (use the shared storage service interface, never call SDKs directly in routes).

### 5. Deployment Target

**Question:** Where will it run? (Cloud Run, Docker/Kubernetes, VM, other)

**Auto-detection:** `api/Dockerfile`, `.github/workflows/build-and-push*.yaml`, `gcp_logging.py`.

**Instructions Mapping:** Tech Stack Details → `Hosting` row; Critical Rule 1 (never auto-deploy) names the target and environments (local, dev, staging, prod).

### 6. Environments & Configuration

**Question:** Which environments exist, and what secrets/settings does each need? (names only, never values)

**Auto-detection:** `api/config/config.{local,dev,staging,prod}.yaml`, `app_environment`.

**Instructions Mapping:** Service Ports & Configuration; Project-Specific Rules (config is YAML plus pydantic-settings; secrets never in YAML).

### 7. Python & Tooling

**Question:** Python version and tooling? (uv, Black, Ruff, pre-commit, detect-secrets)

**Auto-detection:** `requires-python`, `[tool.ruff]`, `[tool.black]`, `.pre-commit-config.yaml`.

**Instructions Mapping:** Development Commands (`uv sync`, `uv run ruff check`, `uv run black .`, `uv run pytest`); Code Style table (line length 120, Ruff `ALL` rules).

### 8. Testing

**Question:** Testing approach? (pytest + pytest-asyncio, database-backed integration tests, CI)

**Auto-detection:** `tests/`, `conftest.py`, `.github/workflows/pytest.yaml`.

**Instructions Mapping:** Development Commands → test rows; Key Patterns (use `tests/utils/` helpers; integration tests need PostgreSQL).

### 9. API Versioning & Structure

**Question:** API versioning and layout? (`/v1` routers, shared library vs app code)

**Auto-detection:** `api/v1/`, `shared/` package, `include_router` calls in `api/main.py`.

**Instructions Mapping:** Project Structure; Key Patterns (routers registered via `include_router`, reusable code goes in `shared/`, app-specific code in `api/`).
