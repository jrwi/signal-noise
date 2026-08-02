# Signal:Noise

Signal:Noise is a learning-first data pipeline for recording Spotify listening history in PostgreSQL.

## Setup

The project uses [uv](https://docs.astral.sh/uv/) as its only Python and dependency manager. From the repository root:

```bash
uv sync
```

This selects a compatible Python 3.12 interpreter, creates or updates `.venv`, and installs the exact dependency versions recorded in `uv.lock`. Do not install project dependencies with `pip` or manually activate `.venv`.

Keep Spotify credentials in the ignored `.env` file. Never commit secrets.

## Run commands

Run Python and project tools through uv:

```bash
uv run python --version
```

Start the local PostgreSQL database and apply its schema:

```bash
docker compose up -d postgres
uv run alembic upgrade head
```

Stop PostgreSQL without deleting its data:

```bash
docker compose down
```

## Change dependencies

Use uv so `pyproject.toml` and `uv.lock` stay synchronized:

```bash
uv add <package>
uv remove <package>
```

Commit both `pyproject.toml` and `uv.lock` after an intentional dependency change. In CI, use `uv sync --locked` so an outdated lockfile fails instead of changing silently.
