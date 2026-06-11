from __future__ import annotations

import json
from contextlib import contextmanager
from os import environ
from typing import Iterator

try:
    import psycopg
except ImportError:  # Allows model tests without the database dependency.
    psycopg = None


class PredictionRepository:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or environ.get("PREDICTOR_DATABASE_URL")

    @contextmanager
    def _connection(self) -> Iterator:
        if not self.database_url or psycopg is None:
            raise RuntimeError("PostgreSQL is not configured; set PREDICTOR_DATABASE_URL and install psycopg")
        with psycopg.connect(self.database_url) as connection:
            yield connection

    def publish(self, prediction_id: str, payload: dict, model_version: str, data_version: str) -> None:
        """Atomically upsert a published prediction; reruns are idempotent."""
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into predictions (id, match_id, model_version, data_version, payload, published, published_at)
                    values (%s, %s, %s, %s, %s::jsonb, true, now())
                    on conflict (id) do update set
                      model_version = excluded.model_version,
                      data_version = excluded.data_version,
                      payload = excluded.payload,
                      published = true,
                      published_at = now()
                    """,
                    (prediction_id, payload["id"], model_version, data_version, json.dumps(payload, ensure_ascii=False)),
                )

    def start_run(self, source: str) -> int:
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "insert into data_runs (source, status) values (%s, 'running') returning id",
                    (source,),
                )
                return cursor.fetchone()[0]

    def finish_run(self, run_id: int, status: str, details: dict) -> None:
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "update data_runs set status = %s, details = %s::jsonb, finished_at = now() where id = %s",
                    (status, json.dumps(details, ensure_ascii=False), run_id),
                )
