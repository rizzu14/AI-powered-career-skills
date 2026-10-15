"""
2_Profile.py — Student Profile creation and editing page.
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from models.data_models import StudentProfile

st.set_page_config(page_title="Profile — SkillPilot AI", page_icon="👤", layout="centered")
st.title("👤 Student Profile")

db = st.session_state.get("db")
profile: StudentProfile | None = st.session_state.get("active_profile")

# Pre-fill from existing profile
existing = profile.to_dict() if profile else {}

with st.form("profile_form"):
    st.subheader("Personal & Academic Details")
    full_name = st.text_input("Full Name *", value=existing.get("full_name", ""))
    department = st.text_input("Department *", value=existing.get("department", ""))

    col1, col2 = st.columns(2)
    with col1:
        semester = st.selectbox(
            "Semester *",
            options=list(range(1, 9)),
            index=int(existing.get("semester", 1)) - 1,
        )
    with col2:
        skill_level = st.selectbox(
            "Current Skill Level *",
            options=["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(
                existing.get("skill_level", "Beginner")
            ),
        )

    st.subheader("Career & Learning Preferences")
    career_path = st.selectbox(
        "Target Career Path *",
        options=["Data Analyst", "Data Scientist", "Business Analyst"],
        index=["Data Analyst", "Data Scientist", "Business Analyst"].index(
            existing.get("career_path", "Data Analyst")
        ) if existing.get("career_path") in ["Data Analyst", "Data Scientist", "Business Analyst"] else 0,
    )
    learning_goals = st.text_area(
        "Learning Goals *",
        value=existing.get("learning_goals", ""),
        placeholder="e.g. Get an internship in data analytics by next semester",
    )
    learning_preferences = st.selectbox(
        "Learning Preferences *",
        options=["Video", "Article", "Project-based", "Mixed"],
        index=["Video", "Article", "Project-based", "Mixed"].index(
            existing.get("learning_preferences", "Mixed")
        ),
    )

    submitted = st.form_submit_button("💾 Save Profile", type="primary")

if submitted:
    # Validate required fields
    errors = []
    if not full_name.strip():
        errors.append("Full Name is required.")
    if not department.strip():
        errors.append("Department is required.")
    if not learning_goals.strip():
        errors.append("Learning Goals are required.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        import datetime
        now = datetime.datetime.utcnow().isoformat()
        if profile:
            # Update existing
            profile.full_name = full_name.strip()
            profile.department = department.strip()
            profile.semester = semester
            profile.skill_level = skill_level
            profile.career_path = career_path
            profile.learning_goals = learning_goals.strip()
            profile.learning_preferences = learning_preferences
            profile.updated_at = now
        else:
            profile = StudentProfile(
                full_name=full_name.strip(),
                department=department.strip(),
                semester=semester,
                skill_level=skill_level,
                career_path=career_path,
                learning_goals=learning_goals.strip(),
                learning_preferences=learning_preferences,
            )

        if db:
            db.save_profile(profile.to_dict())
        st.session_state["active_profile"] = profile
        st.success("✅ Profile saved successfully!")
        st.rerun()

# Show currently loaded profiles for switching
st.divider()
st.subheader("Existing Profiles")
if db:
    all_profiles = db.load_all_profiles()
    if all_profiles:
        for p in all_profiles:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(f"**{p.get('full_name')}** — {p.get('department')} · Sem {p.get('semester')}")
            with col_b:
                if st.button("Load", key=f"load_{p.get('student_id')}"):
                    try:
                        loaded = StudentProfile.from_dict(p)
                        st.session_state["active_profile"] = loaded
                        # Reset assessment state when switching profiles
                        st.session_state["skill_scores"] = {}
                        st.session_state["assessment_done"] = False
                        st.session_state["skill_gaps"] = []
                        st.session_state["activities"] = []
                        st.session_state["roadmap"] = []
                        scores = db.load_scores(loaded.student_id)
                        if scores:
                            st.session_state["skill_scores"] = scores
                            st.session_state["assessment_done"] = True
                        st.success(f"Loaded profile: {loaded.full_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not load profile: {e}")
    else:
        st.info("No saved profiles yet.")
