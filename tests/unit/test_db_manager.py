"""
Unit tests for modules/db_manager.py

Tests cover:
- CSV backend: save + load profile round-trip, score upsert, task status upsert
- SQLite backend: same operations with a temp SQLite file
- Missing file returns empty default and logs a warning

Requirements: 8.1, 8.2, 8.3, 8.4
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

import pytest

from modules.db_manager import DBManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_db(tmpdir: Path, backend: str = "csv") -> DBManager:
    """Create a DBManager pointing at a temporary directory."""
    cfg = {
        "storage_backend": backend,
        "data_dir": str(tmpdir / "data"),
        "sqlite_path": str(tmpdir / "data" / "test.db"),
    }
    cfg_path = tmpdir / "config.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    return DBManager(config_path=str(cfg_path))


SAMPLE_PROFILE = {
    "student_id": "stu-001",
    "full_name": "Alice Test",
    "department": "Computer Science",
    "semester": "3",
    "skill_level": "Beginner",
    "career_path": "Data Analyst",
    "learning_goals": "Learn Python and SQL",
    "learning_preferences": "Video",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

SAMPLE_SCORES = {
    "Python": 65.0,
    "SQL": 50.0,
    "Excel": 70.0,
}


# ===========================================================================
# CSV Backend Tests
# ===========================================================================

class TestCSVProfileOperations:
    def test_save_and_load_profile_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_profile(SAMPLE_PROFILE)
            loaded = db.load_profile("stu-001")
            assert loaded["full_name"] == "Alice Test"
            assert loaded["department"] == "Computer Science"
            assert loaded["career_path"] == "Data Analyst"

    def test_save_profile_overwrites_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_profile(SAMPLE_PROFILE)
            updated = {**SAMPLE_PROFILE, "full_name": "Alice Updated", "updated_at": "2024-06-01T00:00:00"}
            db.save_profile(updated)
            loaded = db.load_profile("stu-001")
            assert loaded["full_name"] == "Alice Updated"
            # Only one record for this student_id
            all_profiles = db.load_all_profiles()
            matching = [p for p in all_profiles if p["student_id"] == "stu-001"]
            assert len(matching) == 1

    def test_load_profile_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_profile("no-such-student")
            assert result == {}

    def test_load_all_profiles_empty_when_no_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_all_profiles()
            assert result == []

    def test_load_all_profiles_returns_all_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            p2 = {**SAMPLE_PROFILE, "student_id": "stu-002", "full_name": "Bob Test"}
            db.save_profile(SAMPLE_PROFILE)
            db.save_profile(p2)
            all_profiles = db.load_all_profiles()
            assert len(all_profiles) == 2
            ids = {p["student_id"] for p in all_profiles}
            assert ids == {"stu-001", "stu-002"}


class TestCSVScoreOperations:
    def test_save_and_load_scores_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_scores("stu-001", SAMPLE_SCORES, "2024-01-01T00:00:00")
            loaded = db.load_scores("stu-001")
            assert loaded["Python"] == 65.0
            assert loaded["SQL"] == 50.0
            assert loaded["Excel"] == 70.0

    def test_save_scores_replaces_previous(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_scores("stu-001", SAMPLE_SCORES, "2024-01-01T00:00:00")
            new_scores = {"Python": 85.0, "SQL": 90.0, "Excel": 75.0}
            db.save_scores("stu-001", new_scores, "2024-06-01T00:00:00")
            loaded = db.load_scores("stu-001")
            assert loaded["Python"] == 85.0
            assert loaded["SQL"] == 90.0

    def test_load_scores_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_scores("stu-001")
            assert result == {}

    def test_scores_isolated_per_student(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_scores("stu-001", {"Python": 60.0}, "2024-01-01T00:00:00")
            db.save_scores("stu-002", {"Python": 80.0}, "2024-01-01T00:00:00")
            s1 = db.load_scores("stu-001")
            s2 = db.load_scores("stu-002")
            assert s1["Python"] == 60.0
            assert s2["Python"] == 80.0


class TestCSVTaskStatusOperations:
    def test_save_and_load_task_status_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_task_status("stu-001", "task-1", True)
            statuses = db.load_task_statuses("stu-001")
            assert statuses["task-1"] is True

    def test_save_task_status_upsert(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_task_status("stu-001", "task-1", True)
            db.save_task_status("stu-001", "task-1", False)  # overwrite
            statuses = db.load_task_statuses("stu-001")
            assert statuses["task-1"] is False

    def test_load_task_statuses_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_task_statuses("stu-001")
            assert result == {}

    def test_multiple_task_statuses(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_task_status("stu-001", "task-1", True)
            db.save_task_status("stu-001", "task-2", False)
            db.save_task_status("stu-001", "task-3", True)
            statuses = db.load_task_statuses("stu-001")
            assert statuses["task-1"] is True
            assert statuses["task-2"] is False
            assert statuses["task-3"] is True


# ===========================================================================
# SQLite Backend Tests
# ===========================================================================

class TestSQLiteProfileOperations:
    def test_save_and_load_profile_round_trip(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            db.save_profile(SAMPLE_PROFILE)
            loaded = db.load_profile("stu-001")
            assert loaded["full_name"] == "Alice Test"
            assert loaded["career_path"] == "Data Analyst"

    def test_save_profile_overwrites_existing(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            db.save_profile(SAMPLE_PROFILE)
            updated = {**SAMPLE_PROFILE, "full_name": "Alice Updated"}
            db.save_profile(updated)
            loaded = db.load_profile("stu-001")
            assert loaded["full_name"] == "Alice Updated"
            all_profiles = db.load_all_profiles()
            matching = [p for p in all_profiles if p["student_id"] == "stu-001"]
            assert len(matching) == 1

    def test_load_profile_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            result = db.load_profile("no-such-student")
            assert result == {}

    def test_load_all_profiles_empty_initially(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            result = db.load_all_profiles()
            assert result == []


class TestSQLiteScoreOperations:
    def test_save_and_load_scores_round_trip(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            db.save_scores("stu-001", SAMPLE_SCORES, "2024-01-01T00:00:00")
            loaded = db.load_scores("stu-001")
            assert loaded["Python"] == 65.0
            assert loaded["SQL"] == 50.0

    def test_save_scores_replaces_previous(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            db.save_scores("stu-001", SAMPLE_SCORES, "2024-01-01T00:00:00")
            new_scores = {"Python": 95.0, "SQL": 88.0}
            db.save_scores("stu-001", new_scores, "2024-06-01T00:00:00")
            loaded = db.load_scores("stu-001")
            assert loaded["Python"] == 95.0
            assert "Excel" not in loaded  # old score replaced entirely

    def test_load_scores_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            result = db.load_scores("stu-999")
            assert result == {}


class TestSQLiteTaskStatusOperations:
    def test_save_and_load_task_status_round_trip(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            db.save_task_status("stu-001", "task-A", True)
            statuses = db.load_task_statuses("stu-001")
            assert statuses["task-A"] is True

    def test_save_task_status_upsert(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            db.save_task_status("stu-001", "task-A", True)
            db.save_task_status("stu-001", "task-A", False)
            statuses = db.load_task_statuses("stu-001")
            assert statuses["task-A"] is False

    def test_load_task_statuses_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            result = db.load_task_statuses("stu-999")
            assert result == {}


# ===========================================================================
# Missing file / graceful degradation tests
# ===========================================================================

class TestMissingFileGracefulDegradation:
    def test_load_profile_logs_warning_on_missing_file(self, caplog):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            with caplog.at_level(logging.WARNING, logger="skillpilot"):
                result = db.load_profile("stu-xyz")
            assert result == {}
            # Warning should be logged (missing file or missing record)
            assert any("not found" in r.message.lower() or "profile not found" in r.message.lower()
                       for r in caplog.records)

    def test_load_all_profiles_logs_warning_on_missing_file(self, caplog):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            with caplog.at_level(logging.WARNING, logger="skillpilot"):
                result = db.load_all_profiles()
            assert result == []
            assert any("not found" in r.message.lower() for r in caplog.records)

    def test_load_skill_requirements_missing_file_returns_empty(self, caplog):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            with caplog.at_level(logging.WARNING, logger="skillpilot"):
                result = db.load_skill_requirements("Data Analyst")
            assert result == {}
            assert any("not found" in r.message.lower() for r in caplog.records)

    def test_load_learning_resources_missing_file_returns_empty(self, caplog):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            with caplog.at_level(logging.WARNING, logger="skillpilot"):
                result = db.load_learning_resources()
            assert result == []
            assert any("not found" in r.message.lower() for r in caplog.records)

    def test_load_sample_students_missing_file_returns_empty(self, caplog):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            with caplog.at_level(logging.WARNING, logger="skillpilot"):
                result = db.load_sample_students()
            assert result == []
            assert any("not found" in r.message.lower() for r in caplog.records)

    def test_load_projects_missing_file_returns_empty(self, caplog):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            with caplog.at_level(logging.WARNING, logger="skillpilot"):
                result = db.load_projects()
            assert result == []
            assert any("not found" in r.message.lower() for r in caplog.records)

    def test_missing_config_uses_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # No config.json at that path
            db = DBManager(config_path=str(Path(tmpdir) / "nonexistent.json"))
            assert db.backend == "csv"

    def test_config_not_found_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = DBManager(config_path=str(Path(tmpdir) / "missing.json"))
            # Should not raise; just use defaults
            assert db.backend in ("csv", "sqlite")


# ===========================================================================
# Roadmap persistence tests
# ===========================================================================

class TestRoadmapPersistence:
    def test_save_and_load_roadmap_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            roadmap = [{"week": 1, "tasks": ["task-1", "task-2"]}]
            db.save_roadmap("stu-001", roadmap)
            loaded = db.load_roadmap("stu-001")
            assert loaded == roadmap

    def test_load_roadmap_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_roadmap("stu-001")
            assert result == []

    def test_load_roadmap_missing_student_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_roadmap("stu-001", [{"week": 1}])
            result = db.load_roadmap("stu-999")
            assert result == []

    def test_save_roadmap_overwrites_previous(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_roadmap("stu-001", [{"week": 1}])
            db.save_roadmap("stu-001", [{"week": 1}, {"week": 2}])
            loaded = db.load_roadmap("stu-001")
            assert len(loaded) == 2
