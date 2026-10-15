"""
3_Assessment.py — Skill Assessment page for SkillPilot AI.
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import datetime
import streamlit as st
from modules.assessment import SKILLS, get_assessment_questions, validate_assessment, compute_skill_scores

st.set_page_config(page_title="Assessment — SkillPilot AI", page_icon="📝", layout="wide")
st.title("📝 Skill Assessment")
st.caption(
    "Rate each skill honestly. Your scores are used to calculate skill gaps and personalise your learning plan."
)

db = st.session_state.get("db")
profile = st.session_state.get("active_profile")

if not profile:
    st.warning("Please create your profile first.")
    st.page_link("pages/2_Profile.py", label="👤 Go to Profile")
    st.stop()

# ---------------------------------------------------------------------------
# Build assessment form
# ---------------------------------------------------------------------------
st.subheader(f"Assessment for: {profile.career_path}")
st.info(
    "For each skill, move the slider to reflect your current level, then answer the optional quiz question.",
    icon="ℹ️",
)

responses: dict[str, dict] = {}

for skill in SKILLS:
    questions = get_assessment_questions(skill)
    label = skill.replace("_", " ")

    with st.expander(f"**{label}**", expanded=True):
        slider_q = next((q for q in questions if q["type"] == "slider"), None)
        mcq_q = next((q for q in questions if q["type"] == "mcq"), None)

        slider_val = None
        mcq_val = None

        if slider_q:
            slider_val = st.slider(
                slider_q["prompt"],
                min_value=0, max_value=10, value=5,
                key=f"slider_{skill}",
            )

        if mcq_q:
            opts = mcq_q.get("options", {})
            option_list = [f"{k}: {v}" for k, v in opts.items()]
            choice = st.radio(
                mcq_q["prompt"],
                options=["(skip)"] + option_list,
                key=f"mcq_{skill}",
            )
            if choice != "(skip)":
                mcq_val = choice[0]  # Extract letter "A", "B", etc.

        responses[skill] = {}
        if slider_val is not None:
            responses[skill]["slider"] = slider_val
        if mcq_val is not None:
            responses[skill]["mcq"] = mcq_val
        if not responses[skill]:
            responses[skill] = None  # type: ignore

st.divider()

# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------
if st.button("🚀 Submit Assessment", type="primary"):
    # Validate — ensure all skills have at least a slider response
    flat_responses = {
        skill: (resp if resp else None)
        for skill, resp in responses.items()
    }
    missing = [skill for skill, v in flat_responses.items() if v is None]
    if missing:
        st.error(f"Please provide a response for: {', '.join(s.replace('_', ' ') for s in missing)}")
    else:
        scores = compute_skill_scores(flat_responses)
        timestamp = datetime.datetime.utcnow().isoformat()

        if db:
            db.save_scores(profile.student_id, scores, timestamp)

        st.session_state["skill_scores"] = scores
        st.session_state["assessment_done"] = True
        # Reset downstream state when re-assessed
        st.session_state["skill_gaps"] = []
        st.session_state["activities"] = []

        st.success("✅ Assessment submitted! Your scores have been saved.")

        # Show results table
        st.subheader("Your Skill Scores")
        score_data = [
            {"Skill": skill.replace("_", " "), "Score": f"{score:.0f}/100"}
            for skill, score in sorted(scores.items(), key=lambda x: -x[1])
        ]
        st.table(score_data)

        st.info("👉 Next: view your **Gap Analysis** to see where you need to improve.")
        st.page_link("pages/4_Gap_Analysis.py", label="📊 Go to Gap Analysis")
