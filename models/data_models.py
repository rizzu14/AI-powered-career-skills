from __future__ import annotations
import uuid
import json
import datetime
from dataclasses import dataclass, field
from typing import List, Optional


def _now() -> str:
    return datetime.datetime.utcnow().isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class StudentProfile:
    full_name: str
    department: str
    semester: int
    skill_level: str
    career_path: str
    learning_goals: str
    learning_preferences: str
    student_id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "full_name": self.full_name,
            "department": self.department,
            "semester": self.semester,
            "skill_level": self.skill_level,
            "career_path": self.career_path,
            "learning_goals": self.learning_goals,
            "learning_preferences": self.learning_preferences,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StudentProfile":
        obj = cls(
            full_name=data["full_name"],
            department=data["department"],
            semester=int(data["semester"]),
            skill_level=data["skill_level"],
            career_path=data["career_path"],
            learning_goals=data.get("learning_goals", ""),
            learning_preferences=data.get("learning_preferences", "Mixed"),
        )
        obj.student_id = data.get("student_id", obj.student_id)
        obj.created_at = data.get("created_at", obj.created_at)
        obj.updated_at = data.get("updated_at", obj.updated_at)
        return obj


@dataclass
class SkillScore:
    student_id: str
    skill_name: str
    score: float
    assessed_at: str = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "skill_name": self.skill_name,
            "score": self.score,
            "assessed_at": self.assessed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillScore":
        return cls(
            student_id=data["student_id"],
            skill_name=data["skill_name"],
            score=float(data["score"]),
            assessed_at=data.get("assessed_at", _now()),
        )


@dataclass
class SkillGap:
    skill_name: str
    score: float
    target: float
    gap: float
    priority: str  # "High" | "Medium" | "Low" | ""

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "score": self.score,
            "target": self.target,
            "gap": self.gap,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillGap":
        return cls(
            skill_name=data["skill_name"],
            score=float(data["score"]),
            target=float(data["target"]),
            gap=float(data["gap"]),
            priority=data.get("priority", ""),
        )


@dataclass
class LearningActivity:
    skill_name: str
    topic: str
    objective: str
    exercise: str
    mini_project: str
    estimated_hours: float
    resource_url: str
    resource_title: str
    priority: str
    gap_value: float
    activity_id: str = field(default_factory=_new_id)

    def to_dict(self) -> dict:
        return {
            "activity_id": self.activity_id,
            "skill_name": self.skill_name,
            "topic": self.topic,
            "objective": self.objective,
            "exercise": self.exercise,
            "mini_project": self.mini_project,
            "estimated_hours": self.estimated_hours,
            "resource_url": self.resource_url,
            "resource_title": self.resource_title,
            "priority": self.priority,
            "gap_value": self.gap_value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LearningActivity":
        obj = cls(
            skill_name=data["skill_name"],
            topic=data["topic"],
            objective=data["objective"],
            exercise=data["exercise"],
            mini_project=data["mini_project"],
            estimated_hours=float(data["estimated_hours"]),
            resource_url=data["resource_url"],
            resource_title=data["resource_title"],
            priority=data["priority"],
            gap_value=float(data["gap_value"]),
        )
        obj.activity_id = data.get("activity_id", obj.activity_id)
        return obj


@dataclass
class RoadmapTask:
    activity_id: str
    week_number: int
    day_number: int
    description: str
    hours_allocated: float
    completed: bool = False
    task_id: str = field(default_factory=_new_id)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "activity_id": self.activity_id,
            "week_number": self.week_number,
            "day_number": self.day_number,
            "description": self.description,
            "hours_allocated": self.hours_allocated,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RoadmapTask":
        obj = cls(
            activity_id=data["activity_id"],
            week_number=int(data["week_number"]),
            day_number=int(data["day_number"]),
            description=data["description"],
            hours_allocated=float(data["hours_allocated"]),
            completed=bool(data.get("completed", False)),
        )
        obj.task_id = data.get("task_id", obj.task_id)
        return obj


@dataclass
class RoadmapDay:
    day_number: int
    tasks: List[RoadmapTask] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "day_number": self.day_number,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RoadmapDay":
        tasks = [RoadmapTask.from_dict(t) for t in data.get("tasks", [])]
        return cls(day_number=int(data["day_number"]), tasks=tasks)


@dataclass
class RoadmapWeek:
    week_number: int
    milestone: str
    checkpoint: str
    days: List[RoadmapDay] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "week_number": self.week_number,
            "milestone": self.milestone,
            "checkpoint": self.checkpoint,
            "days": [d.to_dict() for d in self.days],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RoadmapWeek":
        days = [RoadmapDay.from_dict(d) for d in data.get("days", [])]
        return cls(
            week_number=int(data["week_number"]),
            milestone=data.get("milestone", ""),
            checkpoint=data.get("checkpoint", ""),
            days=days,
        )


@dataclass
class ProjectRecommendation:
    project_id: str
    name: str
    objective: str
    required_skills: List[str]
    tools: List[str]
    expected_output: str
    relevance_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "objective": self.objective,
            "required_skills": json.dumps(self.required_skills),
            "tools": json.dumps(self.tools),
            "expected_output": self.expected_output,
            "relevance_score": self.relevance_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectRecommendation":
        required_skills = data.get("required_skills", [])
        tools = data.get("tools", [])
        if isinstance(required_skills, str):
            required_skills = json.loads(required_skills)
        if isinstance(tools, str):
            tools = json.loads(tools)
        return cls(
            project_id=data["project_id"],
            name=data["name"],
            objective=data["objective"],
            required_skills=required_skills,
            tools=tools,
            expected_output=data["expected_output"],
            relevance_score=float(data.get("relevance_score", 0.0)),
        )
