"""
skill_gap.py — Gap analysis module for SkillPilot AI.

Computes skill gaps, assigns priority tiers, and identifies strongest/weakest skills.
Target scores are always loaded from data/skill_requirements.csv via DBManager —
never hardcoded.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.db_manager import DBManager

from models.data_models import SkillGap


def compute_gaps(
    scores: dict[str, float],
    target_scores: dict[str, float],
) -> dict[str, float]:
    """
    Return {skill: gap} where gap = max(0.0, target - score).
    Skills present in target_scores but missing from scores are treated as score=0.
    """
    return {skill: max(0.0, target - scores.get(skill, 0.0)) for skill, target in target_scores.items()}


def assign_priority(gap: float) -> str:
    """
    Return priority label for a gap value.
    gap >= 40       → 'High'
    20 <= gap < 40  → 'Medium'
    1  <= gap < 20  → 'Low'
    gap == 0        → '' (skill met or exceeded)
    """
    if gap >= 40:
        return "High"
    if gap >= 20:
        return "Medium"
    if gap >= 1:
        return "Low"
    return ""


def get_gap_summary(
    scores: dict[str, float],
    career_path: str,
    db: "DBManager",
) -> list[SkillGap]:
    """
    Load target scores from CSV, compute gaps, assign priorities.
    Returns list of SkillGap sorted descending by gap value (ties broken alphabetically).
    """
    target_scores = db.load_skill_requirements(career_path)
    gaps = compute_gaps(scores, target_scores)

    summary: list[SkillGap] = [
        SkillGap(
            skill_name=skill,
            score=scores.get(skill, 0.0),
            target=target_scores[skill],
            gap=gap,
            priority=assign_priority(gap),
        )
        for skill, gap in gaps.items()
    ]

    summary.sort(key=lambda g: (-g.gap, g.skill_name))
    return summary


def identify_strongest_weakest(
    scores: dict[str, float],
    n: int = 2,
) -> tuple[list[str], list[str]]:
    """
    Return (top_n_skills, bottom_n_skills) by score.
    Ties broken alphabetically by skill name.
    """
    if not scores:
        return [], []
    sorted_skills = sorted(scores.keys(), key=lambda s: (-scores[s], s))
    top_n = sorted_skills[:n]
    bottom_n = sorted(sorted_skills[-n:], key=lambda s: (scores[s], s))
    return top_n, bottom_n
