"""DuckDB database manager for persistent storage."""
import os
import duckdb
import pandas as pd
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("DatabaseManager")
config = load_config()


class DatabaseManager:
    """Manages all read/write operations to DuckDB."""

    def __init__(self):
        os.makedirs("output", exist_ok=True)
        self.db_path = config["paths"]["database"]
        self._init_schema()

    def _conn(self):
        return duckdb.connect(self.db_path)

    def _init_schema(self):
        with self._conn() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    filename TEXT PRIMARY KEY,
                    quiz_number INTEGER,
                    processed_at TIMESTAMP DEFAULT current_timestamp
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS quiz_scores (
                    email TEXT,
                    name TEXT,
                    quiz_number INTEGER,
                    raw_score DOUBLE,
                    max_score DOUBLE,
                    percentage DOUBLE,
                    quiz_date DATE,
                    module TEXT,
                    PRIMARY KEY (email, quiz_number)
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS student_performance (
                    email TEXT PRIMARY KEY,
                    name TEXT,
                    total_marks DOUBLE,
                    total_max DOUBLE,
                    overall_percentage DOUBLE,
                    overall_percentile DOUBLE,
                    rank INTEGER,
                    grade TEXT,
                    quizzes_attempted INTEGER,
                    last_updated TIMESTAMP DEFAULT current_timestamp
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS module_performance (
                    email TEXT,
                    module TEXT,
                    module_marks DOUBLE,
                    module_max DOUBLE,
                    module_percentage DOUBLE,
                    module_percentile DOUBLE,
                    PRIMARY KEY (email, module)
                )
            """)
        logger.info("Database schema initialized.")

    # ── File tracking ──────────────────────────────────────────────
    def is_processed(self, filename: str) -> bool:
        with self._conn() as con:
            r = con.execute(
                "SELECT 1 FROM processed_files WHERE filename = ?", [filename]
            ).fetchone()
        return r is not None

    def mark_processed(self, filename: str, quiz_number: int):
        with self._conn() as con:
            con.execute(
                "INSERT OR REPLACE INTO processed_files VALUES (?, ?, current_timestamp)",
                [filename, quiz_number],
            )

    # ── Quiz scores ────────────────────────────────────────────────
    def upsert_quiz_scores(self, df: pd.DataFrame):
        """Insert or replace quiz score rows."""
        with self._conn() as con:
            con.register("_df", df)
            con.execute("""
                INSERT OR REPLACE INTO quiz_scores
                SELECT email, name, quiz_number, raw_score, max_score,
                       percentage, quiz_date, module
                FROM _df
            """)
        logger.info(f"Upserted {len(df)} quiz score rows.")

    def get_all_scores(self) -> pd.DataFrame:
        with self._conn() as con:
            return con.execute("SELECT * FROM quiz_scores").df()

    # ── Student performance ────────────────────────────────────────
    def upsert_performance(self, df: pd.DataFrame):
        with self._conn() as con:
            con.register("_df", df)
            con.execute("""
                INSERT OR REPLACE INTO student_performance
                SELECT email, name, total_marks, total_max, overall_percentage,
                       overall_percentile, rank, grade, quizzes_attempted,
                       current_timestamp
                FROM _df
            """)

    def get_performance(self) -> pd.DataFrame:
        with self._conn() as con:
            return con.execute(
                "SELECT * FROM student_performance ORDER BY rank"
            ).df()

    # ── Module performance ─────────────────────────────────────────
    def upsert_module_performance(self, df: pd.DataFrame):
        with self._conn() as con:
            con.register("_df", df)
            con.execute("""
                INSERT OR REPLACE INTO module_performance
                SELECT email, module, module_marks, module_max,
                       module_percentage, module_percentile
                FROM _df
            """)

    def get_module_performance(self) -> pd.DataFrame:
        with self._conn() as con:
            return con.execute("SELECT * FROM module_performance").df()

    def get_processed_files(self) -> pd.DataFrame:
        with self._conn() as con:
            return con.execute("SELECT * FROM processed_files ORDER BY quiz_number").df()
