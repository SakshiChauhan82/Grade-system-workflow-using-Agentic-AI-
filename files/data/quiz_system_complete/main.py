"""
Main entry point for the Automated Training Performance Management System.

Usage:
  python main.py            # Run pipeline once (processes any new files)
  python main.py --watch    # Run continuously, auto-detecting new quiz files
  python main.py --test     # Quick smoke test
"""
import sys
import time
import argparse
from utils.logger import get_logger
from pipeline import run_pipeline
from agents.file_monitor_agent import start_watcher
from utils.config_loader import load_config

logger = get_logger("Main")
config = load_config()


def _on_new_file(file_info: dict):
    """Callback fired by watchdog when a new quiz file appears."""
    logger.info(f"Watchdog triggered pipeline for: {file_info['filename']}")
    try:
        result = run_pipeline()
        errors = result.get("errors", [])
        n_students = len(result.get("student_perf", []))
        logger.info(f"Pipeline done. Students: {n_students}, Errors: {errors}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Training Performance Management System")
    parser.add_argument("--watch", action="store_true",
                        help="Keep running and watch for new files")
    parser.add_argument("--test", action="store_true",
                        help="Run a quick smoke test")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  Automated Training Performance Management System")
    print("  ML & Agentic AI Training — Lloyd Institute")
    print("="*60 + "\n")

    if args.test:
        _run_smoke_test()
        return

    # Always run pipeline once on startup (picks up any unprocessed files)
    logger.info("Running initial pipeline pass...")
    result = run_pipeline()
    _print_summary(result)

    if args.watch:
        quiz_folder = config["paths"]["quiz_folder"]
        logger.info(f"Watching folder: {quiz_folder}")
        print(f"\n📡 Watching for new quiz files in: {quiz_folder}")
        print("   Drop a new quiz CSV into that folder and the system will auto-update.")
        print("   Press Ctrl+C to stop.\n")
        observer = start_watcher(quiz_folder, _on_new_file)
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info("Shutting down watchdog...")
            observer.stop()
            observer.join()


def _print_summary(result: dict):
    perf = result.get("student_perf")
    if perf is None or (hasattr(perf, "empty") and perf.empty):
        print("⚠️  No student data processed yet.\n")
        return

    print(f"\n{'─'*50}")
    print(f"  Students processed : {len(perf)}")
    print(f"  Top student        : {perf.iloc[0]['name']} ({perf.iloc[0]['overall_percentage']:.1f}%)")
    print(f"  Grade distribution : {perf['grade'].value_counts().to_dict()}")
    print(f"  Grade cards saved  : {len(result.get('grade_card_paths', {}))}")
    errors = result.get("errors", [])
    if errors:
        print(f"  ⚠️  Errors          : {len(errors)}")
    print(f"{'─'*50}\n")
    print("✅ Output files saved in: output/")
    print("📄 Grade cards saved in: reports/grade_cards/")
    print("📊 Launch dashboard   : streamlit run dashboard/app.py\n")


def _run_smoke_test():
    """Quick validation that all imports and DB work."""
    print("Running smoke test...")
    from utils.database import DatabaseManager
    db = DatabaseManager()
    print("  ✅ Database OK")
    from utils.schedule_loader import load_schedule
    s = load_schedule()
    print(f"  ✅ Schedule OK ({len(s)} quiz entries)")
    result = run_pipeline()
    perf = result.get("student_perf")
    if perf is not None and not perf.empty:
        print(f"  ✅ Pipeline OK — {len(perf)} students processed")
    else:
        print("  ⚠️  Pipeline ran but no data (may be no quiz files yet)")
    print("Smoke test complete.\n")


if __name__ == "__main__":
    main()
