"""
5_Recommendations.py — Personalized Learning Recommendations page for SkillPilot AI.
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from modules.skill_gap import get_gap_summary
from modules.recommendations import generate_activities
from modules.roadmap import generate_roadmap, flatten_tasks

st.set_page_config(page_title="Recommendations — SkillPilot AI", page_icon="💡", layout="wide")
st.title("💡 Personalized Learning Recommendations")

db = st.session_state.get("db")
profile = st.session_state.get("active_profile")
scores = st.session_state.get("skill_scores", {})
llm_client = st.session_state.get("llm_client")

if not profile:
    st.warning("Please create your profile first.")
    st.page_link("pages/2_Profile.py", label="👤 Go to Profile")
    st.stop()

if not scores:
    st.info("Complete your skill assessment to get recommendations.")
    st.page_link("pages/3_Assessment.py", label="📝 Go to Assessment")
    st.stop()

# ---------------------------------------------------------------------------
# Compute gaps & generate activities
# ---------------------------------------------------------------------------
gap_summary = get_gap_summary(scores, profile.career_path, db)
st.session_state["skill_gaps"] = gap_summary

resources = db.load_learning_resources() if db else []
activities = generate_activities(gap_summary, resources, llm_client)
st.session_state["activities"] = activities

if llm_client:
    st.caption("✨ AI-enriched recommendations enabled")
else:
    st.caption("🔌 Offline mode — curated resource recommendations")

# ---------------------------------------------------------------------------
# No gaps case
# ---------------------------------------------------------------------------
if not activities:
    st.success(
        "🎉 Outstanding! You've met all target scores for your career path. "
        "No skill gaps detected. Focus on building projects to strengthen your portfolio."
    )
    st.page_link("pages/7_Projects.py", label="📁 Browse Project Ideas")
    st.stop()

# ---------------------------------------------------------------------------
# Activity cards
# ---------------------------------------------------------------------------
priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}

st.subheader(f"{len(activities)} Learning Activities — ordered by priority")
st.caption("Expand each card to see exercises, mini-projects, and resources.")

for activity in activities:
    icon = priority_icon.get(activity.priority, "⚪")
    header = f"{icon} **{activity.skill_name.replace('_', ' ')}** — {activity.topic} · Gap: {activity.gap_value:.0f} pts"

    with st.expander(header, expanded=(activity.priority == "High")):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**🎯 Objective:** {activity.objective}")
            st.markdown(f"**📝 Exercise:** {activity.exercise}")
            st.markdown(f"**🔨 Mini-Project:** {activity.mini_project}")
        with col2:
            st.metric("Priority", activity.priority)
            st.metric("Est. Time", f"{activity.estimated_hours:.0f} hrs")

        st.markdown(
            f"📚 **Resource:** [{activity.resource_title}]({activity.resource_url})"
        )

        if llm_client:
            st.caption("✨ AI-enriched")

st.divider()

# ---------------------------------------------------------------------------
# Generate roadmap button
# ---------------------------------------------------------------------------
st.subheader("🗺️ Generate Your Learning Roadmap")
st.write("Click below to create a personalised weekly roadmap from these recommendations.")

if st.button("🚀 Generate Roadmap", type="primary"):
    roadmap = generate_roadmap(activities)
    st.session_state["roadmap"] = roadmap

    # Persist roadmap
    if db and roadmap:
        roadmap_data = [w.to_dict() for w in roadmap]
        db.save_roadmap(profile.student_id, roadmap_data)

    total = len(flatten_tasks(roadmap))
    st.success(f"✅ Roadmap generated! {len(roadmap)} week(s) · {total} tasks total.")
    st.page_link("pages/6_Roadmap.py", label="🗺️ View Your Roadmap")
