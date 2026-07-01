"""
Agent 1: File Monitoring Agent
Watches the quiz folder for new CSV/Excel files and triggers the pipeline.
"""
import os
import re
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import get_logger
from utils.config_loader import load_config
from utils.database import DatabaseManager

logger = get_logger("FileMonitorAgent")
config = load_config()


def extract_quiz_number(filename: str) -> int | None:
    """Parse quiz number from filename like Quiz1_15_6_26.csv or Quiz_3_17_6_26.csv"""
    name = Path(filename).stem
    # Try patterns: Quiz1, Quiz_1, Quiz 1
    m = re.search(r'[Qq]uiz[_\s]?(\d+)', name)
    if m:
        return int(m.group(1))
    return None


def scan_existing_files(quiz_folder: str, db: DatabaseManager) -> list[dict]:
    """Scan folder for quiz files not yet processed."""
    new_files = []
    supported = {".csv", ".xlsx", ".xls"}
    folder = Path(quiz_folder)
    if not folder.exists():
        logger.warning(f"Quiz folder not found: {quiz_folder}")
        return []

    for f in sorted(folder.iterdir()):
        if f.suffix.lower() not in supported:
            continue
        if db.is_processed(f.name):
            logger.debug(f"Already processed: {f.name}")
            continue
        qnum = extract_quiz_number(f.name)
        if qnum is None:
            logger.warning(f"Cannot parse quiz number from: {f.name}")
            continue
        new_files.append({"path": str(f), "filename": f.name, "quiz_number": qnum})
        logger.info(f"New file detected: {f.name} (Quiz {qnum})")

    return new_files


class QuizFileHandler(FileSystemEventHandler):
    """Watchdog handler — fires when a file is created/moved into the folder."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self._cooldown: dict[str, float] = {}

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._handle(event.dest_path)

    def _handle(self, path: str):
        p = Path(path)
        if p.suffix.lower() not in {".csv", ".xlsx", ".xls"}:
            return
        # Debounce: ignore repeated events within 2 s
        now = time.time()
        if now - self._cooldown.get(path, 0) < 2:
            return
        self._cooldown[path] = now
        qnum = extract_quiz_number(p.name)
        if qnum is None:
            logger.warning(f"Skipping unrecognised file: {p.name}")
            return
        logger.info(f"Watchdog detected new file: {p.name}")
        self.callback({"path": path, "filename": p.name, "quiz_number": qnum})


def start_watcher(quiz_folder: str, callback, daemon: bool = True):
    """Start background watchdog observer thread."""
    handler = QuizFileHandler(callback)
    observer = Observer()
    observer.schedule(handler, quiz_folder, recursive=False)
    t = threading.Thread(target=observer.start, daemon=daemon)
    t.start()
    logger.info(f"Watchdog observer started on: {quiz_folder}")
    return observer
