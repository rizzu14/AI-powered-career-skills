"""
roadmap.py — Learning roadmap generator for SkillPilot AI.

Packs LearningActivity objects into weekly blocks with daily assignments using
a greedy day-filling algorithm.
"""

from __future__ import annotations
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.data_models import LearningActivity

from models.data_models import RoadmapDay, RoadmapTask, RoadmapWeek

DAILY_HOURS_TARGET: float = 1.5
DAYS_PER_WEEK: int = 5


def generate_roadmap(activities: list["LearningActivity"]) -> list[RoadmapWeek]:
    """
    Pack activities into weekly blocks using a day-filling algorithm.

    - Iterates activities in order (already sorted by gap descending).
    - Fills the current day up to DAILY_HOURS_TARGET.
    - Advances to next day when full; starts a new week every DAYS_PER_WEEK days.
    - Returns a list of RoadmapWeek objects.
    """
    if not activities:
        return []

    day_hours_used: dict[int, float] = defaultdict(float)
    task_list: list[RoadmapTask] = []
    day_index = 0

    for activity in activities:
        remaining = activity.estimated_hours
        while remaining > 0.001:
            capacity = DAILY_HOURS_TARGET - day_hours_used[day_index]
            if capacity <= 0.001:
                day_index += 1
                continue
            allocated = min(remaining, capacity)
            day_hours_used[day_index] += allocated
            week_num = day_index // DAYS_PER_WEEK + 1
            day_in_week = day_index % DAYS_PER_WEEK + 1
            task = RoadmapTask(
                activity_id=activity.activity_id,
                week_number=week_num,
                day_number=day_in_week,
                description=f"{activity.topic} — {activity.objective}",
                hours_allocated=round(allocated, 2),
            )
            task_list.append(task)
            remaining -= allocated

    # Group tasks into weeks → days
    tasks_by_week: dict[int, list[RoadmapTask]] = defaultdict(list)
    for task in task_list:
        tasks_by_week[task.week_number].append(task)

    weeks: list[RoadmapWeek] = []
    for week_num in sorted(tasks_by_week.keys()):
        week_tasks = tasks_by_week[week_num]

        # Unique activities for this week (for milestone/checkpoint text)
        seen_ids: set[str] = set()
        week_activities: list[LearningActivity] = []
        for t in week_tasks:
            if t.activity_id not in seen_ids:
                seen_ids.add(t.activity_id)
                act = next((a for a in activities if a.activity_id == t.activity_id), None)
                if act:
                    week_activities.append(act)

        days_map: dict[int, list[RoadmapTask]] = defaultdict(list)
        for t in week_tasks:
            days_map[t.day_number].append(t)
        days = [RoadmapDay(day_number=d, tasks=ts) for d, ts in sorted(days_map.items())]

        weeks.append(RoadmapWeek(
            week_number=week_num,
            milestone=generate_milestone(week_activities),
            checkpoint=generate_checkpoint(week_activities),
            days=days,
        ))

    return weeks


def flatten_tasks(roadmap: list[RoadmapWeek]) -> list[RoadmapTask]:
    """Return a flat list of all RoadmapTask objects across all weeks and days."""
    result: list[RoadmapTask] = []
    for week in roadmap:
        for day in week.days:
            result.extend(day.tasks)
    return result


def generate_milestone(week_activities: list["LearningActivity"]) -> str:
    """Produce a human-readable milestone string for the week's activities."""
    if not week_activities:
        return "Complete this week's learning tasks"
    skills = ", ".join(a.skill_name.replace("_", " ") for a in week_activities[:3])
    return f"Build working knowledge of: {skills}"


def generate_checkpoint(week_activities: list["LearningActivity"]) -> str:
    """Produce a checkpoint exercise description for the week."""
    if not week_activities:
        return "Review what you have learned this week"
    first = week_activities[0]
    return (
        f"Checkpoint: {first.exercise}. "
        f"Reflect on what you found most challenging and revisit that topic."
    )
