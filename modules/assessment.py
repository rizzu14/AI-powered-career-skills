"""
assessment.py — Skill assessment module for SkillPilot AI.

Provides question banks, response normalization, validation, and score
computation for the seven assessed skills.
"""

from __future__ import annotations
from typing import Any

SKILLS = [
    "Python",
    "SQL",
    "Excel",
    "Statistics",
    "Data_Visualization",
    "Data_Cleaning",
    "Communication_Analytical_Thinking",
]

# One slider + one MCQ per skill
QUESTION_BANK: dict[str, list[dict]] = {
    "Python": [
        {
            "type": "slider",
            "prompt": "Rate your Python programming proficiency (0 = no experience, 10 = expert)",
            "weight": 0.6,
        },
        {
            "type": "mcq",
            "prompt": "Which of the following creates a DataFrame in pandas?",
            "options": {"A": "pd.DataFrame()", "B": "pd.Table()", "C": "pd.Array()", "D": "pd.List()"},
            "answer": "A",
            "weight": 0.4,
        },
    ],
    "SQL": [
        {
            "type": "slider",
            "prompt": "Rate your SQL proficiency (0 = no experience, 10 = expert)",
            "weight": 0.6,
        },
        {
            "type": "mcq",
            "prompt": "Which SQL clause filters grouped results?",
            "options": {"A": "WHERE", "B": "HAVING", "C": "FILTER", "D": "GROUP BY"},
            "answer": "B",
            "weight": 0.4,
        },
    ],
    "Excel": [
        {
            "type": "slider",
            "prompt": "Rate your Excel proficiency (0 = no experience, 10 = expert)",
            "weight": 0.6,
        },
        {
            "type": "mcq",
            "prompt": "Which Excel feature summarises data by categories?",
            "options": {"A": "VLOOKUP", "B": "Pivot Table", "C": "IF Formula", "D": "COUNTIF"},
            "answer": "B",
            "weight": 0.4,
        },
    ],
    "Statistics": [
        {
            "type": "slider",
            "prompt": "Rate your Statistics knowledge (0 = no knowledge, 10 = expert)",
            "weight": 0.6,
        },
        {
            "type": "mcq",
            "prompt": "Which measure is least affected by outliers?",
            "options": {"A": "Mean", "B": "Variance", "C": "Median", "D": "Standard Deviation"},
            "answer": "C",
            "weight": 0.4,
        },
    ],
    "Data_Visualization": [
        {
            "type": "slider",
            "prompt": "Rate your data visualisation skills (0 = no experience, 10 = expert)",
            "weight": 0.6,
        },
        {
            "type": "mcq",
            "prompt": "Which chart type best shows part-to-whole relationships?",
            "options": {"A": "Line Chart", "B": "Bar Chart", "C": "Pie Chart", "D": "Scatter Plot"},
            "answer": "C",
            "weight": 0.4,
        },
    ],
    "Data_Cleaning": [
        {
            "type": "slider",
            "prompt": "Rate your data cleaning skills (0 = no experience, 10 = expert)",
            "weight": 0.6,
        },
        {
            "type": "mcq",
            "prompt": "Which pandas method removes rows with missing values?",
            "options": {"A": "df.drop()", "B": "df.dropna()", "C": "df.fillna()", "D": "df.clean()"},
            "answer": "B",
            "weight": 0.4,
        },
    ],
    "Communication_Analytical_Thinking": [
        {
            "type": "slider",
            "prompt": "Rate your communication and analytical thinking skills (0 = poor, 10 = excellent)",
            "weight": 0.6,
        },
        {
            "type": "mcq",
            "prompt": "When presenting findings to non-technical stakeholders, you should:",
            "options": {
                "A": "Use technical jargon for precision",
                "B": "Focus on actionable insights with clear visuals",
                "C": "Share raw data tables",
                "D": "Avoid charts and use only text",
            },
            "answer": "B",
            "weight": 0.4,
        },
    ],
}


def get_assessment_questions(skill: str) -> list[dict]:
    """Return the question bank for the given skill."""
    return QUESTION_BANK.get(skill, [])


def normalize_response(skill: str, raw_value: Any, question_type: str) -> float:
    """
    Convert a raw assessment response to a Skill_Score in [0.0, 100.0].

    slider  (0–10) → multiply by 10
    mcq            → correct=100, wrong=20
    practical      → keyword-count heuristic
    """
    if question_type == "slider":
        try:
            val = float(raw_value)
        except (TypeError, ValueError):
            val = 0.0
        return max(0.0, min(100.0, val * 10.0))

    if question_type == "mcq":
        questions = get_assessment_questions(skill)
        for q in questions:
            if q.get("type") == "mcq":
                if str(raw_value).strip().upper() == q.get("answer", "").upper():
                    return 100.0
        return 20.0

    if question_type == "practical":
        keywords: dict[str, list[str]] = {
            "Python": ["pandas", "numpy", "dataframe", "function", "loop", "library"],
            "SQL": ["select", "join", "where", "group", "aggregate", "query"],
            "Excel": ["pivot", "vlookup", "formula", "chart", "filter", "cell"],
            "Statistics": ["mean", "median", "variance", "hypothesis", "distribution", "probability"],
            "Data_Visualization": ["chart", "plot", "dashboard", "plotly", "matplotlib", "seaborn"],
            "Data_Cleaning": ["missing", "null", "duplicate", "outlier", "impute", "clean"],
            "Communication_Analytical_Thinking": ["insight", "present", "stakeholder", "finding", "recommend", "explain"],
        }
        text = str(raw_value).lower()
        skill_kw = keywords.get(skill, [])
        if not skill_kw:
            return 50.0
        matches = sum(1 for kw in skill_kw if kw in text)
        return max(0.0, min(100.0, (matches / len(skill_kw)) * 100.0))

    return 0.0


def validate_assessment(responses: dict[str, Any]) -> list[str]:
    """Return list of unanswered skill names. Empty list = all answered."""
    return [skill for skill in SKILLS if responses.get(skill) is None]


def compute_skill_scores(responses: dict[str, Any]) -> dict[str, float]:
    """
    Compute a Skill_Score in [0, 100] for each skill.

    Each response value may be:
    - A number/string (slider value) → normalized directly
    - A dict with keys 'slider' and/or 'mcq' → weighted combination
    """
    scores: dict[str, float] = {}
    for skill in SKILLS:
        raw = responses.get(skill)
        if raw is None:
            scores[skill] = 0.0
            continue

        if isinstance(raw, dict):
            slider_val = raw.get("slider")
            mcq_val = raw.get("mcq")

            questions = get_assessment_questions(skill)
            slider_w = next((q["weight"] for q in questions if q["type"] == "slider"), 1.0)
            mcq_w = next((q["weight"] for q in questions if q["type"] == "mcq"), 0.0)

            slider_score = normalize_response(skill, slider_val, "slider") if slider_val is not None else 0.0
            mcq_score = normalize_response(skill, mcq_val, "mcq") if mcq_val is not None else 0.0

            if mcq_val is not None:
                combined = (slider_score * slider_w + mcq_score * mcq_w) / (slider_w + mcq_w)
            else:
                combined = slider_score

            scores[skill] = round(max(0.0, min(100.0, combined)), 2)
        else:
            scores[skill] = round(normalize_response(skill, raw, "slider"), 2)

    return scores
