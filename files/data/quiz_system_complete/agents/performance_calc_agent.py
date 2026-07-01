"""
Agent 3: Performance Calculation Agent
Aggregates all quiz scores per student and computes cumulative,
module-wise, and daily metrics.
"""
import pandas as pd
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("PerformanceCalculationAgent")
config = load_config()


def calculate_student_performance(all_scores: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  all_scores — every row is one student's score for one quiz
    Output: one row per student with cumulative performance metrics
    """
    if all_scores.empty:
        return pd.DataFrame()

    grp = all_scores.groupby("email")

    perf = pd.DataFrame()
    perf["email"] = list(grp.groups.keys())
    perf = perf.set_index("email")

    perf["name"] = grp["name"].last()
    perf["total_marks"] = grp["raw_score"].sum()
    perf["total_max"] = grp["max_score"].sum()
    perf["quizzes_attempted"] = grp["quiz_number"].nunique()
    perf["overall_percentage"] = (perf["total_marks"] / perf["total_max"] * 100).round(2)

    return perf.reset_index()


def calculate_module_performance(all_scores: pd.DataFrame) -> pd.DataFrame:
    """
    Returns module-level aggregated marks per student.
    """
    if all_scores.empty:
        return pd.DataFrame()

    grp = all_scores.groupby(["email", "module"])
    mod = pd.DataFrame()
    mod["module_marks"] = grp["raw_score"].sum()
    mod["module_max"] = grp["max_score"].sum()
    mod = mod.reset_index()
    mod["module_percentage"] = (mod["module_marks"] / mod["module_max"] * 100).round(2)
    return mod


def calculate_daily_performance(all_scores: pd.DataFrame) -> pd.DataFrame:
    """Returns per-student per-quiz percentage (daily view)."""
    if all_scores.empty:
        return pd.DataFrame()
    return all_scores[
        ["email", "name", "quiz_number", "quiz_date", "module",
         "raw_score", "max_score", "percentage"]
    ].copy()
