"""
Utility: Load training schedule to map quiz numbers to modules and dates.
"""
import pandas as pd
from pathlib import Path
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("ScheduleLoader")
config = load_config()

_cache: dict = {}


def load_schedule() -> dict[int, dict]:
    """
    Returns {quiz_number: {"module": str, "date": str}}
    Loaded from training_schedule.xlsx.
    Falls back to config.yaml module mapping if file not found.
    """
    global _cache
    if _cache:
        return _cache

    schedule_path = config["paths"]["schedule"]
    if not Path(schedule_path).exists():
        logger.warning(f"Schedule file not found: {schedule_path}. Using config fallback.")
        return _build_from_config()

    try:
        df = pd.read_excel(schedule_path)
        df.columns = [c.strip().lower() for c in df.columns]

        # Expected columns: Day, Date, Module, Quiz
        mapping = {}
        for _, row in df.iterrows():
            quiz_col = str(row.get("quiz", "")).strip()
            if not quiz_col.lower().startswith("quiz"):
                continue
            try:
                qnum = int("".join(filter(str.isdigit, quiz_col)))
            except ValueError:
                continue
            # Normalise date to ISO format for safe pd.to_datetime parsing
            raw_date = str(row.get("date", "")).strip()
            try:
                iso_date = pd.to_datetime(raw_date, dayfirst=True).strftime("%Y-%m-%d")
            except Exception:
                iso_date = "2026-01-01"
            mapping[qnum] = {
                "module": str(row.get("module", "Unknown")).strip(),
                "date": iso_date,
            }

        _cache = mapping
        logger.info(f"Schedule loaded: {len(mapping)} quiz entries.")
        return _cache
    except Exception as e:
        logger.error(f"Error reading schedule: {e}")
        return _build_from_config()


def _build_from_config() -> dict[int, dict]:
    """Fallback: build mapping from config.yaml modules."""
    mapping = {}
    for module, info in config.get("modules", {}).items():
        for qnum in info.get("quizzes", []):
            mapping[qnum] = {"module": module, "date": ""}
    return mapping


def get_quiz_info(quiz_number: int) -> dict:
    schedule = load_schedule()
    return schedule.get(quiz_number, {"module": f"Module Unknown", "date": ""})
