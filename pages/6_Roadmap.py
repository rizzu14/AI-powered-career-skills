"""
6_Roadmap.py — Learning Roadmap page for SkillPilot AI.
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from models.data_models import RoadmapWeek
from modules.progress import (
    mark_task,
    get_completion_percentage,
    get_week_completion,
    get_completed_by_week,
)
from modules.roadmap import flatten_tasks, generate_roadmap
from modules.visualizations import roadmap_progress_chart

st.set_page_config(page_title="Roadmap — SkillPilot AI", page_icon="🗺️", layout="wide")
st.title("🗺️ Learning Roadmap")

db = st.session_state.get("db")
profile = st.session_state.get("active_profile")
roadmap: list[RoadmapWeek] = st.session_state.get("roadmap", [])
activities = st.session_state.get("activities", [])

if not profile:
    st.warning("Please create your profile first.")
    st.page_link("pages/2_Profile.py", label="👤 Go to Profile")
    st.stop()

# ---------------------------------------------------------------------------
# Try to load saved roadmap if session has none
# ---------------------------------------------------------------------------
if not roadmap and db:
    raw_roadmap = db.load_roadmap(profile.student_id)
    if raw_roadmap:
        try:
            roadmap = [RoadmapWeek.from_dict(w) for w in raw_roadmap]
            st.session_state["roadmap"] = roadmap
        except Exception:
            roadmap = []

if not roadmap:
    st.info("No roadmap found. Generate one from the Recommendations page.")
    st.page_link("pages/5_Recommendations.py", label="💡 Go to Recommendations")
    st.stop()

# ---------------------------------------------------------------------------
# Overall progress metrics
# ---------------------------------------------------------------------------
all_tasks = flatten_tasks(roadmap)
total_tasks = len(all_tasks)
completion_pct = get_completion_percentage(profile.student_id, total_tasks, db) if db else 0.0

col1, col2, col3 = st.columns(3)
col1.metric("📅 Total Weeks", len(roadmap))
col2.metric("✅ Total Tasks", total_tasks)
col3.metric("📈 Overall Progress", f"{completion_pct}%")

st.progress(completion_pct / 100.0)
st.divider()

# ---------------------------------------------------------------------------
# Progress chart
# ---------------------------------------------------------------------------
if db:
    completed_by_week = get_completed_by_week(profile.student_id, roadmap, db)
    total_by_week = {w.week_number: sum(len(d.tasks) for d in w.days) for w in roadmap}
    st.plotly_chart(
        roadmap_progress_chart(completed_by_week, total_by_week),
        use_container_width=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Week accordions with daily checklists
# ---------------------------------------------------------------------------
st.subheader("Weekly Tasks")

for week in roadmap:
    week_done = get_week_completion(profile.student_id, week, db) if db else False
    milestone_icon = "🏆" if week_done else "📅"
    header = f"{milestone_icon} Week {week.week_number} — {week.milestone}"

    week_task_count = sum(len(d.tasks) for d in week.days)
    week_completed = sum(
        1 for d in week.days for t in d.tasks
        if (db.load_task_statuses(profile.student_id) if db else {}).get(t.task_id, False)
    )
    week_pct = round((week_completed / week_task_count) * 100) if week_task_count else 0

    with st.expander(f"{header} · {week_pct}% complete", expanded=(week.week_number == 1)):
        st.caption(f"🎯 Milestone: {week.milestone}")
        st.caption(f"📋 Checkpoint: {week.checkpoint}")

        if week_done:
            st.success("🏆 Week complete!")

        for day in week.days:
            st.markdown(f"**Day {day.day_number}**")
            for task in day.tasks:
                current_status = (
                    db.load_task_statuses(profile.student_id).get(task.task_id, False)
                    if db else False
                )
                new_status = st.checkbox(
                    f"{task.description} *(~{task.hours_allocated:.1f}h)*",
                    value=current_status,
                    key=f"task_{task.task_id}",
                )
                if new_status != current_status and db:
                    mark_task(profile.student_id, task.task_id, new_status, db)
                    st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Regenerate roadmap
# ---------------------------------------------------------------------------
st.subheader("⚙️ Regenerate Roadmap")
st.caption("This will replace your current roadmap. Your completed task history will be lost.")

if st.button("🔄 Regenerate Roadmap"):
    if not activities:
        st.warning("No activities found. Please regenerate from the Recommendations page first.")
    else:
        confirm = st.warning(
            "Are you sure? This will replace your current roadmap and reset all progress checkboxes."
        )
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("✅ Yes, regenerate", key="confirm_regen"):
                new_roadmap = generate_roadmap(activities)
                st.session_state["roadmap"] = new_roadmap
                if db:
                    db.save_roadmap(profile.student_id, [w.to_dict() for w in new_roadmap])
                st.success("Roadmap regenerated!")
                st.rerun()
        with col_no:
            if st.button("❌ Cancel", key="cancel_regen"):
                st.rerun()
