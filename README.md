# SkillPilot AI 🎯
**Personalized Skill-Gap Analyzer and Learning Recommendation System**

SkillPilot AI is a Streamlit web application that helps college students identify technical skill gaps, understand strengths and weaknesses, and receive a personalized learning roadmap for their chosen career path.

---

## Features

| Module | Description |
|---|---|
| 👤 Profile | Create and manage your student profile |
| 📝 Assessment | Rate your proficiency across 7 key skills |
| 📊 Gap Analysis | See your gaps vs. career-path benchmarks |
| 💡 Recommendations | Personalized learning activities, ranked by gap size |
| 🗺️ Roadmap | Weekly learning plan with daily tasks and milestones |
| 📁 Projects | Beginner Data Analyst project suggestions |

---

## Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- pip

### 2. Install dependencies
```bash
cd "SkillPilot-AI"
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## Optional: LLM API (AI-enriched recommendations)

To enable AI-enriched recommendations, create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
SKILLPILOT_LLM_API_KEY=your_real_api_key
SKILLPILOT_LLM_ENDPOINT=https://api.openai.com/v1
```

The app works fully offline without these — AI enrichment is optional.

---

## Optional: Switch to SQLite storage

Edit `config.json`:
```json
{
  "storage_backend": "sqlite",
  "data_dir": "data/",
  "sqlite_path": "data/skillpilot.db"
}
```

---

## Project Structure

```
SkillPilot-AI/
├── app.py                    # Streamlit entry point
├── requirements.txt
├── config.json               # Storage backend config
├── .env.example              # LLM env var template
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Profile.py
│   ├── 3_Assessment.py
│   ├── 4_Gap_Analysis.py
│   ├── 5_Recommendations.py
│   ├── 6_Roadmap.py
│   └── 7_Projects.py
├── modules/
│   ├── assessment.py         # Question banks, score normalization
│   ├── skill_gap.py          # Gap formula, priority tiers
│   ├── recommendations.py    # Activity generation, project ranking
│   ├── roadmap.py            # Weekly schedule generation
│   ├── progress.py           # Task completion tracking
│   ├── visualizations.py     # Plotly chart factory
│   └── db_manager.py         # CSV/SQLite storage layer
├── models/
│   └── data_models.py        # Python dataclasses
├── data/
│   ├── skill_requirements.csv
│   ├── learning_resources.csv
│   ├── sample_students.csv
│   └── projects.json
├── tests/
│   ├── unit/
│   ├── property/
│   └── integration/
└── logs/                     # Auto-created at runtime
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Property-based tests
pytest tests/property/ -v

# Integration tests
pytest tests/integration/ -v
```

---

## Sample Data

Three sample student profiles are pre-loaded on first start:
- **Alice Nguyen** — Computer Science, Semester 4, Intermediate
- **Bob Patel** — Mathematics, Semester 6, Beginner
- **Clara Smith** — Business Analytics, Semester 3, Beginner

These are synthetic records for demonstration purposes only.

---

## Notes

- Target scores are **project-defined learning benchmarks**, not official industry standards or guarantees of employability.
- All data is stored locally in the `data/` directory.
- API credentials are never hardcoded — always use environment variables.
