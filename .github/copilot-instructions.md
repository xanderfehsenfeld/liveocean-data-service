Purpose

Short reference for Copilot sessions working on this repository: build/run/test commands, high-level architecture, and repo-specific conventions.

Quick commands

- Install dependencies (project uses "uv"):
  - uv sync
- Database (Postgres + PostGIS):
  - Start DB (if using docker-compose per README): docker compose up
- Run local server:
  - uv run --env-file=.env python manage.py runserver
- Migrations and DB tasks:
  - uv run --env-file=.env python manage.py migrate
  - Create superuser: uv run --env-file=.env python manage.py createsuperuser
- Load provided world shapefile into DB:
  - uv run --env-file=.env python manage.py shell
    then inside the shell: from world.load import run; run()
- Tests (Django test runner):
  - Run full test suite: uv run --env-file=.env python manage.py test
  - Run a single test: uv run --env-file=.env python manage.py test <module.Class.test_method>
    Example: uv run --env-file=.env python manage.py test world.tests.MyTestCase.test_something

Notes about commands

- The project uses the "uv" wrapper to run commands and manage the virtualenv; commands above follow README examples.

CI examples (GitHub Actions)

- Minimal CI that installs dependencies, brings up a PostGIS service, runs migrations, and executes tests:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:15-3.3
        ports: ['5432:5432']
        env:
          POSTGRES_USER: admin
          POSTGRES_PASSWORD: password
          POSTGRES_DB: pg4django
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install .
      - name: Wait for Postgres
        run: |
          until pg_isready -h localhost -p 5432; do sleep 1; done
      - name: Run migrations
        env:
          PG_DB_NAME: pg4django
          PG_USER: admin
          PG_PSWD: password
          PG_HOST_DEV: 127.0.0.1
          PG_PORT: 5432
        run: python manage.py migrate --noinput
      - name: Run tests
        env:
          PG_DB_NAME: pg4django
          PG_USER: admin
          PG_PSWD: password
          PG_HOST_DEV: 127.0.0.1
          PG_PORT: 5432
        run: python manage.py test
```

- Example lint workflow (add if you enable tooling like flake8/black):

```yaml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - name: Install linters
        run: |
          python -m pip install --upgrade pip
          pip install flake8 black
      - name: Run flake8
        run: flake8 .
      - name: Check black
        run: black --check .
```

Notes for CI

- The workflows assume a PostGIS service container; adjust image/tag and env vars to match your production DB settings and secrets (use GitHub Secrets for passwords).
- If you prefer using the repo's "uv" wrapper in CI, replace pip install steps with `pip install uv` and run `uv sync` before invoking manage.py commands.
- Add caching for pip and test artifacts as needed to speed up runs.

High-level architecture

- Django project root: liveocean_data_service/
  - settings.py configures GeoDjango ("django.contrib.gis") and PostGIS backend.
- Main app: world/
  - models.py: WorldBorder model with MultiPolygonField (mpoly) storing shapefile geometries.
  - load.py: LayerMapping based import of the provided shapefile (world/data/TM_WORLD_BORDERS-0.3.shp).
  - tests.py: Django TestCase usage (empty placeholder currently).
- Entry point: manage.py (standard Django management commands).
- pyproject.toml sets Python requirement (>=3.14) and lists core deps (django, psycopg2-binary, python-dotenv).

Key conventions and repo-specific patterns

- GeoDjango/PostGIS expectation: DATABASES in settings.py use 'django.contrib.gis.db.backends.postgis' and environment variables for credentials.
  - Important env vars (used in settings.py/.env): PG_DB_NAME, PG_USER, PG_PSWD, PG_HOST_DEV, PG_HOST, PG_PORT.
  - settings.py switches host key between PG_HOST_DEV (when DEBUG=True) and PG_HOST (when DEBUG=False).
- Data import: world/load.py uses LayerMapping with explicit field mapping (world_mapping). If updating model fields ensure mapping keys match shapefile attributes.
- Geometry field name: MultiPolygonField is named "mpoly" across model and LayerMapping.
- Use uv to run python/manage.py commands; pass --env-file=.env to load environment variables consistently.

Important files to check when reasoning across the repo

- README.md — setup and run instructions (source for many commands in this file).
- pyproject.toml — Python version and dependency hints.
- liveocean_data_service/settings.py — DB, installed apps, and GeoDjango setup.
- world/load.py & world/models.py — shapefile import logic and model schema.

AI assistant / tooling notes

- No existing .github/copilot-instructions.md was found; this file was created from README and pyproject.toml.
- No other AI assistant config files (CLAUDE.md, AGENTS.md, .cursorrules, etc.) were detected.

If making edits

- Keep changes surgical. If updating model fields, also update world_mapping in world/load.py and any data files.
- Verify DB migrations run cleanly and that LayerMapping import still matches shapefile attribute names.

Contact / further guidance

If additional coverage is desired (CI, linting, or end-to-end testing), say which area to add and Copilot can add recommended configs or workflows.
