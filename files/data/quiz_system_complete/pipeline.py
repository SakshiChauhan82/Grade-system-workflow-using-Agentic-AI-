"""
Core Pipeline: LangGraph Agentic Workflow
Orchestrates all 8 agents as a directed graph.

State flows through nodes:
  scan_files → clean_data → calculate_performance → assign_percentiles
  → assign_grades → generate_cards → send_emails → write_outputs → END
"""
from __future__ import annotations
import os
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END

from agents.file_monitor_agent import scan_existing_files, extract_quiz_number
from agents.data_cleaning_agent import clean_quiz_file
from agents.performance_calc_agent import (
    calculate_student_performance,
    calculate_module_performance,
    calculate_daily_performance,
)
from agents.percentile_ranking_agent import (
    assign_overall_percentile_and_rank,
    assign_module_percentile,
)
from agents.grade_assignment_agent import assign_grades_to_df
from agents.grade_card_agent import generate_all_grade_cards
from agents.email_agent import send_all_emails
from utils.database import DatabaseManager
from utils.output_writer import write_all_outputs
from utils.schedule_loader import get_quiz_info
from utils.logger import get_logger
from utils.config_loader import load_config

import pandas as pd

logger = get_logger("Pipeline")
config = load_config()


# ── LangGraph State ────────────────────────────────────────────────────────────
class PipelineState(TypedDict):
    new_files: list[dict]          # files to process
    all_scores: pd.DataFrame       # cumulative quiz scores
    student_perf: pd.DataFrame     # per-student aggregated performance
    module_perf: pd.DataFrame      # module-level performance
    daily_perf: pd.DataFrame       # daily quiz performance
    grade_card_paths: dict         # {email: pdf_path}
    email_results: dict
    errors: list[str]


# ── Node functions ─────────────────────────────────────────────────────────────

def node_scan_files(state: PipelineState) -> PipelineState:
    """Agent 1: Detect new quiz files."""
    logger.info("=== NODE: Scan Files ===")
    db = DatabaseManager()
    quiz_folder = config["paths"]["quiz_folder"]
    new_files = scan_existing_files(quiz_folder, db)
    logger.info(f"Found {len(new_files)} new file(s) to process.")
    state["new_files"] = new_files
    return state


def node_clean_data(state: PipelineState) -> PipelineState:
    """Agent 2: Clean and merge quiz data into DB."""
    logger.info("=== NODE: Clean Data ===")
    db = DatabaseManager()
    errors = list(state.get("errors", []))

    for file_info in state["new_files"]:
        try:
            qnum = file_info["quiz_number"]
            info = get_quiz_info(qnum)
            module = info.get("module", "Unknown")
            date_str = info.get("date", "2026-01-01") or "2026-01-01"

            cleaned = clean_quiz_file(
                filepath=file_info["path"],
                quiz_number=qnum,
                quiz_date=date_str,
                module=module,
            )
            if not cleaned.empty:
                db.upsert_quiz_scores(cleaned)
                db.mark_processed(file_info["filename"], qnum)
                logger.info(f"Stored {len(cleaned)} rows for Quiz {qnum}.")
            else:
                errors.append(f"Empty result for {file_info['filename']}")
        except Exception as e:
            msg = f"Error cleaning {file_info.get('filename')}: {e}"
            logger.error(msg)
            errors.append(msg)

    state["errors"] = errors
    return state


def node_calculate_performance(state: PipelineState) -> PipelineState:
    """Agent 3: Calculate all performance metrics."""
    logger.info("=== NODE: Calculate Performance ===")
    db = DatabaseManager()
    all_scores = db.get_all_scores()

    if all_scores.empty:
        logger.warning("No scores in database yet.")
        state["all_scores"] = pd.DataFrame()
        state["student_perf"] = pd.DataFrame()
        state["module_perf"] = pd.DataFrame()
        state["daily_perf"] = pd.DataFrame()
        return state

    state["all_scores"] = all_scores
    state["student_perf"] = calculate_student_performance(all_scores)
    state["module_perf"] = calculate_module_performance(all_scores)
    state["daily_perf"] = calculate_daily_performance(all_scores)
    return state


def node_assign_percentiles(state: PipelineState) -> PipelineState:
    """Agent 4: Assign percentiles and ranks."""
    logger.info("=== NODE: Assign Percentiles ===")
    if state["student_perf"].empty:
        return state

    state["student_perf"] = assign_overall_percentile_and_rank(state["student_perf"])
    state["module_perf"] = assign_module_percentile(state["module_perf"])
    return state


def node_assign_grades(state: PipelineState) -> PipelineState:
    """Agent 5: Assign letter grades."""
    logger.info("=== NODE: Assign Grades ===")
    if state["student_perf"].empty:
        return state
    state["student_perf"] = assign_grades_to_df(state["student_perf"])
    return state


def node_generate_cards(state: PipelineState) -> PipelineState:
    """Agent 6: Generate PDF grade cards."""
    logger.info("=== NODE: Generate Grade Cards ===")
    perf = state["student_perf"]
    if perf.empty:
        state["grade_card_paths"] = {}
        return state

    output_dir = config["paths"]["reports_folder"]
    paths = generate_all_grade_cards(
        perf, state["module_perf"], state["daily_perf"], output_dir
    )
    # Build {email: path} mapping
    card_map = {}
    for _, student in perf.iterrows():
        safe_name = "".join(c if c.isalnum() else "_" for c in student["name"])
        pdf = os.path.join(output_dir, f"grade_card_{safe_name}.pdf")
        if os.path.exists(pdf):
            card_map[student["email"]] = pdf
    state["grade_card_paths"] = card_map
    return state


def node_send_emails(state: PipelineState) -> PipelineState:
    """Agent 7: Email grade cards."""
    logger.info("=== NODE: Send Emails ===")
    if state["student_perf"].empty:
        state["email_results"] = {}
        return state
    results = send_all_emails(state["student_perf"], state["grade_card_paths"])
    state["email_results"] = results
    return state


def node_write_outputs(state: PipelineState) -> PipelineState:
    """Agent 8 (Dashboard data + file outputs): Write master/summary/rankings CSVs."""
    logger.info("=== NODE: Write Outputs ===")
    if not state["student_perf"].empty:
        db = DatabaseManager()
        db.upsert_performance(state["student_perf"])
        db.upsert_module_performance(state["module_perf"])
        write_all_outputs(
            state["student_perf"],
            state["module_perf"],
            config["paths"]["output_folder"],
        )
    logger.info("=== Pipeline Complete ===")
    return state


# ── Build the graph ────────────────────────────────────────────────────────────
def build_pipeline() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("scan_files",            node_scan_files)
    graph.add_node("clean_data",            node_clean_data)
    graph.add_node("calculate_performance", node_calculate_performance)
    graph.add_node("assign_percentiles",    node_assign_percentiles)
    graph.add_node("assign_grades",         node_assign_grades)
    graph.add_node("generate_cards",        node_generate_cards)
    graph.add_node("send_emails",           node_send_emails)
    graph.add_node("write_outputs",         node_write_outputs)

    graph.set_entry_point("scan_files")
    graph.add_edge("scan_files",            "clean_data")
    graph.add_edge("clean_data",            "calculate_performance")
    graph.add_edge("calculate_performance", "assign_percentiles")
    graph.add_edge("assign_percentiles",    "assign_grades")
    graph.add_edge("assign_grades",         "generate_cards")
    graph.add_edge("generate_cards",        "send_emails")
    graph.add_edge("send_emails",           "write_outputs")
    graph.add_edge("write_outputs",         END)

    return graph.compile()


def run_pipeline() -> PipelineState:
    """Run the full agentic pipeline once."""
    app = build_pipeline()
    initial_state: PipelineState = {
        "new_files": [],
        "all_scores": pd.DataFrame(),
        "student_perf": pd.DataFrame(),
        "module_perf": pd.DataFrame(),
        "daily_perf": pd.DataFrame(),
        "grade_card_paths": {},
        "email_results": {},
        "errors": [],
    }
    result = app.invoke(initial_state)
    return result
