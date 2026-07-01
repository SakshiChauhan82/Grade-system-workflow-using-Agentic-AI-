"""
Agent 8: Dashboard Agent
Streamlit dashboard — auto-reads from DuckDB, refreshes every 30 s.

Run: streamlit run dashboard/app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import DatabaseManager
from utils.config_loader import load_config

config = load_config()

st.set_page_config(
    page_title="Training Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1A237E, #42A5F5);
    color: white; border-radius: 10px; padding: 16px; text-align: center;
}
.metric-value { font-size: 2rem; font-weight: bold; }
.metric-label { font-size: 0.85rem; opacity: 0.85; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def load_data():
    db = DatabaseManager()
    perf   = db.get_performance()
    mod    = db.get_module_performance()
    scores = db.get_all_scores()
    files  = db.get_processed_files()
    return perf, mod, scores, files


def grade_color(grade: str) -> str:
    return {"A+": "#2E7D32", "A": "#388E3C", "B+": "#1976D2",
            "B": "#42A5F5", "C": "#FFA000", "D": "#F57C00", "F": "#C62828"}.get(grade, "#666")


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Lloyd_Institute_of_Engineering_%26_Technology_logo.jpg/120px-Lloyd_Institute_of_Engineering_%26_Technology_logo.jpg",
             use_container_width=True)
    st.title("🎓 Performance Dashboard")
    st.caption(config["system"]["training"])
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Auto-refreshes every 30 s")

perf, mod, scores, files = load_data()

if perf.empty:
    st.warning("⚠️ No performance data yet. Run the pipeline first: `python main.py`")
    st.stop()

# ── KPI Row ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Overall Statistics")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Students",    len(perf))
k2.metric("Quizzes Processed", len(files))
k3.metric("Class Average",     f"{perf['overall_percentage'].mean():.1f}%")
k4.metric("Top Score",         f"{perf['overall_percentage'].max():.1f}%")
k5.metric("Pass Rate (≥50%)",
          f"{(perf['overall_percentage'] >= 50).sum() / len(perf) * 100:.0f}%")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 Rankings", "📚 Module Analysis",
    "📅 Daily Trends", "📊 Grade Distribution",
    "🔍 Student Search", "📁 Files Processed"
])

# Tab 1 — Rankings
with tab1:
    st.subheader("🏆 Top Performers")
    top_n = st.slider("Show top N students", 5, len(perf), min(10, len(perf)))
    perf = perf[perf["quizzes_attempted"] > 2] 
    top = perf.head(top_n)[["rank", "name", "total_marks", "total_max",
                              "overall_percentage", "overall_percentile",
                              "quizzes_attempted", "grade"]].copy()
    top.columns = ["Rank", "Name", "Marks", "Max", "Percentage", "Percentile",
                   "Quizzes", "Grade"]
    st.dataframe(top, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            top, x="Name", y="Percentage", color="Grade",
            title="Top Students by Percentage",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.scatter(
            perf, x="overall_percentage", y="overall_percentile",
            color="grade", size="quizzes_attempted", hover_data=["name"],
            title="Percentile vs Percentage",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("⚠️ Weak Students (< 50%)")
    weak = perf[perf["overall_percentage"] < 50][
        ["rank", "name", "overall_percentage", "grade"]
    ]
    if weak.empty:
        st.success("All students scored above 50%! 🎉")
    else:
        st.dataframe(weak, use_container_width=True, hide_index=True)

# Tab 2 — Module Analysis
with tab2:
    st.subheader("📚 Module-wise Performance")
    if mod.empty:
        st.info("No module data yet.")
    else:
        mod_agg = mod.groupby("module").agg(
            avg_pct=("module_percentage", "mean"),
            avg_marks=("module_marks", "mean"),
        ).reset_index()

        fig = px.bar(mod_agg, x="module", y="avg_pct",
                     title="Average Percentage per Module",
                     color="avg_pct", color_continuous_scale="Blues")
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.box(mod, x="module", y="module_percentage",
                      title="Score Distribution per Module",
                      color="module")
        fig2.update_layout(xaxis_tickangle=-30, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# Tab 3 — Daily Trends
with tab3:
    st.subheader("📅 Daily Quiz Performance Trends")
    if scores.empty:
        st.info("No daily scores yet.")
    else:
        daily_avg = scores.groupby("quiz_number")["percentage"].agg(
            ["mean", "max", "min"]
        ).reset_index()
        daily_avg.columns = ["Quiz", "Average", "Max", "Min"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_avg["Quiz"], y=daily_avg["Max"],
                                 name="Max", line=dict(color="#2E7D32", dash="dot")))
        fig.add_trace(go.Scatter(x=daily_avg["Quiz"], y=daily_avg["Average"],
                                 name="Average", line=dict(color="#1976D2", width=2)))
        fig.add_trace(go.Scatter(x=daily_avg["Quiz"], y=daily_avg["Min"],
                                 name="Min", line=dict(color="#C62828", dash="dot")))
        fig.update_layout(title="Quiz Score Trend (Class Average)",
                          xaxis_title="Quiz Number", yaxis_title="Percentage")
        st.plotly_chart(fig, use_container_width=True)

        selected_email = st.selectbox(
            "View individual student trend",
            options=[""] + sorted(perf["email"].tolist()),
            format_func=lambda e: next(
                (perf[perf["email"] == e]["name"].values[0] for _ in [1] if e), e
            ) if e else "-- Select student --"
        )
        if selected_email:
            s_scores = scores[scores["email"] == selected_email].sort_values("quiz_number")
            fig3 = px.line(s_scores, x="quiz_number", y="percentage",
                           markers=True, title="Individual Performance Trend",
                           color_discrete_sequence=["#1A237E"])
            st.plotly_chart(fig3, use_container_width=True)

# Tab 4 — Grade Distribution
with tab4:
    st.subheader("📊 Grade Distribution")
    grade_counts = perf["grade"].value_counts().reset_index()
    grade_counts.columns = ["Grade", "Count"]
    grade_order = ["A+", "A", "B+", "B", "C", "D", "F"]
    grade_counts["Grade"] = pd.Categorical(grade_counts["Grade"],
                                            categories=grade_order, ordered=True)
    grade_counts = grade_counts.sort_values("Grade")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(grade_counts, names="Grade", values="Count",
                     title="Grade Distribution",
                     color="Grade",
                     color_discrete_map={g: grade_color(g) for g in grade_order})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(grade_counts, x="Grade", y="Count",
                      title="Grade Counts",
                      color="Grade",
                      color_discrete_map={g: grade_color(g) for g in grade_order})
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(perf, x="overall_percentage", nbins=20,
                        title="Score Distribution (All Students)",
                        color_discrete_sequence=["#42A5F5"])
    fig3.add_vline(x=perf["overall_percentage"].mean(), line_dash="dash",
                   annotation_text="Class Avg", line_color="#C62828")
    st.plotly_chart(fig3, use_container_width=True)

# Tab 5 — Student Search
with tab5:
    st.subheader("🔍 Student Search & Detail")
    search = st.text_input("Search by name or email")
    if search:
        mask = (
            perf["name"].str.contains(search, case=False, na=False) |
            perf["email"].str.contains(search, case=False, na=False)
        )
        results = perf[mask]
        if results.empty:
            st.warning("No students found.")
        else:
            for _, row in results.iterrows():
                with st.expander(f"#{row['rank']} {row['name']} — {row['grade']} "
                                 f"({row['overall_percentage']:.1f}%)"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Marks",      f"{row['total_marks']:.0f}/{row['total_max']:.0f}")
                    c2.metric("Percentile", f"{row['overall_percentile']:.1f}")
                    c3.metric("Quizzes",    row["quizzes_attempted"])

                    if not mod.empty:
                        s_mod = mod[mod["email"] == row["email"]]
                        if not s_mod.empty:
                            st.dataframe(
                                s_mod[["module","module_marks","module_max",
                                       "module_percentage","module_percentile"]],
                                use_container_width=True, hide_index=True
                            )

# Tab 6 — Files Processed
with tab6:
    st.subheader("📁 Quiz Files Processed")
    if files.empty:
        st.info("No files processed yet.")
    else:
        st.dataframe(files, use_container_width=True, hide_index=True)
        st.success(f"✅ {len(files)} quiz file(s) processed so far.")

st.caption("Automated Training Performance Management System | Agentic AI Project | Lloyd IET")
