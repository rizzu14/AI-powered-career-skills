"""
4_Gap_Analysis.py — Skill Gap Analysis page for SkillPilot AI.
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
from modules.skill_gap import get_gap_summary
from modules.visualizations import skill_bar_chart, skill_radar_chart, gap_heatmap

st.set_page_config(page_title="Gap Analysis — SkillPilot AI", page_icon="📊", layout="wide")
st.title("📊 Skill Gap Analysis")
st.caption(
    "Target scores are project-defined learning benchmarks, not official industry standards "
    "or guarantees of employability."
)

db = st.session_state.get("db")
profile = st.session_state.get("active_profile")
scores = st.session_state.get("skill_scores", {})

if not profile:
    st.warning("Please create your profile first.")
    st.page_link("pages/2_Profile.py", label="👤 Go to Profile")
    st.stop()

if not scores:
    st.info("Complete your skill assessment to see gap analysis.")
    st.page_link("pages/3_Assessment.py", label="📝 Go to Assessment")
    st.stop()

# ---------------------------------------------------------------------------
# Compute gaps
# ---------------------------------------------------------------------------
gap_summary = get_gap_summary(scores, profile.career_path, db)
st.session_state["skill_gaps"] = gap_summary

targets = {g.skill_name: g.target for g in gap_summary}

# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
st.subheader("Skill Gap Summary")

PRIORITY_COLORS = {"High": "🔴", "Medium": "🟡", "Low": "🟢", "": "✅"}

rows = []
for g in gap_summary:
    rows.append({
        "Skill": g.skill_name.replace("_", " "),
        "Your Score": f"{g.score:.0f}",
        "Target Score": f"{g.target:.0f}",
        "Gap": f"{g.gap:.0f}",
        "Priority": f"{PRIORITY_COLORS.get(g.priority, '')} {g.priority}" if g.priority else "✅ Met",
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

# Export
csv = df.to_csv(index=False)
st.download_button("⬇️ Export to CSV", csv, "skill_gap_analysis.csv", "text/csv")

st.divider()

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
chart_choice = st.radio(
    "Choose chart type", ["Bar Chart", "Radar Chart", "Gap Heatmap"],
    horizontal=True, key="gap_chart",
)

if chart_choice == "Bar Chart":
    st.plotly_chart(skill_bar_chart(scores, targets), use_container_width=True)
elif chart_choice == "Radar Chart":
    st.plotly_chart(skill_radar_chart(scores, targets), use_container_width=True)
else:
    gaps_dict = {g.skill_name: g.gap for g in gap_summary}
    st.plotly_chart(gap_heatmap(gaps_dict), use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Insights callout
# ---------------------------------------------------------------------------
high_gaps = [g for g in gap_summary if g.priority == "High"]
zero_gaps = [g for g in gap_summary if g.gap == 0]

if not any(g.gap > 0 for g in gap_summary):
    st.success(
        "🎉 Great news — you've met all target scores for your career path! "
        "Keep building projects to solidify your skills."
    )
elif high_gaps:
    st.warning(
        f"🔴 **{len(high_gaps)} high-priority gap(s):** "
        + ", ".join(g.skill_name.replace("_", " ") for g in high_gaps)
        + ". Focus on these first."
    )

if zero_gaps:
    st.info(
        f"✅ **Skills meeting the target:** "
        + ", ".join(g.skill_name.replace("_", " ") for g in zero_gaps)
    )

st.divider()
st.info("👉 Next: get personalised learning recommendations.")
st.page_link("pages/5_Recommendations.py", label="💡 Go to Recommendations")
