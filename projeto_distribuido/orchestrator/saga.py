import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DB_PATH = Path(__file__).with_name("saga_log.db")


class SagaCoordinator:
    """Coordinates the local orchestration saga and stores its audit trail."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute("PRAGMA journal_mode=MEMORY")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sagas (
                    saga_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_step TEXT,
                    response TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS saga_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    saga_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request_payload TEXT,
                    response_payload TEXT,
                    error TEXT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    FOREIGN KEY (saga_id) REFERENCES sagas (saga_id)
                );

                CREATE TABLE IF NOT EXISTS priority_plans (
                    plan_id TEXT PRIMARY KEY,
                    saga_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    cancelled_at TEXT,
                    cancellation_reason TEXT,
                    FOREIGN KEY (saga_id) REFERENCES sagas (saga_id)
                );

                CREATE TABLE IF NOT EXISTS saga_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    saga_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    compensated_at TEXT,
                    FOREIGN KEY (saga_id) REFERENCES sagas (saga_id)
                );
                """
            )

    def _now(self) -> str:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def _to_json(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, default=str)

    def create_saga(self, query: str, saga_id: Optional[str] = None) -> str:
        saga_id = saga_id or str(uuid.uuid4())
        now = self._now()
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT saga_id FROM sagas WHERE saga_id = ?", (saga_id,)
            ).fetchone()
            if existing:
                return saga_id
            conn.execute(
                """
                INSERT INTO sagas (saga_id, query, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (saga_id, query, "STARTED", now, now),
            )
        return saga_id

    def start_step(
        self, saga_id: str, step_name: str, request_payload: Optional[Dict[str, Any]] = None
    ) -> int:
        now = self._now()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO saga_steps (saga_id, step_name, status, request_payload, started_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    saga_id,
                    step_name,
                    "STARTED",
                    self._to_json(request_payload or {}),
                    now,
                ),
            )
            conn.execute(
                """
                UPDATE sagas
                SET status = ?, current_step = ?, updated_at = ?
                WHERE saga_id = ?
                """,
                ("RUNNING", step_name, now, saga_id),
            )
            return int(cursor.lastrowid)

    def complete_step(self, step_id: int, response_payload: Optional[Dict[str, Any]] = None) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE saga_steps
                SET status = ?, response_payload = ?, finished_at = ?
                WHERE id = ?
                """,
                ("COMPLETED", self._to_json(response_payload or {}), now, step_id),
            )
            saga_id = conn.execute(
                "SELECT saga_id FROM saga_steps WHERE id = ?", (step_id,)
            ).fetchone()["saga_id"]
            conn.execute(
                "UPDATE sagas SET updated_at = ? WHERE saga_id = ?",
                (now, saga_id),
            )

    def fail_step(self, step_id: int, error: str) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE saga_steps
                SET status = ?, error = ?, finished_at = ?
                WHERE id = ?
                """,
                ("FAILED", error, now, step_id),
            )
            saga_id = conn.execute(
                "SELECT saga_id FROM saga_steps WHERE id = ?", (step_id,)
            ).fetchone()["saga_id"]
            conn.execute(
                """
                UPDATE sagas
                SET status = ?, error = ?, updated_at = ?
                WHERE saga_id = ?
                """,
                ("FAILED", error, now, saga_id),
            )

    def mark_completed(self, saga_id: str, response: str) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sagas
                SET status = ?, response = ?, updated_at = ?, completed_at = ?
                WHERE saga_id = ?
                """,
                ("COMPLETED", response, now, now, saga_id),
            )

    def mark_rejected(self, saga_id: str, response: str) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sagas
                SET status = ?, response = ?, updated_at = ?, completed_at = ?
                WHERE saga_id = ?
                """,
                ("REJECTED", response, now, now, saga_id),
            )

    def mark_failed(self, saga_id: str, error: str) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sagas
                SET status = ?, error = ?, updated_at = ?
                WHERE saga_id = ?
                """,
                ("FAILED", error, now, saga_id),
            )

    def create_priority_plan(self, saga_id: str, query: str) -> str:
        plan_id = str(uuid.uuid4())
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO priority_plans (plan_id, saga_id, query, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (plan_id, saga_id, query, "PENDING", now, now),
            )
            conn.execute(
                """
                INSERT INTO saga_resources
                    (saga_id, resource_type, resource_id, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (saga_id, "priority_plan", plan_id, "CREATED", now),
            )
        return plan_id

    def register_resource(self, saga_id: str, resource_type: str, resource_id: str) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO saga_resources
                    (saga_id, resource_type, resource_id, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (saga_id, resource_type, resource_id, "CREATED", now),
            )

    def mark_resource_compensated(
        self, saga_id: str, resource_type: str, resource_id: str
    ) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE saga_resources
                SET status = ?, compensated_at = ?
                WHERE saga_id = ? AND resource_type = ? AND resource_id = ?
                """,
                ("COMPENSATED", now, saga_id, resource_type, resource_id),
            )

    def activate_priority_plan(self, plan_id: str, response: str) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE priority_plans
                SET status = ?, response = ?, updated_at = ?
                WHERE plan_id = ?
                """,
                ("ACTIVE", response, now, plan_id),
            )

    def cancel_priority_plan(self, plan_id: str, reason: str) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE priority_plans
                SET status = ?, updated_at = ?, cancelled_at = ?, cancellation_reason = ?
                WHERE plan_id = ? AND status != ?
                """,
                ("CANCELLED", now, now, reason, plan_id, "CANCELLED"),
            )
            conn.execute(
                """
                UPDATE saga_resources
                SET status = ?, compensated_at = ?
                WHERE resource_type = ? AND resource_id = ?
                """,
                ("COMPENSATED", now, "priority_plan", plan_id),
            )

    async def compensate(
        self,
        saga_id: str,
        resources: Iterable[Dict[str, Any]],
        reason: str,
        client: Any,
        headers: Dict[str, str],
    ) -> None:
        resources_to_compensate = list(resources)
        step_id = self.start_step(
            saga_id,
            "COMPENSATE",
            {"reason": reason, "resources": resources_to_compensate},
        )
        errors: List[str] = []
        for resource in reversed(resources_to_compensate):
            resource_type = resource.get("type")
            resource_id = resource.get("id")
            try:
                if resource_type == "priority_plan" and resource_id:
                    self.cancel_priority_plan(resource_id, reason)
                    self.mark_resource_compensated(saga_id, resource_type, resource_id)
                elif resource_type == "google_task" and resource_id:
                    response = await client.delete(
                        f"http://127.0.0.1:8002/tasks/{resource_id}",
                        headers=headers,
                    )
                    response.raise_for_status()
                    self.mark_resource_compensated(saga_id, resource_type, resource_id)
                elif resource_type == "google_calendar_event" and resource_id:
                    response = await client.delete(
                        f"http://127.0.0.1:8002/calendar/events/{resource_id}",
                        headers=headers,
                    )
                    response.raise_for_status()
                    self.mark_resource_compensated(saga_id, resource_type, resource_id)
            except Exception as exc:
                errors.append(f"{resource_type}:{resource_id}: {exc}")

        if errors:
            error_text = "; ".join(errors)
            self.fail_step(step_id, error_text)
            raise RuntimeError(error_text)

        self.complete_step(step_id, {"compensated": True})

    def get_saga(self, saga_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            saga = conn.execute(
                "SELECT * FROM sagas WHERE saga_id = ?", (saga_id,)
            ).fetchone()
            if saga is None:
                return None
            steps = conn.execute(
                """
                SELECT * FROM saga_steps
                WHERE saga_id = ?
                ORDER BY id
                """,
                (saga_id,),
            ).fetchall()
            plans = conn.execute(
                """
                SELECT * FROM priority_plans
                WHERE saga_id = ?
                ORDER BY created_at
                """,
                (saga_id,),
            ).fetchall()
            resources = conn.execute(
                """
                SELECT * FROM saga_resources
                WHERE saga_id = ?
                ORDER BY id
                """,
                (saga_id,),
            ).fetchall()
            return {
                "saga": dict(saga),
                "steps": [dict(step) for step in steps],
                "priority_plans": [dict(plan) for plan in plans],
                "resources": [dict(resource) for resource in resources],
            }
