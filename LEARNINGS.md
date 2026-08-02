# Signal:Noise Learnings

This file records concepts we have already learned while creating the project's lean foundation.

## Docker Compose and containers

A **container** is one isolated running process with its software and filesystem packaged together. Our PostgreSQL database runs in a container.

**Docker Compose** is the tool that reads `docker-compose.yml` and manages one or more related containers as a project. The file describes the desired setup; Compose creates and starts it consistently.

## Host and container ports

This Compose mapping exposes PostgreSQL to programs running on the Mac:

```yaml
ports:
  - "5432:5432"
```

The left `5432` is the port on the **host** machine. The right `5432` is the port inside the container. Traffic sent to the Mac's port 5432 is forwarded to PostgreSQL's port 5432 in the container.

## Named volumes

A container can be replaced, so important data should not live only inside it. A **named volume** is storage managed by Docker separately from the container.

Our `postgres_data` volume is mounted at PostgreSQL's data directory. This lets database data survive stopping, deleting, or recreating the Postgres container. Deleting the volume is different: that deletes the stored database state.

## PostgreSQL readiness health check

A running container is not necessarily ready to accept database connections. PostgreSQL needs time to initialize.

The Compose health check runs `pg_isready` inside the container. Docker marks the service healthy only after PostgreSQL responds. Its interval, timeout, retries, and start period control how often Docker checks, how long each check may take, how many failures are allowed, and how much startup grace time PostgreSQL receives.

## PostgreSQL initialization variables

The official Postgres image reads `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` when it initializes a **new, empty data volume**.

Changing those values later does not rewrite users, passwords, or databases already stored in an existing volume. That protects persistent data, but it means configuration changes and stored state can differ. To change an existing database, use PostgreSQL commands or intentionally create a new volume when losing the old local data is safe.

## Alembic migrations

An **Alembic migration** is a versioned, ordered database-schema change. It describes how to move the schema forward and, when practical, backward.

Migration history matters because databases evolve over time. Editing or deleting a migration that another database has already recorded as applied makes the code's history disagree with that database. Preserve applied migrations; add a new migration for the next change. This gives every environment the same reproducible path from one schema version to another.

## uv and `uv.lock`

**uv** is the project's Python and dependency manager. It selects Python, creates or updates `.venv`, resolves dependencies from `pyproject.toml`, and runs project commands.

```bash
uv sync
uv run python --version
uv run alembic upgrade head
```

`pyproject.toml` states the dependency requirements we intend to support. `uv.lock` records the exact resolved versions and checksums. Committing both gives other machines the same dependency set.

After an intentional dependency change, regenerate and commit the lockfile. A locked sync verifies that project metadata and the lockfile still agree:

```bash
uv lock
uv sync --locked
```
