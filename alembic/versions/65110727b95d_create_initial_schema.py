"""create Spotify listening-history schema

Revision ID: 65110727b95d
Revises: 
Create Date: 2026-03-15 19:48:09.849524

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '65110727b95d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE tracks (
            spotify_id  TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            artist      TEXT NOT NULL,
            duration_ms INTEGER NOT NULL CHECK (duration_ms > 0),
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE listening_events (
            id               BIGSERIAL PRIMARY KEY,
            spotify_track_id TEXT NOT NULL REFERENCES tracks(spotify_id),
            played_at        TIMESTAMPTZ NOT NULL,
            ingested_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (spotify_track_id, played_at)
        )
    """)

    op.execute("CREATE INDEX listening_events_played_at_idx ON listening_events (played_at)")


def downgrade() -> None:
    op.execute("DROP TABLE listening_events")
    op.execute("DROP TABLE tracks")
