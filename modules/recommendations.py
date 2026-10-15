"""
recommendations.py — Personalized learning recommendation engine for SkillPilot AI.

Generates LearningActivity objects ranked by skill gap magnitude.
LLM enrichment is opt-in via environment variables and falls back to offline mode.
"""

from __future__ import annotations
import logging
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from modules.db_manager import DBManager

from models.data_models import LearningActivity, ProjectRecommendation, SkillGap

log = logging.getLogger("skillpilot")

_REQUIRED_LLM_FIELDS = {"topic", "objective", "exercise", "mini_project", "estimated_hours", "resource_url"}

# Offline content per skill
_OFFLINE_CONTENT: dict[str, dict] = {
    "Python": {
        "topic": "Python for Data Analysis",
        "objective": "Write Python scripts using pandas and numpy to manipulate and analyse datasets",
        "exercise": "Load a CSV with pandas, compute summary statistics, and filter rows by a condition",
        "mini_project": "Analyse the Titanic dataset and produce a summary report with charts",
    },
    "SQL": {
        "topic": "SQL for Data Extraction and Aggregation",
        "objective": "Write SQL queries to extract, filter, join, and aggregate data from relational databases",
        "exercise": "Write SELECT, WHERE, GROUP BY, and JOIN queries on a sample database",
        "mini_project": "Query a sales database to produce a monthly revenue report",
    },
    "Excel": {
        "topic": "Excel for Data Analysis",
        "objective": "Use Excel pivot tables, formulas, and charts for data analysis",
        "exercise": "Create a pivot table from transactional data and build a summary chart",
        "mini_project": "Build a sales dashboard with pivot tables and a dynamic chart using sample data",
    },
    "Statistics": {
        "topic": "Descriptive and Inferential Statistics",
        "objective": "Apply mean, median, variance, and hypothesis testing to real datasets",
        "exercise": "Calculate descriptive statistics for a dataset and interpret the results",
        "mini_project": "Conduct a hypothesis test on survey data and write up the conclusions",
    },
    "Data_Visualization": {
        "topic": "Data Visualisation with Plotly",
        "objective": "Create clear and informative charts and dashboards to communicate findings",
        "exercise": "Build a bar chart, line chart, and scatter plot from the same dataset using Plotly",
        "mini_project": "Design an interactive dashboard for a public dataset using Plotly and Streamlit",
    },
    "Data_Cleaning": {
        "topic": "Data Cleaning and Quality",
        "objective": "Identify and handle missing values, duplicates, outliers, and inconsistent formats",
        "exercise": "Clean a messy CSV: handle nulls, fix data types, remove duplicates",
        "mini_project": "Clean and standardise a real-world dataset (e.g., Kaggle housing data) and document each step",
    },
    "Communication_Analytical_Thinking": {
        "topic": "Presenting Data Insights",
        "objective": "Communicate findings clearly to both technical and non-technical audiences",
        "exercise": "Write a one-page summary of an analysis for a non-technical manager",
        "mini_project": "Present a data analysis project as a slide deck with key insights and recommendations",
    },
}


def get_llm_client() -> Any | None:
    """
    Load LLM API credentials from environment variables only.
    Returns a configured client or None (offline mode). Never logs credentials.
    """
    api_key = os.environ.get("SKILLPILOT_LLM_API_KEY")
    endpoint = os.environ.get("SKILLPILOT_LLM_ENDPOINT")
    if not api_key or not endpoint:
        return None
    try:
        import openai  # type: ignore
        client = openai.OpenAI(api_key=api_key, base_url=endpoint)
        log.info("LLM client initialised.")
        return client
    except ImportError:
        log.warning("openai package not installed — running in offline mode.")
        return None
    except Exception as exc:
        log.warning("LLM client init failed (%s) — offline mode.", type(exc).__name__)
        return None


def _validate_llm_response(response: Any) -> bool:
    """Return True if response contains all required fields with correct types."""
    if not isinstance(response, dict):
        return False
    if not _REQUIRED_LLM_FIELDS.issubset(response.keys()):
        return False
    if not isinstance(response.get("estimated_hours"), (int, float)):
        return False
    url = response.get("resource_url", "")
    return isinstance(url, str) and len(url.strip()) > 0


def _enrich_with_llm(activity: LearningActivity, llm_client: Any) -> LearningActivity:
    """Attempt LLM enrichment; fall back to offline activity on any failure."""
    prompt = (
        f"You are a learning advisor. For a student with a skill gap in '{activity.skill_name}', "
        "provide an enriched learning activity as a JSON object with these exact keys: "
        "topic, objective, exercise, mini_project, estimated_hours (number), resource_url (string). "
        "Respond with valid JSON only."
    )
    try:
        response = llm_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        import json
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)
        if _validate_llm_response(parsed):
            activity.topic = parsed.get("topic", activity.topic)
            activity.objective = parsed.get("objective", activity.objective)
            activity.exercise = parsed.get("exercise", activity.exercise)
            activity.mini_project = parsed.get("mini_project", activity.mini_project)
            activity.estimated_hours = float(parsed.get("estimated_hours", activity.estimated_hours))
            activity.resource_url = parsed.get("resource_url", activity.resource_url)
            log.info("LLM enrichment applied for: %s", activity.skill_name)
        else:
            log.warning("LLM response invalid for %s — using offline.", activity.skill_name)
    except Exception as exc:
        log.warning("LLM enrichment failed for %s (%s) — offline.", activity.skill_name, type(exc).__name__)
    return activity


def _make_offline_activity(gap: SkillGap, resources: list[dict]) -> LearningActivity:
    """Build a LearningActivity from offline content and the resource CSV."""
    from modules.skill_gap import assign_priority

    content = _OFFLINE_CONTENT.get(gap.skill_name, {
        "topic": f"{gap.skill_name} Fundamentals",
        "objective": f"Improve proficiency in {gap.skill_name}",
        "exercise": f"Practice {gap.skill_name} with hands-on exercises",
        "mini_project": f"Build a small project using {gap.skill_name}",
    })

    matching = [r for r in resources if r.get("skill_name") == gap.skill_name]
    if matching:
        r = matching[0]
        resource_url = r.get("url", "https://www.kaggle.com/learn")
        resource_title = r.get("title", "Kaggle Learn")
        estimated_hours = float(r.get("estimated_hours", 4.0))
    else:
        resource_url = "https://www.kaggle.com/learn"
        resource_title = "Kaggle Learn"
        estimated_hours = 4.0

    return LearningActivity(
        skill_name=gap.skill_name,
        topic=content["topic"],
        objective=content["objective"],
        exercise=content["exercise"],
        mini_project=content["mini_project"],
        estimated_hours=estimated_hours,
        resource_url=resource_url,
        resource_title=resource_title,
        priority=assign_priority(gap.gap),
        gap_value=gap.gap,
    )


def generate_activities(
    gap_summary: list[SkillGap],
    resources: list[dict],
    llm_client: Any = None,
) -> list[LearningActivity]:
    """
    Generate one LearningActivity per skill with gap > 0, sorted by gap descending.
    Returns empty list when all gaps are zero.
    """
    activities: list[LearningActivity] = []
    for gap in gap_summary:
        if gap.gap <= 0:
            continue
        activity = _make_offline_activity(gap, resources)
        if llm_client is not None:
            activity = _enrich_with_llm(activity, llm_client)
        activities.append(activity)

    activities.sort(key=lambda a: (-a.gap_value, a.skill_name))
    return activities


def rank_projects(
    gap_summary: list[SkillGap],
    projects: list[ProjectRecommendation],
) -> list[ProjectRecommendation]:
    """
    Rank projects by count of required_skills overlapping with skills where gap > 0.
    Tie-break: alphabetical by project name.
    """
    high_gap_skills = {g.skill_name for g in gap_summary if g.gap > 0}
    for project in projects:
        project.relevance_score = float(len(set(project.required_skills) & high_gap_skills))
    return sorted(projects, key=lambda p: (-p.relevance_score, p.name))
