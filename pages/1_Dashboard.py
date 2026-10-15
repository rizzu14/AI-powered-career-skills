"""
1_Dashboard.py — Student Dashboard page for SkillPilot AI.
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from modules.skill_gap import get_gap_summary, identify_strongest_weakest
from modules.progress import get_completion_percentage, get_completed_by_week
from modules.visualizations import skill_bar_chart, skill_radar_chart, roadmap_progress_chart
from modules.roadmap import flatten_tasks

# Import shared CSS injector from app.py (available via sys.path)
try:
    from app import inject_css
except Exception:
    def inject_css():
        pass

st.set_page_config(page_title="Dashboard — SkillPilot AI", page_icon="📊", layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
db = st.session_state.get("db")
profile = st.session_state.get("active_profile")
scores = st.session_state.get("skill_scores", {})
assessment_done = st.session_state.get("assessment_done", False)
roadmap = st.session_state.get("roadmap", [])

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="margin-bottom:1.75rem;">
        <h1 style="font-size:1.85rem!important;font-weight:700!important;
                    letter-spacing:-0.03em!important;color:#f1f1f5!important;
                    margin-bottom:0.2rem!important;">
            Dashboard
        </h1>
        <p style="font-size:0.87rem;color:rgba(255,255,255,0.4);margin:0;">
            Your skill overview, progress, and learning insights at a glance.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Guard: no profile
# ---------------------------------------------------------------------------
if not profile:
    st.markdown(
        """
        <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                     border-radius:16px;padding:1.5rem 2rem;max-width:480px;margin:2rem auto;">
            <div style="font-size:1.6rem;margin-bottom:0.8rem;">⚠️</div>
            <div style="font-size:1rem;font-weight:600;color:rgba(245,158,11,0.95);
                         margin-bottom:0.4rem;">No Profile Found</div>
            <div style="font-size:0.83rem;color:rgba(255,255,255,0.45);line-height:1.6;">
                Create your student profile first so SkillPilot AI can tailor
                the assessment and recommendations to your career path.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Profile.py", label="👤 Create your profile", icon="👤")
    st.stop()

# ---------------------------------------------------------------------------
# Guard: assessment not done — premium locked state
# ---------------------------------------------------------------------------
if not assessment_done or not scores:
    st.markdown(
        f"""
        <div style="max-width:600px;margin:3rem auto 0 auto;text-align:center;">
            <div style="width:72px;height:72px;border-radius:50%;
                         background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(129,140,248,0.08));
                         border:1px solid rgba(99,102,241,0.25);
                         display:flex;align-items:center;justify-content:center;
                         font-size:2rem;margin:0 auto 1.5rem auto;">🔒</div>
            <h2 style="font-size:1.5rem!important;font-weight:700!important;
                        letter-spacing:-0.03em!important;color:#f1f1f5!important;
                        margin-bottom:0.6rem!important;">Dashboard Locked</h2>
            <p style="font-size:0.9rem;color:rgba(255,255,255,0.45);
                       line-height:1.65;max-width:400px;margin:0 auto 1.8rem auto;">
                Complete your skill assessment to unlock your personalised dashboard
                — skill scores, gap analysis, charts, and roadmap progress all in one place.
            </p>
            <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;
                         margin-bottom:2.5rem;">
        """,
        unsafe_allow_html=True,
    )

    # Preview cards (what they'll unlock)
    preview = [
        ("📈", "Skill Scores", "See all 7 skill scores vs. benchmarks"),
        ("📊", "Gap Analysis", "Interactive bar & radar charts"),
        ("🗺️", "Roadmap Progress", "Track weekly learning milestones"),
        ("💪", "Strengths", "Your top and bottom skills highlighted"),
    ]
    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(preview):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                             border-radius:14px;padding:1.1rem;text-align:center;
                             opacity:0.55;filter:blur(0.3px);">
                    <div style="font-size:1.4rem;margin-bottom:0.4rem;">{icon}</div>
                    <div style="font-size:0.82rem;font-weight:600;color:#d1d1db;
                                 margin-bottom:0.2rem;">{title}</div>
                    <div style="font-size:0.72rem;color:rgba(255,255,255,0.35);
                                 line-height:1.4;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:1.5rem;text-align:center;'>", unsafe_allow_html=True)
    col_center = st.columns([2, 2, 2])[1]
    with col_center:
        st.page_link("pages/3_Assessment.py", label="📝 Start your assessment", icon="📝")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Load gap data
# ---------------------------------------------------------------------------
if db:
    gap_summary = get_gap_summary(scores, profile.career_path, db)
    targets = {g.skill_name: g.target for g in gap_summary}
    st.session_state["skill_gaps"] = gap_summary
else:
    gap_summary = []
    targets = {}

# ---------------------------------------------------------------------------
# Metric cards — Row 1
# ---------------------------------------------------------------------------
total_tasks = len(flatten_tasks(roadmap)) if roadmap else 0
completion_pct = (
    get_completion_percentage(profile.student_id, total_tasks, db)
    if db and total_tasks > 0 else 0.0
)
avg_score = round(sum(scores.values()) / len(scores), 1) if scores else 0.0
high_gaps = sum(1 for g in gap_summary if g.priority == "High")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Student", profile.full_name)
with col2:
    st.metric("Career Path", profile.career_path)
with col3:
    delta_label = "meets targets 🟢" if avg_score >= 70 else "below target 🟡"
    st.metric("Avg Score", f"{avg_score}/100", delta=delta_label)
with col4:
    pct_label = f"{completion_pct}%" if total_tasks > 0 else "No roadmap yet"
    st.metric("Roadmap Progress", pct_label)

st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2 — Strongest & weakest skills
# ---------------------------------------------------------------------------
if scores:
    strongest, weakest = identify_strongest_weakest(scores, n=2)
    col_s, col_w = st.columns(2)

    with col_s:
        st.markdown(
            "<h3 style='margin-bottom:0.75rem;'>💪 Strongest Skills</h3>",
            unsafe_allow_html=True,
        )
        for skill in strongest:
            score_val = scores.get(skill, 0)
            bar_pct = int(score_val)
            st.markdown(
                f"""
                <div style="background:#12121c;border:1px solid rgba(16,185,129,0.2);
                             border-radius:12px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;
                                 align-items:center;margin-bottom:0.5rem;">
                        <span style="font-size:0.87rem;font-weight:600;
                                      color:rgba(255,255,255,0.85);">
                            {skill.replace('_', ' ')}
                        </span>
                        <span style="font-size:0.87rem;font-weight:700;color:#10b981;">
                            {score_val:.0f}/100
                        </span>
                    </div>
                    <div style="background:rgba(255,255,255,0.07);border-radius:99px;height:4px;">
                        <div style="background:linear-gradient(90deg,#10b981,#34d399);
                                     width:{bar_pct}%;height:4px;border-radius:99px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_w:
        st.markdown(
            "<h3 style='margin-bottom:0.75rem;'>⚠️ Needs Improvement</h3>",
            unsafe_allow_html=True,
        )
        for skill in weakest:
            score_val = scores.get(skill, 0)
            gap_val = next((g.gap for g in gap_summary if g.skill_name == skill), 0)
            bar_pct = int(score_val)
            st.markdown(
                f"""
                <div style="background:#12121c;border:1px solid rgba(245,158,11,0.2);
                             border-radius:12px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;
                                 align-items:center;margin-bottom:0.5rem;">
                        <span style="font-size:0.87rem;font-weight:600;
                                      color:rgba(255,255,255,0.85);">
                            {skill.replace('_', ' ')}
                        </span>
                        <div style="display:flex;gap:0.5rem;align-items:center;">
                            <span style="font-size:0.72rem;color:rgba(239,68,68,0.85);
                                          background:rgba(239,68,68,0.1);border-radius:5px;
                                          padding:0.1rem 0.45rem;">
                                gap {gap_val:.0f}
                            </span>
                            <span style="font-size:0.87rem;font-weight:700;
                                          color:#f59e0b;">{score_val:.0f}/100</span>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.07);border-radius:99px;height:4px;">
                        <div style="background:linear-gradient(90deg,#f59e0b,#fbbf24);
                                     width:{bar_pct}%;height:4px;border-radius:99px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("<div style='margin-top:0.25rem;'></div>", unsafe_allow_html=True)
st.divider()

# ---------------------------------------------------------------------------
# Row 3 — Charts
# ---------------------------------------------------------------------------
if scores and targets:
    st.markdown(
        "<h3 style='margin-bottom:1rem;'>📊 Skill Scores vs. Targets</h3>",
        unsafe_allow_html=True,
    )
    chart_type = st.radio(
        "Visualisation",
        ["Bar Chart", "Radar Chart"],
        horizontal=True,
        key="dash_chart",
        label_visibility="collapsed",
    )
    if chart_type == "Bar Chart":
        st.plotly_chart(skill_bar_chart(scores, targets), use_container_width=True)
    else:
        st.plotly_chart(skill_radar_chart(scores, targets), use_container_width=True)

# ---------------------------------------------------------------------------
# Row 4 — Roadmap progress
# ---------------------------------------------------------------------------
if roadmap and db:
    st.divider()
    st.markdown(
        "<h3 style='margin-bottom:1rem;'>🗺️ Roadmap Progress</h3>",
        unsafe_allow_html=True,
    )
    completed_by_week = get_completed_by_week(profile.student_id, roadmap, db)
    total_by_week = {w.week_number: sum(len(d.tasks) for d in w.days) for w in roadmap}
    st.plotly_chart(
        roadmap_progress_chart(completed_by_week, total_by_week),
        use_container_width=True,
    )
elif not roadmap:
    st.divider()
    st.markdown(
        """
        <div style="background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.18);
                     border-radius:14px;padding:1.1rem 1.4rem;display:flex;
                     align-items:center;gap:1rem;max-width:480px;">
            <span style="font-size:1.5rem;">🗺️</span>
            <div>
                <div style="font-size:0.87rem;font-weight:600;color:#a5b4fc;
                             margin-bottom:0.2rem;">No roadmap yet</div>
                <div style="font-size:0.78rem;color:rgba(255,255,255,0.4);">
                    Generate your roadmap from the Recommendations page to track
                    weekly progress here.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/5_Recommendations.py", label="💡 Go to Recommendations", icon="💡")
