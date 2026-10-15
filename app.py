"""
app.py — SkillPilot AI entry point.

Run with:  streamlit run app.py
"""

# ── sys.path MUST be set before any local package imports ──
import sys
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
# Propagate to sub-processes / Streamlit page runner
os.environ.setdefault("PYTHONPATH", str(_ROOT))

import streamlit as st

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SkillPilot AI — Personalized Skill-Gap Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Premium design system — injected globally on every page
# ---------------------------------------------------------------------------
PREMIUM_CSS = """
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
}

/* ── App background ── */
.stApp { background: #0B0D12 !important; }

/* ── Main content padding ── */
section[data-testid="stMainBlockContainer"] > div {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #10131A !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.4rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
[data-testid="stSidebarNav"] a {
    border-radius: 10px !important;
    padding: 0.52rem 0.85rem !important;
    margin-bottom: 2px !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    color: rgba(255,255,255,0.55) !important;
    font-size: 0.855rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.005em !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255,255,255,0.06) !important;
    color: rgba(255,255,255,0.9) !important;
}
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: rgba(77,141,255,0.15) !important;
    color: #7EB5FF !important;
}

/* ── Typography ── */
h1 {
    font-size: 1.8rem !important; font-weight: 700 !important;
    letter-spacing: -0.03em !important; color: #F5F7FA !important;
    margin-bottom: 0.15rem !important;
}
h2 { font-size: 1.15rem !important; font-weight: 600 !important;
     color: #C8CDD8 !important; letter-spacing: -0.015em !important; }
h3 { font-size: 0.97rem !important; font-weight: 600 !important; color: #A1A9B8 !important; }
p, .stMarkdown p {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.88rem !important; line-height: 1.65 !important;
}
[data-testid="stCaptionContainer"] p {
    color: rgba(255,255,255,0.35) !important; font-size: 0.78rem !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #151922 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.4rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(77,141,255,0.25) !important;
    box-shadow: 0 6px 28px rgba(0,0,0,0.4) !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.4) !important; font-size: 0.72rem !important;
    font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] {
    color: #F5F7FA !important; font-size: 1.45rem !important;
    font-weight: 700 !important; letter-spacing: -0.02em !important;
}

/* ── Dividers ── */
hr { border: none !important; border-top: 1px solid rgba(255,255,255,0.06) !important; margin: 1.4rem 0 !important; }

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3B6FE0 0%, #4D8DFF 100%) !important;
    border: none !important; border-radius: 12px !important; color: #fff !important;
    font-weight: 600 !important; font-size: 0.87rem !important; letter-spacing: 0.01em !important;
    padding: 0.58rem 1.4rem !important;
    box-shadow: 0 4px 16px rgba(77,141,255,0.35) !important;
    transition: all 0.16s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2B5BC4 0%, #3B6FE0 100%) !important;
    box-shadow: 0 6px 22px rgba(77,141,255,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary / ghost button ── */
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important; color: rgba(255,255,255,0.78) !important;
    font-weight: 500 !important; font-size: 0.87rem !important;
    transition: all 0.16s ease !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.18) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #151922 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important; margin-bottom: 0.65rem !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.22) !important; overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    color: rgba(255,255,255,0.82) !important; font-weight: 600 !important;
    font-size: 0.9rem !important; padding: 0.8rem 1rem !important;
}

/* ── Alert / callout ── */
[data-testid="stAlert"] { border-radius: 12px !important; border: none !important; }

/* ── Dataframe / table ── */
[data-testid="stDataFrame"], .stTable {
    border-radius: 14px !important; overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #1B202B !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: #1B202B !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #4D8DFF !important; border: 2px solid #7EB5FF !important;
}

/* ── Radio ── */
[data-testid="stRadio"] label { color: rgba(255,255,255,0.7) !important; font-size: 0.86rem !important; }

/* ── Plotly charts ── */
[data-testid="stPlotlyChart"] {
    background: #151922 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important; padding: 0.5rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.28) !important;
}

/* ── Page links ── */
a[data-testid="stPageLink-NavLink"] {
    background: rgba(77,141,255,0.1) !important; border: 1px solid rgba(77,141,255,0.22) !important;
    border-radius: 10px !important; color: #7EB5FF !important; font-weight: 600 !important;
    padding: 0.5rem 1rem !important; text-decoration: none !important;
    transition: all 0.15s ease !important;
}
a[data-testid="stPageLink-NavLink"]:hover { background: rgba(77,141,255,0.18) !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: rgba(255,255,255,0.7) !important; font-size: 0.82rem !important;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.07) !important; border-radius: 99px !important; height: 5px !important;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #3B6FE0, #4D8DFF) !important; border-radius: 99px !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label { color: rgba(255,255,255,0.73) !important; font-size: 0.87rem !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Landing page utility classes ── */
.sp-section { padding: 4rem 5vw; }
.sp-section-sm { padding: 2.5rem 5vw; }
.sp-center { text-align: center; }
</style>
"""

def inject_css() -> None:
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


# (sys.path already set at module top)

from modules.db_manager import DBManager
from modules.recommendations import get_llm_client
from models.data_models import StudentProfile


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def init_session_state() -> None:
    defaults = {
        "active_profile": None,
        "skill_scores": {},
        "skill_gaps": [],
        "activities": [],
        "roadmap": [],
        "task_statuses": {},
        "assessment_done": False,
        "llm_client": None,
        "db": None,
        "show_landing": True,   # True = show landing, False = go into app
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_active_profile(db: DBManager) -> StudentProfile | None:
    profiles = db.load_all_profiles()
    if not profiles:
        samples = db.load_sample_students()
        for s in samples:
            db.save_profile(s)
        profiles = db.load_sample_students()
    if not profiles:
        return None
    raw = profiles[-1]
    try:
        return StudentProfile.from_dict(raw)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Landing page sections
# ---------------------------------------------------------------------------

def _nav_bar(profile_name: str | None) -> None:
    """Top navigation bar for the landing page."""
    cta_label = f"Go to Dashboard  →" if profile_name else "Get Started  →"
    st.markdown(
        f"""
        <nav style="
            position:sticky;top:0;z-index:100;
            background:rgba(11,13,18,0.92);
            border-bottom:1px solid rgba(255,255,255,0.06);
            backdrop-filter:blur(16px);
            padding:0.85rem 5vw;
            display:flex;align-items:center;justify-content:space-between;
        ">
            <div style="display:flex;align-items:center;gap:0.6rem;">
                <span style="font-size:1.2rem;">🎯</span>
                <span style="font-size:1rem;font-weight:700;color:#F5F7FA;letter-spacing:-0.02em;">
                    SkillPilot AI
                </span>
            </div>
            <div style="display:flex;align-items:center;gap:1.5rem;">
                <a href="#features"
                   style="font-size:0.83rem;color:rgba(255,255,255,0.55);text-decoration:none;
                          font-weight:500;transition:color 0.15s;">Features</a>
                <a href="#how-it-works"
                   style="font-size:0.83rem;color:rgba(255,255,255,0.55);text-decoration:none;
                          font-weight:500;">How It Works</a>
                <a href="#about"
                   style="font-size:0.83rem;color:rgba(255,255,255,0.55);text-decoration:none;
                          font-weight:500;">About</a>
            </div>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def _hero_section(has_profile: bool, assessment_done: bool) -> bool:
    """Hero. Returns True if user clicked Get Started / Dashboard."""
    headline = "Close the Gap Between\nWhere You Are and\nWhere You Want to Be"
    subtitle = (
        "SkillPilot AI assesses your technical skills, reveals the exact gaps "
        "standing between you and your target career, and generates a personalised "
        "week-by-week learning roadmap to close them."
    )

    st.markdown(
        f"""
        <section style="
            padding: 6rem 5vw 4rem 5vw;
            background: radial-gradient(ellipse 80% 50% at 50% -10%,
                        rgba(77,141,255,0.12) 0%, transparent 70%);
            text-align: center;
        ">
            <div style="
                display:inline-block;
                background:rgba(77,141,255,0.1);
                border:1px solid rgba(77,141,255,0.22);
                border-radius:99px;
                padding:0.3rem 0.9rem;
                font-size:0.75rem;font-weight:600;
                color:#7EB5FF;letter-spacing:0.06em;
                text-transform:uppercase;margin-bottom:1.5rem;
            ">Personalized Skill-Gap Analyzer</div>

            <h1 style="
                font-size:clamp(2rem,5vw,3.4rem)!important;
                font-weight:800!important;
                letter-spacing:-0.04em!important;
                color:#F5F7FA!important;
                line-height:1.18!important;
                max-width:700px;margin:0 auto 1.25rem auto;
                white-space:pre-line;
            ">{headline}</h1>

            <p style="
                font-size:1.05rem;color:rgba(255,255,255,0.52);
                max-width:540px;margin:0 auto 2.5rem auto;line-height:1.7;
            ">{subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # CTA buttons using Streamlit so they're interactive
    _, c1, c2, _ = st.columns([3, 2, 2, 3])
    clicked = False
    with c1:
        label = "Go to Dashboard →" if assessment_done else ("Continue →" if has_profile else "Get Started →")
        if st.button(label, type="primary", use_container_width=True, key="hero_cta"):
            clicked = True
    with c2:
        if st.button("Explore Features ↓", use_container_width=True, key="hero_secondary"):
            pass  # page scrolls naturally

    # Dashboard mock preview
    st.markdown(
        """
        <div style="
            max-width:860px;margin:2rem auto 0 auto;
            background:#151922;border:1px solid rgba(255,255,255,0.08);
            border-radius:20px;overflow:hidden;
            box-shadow:0 24px 80px rgba(0,0,0,0.55),0 0 0 1px rgba(77,141,255,0.08);
        ">
            <!-- mock title bar -->
            <div style="
                background:#1B202B;padding:0.7rem 1.2rem;
                border-bottom:1px solid rgba(255,255,255,0.06);
                display:flex;align-items:center;gap:0.5rem;
            ">
                <span style="width:10px;height:10px;border-radius:50%;
                              background:#FF5F57;display:inline-block;"></span>
                <span style="width:10px;height:10px;border-radius:50%;
                              background:#FEBC2E;display:inline-block;margin-left:4px;"></span>
                <span style="width:10px;height:10px;border-radius:50%;
                              background:#28C840;display:inline-block;margin-left:4px;"></span>
                <span style="font-size:0.72rem;color:rgba(255,255,255,0.25);
                              margin-left:0.8rem;font-family:monospace;">
                    SkillPilot AI — Dashboard
                </span>
            </div>
            <!-- mock content -->
            <div style="padding:1.5rem;display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:0.9rem;">
                <!-- metric tiles -->
                <div style="background:#1B202B;border:1px solid rgba(255,255,255,0.06);
                             border-radius:12px;padding:1rem;">
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.35);
                                 text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.4rem;">
                        Career Path
                    </div>
                    <div style="font-size:0.95rem;font-weight:700;color:#F5F7FA;">Data Analyst</div>
                </div>
                <div style="background:#1B202B;border:1px solid rgba(255,255,255,0.06);
                             border-radius:12px;padding:1rem;">
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.35);
                                 text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.4rem;">
                        Avg Score
                    </div>
                    <div style="font-size:0.95rem;font-weight:700;color:#4D8DFF;">62 / 100</div>
                </div>
                <div style="background:#1B202B;border:1px solid rgba(255,255,255,0.06);
                             border-radius:12px;padding:1rem;">
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.35);
                                 text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.4rem;">
                        Skill Gaps
                    </div>
                    <div style="font-size:0.95rem;font-weight:700;color:#F59E0B;">4 active</div>
                </div>
                <div style="background:#1B202B;border:1px solid rgba(255,255,255,0.06);
                             border-radius:12px;padding:1rem;">
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.35);
                                 text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.4rem;">
                        Roadmap
                    </div>
                    <div style="font-size:0.95rem;font-weight:700;color:#10B981;">35%</div>
                </div>
            </div>
            <!-- mock skill bars -->
            <div style="padding:0 1.5rem 1.5rem 1.5rem;">
                <div style="font-size:0.72rem;color:rgba(255,255,255,0.3);
                             text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.8rem;">
                    Skill Overview
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">
                    {"".join([
                        f'''<div style="background:#1B202B;border-radius:8px;padding:0.65rem 0.85rem;">
                            <div style="display:flex;justify-content:space-between;
                                         margin-bottom:0.4rem;">
                                <span style="font-size:0.72rem;color:rgba(255,255,255,0.55);">{s}</span>
                                <span style="font-size:0.72rem;font-weight:600;color:{c};">{v}</span>
                            </div>
                            <div style="background:rgba(255,255,255,0.06);border-radius:99px;height:3px;">
                                <div style="background:{c};width:{v};height:3px;border-radius:99px;"></div>
                            </div>
                        </div>'''
                        for s, v, c in [
                            ("Python", "68%", "#4D8DFF"),
                            ("SQL", "55%", "#F59E0B"),
                            ("Data Viz", "72%", "#10B981"),
                            ("Statistics", "48%", "#EF4444"),
                        ]
                    ])}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return clicked


def _features_section() -> None:
    st.markdown(
        """
        <section id="features" style="padding:5rem 5vw;
            border-top:1px solid rgba(255,255,255,0.05);">
            <div style="text-align:center;margin-bottom:3rem;">
                <div style="display:inline-block;background:rgba(77,141,255,0.08);
                             border:1px solid rgba(77,141,255,0.18);border-radius:99px;
                             padding:0.3rem 0.9rem;font-size:0.72rem;font-weight:600;
                             color:#7EB5FF;letter-spacing:0.06em;text-transform:uppercase;
                             margin-bottom:1rem;">Platform Features</div>
                <h2 style="font-size:clamp(1.5rem,3vw,2.2rem)!important;font-weight:700!important;
                             letter-spacing:-0.03em!important;color:#F5F7FA!important;
                             max-width:520px;margin:0 auto 0.75rem auto;">
                    Everything you need to advance your career
                </h2>
                <p style="font-size:0.93rem;color:rgba(255,255,255,0.45);
                           max-width:420px;margin:0 auto;line-height:1.65;">
                    SkillPilot AI brings structured learning intelligence to your
                    skill development journey.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    features = [
        (
            "📊", "Skill Assessment",
            "Rate your proficiency across seven Data Analyst skills — Python, SQL, Excel, Statistics, "
            "Data Visualisation, Data Cleaning, and Analytical Thinking — using sliders and quick-check questions.",
        ),
        (
            "🔍", "Skill Gap Analysis",
            "Compare your scores against career-path benchmarks. Instantly see which skills "
            "have High, Medium, or Low gaps, visualised in interactive bar and radar charts.",
        ),
        (
            "💡", "Personalised Recommendations",
            "Every recommended learning activity is ranked by your actual gap size — "
            "topics, exercises, mini-projects, time estimates, and curated resource links tailored to you.",
        ),
        (
            "🗺️", "Learning Roadmap",
            "A week-by-week, day-by-day learning schedule generated from your recommendations. "
            "Mark tasks complete and track your progress milestone by milestone.",
        ),
        (
            "📁", "Project Suggestions",
            "Discover beginner Data Analyst portfolio projects ranked by relevance to your gaps — "
            "from EDA notebooks to sales dashboards — with objectives, tools, and expected outputs.",
        ),
        (
            "👤", "Profile Management",
            "Store your academic details, department, semester, skill level, career goal, "
            "and learning preferences. Your data persists across sessions automatically.",
        ),
    ]

    rows = [features[:3], features[3:]]
    for row in rows:
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, row):
            with col:
                st.markdown(
                    f"""
                    <div style="
                        background:#151922;border:1px solid rgba(255,255,255,0.07);
                        border-radius:18px;padding:1.6rem 1.5rem;margin-bottom:1rem;
                        box-shadow:0 4px 20px rgba(0,0,0,0.25);
                        transition:border-color 0.2s;
                    ">
                        <div style="
                            width:42px;height:42px;border-radius:11px;
                            background:rgba(77,141,255,0.1);
                            border:1px solid rgba(77,141,255,0.2);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.2rem;margin-bottom:1rem;
                        ">{icon}</div>
                        <div style="font-size:0.95rem;font-weight:600;color:#F5F7FA;
                                     margin-bottom:0.45rem;letter-spacing:-0.01em;">{title}</div>
                        <div style="font-size:0.8rem;color:rgba(255,255,255,0.42);line-height:1.6;">
                            {desc}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _how_it_works_section() -> None:
    steps = [
        ("01", "Create Your Profile",
         "Enter your name, department, semester, skill level, and career goal. "
         "Your profile personalises every part of the platform."),
        ("02", "Complete the Assessment",
         "Rate yourself on seven core Data Analyst skills and answer quick quiz questions. "
         "Takes under five minutes."),
        ("03", "Discover Your Gaps",
         "See your scores plotted against career benchmarks. High-priority gaps are "
         "flagged immediately so you know exactly where to focus."),
        ("04", "Get Recommendations",
         "Receive ranked learning activities — one per gap — with topics, exercises, "
         "mini-projects, time estimates, and resource links."),
        ("05", "Follow Your Roadmap",
         "A weekly schedule is generated from your recommendations. Check off daily tasks "
         "and watch your progress percentage climb."),
    ]

    st.markdown(
        """
        <section id="how-it-works" style="padding:5rem 5vw;
            background:linear-gradient(180deg,rgba(77,141,255,0.03) 0%,transparent 100%);
            border-top:1px solid rgba(255,255,255,0.05);">
            <div style="text-align:center;margin-bottom:3rem;">
                <div style="display:inline-block;background:rgba(16,185,129,0.08);
                             border:1px solid rgba(16,185,129,0.18);border-radius:99px;
                             padding:0.3rem 0.9rem;font-size:0.72rem;font-weight:600;
                             color:#34D399;letter-spacing:0.06em;text-transform:uppercase;
                             margin-bottom:1rem;">How It Works</div>
                <h2 style="font-size:clamp(1.5rem,3vw,2.2rem)!important;font-weight:700!important;
                             letter-spacing:-0.03em!important;color:#F5F7FA!important;
                             max-width:480px;margin:0 auto 0.75rem auto;">
                    From zero to roadmap in minutes
                </h2>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div style="text-align:center;padding:0 0.5rem 2rem 0.5rem;">
                    <div style="
                        width:48px;height:48px;border-radius:50%;
                        background:rgba(77,141,255,0.1);border:1px solid rgba(77,141,255,0.2);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.78rem;font-weight:700;color:#7EB5FF;
                        margin:0 auto 1rem auto;letter-spacing:0.02em;
                    ">{num}</div>
                    <div style="font-size:0.87rem;font-weight:600;color:#F5F7FA;
                                 margin-bottom:0.45rem;letter-spacing:-0.01em;">{title}</div>
                    <div style="font-size:0.75rem;color:rgba(255,255,255,0.38);line-height:1.6;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _about_section() -> None:
    st.markdown(
        """
        <section id="about" style="padding:4rem 5vw;border-top:1px solid rgba(255,255,255,0.05);">
            <div style="
                max-width:680px;margin:0 auto;text-align:center;
            ">
                <h2 style="font-size:1.4rem!important;font-weight:700!important;
                             color:#F5F7FA!important;letter-spacing:-0.02em!important;
                             margin-bottom:0.8rem!important;">About SkillPilot AI</h2>
                <p style="font-size:0.9rem;color:rgba(255,255,255,0.48);line-height:1.75;margin:0;">
                    SkillPilot AI is an academic mini-project built to bridge the gap between
                    classroom learning and industry expectations for Data Analyst roles.
                    It uses a rule-based recommendation engine — no paid AI API required —
                    backed by curated CSV datasets for skill requirements, learning resources,
                    and project suggestions.
                    Target scores are project-defined learning benchmarks and are not official
                    industry standards or guarantees of employability.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _cta_section() -> bool:
    st.markdown(
        """
        <section style="padding:5rem 5vw;text-align:center;
            background:radial-gradient(ellipse 70% 60% at 50% 50%,
                        rgba(77,141,255,0.09) 0%,transparent 75%);
            border-top:1px solid rgba(255,255,255,0.05);">
            <h2 style="font-size:clamp(1.6rem,3.5vw,2.4rem)!important;font-weight:800!important;
                         letter-spacing:-0.04em!important;color:#F5F7FA!important;
                         max-width:560px;margin:0 auto 0.8rem auto;">
                Start closing your skill gaps today
            </h2>
            <p style="font-size:0.95rem;color:rgba(255,255,255,0.45);
                       max-width:420px;margin:0 auto 2.5rem auto;line-height:1.65;">
                Create your profile, complete the assessment, and get a
                personalised roadmap in under ten minutes.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    _, c, _ = st.columns([3, 3, 3])
    with c:
        return st.button("Get Started — It's Free →", type="primary",
                         use_container_width=True, key="bottom_cta")


def _footer() -> None:
    st.markdown(
        """
        <footer style="
            padding:2rem 5vw;border-top:1px solid rgba(255,255,255,0.05);
            display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;
        ">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <span style="font-size:1rem;">🎯</span>
                <span style="font-size:0.85rem;font-weight:600;color:rgba(255,255,255,0.55);">
                    SkillPilot AI
                </span>
            </div>
            <div style="font-size:0.75rem;color:rgba(255,255,255,0.25);">
                Academic mini-project · target scores are learning benchmarks,
                not official industry standards.
            </div>
            <div style="display:flex;gap:1.5rem;">
                <a href="#features"
                   style="font-size:0.75rem;color:rgba(255,255,255,0.3);text-decoration:none;">
                    Features
                </a>
                <a href="#how-it-works"
                   style="font-size:0.75rem;color:rgba(255,255,255,0.3);text-decoration:none;">
                    How It Works
                </a>
                <a href="#about"
                   style="font-size:0.75rem;color:rgba(255,255,255,0.3);text-decoration:none;">
                    About
                </a>
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar — used in app mode (not on landing)
# ---------------------------------------------------------------------------

def _render_sidebar(profile: StudentProfile | None) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.2rem 0 0.9rem 0;">
                <div style="display:flex;align-items:center;gap:0.55rem;margin-bottom:0.25rem;">
                    <span style="font-size:1.3rem;">🎯</span>
                    <span style="font-size:1.05rem;font-weight:700;color:#F5F7FA;
                                 letter-spacing:-0.025em;">SkillPilot AI</span>
                </div>
                <p style="font-size:0.68rem;color:rgba(255,255,255,0.3);
                           margin:0;letter-spacing:0.06em;text-transform:uppercase;">
                    Skill-Gap Analyzer
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        if profile:
            level_color = {"Beginner": "#F59E0B", "Intermediate": "#4D8DFF", "Advanced": "#10B981"}.get(
                profile.skill_level, "#4D8DFF"
            )
            st.markdown(
                f"""
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                             border-radius:13px;padding:0.85rem 0.95rem;margin-bottom:0.5rem;">
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.35);
                                 text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.35rem;">
                        Active Student
                    </div>
                    <div style="font-size:0.93rem;font-weight:600;color:#F5F7FA;
                                 margin-bottom:0.2rem;">{profile.full_name}</div>
                    <div style="font-size:0.75rem;color:rgba(255,255,255,0.45);
                                 margin-bottom:0.35rem;">{profile.department} · Sem {profile.semester}</div>
                    <span style="display:inline-block;background:rgba(77,141,255,0.12);
                                  border:1px solid rgba(77,141,255,0.25);border-radius:5px;
                                  padding:0.12rem 0.55rem;font-size:0.68rem;font-weight:600;
                                  color:#7EB5FF;">{profile.career_path}</span>
                    <span style="display:inline-block;margin-left:0.35rem;
                                  background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);
                                  border-radius:5px;padding:0.12rem 0.55rem;font-size:0.68rem;
                                  font-weight:600;color:{level_color};">{profile.skill_level}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.18);
                             border-radius:11px;padding:0.75rem 0.9rem;font-size:0.8rem;
                             color:rgba(245,158,11,0.85);">⚠️ No profile loaded</div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Back to landing page button
        if st.button("← Back to Home", key="back_to_landing", use_container_width=True):
            st.session_state["show_landing"] = True
            st.rerun()

        if st.session_state.get("llm_client") is None:
            st.markdown(
                """
                <div style="margin-top:0.6rem;font-size:0.68rem;color:rgba(255,255,255,0.28);
                             display:flex;align-items:center;gap:0.35rem;">
                    <span style="width:5px;height:5px;border-radius:50%;background:#4D8DFF;
                                  display:inline-block;box-shadow:0 0 5px #4D8DFF;"></span>
                    Offline mode · curated resources
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# App home (post-landing onboarding hub)
# ---------------------------------------------------------------------------

def _render_app_home(profile: StudentProfile | None, assessment_done: bool) -> None:
    """The home page shown when user enters the app (after landing)."""

    # Page header
    greeting = f"Welcome back, {profile.full_name.split()[0]}" if profile else "Welcome to SkillPilot AI"
    st.markdown(
        f"""
        <div style="padding:2.5rem 2.5rem 0 2.5rem;">
            <h1 style="font-size:1.75rem!important;font-weight:700!important;
                        letter-spacing:-0.03em!important;color:#F5F7FA!important;
                        margin-bottom:0.2rem!important;">{greeting}</h1>
            <p style="font-size:0.87rem;color:rgba(255,255,255,0.38);margin:0;">
                Your personalised skill-development hub
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Step 1: No profile ──
    if profile is None:
        st.markdown(
            """
            <div style="padding:0 2.5rem;">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="
                background:linear-gradient(135deg,#151922 0%,#1B202B 100%);
                border:1px solid rgba(77,141,255,0.2);
                border-radius:20px;padding:2.5rem 2.5rem;max-width:580px;
                box-shadow:0 8px 32px rgba(0,0,0,0.35);
            ">
                <div style="
                    width:52px;height:52px;border-radius:14px;
                    background:rgba(77,141,255,0.1);border:1px solid rgba(77,141,255,0.2);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.4rem;margin-bottom:1.2rem;
                ">👤</div>
                <div style="font-size:1.2rem;font-weight:700;color:#F5F7FA;
                             letter-spacing:-0.02em;margin-bottom:0.5rem;">
                    Complete Your Profile
                </div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.45);
                             line-height:1.65;margin-bottom:1.5rem;max-width:400px;">
                    Tell SkillPilot AI about your academic background and career goal.
                    Your profile is used to personalise the assessment benchmarks,
                    recommendations, and roadmap.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/2_Profile.py", label="👤 Create your profile →", icon="👤")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Step 2: Profile exists, no assessment ──
    elif not assessment_done:
        st.markdown("<div style='padding:0 2.5rem;'>", unsafe_allow_html=True)

        # Progress indicator
        st.markdown(
            """
            <div style="
                display:flex;align-items:center;gap:0.7rem;
                margin-bottom:1.5rem;
            ">
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    background:#4D8DFF;display:flex;align-items:center;
                    justify-content:center;font-size:0.7rem;font-weight:700;color:#fff;
                ">1</div>
                <div style="font-size:0.78rem;font-weight:600;color:#4D8DFF;">Profile ✓</div>
                <div style="height:1px;width:40px;background:rgba(255,255,255,0.1);"></div>
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.7rem;font-weight:700;color:rgba(255,255,255,0.4);
                ">2</div>
                <div style="font-size:0.78rem;color:rgba(255,255,255,0.35);">Assessment</div>
                <div style="height:1px;width:40px;background:rgba(255,255,255,0.08);"></div>
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.7rem;font-weight:700;color:rgba(255,255,255,0.25);
                ">3</div>
                <div style="font-size:0.78rem;color:rgba(255,255,255,0.25);">Dashboard</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                background:linear-gradient(135deg,#151922 0%,#1B202B 100%);
                border:1px solid rgba(77,141,255,0.22);
                border-radius:20px;padding:2.5rem 2.5rem;max-width:620px;
                box-shadow:0 8px 32px rgba(0,0,0,0.35);
            ">
                <div style="
                    width:52px;height:52px;border-radius:14px;
                    background:rgba(77,141,255,0.12);border:1px solid rgba(77,141,255,0.25);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.4rem;margin-bottom:1.2rem;
                ">📝</div>
                <div style="font-size:1.2rem;font-weight:700;color:#F5F7FA;
                             letter-spacing:-0.02em;margin-bottom:0.5rem;">
                    Start Your Skill Assessment
                </div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.45);
                             line-height:1.65;margin-bottom:1.5rem;max-width:440px;">
                    Rate your proficiency in 7 Data Analyst skills using sliders and
                    quick-check questions. Your scores unlock a personalised gap analysis,
                    ranked recommendations, and a week-by-week learning roadmap.
                </div>
                <div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:1.5rem;">
                    <div style="display:flex;align-items:center;gap:0.45rem;">
                        <span style="font-size:0.8rem;color:#10B981;">✓</span>
                        <span style="font-size:0.78rem;color:rgba(255,255,255,0.45);">
                            Takes under 5 minutes
                        </span>
                    </div>
                    <div style="display:flex;align-items:center;gap:0.45rem;">
                        <span style="font-size:0.8rem;color:#10B981;">✓</span>
                        <span style="font-size:0.78rem;color:rgba(255,255,255,0.45);">
                            7 key skills assessed
                        </span>
                    </div>
                    <div style="display:flex;align-items:center;gap:0.45rem;">
                        <span style="font-size:0.8rem;color:#10B981;">✓</span>
                        <span style="font-size:0.78rem;color:rgba(255,255,255,0.45);">
                            Unlocks full dashboard
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/3_Assessment.py", label="📝 Start Assessment →", icon="📝")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Step 3: Assessment done — quick actions hub ──
    else:
        st.markdown("<div style='padding:0 2.5rem;'>", unsafe_allow_html=True)

        # Status bar
        st.markdown(
            """
            <div style="
                background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.18);
                border-radius:12px;padding:0.8rem 1.2rem;max-width:520px;
                display:flex;align-items:center;gap:0.8rem;margin-bottom:2rem;
            ">
                <span style="font-size:1rem;">🚀</span>
                <div>
                    <div style="font-size:0.85rem;font-weight:600;color:rgba(16,185,129,0.95);
                                 margin-bottom:0.1rem;">Assessment complete</div>
                    <div style="font-size:0.75rem;color:rgba(255,255,255,0.38);">
                        All features unlocked · head to Dashboard for your full overview
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick actions grid
        actions = [
            ("📊", "Dashboard", "Full skill overview and progress summary", "pages/1_Dashboard.py"),
            ("🔍", "Gap Analysis", "See your skill gaps and priority areas", "pages/4_Gap_Analysis.py"),
            ("💡", "Recommendations", "Get ranked learning activities", "pages/5_Recommendations.py"),
            ("🗺️", "Roadmap", "Follow your week-by-week learning plan", "pages/6_Roadmap.py"),
            ("📁", "Projects", "Explore beginner portfolio projects", "pages/7_Projects.py"),
            ("👤", "Profile", "Update your academic details", "pages/2_Profile.py"),
        ]

        st.markdown(
            "<div style='font-size:0.72rem;font-weight:600;color:rgba(255,255,255,0.3);"
            "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.9rem;'>"
            "Quick Actions</div>",
            unsafe_allow_html=True,
        )

        cols = st.columns(3)
        for i, (icon, title, desc, page) in enumerate(actions):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="
                        background:#151922;border:1px solid rgba(255,255,255,0.07);
                        border-radius:14px;padding:1.1rem 1.2rem;margin-bottom:0.75rem;
                        box-shadow:0 2px 12px rgba(0,0,0,0.2);
                    ">
                        <div style="font-size:1.2rem;margin-bottom:0.5rem;">{icon}</div>
                        <div style="font-size:0.88rem;font-weight:600;color:#F5F7FA;
                                     margin-bottom:0.25rem;">{title}</div>
                        <div style="font-size:0.74rem;color:rgba(255,255,255,0.38);
                                     line-height:1.5;margin-bottom:0.75rem;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.page_link(page, label=f"Open {title} →")

        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    init_session_state()
    inject_css()

    # Init DB
    if st.session_state["db"] is None:
        st.session_state["db"] = DBManager()
    db: DBManager = st.session_state["db"]

    # Init LLM
    if st.session_state["llm_client"] is None:
        st.session_state["llm_client"] = get_llm_client()

    # Load profile
    if st.session_state["active_profile"] is None:
        st.session_state["active_profile"] = load_active_profile(db)
    profile: StudentProfile | None = st.session_state["active_profile"]

    # Load scores
    if profile and not st.session_state["skill_scores"]:
        scores = db.load_scores(profile.student_id)
        if scores:
            st.session_state["skill_scores"] = scores
            st.session_state["assessment_done"] = True

    assessment_done: bool = st.session_state.get("assessment_done", False)
    show_landing: bool = st.session_state.get("show_landing", True)

    # ── Landing page (no sidebar) ──
    if show_landing:
        # Hide sidebar on landing page
        st.markdown(
            "<style>[data-testid='stSidebar']{display:none!important;}</style>",
            unsafe_allow_html=True,
        )
        _nav_bar(profile.full_name if profile else None)
        clicked = _hero_section(bool(profile), assessment_done)
        _features_section()
        _how_it_works_section()
        _about_section()
        bottom_clicked = _cta_section()
        _footer()

        if clicked or bottom_clicked:
            st.session_state["show_landing"] = False
            st.rerun()

    # ── App home (with sidebar) ──
    else:
        _render_sidebar(profile)
        _render_app_home(profile, assessment_done)


if __name__ == "__main__":
    main()
