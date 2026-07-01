# 🎓 Automated Training Performance Management System
### ML & Agentic AI Summer Training — Lloyd Institute of Engineering & Technology

> **Project #1 — Grade System Workflow using Agentic AI**

---

## 🌟 Overview

An end-to-end, fully automated grading system that:
- **Monitors** a folder for new Google Forms quiz CSV files
- **Cleans & merges** records by Email ID
- **Calculates** daily, module-wise, and cumulative performance
- **Computes** percentiles, ranks, and letter grades
- **Generates** individual PDF grade cards
- **Emails** reports to students
- **Displays** a live Streamlit dashboard

Zero code changes needed when new quiz files arrive — the system handles everything automatically.

---

## 🏗️ Architecture

```
                      ┌─────────────────────────────┐
                      │   LangGraph Agentic Pipeline │
                      └───────────────┬─────────────┘
                                      │
    ┌─────────────────────────────────▼──────────────────────────────────┐
    │                                                                      │
    ▼                                                                      │
Agent 1: File Monitor ──► Agent 2: Data Cleaning ──► Agent 3: Performance │
   (Watchdog)                 (Pandas, DuckDB)         Calculation         │
                                                            │              │
                                                            ▼              │
Agent 8: Dashboard  ◄── Agent 7: Email ◄── Agent 6: Grade Card ◄── Agent 5: Grade
  (Streamlit)            (SMTP)             (ReportLab PDF)           (Config rules)
                                                            ▲
                                                            │
                                                    Agent 4: Percentile
                                                       & Ranking
```

---

## 📁 Project Structure

```
quiz_system/
├── main.py                      # Entry point
├── pipeline.py                  # LangGraph orchestration
├── requirements.txt
├── README.md
├── .env.example                 # Copy to .env and fill credentials
│
├── agents/
│   ├── file_monitor_agent.py    # Agent 1: Watchdog file detection
│   ├── data_cleaning_agent.py   # Agent 2: Clean & normalise quiz CSVs
│   ├── performance_calc_agent.py # Agent 3: Daily/module/cumulative metrics
│   ├── percentile_ranking_agent.py # Agent 4: Percentile & rank
│   ├── grade_assignment_agent.py # Agent 5: Letter grade
│   ├── grade_card_agent.py      # Agent 6: PDF grade cards
│   └── email_agent.py           # Agent 7: Gmail SMTP
│
├── dashboard/
│   └── app.py                   # Agent 8: Streamlit dashboard
│
├── utils/
│   ├── logger.py                # Centralised logging
│   ├── config_loader.py         # YAML + .env reader
│   ├── database.py              # DuckDB manager
│   ├── schedule_loader.py       # Quiz→Module mapping
│   └── output_writer.py         # CSV export helpers
│
├── config/
│   └── config.yaml              # All tunable settings
│
├── data/
│   ├── quiz_files/              # ← Drop new quiz CSVs here
│   ├── training_schedule.xlsx
│   └── sample_data_set.xlsx
│
├── output/                      # Master CSV, rankings, module summary
├── reports/grade_cards/         # Generated PDF grade cards
└── logs/                        # Daily log files
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure email (optional)
```bash
cp .env.example .env
# Edit .env: set EMAIL_SENDER, EMAIL_PASSWORD, SEND_EMAILS=true
```

### 3. Run the pipeline once
```bash
python main.py
```

### 4. Watch for new files automatically
```bash
python main.py --watch
```

### 5. Launch dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📊 Quiz File Naming Convention

Name quiz files so the quiz number can be extracted:

| Filename                  | Detected Quiz # |
|---------------------------|----------------|
| `Quiz1_15_6_26.csv`       | Quiz 1         |
| `Quiz_2_16_6_26.csv`      | Quiz 2         |
| `quiz_10_25_6_26.xlsx`    | Quiz 10        |

---

## 🔢 Grading Scale

| Grade | Percentage |
|-------|-----------|
| A+    | ≥ 90%     |
| A     | ≥ 80%     |
| B+    | ≥ 70%     |
| B     | ≥ 60%     |
| C     | ≥ 50%     |
| D     | ≥ 40%     |
| F     | < 40%     |

---

## 🛠️ Technology Stack

| Purpose                | Tool                    |
|------------------------|-------------------------|
| Programming            | Python 3.10+            |
| Agentic Orchestration  | LangGraph               |
| Data Processing        | Pandas, NumPy           |
| Auto File Detection    | Watchdog                |
| Database               | DuckDB                  |
| Dashboard              | Streamlit + Plotly      |
| PDF Grade Cards        | ReportLab               |
| Email                  | Gmail SMTP + App Password |
| Config                 | YAML + python-dotenv    |
| Logging                | Python logging          |

---

## 🧪 Testing

```bash
python main.py --test    # Smoke test
```

---

## 🚀 Deployment

### Local
```bash
python main.py --watch &
streamlit run dashboard/app.py
```

### Streamlit Community Cloud (Dashboard only)
1. Push to GitHub
2. Connect repo at share.streamlit.io
3. Set `main file` = `dashboard/app.py`
4. Add secrets for email credentials

---

## 📧 Email Setup (Gmail)

1. Enable 2FA on your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate a password for "Mail"
4. Set in `.env`:
   ```
   EMAIL_SENDER=your@gmail.com
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   SEND_EMAILS=true
   ```

---

## 🔮 Future Improvements

- REST API (FastAPI) for external integrations
- Multi-tenant support (multiple training batches)
- SMS notifications via Twilio free tier
- AI-generated personalised feedback per student using free LLMs (Ollama)
- Automated quiz scheduling via Google Forms API
- WhatsApp notifications via WhatsApp Business API (free tier)

---

## 📋 AI Tools Used

This project was designed with assistance from **Claude (Anthropic)** for:
- System architecture design
- Agent workflow planning
- Code generation and review

*Prompt used:* "Design a production-quality Agentic AI system for automated training performance management using LangGraph, Python, DuckDB, ReportLab, and Streamlit — all free and open-source..."

---

*Lloyd Institute of Engineering & Technology | ML & Agentic AI Summer Training 2026*
