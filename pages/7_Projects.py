"""
7_Projects.py — Project Recommendations page for SkillPilot AI.
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from models.data_models import ProjectRecommendation
from modules.recommendations import rank_projects
from modules.skill_gap import get_gap_summary

st.set_page_config(page_title="Projects — SkillPilot AI", page_icon="📁", layout="wide")
st.title("📁 Beginner Project Recommendations")
st.caption(
    "These projects are designed to help you apply your learning and build a portfolio. "
    "Projects are ranked by how well they address your highest skill gaps."
)

db = st.session_state.get("db")
profile = st.session_state.get("active_profile")
scores = st.session_state.get("skill_scores", {})

if not profile:
    st.warning("Please create your profile first.")
    st.page_link("pages/2_Profile.py", label="👤 Go to Profile")
    st.stop()

# ---------------------------------------------------------------------------
# Load & rank projects
# ---------------------------------------------------------------------------
raw_projects = db.load_projects() if db else []
projects = [ProjectRecommendation.from_dict(p) for p in raw_projects]

if scores and db:
    gap_summary = get_gap_summary(scores, profile.career_path, db)
    projects = rank_projects(gap_summary, projects)
else:
    gap_summary = []

if not projects:
    st.warning("No projects found. Please check that `data/projects.json` exists.")
    st.stop()

# ---------------------------------------------------------------------------
# Top 3 recommended projects
# ---------------------------------------------------------------------------
st.subheader("🌟 Top Recommended Projects for You")

top_projects = projects[:3]
for i, project in enumerate(top_projects, start=1):
    relevance = int(project.relevance_score)
    relevance_label = "⭐" * min(relevance, 5) if relevance > 0 else "General practice"

    with st.container():
        col_num, col_content = st.columns([1, 11])
        with col_num:
            st.markdown(f"### {i}")
        with col_content:
            st.subheader(project.name)
            st.caption(f"Relevance to your gaps: {relevance_label}")
            st.write(f"**🎯 Objective:** {project.objective}")

            # Skill badges
            skill_badges = " ".join(
                f"`{s.replace('_', ' ')}`" for s in project.required_skills
            )
            st.markdown(f"**🛠️ Skills needed:** {skill_badges}")

            tool_badges = " · ".join(project.tools)
            st.markdown(f"**🔧 Tools:** {tool_badges}")

            st.write(f"**📤 Expected output:** {project.expected_output}")

        st.divider()

# ---------------------------------------------------------------------------
# All projects toggle
# ---------------------------------------------------------------------------
with st.expander("📋 Show all projects"):
    remaining = projects[3:]
    if not remaining:
        st.info("All projects are already shown above.")
    else:
        for project in remaining:
            st.markdown(f"**{project.name}**")
            st.write(f"*{project.objective}*")
            st.write(
                f"Skills: {', '.join(s.replace('_', ' ') for s in project.required_skills)} · "
                f"Tools: {', '.join(project.tools)}"
            )
            st.write(f"Output: {project.expected_output}")
            st.divider()

# ---------------------------------------------------------------------------
# Tips
# ---------------------------------------------------------------------------
st.subheader("💡 Tips for Getting Started")
st.markdown("""
- **Start small** — pick the project that matches your current skill level.
- **Use public datasets** — Kaggle, UCI ML Repository, and data.gov are great sources.
- **Document everything** — add comments and a README to every project.
- **Share your work** — upload to GitHub to build your portfolio.
""")
