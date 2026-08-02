"""create initial schema

Revision ID: 65110727b95d
Revises: 
Create Date: 2026-03-15 19:48:09.849524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65110727b95d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id          SERIAL PRIMARY KEY,
            spotify_id  VARCHAR(50) UNIQUE,
            title       VARCHAR(500) NOT NULL,
            artist      VARCHAR(500) NOT NULL,
            duration_ms INTEGER,
            source      VARCHAR(50) NOT NULL DEFAULT 'unknown',
            created_at  TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS playlist_sources (
            id              SERIAL PRIMARY KEY,
            spotify_url     VARCHAR(500) NOT NULL UNIQUE,
            name            VARCHAR(500),
            last_checked_at TIMESTAMP,
            created_at      TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id                  SERIAL PRIMARY KEY,
            track_id            INTEGER NOT NULL REFERENCES tracks(id),
            source_playlist_id  INTEGER REFERENCES playlist_sources(id),
            added_at            TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS listening_history (
            id          SERIAL PRIMARY KEY,
            track_id    INTEGER NOT NULL REFERENCES tracks(id),
            played_at   TIMESTAMP NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS listening_history")
    op.execute("DROP TABLE IF EXISTS queue")
    op.execute("DROP TABLE IF EXISTS playlist_sources")
    op.execute("DROP TABLE IF EXISTS tracks")
