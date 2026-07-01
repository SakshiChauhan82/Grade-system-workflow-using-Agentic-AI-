#  Automated Training Performance Management System
### Grade System Workflow using Agentic AI
**Lloyd Institute of Engineering & Technology**
*ML & Agentic AI Summer Training Program 2026*

---

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-green?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![DuckDB](https://img.shields.io/badge/DuckDB-Database-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

---

##  About the Project

During the **25-day ML and Agentic AI Training Program** at Lloyd Institute, students give daily MCQ quizzes through Google Forms. Managing marks manually — combining files, calculating scores, generating grade cards, and emailing reports — becomes time-consuming and error-prone as quizzes grow.

This project solves that completely.

**The Automated Training Performance Management System** detects new quiz files automatically, processes all student data, calculates performance metrics, generates individual PDF grade cards, and emails them to every student — all without changing a single line of code.

> Drop a new quiz file → Everything updates automatically. That's it.

---

##  Demo

```
New Quiz CSV dropped into folder
          ↓
System auto-detects the file (Watchdog)
          ↓
Cleans & merges student records by Email ID
          ↓
Calculates marks, percentile, rank, grade
          ↓
Generates PDF grade card for every student
          ↓
Emails grade cards to all students (Gmail SMTP)
          ↓
Updates live Streamlit dashboard
```

---

##  Features

- ✅ **Auto file detection** — drop a CSV, system detects and processes it instantly
- ✅ **Smart merging** — combines student records across all quizzes using Email ID
- ✅ **Duplicate handling** — keeps highest score if student submits twice
- ✅ **Daily performance** — percentage score for each quiz
- ✅ **Module-wise performance** — marks and percentage per module
- ✅ **Cumulative performance** — overall score across all quizzes
- ✅ **Percentile calculation** — relative standing among all students
- ✅ **Auto ranking** — overall rank for every student
- ✅ **Grade assignment** — A+ to F based on percentage
- ✅ **PDF grade cards** — individual, professional grade card per student
- ✅ **Email automation** — sends grade cards directly to student emails
- ✅ **Live dashboard** — Streamlit dashboard with charts, filters, student search
- ✅ **100% free & open-source** — no paid APIs, no paid services

---

##  System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  LangGraph Agentic Pipeline                      │
│                                                                   │
│  Agent 1          Agent 2         Agent 3         Agent 4        │
│  File Monitor  →  Data Cleaning → Performance  → Percentile &   │
│  (Watchdog)       (Pandas)        Calculation     Ranking        │
│                                                        ↓         │
│  Agent 8          Agent 7         Agent 6         Agent 5        │
│  Dashboard     ←  Email Agent  ← Grade Card    ← Grade          │
│  (Streamlit)      (SMTP)          Generator       Assignment     │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Name | Tool | Responsibility |
|-------|------|------|----------------|
| 1 | File Monitor Agent | Watchdog | Detects new quiz files in folder |
| 2 | Data Cleaning Agent | Pandas | Reads CSV, normalises emails, removes duplicates |
| 3 | Performance Calculation Agent | Pandas, NumPy | Daily, module-wise, cumulative metrics |
| 4 | Percentile & Ranking Agent | NumPy | Percentile rank and overall rank |
| 5 | Grade Assignment Agent | Config | Maps percentage to letter grade |
| 6 | Grade Card Generator Agent | ReportLab | Generates PDF grade cards |
| 7 | Email Agent | SMTP | Emails grade cards to students |
| 8 | Dashboard Agent | Streamlit, Plotly | Live visual dashboard |

---

##  Project Structure

```
quiz_system_complete/
│
├── main.py                          # Entry point
├── pipeline.py                      # LangGraph workflow orchestration
├── requirements.txt                 # All dependencies
├── README.md                        # This file
├── .env.example                     # Environment variables template
│
├── agents/
│   ├── file_monitor_agent.py        # Agent 1: Watchdog file detection
│   ├── data_cleaning_agent.py       # Agent 2: CSV cleaning & normalisation
│   ├── performance_calc_agent.py    # Agent 3: Performance metrics
│   ├── percentile_ranking_agent.py  # Agent 4: Percentile & ranking
│   ├── grade_assignment_agent.py    # Agent 5: Letter grade
│   ├── grade_card_agent.py          # Agent 6: PDF generation
│   └── email_agent.py              # Agent 7: Gmail SMTP
│
├── dashboard/
│   └── app.py                       # Agent 8: Streamlit dashboard
│
├── utils/
│   ├── logger.py                    # Centralised logging
│   ├── config_loader.py             # YAML + .env reader
│   ├── database.py                  # DuckDB manager
│   ├── schedule_loader.py           # Quiz to module mapping
│   └── output_writer.py             # CSV export
│
├── config/
│   └── config.yaml                  # All settings (grades, paths, modules)
│
├── data/
│   ├── quiz_files/                  # ← Drop new quiz CSVs here
│   ├── training_schedule.xlsx       # Quiz to module/date mapping
│   └── sample_data_set.xlsx         # Sample dataset
│
├── output/                          # Generated CSVs and database
│   ├── master_performance.csv
│   ├── module_summary.csv
│   ├── final_rankings.csv
│   └── performance.db               # DuckDB database
│
├── reports/
│   └── grade_cards/                 # Generated PDF grade cards
│
└── logs/                            # Daily log files
```

---

##  Technology Stack

| Purpose | Tool | Why |
|---------|------|-----|
| Programming Language | Python 3.10+ | Core language |
| Agentic Orchestration | LangGraph | Manages 8-agent workflow as directed graph |
| Auto File Detection | Watchdog | Monitors folder for new quiz files |
| Data Processing | Pandas, NumPy | Cleaning, merging, calculations |
| Database | DuckDB | Fast, lightweight, no server needed |
| Dashboard | Streamlit | Interactive web dashboard |
| Charts | Plotly | Beautiful interactive charts |
| PDF Grade Cards | ReportLab | Professional PDF generation |
| Email | Gmail SMTP (smtplib) | Built into Python, no extra cost |
| Config | YAML + python-dotenv | Clean configuration management |
| Logging | Python logging | File + console logging |

> 💡 **Everything is 100% free and open-source.**

---

##  Quick Start

### Prerequisites
- Python 3.10 or above
- A Gmail account (for email feature)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/quiz-performance-system.git
cd quiz-performance-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```

Edit `.env` with your Gmail credentials:
```
EMAIL_SENDER=yourgmail@gmail.com
EMAIL_PASSWORD=yourapppassword
SEND_EMAILS=true
LOG_LEVEL=INFO
```

### 4. Add quiz files
Drop your Google Forms quiz CSV files into:
```
data/quiz_files/
```

Name them with the quiz number:
- `Quiz1_15_6_26.csv`
- `Quiz_2_16_6_26.csv`
- `Quiz_3_17_6_26.csv`

### 5. Run the pipeline
```bash
python main.py
```

### 6. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

### 7. Watch for new files automatically
```bash
python main.py --watch
```

---

##  What Gets Generated

| Output | Location | Description |
|--------|----------|-------------|
| Master Performance File | `output/master_performance.csv` | All student metrics in one file |
| Module Summary | `output/module_summary.csv` | Module-wise breakdown |
| Final Rankings | `output/final_rankings.csv` | Ranked list of all students |
| PDF Grade Cards | `reports/grade_cards/` | Individual PDF per student |
| Database | `output/performance.db` | DuckDB database |
| Log Files | `logs/` | Daily log files |

---

##  Grading Scale

| Grade | Percentage | Description |
|-------|-----------|-------------|
| A+ | ≥ 90% | Outstanding |
| A | ≥ 80% | Excellent |
| B+ | ≥ 70% | Very Good |
| B | ≥ 60% | Good |
| C | ≥ 50% | Average |
| D | ≥ 40% | Below Average |
| F | < 40% | Fail |

---

##  Email Setup (Gmail)

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → **2-Step Verification** → Turn ON
3. Security → **App Passwords** → Create new
4. Name it `QuizSystem` → Click **Create**
5. Copy the 16-character password (no spaces)
6. Paste into `.env`:
```
EMAIL_SENDER=yourgmail@gmail.com
EMAIL_PASSWORD=xxxxxxxxxxxxxx
SEND_EMAILS=true
```

---

##  Quiz File Format

The system expects Google Forms exported CSV files with these columns:

| Column | Example |
|--------|---------|
| Timestamp | 2026/06/15 12:43:38 PM GMT+5:30 |
| Email | student@gmail.com |
| Name | Student Name |
| Total score | 14.00 / 15 |

---

##  Dashboard Features

-  **Top Performers** — ranked table with scores
-  **Module Analysis** — bar charts and box plots per module
-  **Daily Trends** — class average trend across quizzes
-  **Grade Distribution** — pie chart and histogram
-  **Student Search** — find any student by name or email
-  **Files Processed** — list of all quiz files in the system

---

##  Adding New Quiz Files

Just drop the new CSV into `data/quiz_files/` and run:
```bash
python main.py
```
Or if `--watch` mode is running, it triggers automatically.

**To reset and reprocess everything from scratch:**
```bash
del output\performance.db     # Windows
rm output/performance.db      # Mac/Linux
python main.py
```

---

##  Testing

```bash
python main.py --test
```

This runs a quick smoke test to verify all agents, database, and pipeline are working correctly.

---

##  Deployment

### Run Locally
```bash
python main.py --watch &
streamlit run dashboard/app.py
```

### Deploy Dashboard on Streamlit Cloud (Free)
1. Push project to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file as `dashboard/app.py`
5. Add Gmail credentials in Streamlit Secrets

---

##  Future Improvements

- REST API using FastAPI for external integrations
- WhatsApp notifications using free tier
- AI-generated personalised feedback using Ollama (free LLM)
- Multi-batch support for multiple training programs
- Automated Google Forms data fetch using Google Sheets API
- Student self-service portal to view their own grade card

---

##  AI Tools Used

This project was built with assistance from **Claude (Anthropic)** for:
- System architecture and agent design
- LangGraph workflow implementation
- Code generation and review
- Documentation

---

##  Author

**Sakshi Chauhan**
B.Tech Computer Science (Data Science)
Lloyd Institute of Engineering & Technology, Greater Noida
AKTU Affiliated | Batch 2023–2027

---

##  License

This project is open source and available under the [MIT License](LICENSE).

---

*Built as Project #1 for ML & Agentic AI Summer Training 2026 — Lloyd Institute of Engineering & Technology*
