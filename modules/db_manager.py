"""
db_manager.py — Storage layer for SkillPilot AI.

Supports CSV (default) and SQLite backends. Backend is selected via config.json.
All read operations return empty defaults on missing files/records and log a
WARNING rather than raising exceptions. API credentials are never logged.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

# This file lives at  <project_root>/modules/db_manager.py
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent  # one level up from modules/

# ---------------------------------------------------------------------------
# Logging setup — auto-creates logs/ directory
# ---------------------------------------------------------------------------

def _setup_logging() -> logging.Logger:
    log_dir = _PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("skillpilot")
    if not logger.handlers:
        handler = logging.FileHandler(log_dir / "skillpilot.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(module)s | %(message)s",
                              datefmt="%Y-%m-%dT%H:%M:%S")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = _setup_logging()


# ---------------------------------------------------------------------------
# DBManager
# ---------------------------------------------------------------------------

class DBManager:
    """Abstracts all file I/O. Supports 'csv' and 'sqlite' backends."""

    def __init__(self, config_path: str | None = None) -> None:
        # Resolve config path relative to project root if not absolute
        if config_path is None:
            config_path = str(_PROJECT_ROOT / "config.json")
        cfg = self._load_config(config_path)
        self.backend: str = cfg.get("storage_backend", "csv")
        data_dir_str: str = cfg.get("data_dir", "data/")
        sqlite_path_str: str = cfg.get("sqlite_path", "data/skillpilot.db")

        # On Render, /data is a persistent disk mount — use it for writable files.
        # Static seed data (skill_requirements.csv etc.) stays in the project's data/ dir.
        _render_disk = Path("/data")
        if _render_disk.exists() and _render_disk.is_dir():
            self.data_dir = _render_disk
            self.sqlite_path = _render_disk / "skillpilot.db"
        else:
            # Resolve paths relative to project root (local dev)
            self.data_dir = (_PROJECT_ROOT / data_dir_str).resolve()
            self.sqlite_path = (_PROJECT_ROOT / sqlite_path_str).resolve()

        # Static seed data always lives in the project's data/ directory
        self._static_data_dir: Path = (_PROJECT_ROOT / "data").resolve()

        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.backend == "sqlite":
            self._init_sqlite()

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            log.warning("config.json not found — using defaults.")
            return {}
        except json.JSONDecodeError as exc:
            log.error("config.json parse error: %s — using defaults.", exc)
            return {}

    # ------------------------------------------------------------------
    # SQLite initialisation
    # ------------------------------------------------------------------

    def _init_sqlite(self) -> None:
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS profiles (
                    student_id TEXT PRIMARY KEY,
                    full_name TEXT, department TEXT, semester INTEGER,
                    skill_level TEXT, career_path TEXT,
                    learning_goals TEXT, learning_preferences TEXT,
                    created_at TEXT, updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS skill_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT, skill_name TEXT,
                    score REAL, assessed_at TEXT,
                    FOREIGN KEY (student_id) REFERENCES profiles(student_id)
                );
                CREATE TABLE IF NOT EXISTS task_statuses (
                    student_id TEXT, task_id TEXT,
                    completed INTEGER DEFAULT 0,
                    updated_at TEXT,
                    PRIMARY KEY (student_id, task_id),
                    FOREIGN KEY (student_id) REFERENCES profiles(student_id)
                );
            """)
            conn.commit()

    # ------------------------------------------------------------------
    # CSV helpers
    # ------------------------------------------------------------------

    def _csv_path(self, name: str) -> Path:
        return self.data_dir / name

    def _read_csv_from(self, directory: Path, filename: str) -> list[dict]:
        """Read a CSV from a specific directory (used for static seed data)."""
        path = directory / filename
        if not path.exists():
            log.warning("CSV file not found: %s — returning empty list.", path)
            return []
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except Exception as exc:
            log.error("Error reading %s: %s — returning empty list.", path, exc)
            return []

    def _read_csv(self, filename: str) -> list[dict]:
        path = self._csv_path(filename)
        if not path.exists():
            log.warning("CSV file not found: %s — returning empty list.", path)
            return []
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except Exception as exc:
            log.error("Error reading %s: %s — returning empty list.", path, exc)
            return []

    def _write_csv(self, filename: str, rows: list[dict], fieldnames: list[str]) -> None:
        path = self._csv_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as exc:
            log.error("Error writing %s: %s", path, exc)

    # ------------------------------------------------------------------
    # Profile operations
    # ------------------------------------------------------------------

    PROFILE_FIELDS = [
        "student_id", "full_name", "department", "semester",
        "skill_level", "career_path", "learning_goals",
        "learning_preferences", "created_at", "updated_at",
    ]

    def save_profile(self, profile: dict) -> None:
        if self.backend == "sqlite":
            self._sqlite_save_profile(profile)
            return
        rows = self._read_csv("profiles.csv")
        rows = [r for r in rows if r.get("student_id") != profile.get("student_id")]
        rows.append(profile)
        self._write_csv("profiles.csv", rows, self.PROFILE_FIELDS)
        log.info("Profile saved: %s", profile.get("student_id"))

    def load_profile(self, student_id: str) -> dict:
        if self.backend == "sqlite":
            return self._sqlite_load_profile(student_id)
        rows = self._read_csv("profiles.csv")
        for row in rows:
            if row.get("student_id") == student_id:
                return row
        log.warning("Profile not found for student_id: %s", student_id)
        return {}

    def load_all_profiles(self) -> list[dict]:
        if self.backend == "sqlite":
            return self._sqlite_load_all_profiles()
        return self._read_csv("profiles.csv")

    # ------------------------------------------------------------------
    # Score operations
    # ------------------------------------------------------------------

    SCORE_FIELDS = ["student_id", "skill_name", "score", "assessed_at"]

    def save_scores(self, student_id: str, scores: dict, timestamp: str) -> None:
        if self.backend == "sqlite":
            self._sqlite_save_scores(student_id, scores, timestamp)
            return
        rows = self._read_csv("scores.csv")
        rows = [r for r in rows if r.get("student_id") != student_id]
        for skill, score in scores.items():
            rows.append({
                "student_id": student_id,
                "skill_name": skill,
                "score": score,
                "assessed_at": timestamp,
            })
        self._write_csv("scores.csv", rows, self.SCORE_FIELDS)
        log.info("Scores saved for student: %s", student_id)

    def load_scores(self, student_id: str) -> dict:
        if self.backend == "sqlite":
            return self._sqlite_load_scores(student_id)
        rows = self._read_csv("scores.csv")
        result = {}
        for row in rows:
            if row.get("student_id") == student_id:
                try:
                    result[row["skill_name"]] = float(row["score"])
                except (ValueError, KeyError):
                    pass
        return result

    # ------------------------------------------------------------------
    # Progress operations
    # ------------------------------------------------------------------

    STATUS_FIELDS = ["student_id", "task_id", "completed", "updated_at"]

    def save_task_status(self, student_id: str, task_id: str, completed: bool) -> None:
        if self.backend == "sqlite":
            self._sqlite_save_task_status(student_id, task_id, completed)
            return
        import datetime
        rows = self._read_csv("task_statuses.csv")
        rows = [r for r in rows if not (r.get("student_id") == student_id and r.get("task_id") == task_id)]
        rows.append({
            "student_id": student_id,
            "task_id": task_id,
            "completed": str(completed),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        self._write_csv("task_statuses.csv", rows, self.STATUS_FIELDS)

    def load_task_statuses(self, student_id: str) -> dict[str, bool]:
        if self.backend == "sqlite":
            return self._sqlite_load_task_statuses(student_id)
        rows = self._read_csv("task_statuses.csv")
        result: dict[str, bool] = {}
        for row in rows:
            if row.get("student_id") == student_id:
                raw = row.get("completed", "False")
                result[row["task_id"]] = raw.strip().lower() in ("true", "1", "yes")
        return result

    # ------------------------------------------------------------------
    # Reference data loaders (read-only)
    # ------------------------------------------------------------------

    def load_skill_requirements(self, career_path: str) -> dict[str, float]:
        rows = self._read_csv_from(self._static_data_dir, "skill_requirements.csv")
        result: dict[str, float] = {}
        for row in rows:
            if row.get("career_path", "").strip().lower() == career_path.strip().lower():
                try:
                    result[row["skill_name"]] = float(row["target_score"])
                except (ValueError, KeyError):
                    pass
        if not result:
            log.warning("No skill requirements found for career path: %s", career_path)
        return result

    def load_learning_resources(self) -> list[dict]:
        return self._read_csv_from(self._static_data_dir, "learning_resources.csv")

    def load_sample_students(self) -> list[dict]:
        return self._read_csv_from(self._static_data_dir, "sample_students.csv")

    def load_projects(self) -> list[dict]:
        path = self._static_data_dir / "projects.json"
        if not path.exists():
            log.warning("projects.json not found — returning empty list.")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            log.error("Error reading projects.json: %s", exc)
            return []

    def load_roadmap(self, student_id: str) -> list[dict]:
        path = self.data_dir / "roadmaps.json"
        if not path.exists():
            log.warning("roadmaps.json not found — returning empty list.")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(student_id, [])
        except Exception as exc:
            log.error("Error reading roadmaps.json: %s", exc)
            return []

    def save_roadmap(self, student_id: str, roadmap_data: list[dict]) -> None:
        path = self.data_dir / "roadmaps.json"
        data: dict = {}
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data[student_id] = roadmap_data
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            log.info("Roadmap saved for student: %s", student_id)
        except Exception as exc:
            log.error("Error saving roadmap: %s", exc)

    # ------------------------------------------------------------------
    # SQLite backend implementations
    # ------------------------------------------------------------------

    def _sqlite_save_profile(self, profile: dict) -> None:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO profiles
                (student_id, full_name, department, semester, skill_level,
                 career_path, learning_goals, learning_preferences, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                profile.get("student_id"), profile.get("full_name"),
                profile.get("department"), profile.get("semester"),
                profile.get("skill_level"), profile.get("career_path"),
                profile.get("learning_goals"), profile.get("learning_preferences"),
                profile.get("created_at"), profile.get("updated_at"),
            ))
            conn.commit()
        log.info("Profile saved (SQLite): %s", profile.get("student_id"))

    def _sqlite_load_profile(self, student_id: str) -> dict:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM profiles WHERE student_id = ?", (student_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
            log.warning("Profile not found in SQLite for: %s", student_id)
            return {}

    def _sqlite_load_all_profiles(self) -> list[dict]:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM profiles")
            return [dict(r) for r in cur.fetchall()]

    def _sqlite_save_scores(self, student_id: str, scores: dict, timestamp: str) -> None:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute("DELETE FROM skill_scores WHERE student_id = ?", (student_id,))
            conn.executemany(
                "INSERT INTO skill_scores (student_id, skill_name, score, assessed_at) VALUES (?,?,?,?)",
                [(student_id, skill, score, timestamp) for skill, score in scores.items()]
            )
            conn.commit()
        log.info("Scores saved (SQLite) for student: %s", student_id)

    def _sqlite_load_scores(self, student_id: str) -> dict:
        with sqlite3.connect(self.sqlite_path) as conn:
            cur = conn.execute(
                "SELECT skill_name, score FROM skill_scores WHERE student_id = ?", (student_id,)
            )
            return {row[0]: float(row[1]) for row in cur.fetchall()}

    def _sqlite_save_task_status(self, student_id: str, task_id: str, completed: bool) -> None:
        import datetime
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO task_statuses (student_id, task_id, completed, updated_at)
                VALUES (?, ?, ?, ?)
            """, (student_id, task_id, int(completed), datetime.datetime.now(datetime.timezone.utc).isoformat()))
            conn.commit()

    def _sqlite_load_task_statuses(self, student_id: str) -> dict[str, bool]:
        with sqlite3.connect(self.sqlite_path) as conn:
            cur = conn.execute(
                "SELECT task_id, completed FROM task_statuses WHERE student_id = ?", (student_id,)
            )
            return {row[0]: bool(row[1]) for row in cur.fetchall()}

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def close(self) -> None:
        """No-op — connections are opened per-operation. Safe to call."""
        pass
