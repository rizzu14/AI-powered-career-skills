"""
visualizations.py — Plotly chart factory for SkillPilot AI.

Pure functions only — no Streamlit calls, no side effects.
Accept plain dicts/lists and return go.Figure objects.
"""

from __future__ import annotations
import plotly.graph_objects as go

_SKILLS_ORDER = [
    "Python", "SQL", "Excel", "Statistics",
    "Data_Visualization", "Data_Cleaning", "Communication_Analytical_Thinking",
]

_SKILL_LABELS = {
    "Communication_Analytical_Thinking": "Comm & Thinking",
    "Data_Visualization": "Data Viz",
    "Data_Cleaning": "Data Cleaning",
}


def _label(skill: str) -> str:
    return _SKILL_LABELS.get(skill, skill)


def skill_bar_chart(
    scores: dict[str, float],
    targets: dict[str, float],
) -> go.Figure:
    """Grouped bar chart: student score vs. target for each skill."""
    skills = [s for s in _SKILLS_ORDER if s in scores or s in targets]
    student_vals = [scores.get(s, 0) for s in skills]
    target_vals = [targets.get(s, 0) for s in skills]
    labels = [_label(s) for s in skills]

    fig = go.Figure(data=[
        go.Bar(
            name="Your Score",
            x=labels,
            y=student_vals,
            marker_color="#4C9BE8",
            text=[f"{v:.0f}" for v in student_vals],
            textposition="outside",
        ),
        go.Bar(
            name="Target Score",
            x=labels,
            y=target_vals,
            marker_color="#F28C38",
            text=[f"{v:.0f}" for v in target_vals],
            textposition="outside",
        ),
    ])
    fig.update_layout(
        barmode="group",
        title="Skill Scores vs. Target Benchmarks",
        xaxis_title="Skill",
        yaxis_title="Score (0–100)",
        yaxis=dict(range=[0, 115]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=80, b=60),
        plot_bgcolor="white",
    )
    return fig


def skill_radar_chart(
    scores: dict[str, float],
    targets: dict[str, float],
) -> go.Figure:
    """Radar/spider chart overlaying student scores and targets."""
    skills = [s for s in _SKILLS_ORDER if s in scores or s in targets]
    labels = [_label(s) for s in skills]
    student_vals = [scores.get(s, 0) for s in skills]
    target_vals = [targets.get(s, 0) for s in skills]

    # Close the polygon
    labels_c = labels + [labels[0]]
    student_c = student_vals + [student_vals[0]]
    target_c = target_vals + [target_vals[0]]

    fig = go.Figure(data=[
        go.Scatterpolar(
            r=student_c, theta=labels_c, fill="toself",
            name="Your Score", line_color="#4C9BE8",
            fillcolor="rgba(76,155,232,0.2)",
        ),
        go.Scatterpolar(
            r=target_c, theta=labels_c, fill="toself",
            name="Target", line_color="#F28C38",
            fillcolor="rgba(242,140,56,0.1)",
        ),
    ])
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Skill Radar: Your Profile vs. Target",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=80, b=80),
    )
    return fig


def roadmap_progress_chart(
    completed_by_week: dict[int, int],
    total_by_week: dict[int, int],
) -> go.Figure:
    """Stacked bar chart: completed vs. remaining tasks per week."""
    weeks = sorted(set(list(completed_by_week.keys()) + list(total_by_week.keys())))
    completed = [completed_by_week.get(w, 0) for w in weeks]
    remaining = [max(0, total_by_week.get(w, 0) - completed_by_week.get(w, 0)) for w in weeks]
    week_labels = [f"Week {w}" for w in weeks]

    fig = go.Figure(data=[
        go.Bar(name="Completed", x=week_labels, y=completed,
               marker_color="#2ECC71", text=completed, textposition="inside"),
        go.Bar(name="Remaining", x=week_labels, y=remaining,
               marker_color="#E0E0E0", text=remaining, textposition="inside"),
    ])
    fig.update_layout(
        barmode="stack",
        title="Roadmap Progress by Week",
        xaxis_title="Week",
        yaxis_title="Tasks",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        margin=dict(t=80, b=60),
    )
    return fig


def gap_heatmap(gaps: dict[str, float]) -> go.Figure:
    """Single-row heatmap showing gap magnitude per skill."""
    skills = [s for s in _SKILLS_ORDER if s in gaps]
    values = [[gaps.get(s, 0) for s in skills]]
    labels = [_label(s) for s in skills]

    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=labels,
        y=["Gap"],
        colorscale=[
            [0.0, "#2ECC71"],
            [0.4, "#F1C40F"],
            [0.7, "#E67E22"],
            [1.0, "#E74C3C"],
        ],
        zmin=0,
        zmax=100,
        text=values,
        texttemplate="%{z:.0f}",
        showscale=True,
    ))
    fig.update_layout(
        title="Skill Gap Heatmap",
        margin=dict(t=60, b=40, l=60),
        xaxis=dict(side="bottom"),
    )
    return fig
