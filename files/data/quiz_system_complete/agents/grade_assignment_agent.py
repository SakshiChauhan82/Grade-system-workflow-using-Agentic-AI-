"""
Agent 5: Grade Assignment Agent
Maps overall percentage to a letter grade using the config thresholds.
"""
import pandas as pd
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("GradeAssignmentAgent")
config = load_config()

# Build sorted list of (min_pct, grade_label) from config
_GRADE_THRESHOLDS: list[tuple[float, str]] = sorted(
    [
        (v["min"], v["label"])
        for v in config["grading"].values()
    ],
    reverse=True,  # highest first
)


def assign_grade(percentage: float) -> str:
    """Return letter grade for a given percentage."""
    for threshold, label in _GRADE_THRESHOLDS:
        if percentage >= threshold:
            return label
    return "F"


def assign_grades_to_df(perf: pd.DataFrame) -> pd.DataFrame:
    """Add 'grade' column to performance DataFrame."""
    if perf.empty:
        return perf
    df = perf.copy()
    df["grade"] = df["overall_percentage"].apply(assign_grade)
    grade_dist = df["grade"].value_counts().to_dict()
    logger.info(f"Grade distribution: {grade_dist}")
    return df
