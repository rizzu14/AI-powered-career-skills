"""
Property-based tests for modules/db_manager.py

Property 18: Storage read on missing file returns empty default
  **Validates: Requirements 8.4**

Property 19: All data persisted is recoverable
  **Validates: Requirements 8.1**
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from modules.db_manager import DBManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_db(tmpdir: Path, backend: str = "csv") -> DBManager:
    cfg = {
        "storage_backend": backend,
        "data_dir": str(tmpdir / "data"),
        "sqlite_path": str(tmpdir / "data" / "test.db"),
    }
    cfg_path = tmpdir / "config.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    return DBManager(config_path=str(cfg_path))


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

student_id_st = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"),
    min_size=1, max_size=30
)

skill_name_st = st.sampled_from([
    "Python", "SQL", "Excel", "Statistics",
    "Data_Visualization", "Data_Cleaning", "Communication_Analytical_Thinking"
])

score_st = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

profile_st = st.fixed_dictionaries({
    "student_id": student_id_st,
    "full_name": st.text(min_size=1, max_size=80),
    "department": st.text(min_size=1, max_size=50),
    "semester": st.integers(min_value=1, max_value=8).map(str),
    "skill_level": st.sampled_from(["Beginner", "Intermediate", "Advanced"]),
    "career_path": st.just("Data Analyst"),
    "learning_goals": st.text(max_size=200),
    "learning_preferences": st.sampled_from(["Video", "Article", "Project-based", "Mixed"]),
    "created_at": st.just("2024-01-01T00:00:00"),
    "updated_at": st.just("2024-01-01T00:00:00"),
})

scores_dict_st = st.dictionaries(
    keys=skill_name_st,
    values=score_st,
    min_size=1, max_size=7,
)

task_id_st = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"),
    min_size=1, max_size=40
)


# ===========================================================================
# Property 18: Storage read on missing file returns empty default
# **Validates: Requirements 8.4**
# ===========================================================================

class TestProperty18StorageReadMissingFile:
    """
    For any student_id, reading from a storage backend that has no data
    for that student must return the empty default ({} or []) and must
    not raise any exception.
    """

    @given(student_id=student_id_st)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_load_profile_missing_returns_empty_csv(self, student_id):
        """Property 18 (CSV): load_profile on missing file/record returns {}."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_profile(student_id)
            assert result == {}, f"Expected empty dict, got {result!r}"

    @given(student_id=student_id_st)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_load_scores_missing_returns_empty_csv(self, student_id):
        """Property 18 (CSV): load_scores on missing file/record returns {}."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_scores(student_id)
            assert result == {}, f"Expected empty dict, got {result!r}"

    @given(student_id=student_id_st)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_load_task_statuses_missing_returns_empty_csv(self, student_id):
        """Property 18 (CSV): load_task_statuses on missing file/record returns {}."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_task_statuses(student_id)
            assert result == {}, f"Expected empty dict, got {result!r}"

    @given(student_id=student_id_st)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_load_profile_missing_returns_empty_sqlite(self, student_id):
        """Property 18 (SQLite): load_profile on missing record returns {}."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            result = db.load_profile(student_id)
            assert result == {}, f"Expected empty dict, got {result!r}"

    @given(student_id=student_id_st)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_load_scores_missing_returns_empty_sqlite(self, student_id):
        """Property 18 (SQLite): load_scores on missing record returns {}."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            result = db.load_scores(student_id)
            assert result == {}, f"Expected empty dict, got {result!r}"

    @given(student_id=student_id_st)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_load_task_statuses_missing_returns_empty_sqlite(self, student_id):
        """Property 18 (SQLite): load_task_statuses on missing record returns {}."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            result = db.load_task_statuses(student_id)
            assert result == {}, f"Expected empty dict, got {result!r}"

    def test_load_all_profiles_empty_storage_returns_list(self):
        """Property 18: load_all_profiles on empty storage returns []."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            result = db.load_all_profiles()
            assert result == []


# ===========================================================================
# Property 19: All data persisted is recoverable
# **Validates: Requirements 8.1**
# ===========================================================================

class TestProperty19DataPersistedIsRecoverable:
    """
    For any valid profile/scores/task-status data written to storage,
    a subsequent read must return the exact same data.
    """

    @given(profile=profile_st)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_profile_persisted_is_recoverable_csv(self, profile):
        """Property 19 (CSV): saved profile is fully recoverable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_profile(profile)
            loaded = db.load_profile(profile["student_id"])
            assert loaded.get("student_id") == profile["student_id"]
            assert loaded.get("full_name") == profile["full_name"]
            assert loaded.get("career_path") == profile["career_path"]

    @given(profile=profile_st, scores=scores_dict_st)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_scores_persisted_are_recoverable_csv(self, profile, scores):
        """Property 19 (CSV): saved scores are fully recoverable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            sid = profile["student_id"]
            db.save_scores(sid, scores, "2024-01-01T00:00:00")
            loaded = db.load_scores(sid)
            for skill, score in scores.items():
                assert skill in loaded, f"Skill {skill!r} not found in loaded scores"
                assert abs(loaded[skill] - score) < 1e-6, (
                    f"Score mismatch for {skill!r}: expected {score}, got {loaded[skill]}"
                )

    @given(
        student_id=student_id_st,
        task_id=task_id_st,
        completed=st.booleans(),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_task_status_persisted_is_recoverable_csv(self, student_id, task_id, completed):
        """Property 19 (CSV): saved task status is fully recoverable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_task_status(student_id, task_id, completed)
            statuses = db.load_task_statuses(student_id)
            assert task_id in statuses, f"Task {task_id!r} not found in loaded statuses"
            assert statuses[task_id] == completed

    @given(profile=profile_st)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_profile_persisted_is_recoverable_sqlite(self, profile):
        """Property 19 (SQLite): saved profile is fully recoverable."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            db.save_profile(profile)
            loaded = db.load_profile(profile["student_id"])
            assert loaded.get("student_id") == profile["student_id"]
            assert loaded.get("full_name") == profile["full_name"]

    @given(profile=profile_st, scores=scores_dict_st)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_scores_persisted_are_recoverable_sqlite(self, profile, scores):
        """Property 19 (SQLite): saved scores are fully recoverable."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db = _make_db(Path(tmpdir), "sqlite")
            sid = profile["student_id"]
            db.save_scores(sid, scores, "2024-01-01T00:00:00")
            loaded = db.load_scores(sid)
            for skill, score in scores.items():
                assert skill in loaded
                assert abs(loaded[skill] - score) < 1e-6

    @given(profile=profile_st)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_profile_update_last_write_wins_csv(self, profile):
        """Property 19 (CSV): save_profile is last-write-wins (upsert)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            db.save_profile(profile)
            updated = {**profile, "full_name": "Updated Name", "department": "Updated Dept"}
            db.save_profile(updated)
            loaded = db.load_profile(profile["student_id"])
            assert loaded.get("full_name") == "Updated Name"
            assert loaded.get("department") == "Updated Dept"
            # No duplicate rows
            all_profiles = db.load_all_profiles()
            matching = [p for p in all_profiles if p["student_id"] == profile["student_id"]]
            assert len(matching) == 1

    @given(profile=profile_st, scores=scores_dict_st)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_scores_replace_on_resave_csv(self, profile, scores):
        """Property 19 (CSV): re-saving scores replaces all previous scores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = _make_db(Path(tmpdir), "csv")
            sid = profile["student_id"]
            # Save initial scores, then replace with a single-skill set
            db.save_scores(sid, scores, "2024-01-01T00:00:00")
            replacement = {"Python": 42.0}
            db.save_scores(sid, replacement, "2024-06-01T00:00:00")
            loaded = db.load_scores(sid)
            # Only the replacement should be present
            assert "Python" in loaded
            assert loaded["Python"] == pytest.approx(42.0)
            # Old skills should be gone
            for old_skill in scores:
                if old_skill != "Python":
                    assert old_skill not in loaded
