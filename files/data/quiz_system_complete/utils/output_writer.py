"""
Utility: Export master performance, module summary, and rankings to CSV/Excel.
"""
import os
import pandas as pd
from utils.logger import get_logger

logger = get_logger("OutputWriter")


def write_master_file(perf: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "master_performance.csv")
    perf.to_csv(path, index=False)
    logger.info(f"Master file written: {path}")
    return path


def write_module_summary(mod_perf: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "module_summary.csv")
    mod_perf.to_csv(path, index=False)
    logger.info(f"Module summary written: {path}")
    return path


def write_rankings(perf: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "final_rankings.csv")
    cols = ["rank", "name", "email", "total_marks", "total_max",
            "overall_percentage", "overall_percentile", "grade", "quizzes_attempted"]
    perf.sort_values("rank")[cols].to_csv(path, index=False)
    logger.info(f"Rankings file written: {path}")
    return path


def write_all_outputs(perf: pd.DataFrame, mod_perf: pd.DataFrame, output_dir: str):
    write_master_file(perf, output_dir)
    write_module_summary(mod_perf, output_dir)
    write_rankings(perf, output_dir)
