"""
Agent 2: Data Cleaning Agent
Reads raw Google Forms CSV, normalises emails, extracts scores,
handles duplicates, and returns a clean DataFrame.
"""
import re
import pandas as pd
from pathlib import Path
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("DataCleaningAgent")
config = load_config()


def _parse_score(value: str) -> tuple[float, float]:
    """Parse '14.00 / 15' → (14.0, 15.0)."""
    if pd.isna(value):
        return 0.0, 15.0
    m = re.match(r"([\d.]+)\s*/\s*([\d.]+)", str(value))
    if m:
        return float(m.group(1)), float(m.group(2))
    try:
        return float(value), 15.0
    except ValueError:
        return 0.0, 15.0


def _normalise_email(email: str) -> str:
    """Lowercase and strip whitespace from email."""
    if pd.isna(email):
        return ""
    return str(email).strip().lower()


def clean_quiz_file(
    filepath: str,
    quiz_number: int,
    quiz_date: str,
    module: str,
) -> pd.DataFrame:
    """
    Read a raw quiz CSV/Excel and return a clean, normalised DataFrame
    with columns: [email, name, quiz_number, raw_score, max_score,
                   percentage, quiz_date, module]
    """
    path = Path(filepath)
    logger.info(f"Cleaning file: {path.name}")

    # ── Read file ──────────────────────────────────────────────────
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)

    logger.debug(f"Raw shape: {df.shape}, columns: {list(df.columns[:8])}")

    # ── Locate required columns ────────────────────────────────────
    col_map = _find_columns(df)

    email_col = col_map.get("email")
    name_col = col_map.get("name")
    score_col = col_map.get("score")

    if not email_col or not score_col:
        logger.error(f"Cannot find Email or Score column in {path.name}")
        return pd.DataFrame()

    # ── Extract ────────────────────────────────────────────────────
    out = pd.DataFrame()
    out["email"] = df[email_col].apply(_normalise_email)
    out["name"] = df[name_col].apply(lambda x: str(x).strip().title()) if name_col else "Unknown"
    scores = df[score_col].apply(_parse_score)
    out["raw_score"] = scores.apply(lambda t: t[0])
    out["max_score"] = scores.apply(lambda t: t[1])

    # ── Drop missing emails ────────────────────────────────────────
    before = len(out)
    out = out[out["email"].str.len() > 0].copy()
    if len(out) < before:
        logger.warning(f"Dropped {before - len(out)} rows with missing email.")

    # ── Handle duplicates: keep highest score ──────────────────────
    before = len(out)
    out = (
        out.sort_values("raw_score", ascending=False)
        .drop_duplicates(subset=["email"], keep="first")
        .reset_index(drop=True)
    )
    if len(out) < before:
        logger.warning(f"Removed {before - len(out)} duplicate email entries (kept highest score).")

    # ── Add metadata ───────────────────────────────────────────────
    out["quiz_number"] = quiz_number
    out["percentage"] = (out["raw_score"] / out["max_score"] * 100).round(2)
    out["quiz_date"] = pd.to_datetime(quiz_date).date()
    out["module"] = module

    logger.info(f"Cleaned: {len(out)} unique students for Quiz {quiz_number}.")
    return out


def _find_columns(df: pd.DataFrame) -> dict:
    """Heuristically find email, name, and total-score columns."""
    result = {}
    for col in df.columns:
        c = col.lower()
        if "email" in c and "[score]" not in c and "[feedback]" not in c:
            if "email" not in result:
                result["email"] = col
        if "name" in c and "[score]" not in c and "[feedback]" not in c:
            if "name" not in result:
                result["name"] = col
        if "total score" in c or "total_score" in c:
            result["score"] = col
    return result
