"""
Agent 4: Percentile & Ranking Agent
Computes percentile ranks (overall and module-wise) and assigns student ranks.
"""
import numpy as np
import pandas as pd
from utils.logger import get_logger

logger = get_logger("PercentileRankingAgent")


def _percentile_rank(series: pd.Series) -> pd.Series:
    """
    Compute percentile rank for each value in a series.
    Formula: (number of values <= x) / total * 100
    Handles ties by averaging ranks.
    """
    return series.rank(pct=True, method="average").mul(100).round(2)


def assign_overall_percentile_and_rank(perf: pd.DataFrame) -> pd.DataFrame:
    """
    Add overall_percentile and rank columns to student performance DataFrame.
    """
    if perf.empty:
        return perf

    df = perf.copy()
    df["overall_percentile"] = _percentile_rank(df["overall_percentage"])
    df["rank"] = df["overall_percentage"].rank(
        ascending=False, method="min"
    ).astype(int)
    df = df.sort_values("rank").reset_index(drop=True)
    logger.info(f"Assigned ranks and percentiles to {len(df)} students.")
    return df


def assign_module_percentile(mod_perf: pd.DataFrame) -> pd.DataFrame:
    """
    Add module_percentile per module group.
    """
    if mod_perf.empty:
        return mod_perf

    df = mod_perf.copy()
    df["module_percentile"] = (
        df.groupby("module")["module_percentage"]
        .transform(_percentile_rank)
        .round(2)
    )
    return df
