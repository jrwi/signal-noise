import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from pydantic import BaseModel


class PostgresConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    database: str = "signal_noise"
    user: str = "sn_user"
    password: str = "sn_pass"


class PostgresClient:
    def __init__(self, config: PostgresConfig):
        self.config = config
        self._connection = None

    def connect(self):
        self._connection = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            dbname=self.config.database,
            user=self.config.user,
            password=self.config.password
        )

    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    @contextmanager
    def cursor(self):
        if not self._connection:
            self.connect()
        with self._connection.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
            self._connection.commit()

    def execute(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)

    def fetch_one(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def fetch_all(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def upsert_track(self, spotify_id, title, artist, duration_ms, source):
        sql = """
            INSERT INTO tracks (spotify_id, title, artist, duration_ms, source)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (spotify_id) DO UPDATE SET
                title = EXCLUDED.title,
                artist = EXCLUDED.artist,
                duration_ms = EXCLUDED.duration_ms
            RETURNING id
        """
        result = self.fetch_one(sql, params=(spotify_id, title, artist, duration_ms, source))
        return result['id']
