"""
progress.py — Learning progress tracker for SkillPilot AI.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.db_manager import DBManager
    from models.data_models import RoadmapWeek


def mark_task(student_id: str, task_id: str, completed: bool, db: "DBManager") -> None:
    """Persist task completion status via DB_Manager."""
    db.save_task_status(student_id, task_id, completed)


def get_completion_percentage(student_id: str, total_tasks: int, db: "DBManager") -> float:
    """Return round((completed / total) * 100, 1). Returns 0.0 when total == 0."""
    if total_tasks == 0:
        return 0.0
    statuses = db.load_task_statuses(student_id)
    completed_count = sum(1 for v in statuses.values() if v)
    return round((completed_count / total_tasks) * 100.0, 1)


def get_week_completion(student_id: str, week: "RoadmapWeek", db: "DBManager") -> bool:
    """Return True only if every task in the week is marked complete."""
    statuses = db.load_task_statuses(student_id)
    for day in week.days:
        for task in day.tasks:
            if not statuses.get(task.task_id, False):
                return False
    return True


def get_completed_by_week(
    student_id: str,
    roadmap: list["RoadmapWeek"],
    db: "DBManager",
) -> dict[int, int]:
    """Return {week_number: completed_task_count} for progress charting."""
    statuses = db.load_task_statuses(student_id)
    result: dict[int, int] = {}
    for week in roadmap:
        count = sum(
            1
            for day in week.days
            for task in day.tasks
            if statuses.get(task.task_id, False)
        )
        result[week.week_number] = count
    return result
