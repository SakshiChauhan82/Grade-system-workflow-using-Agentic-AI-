"""
Agent 6: Grade Card Generator Agent
Generates individual PDF grade cards using ReportLab.
"""
import os
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("GradeCardGeneratorAgent")
config = load_config()

# Color palette
PRIMARY   = colors.HexColor("#1A237E")   # deep indigo
ACCENT    = colors.HexColor("#42A5F5")   # blue
LIGHT_BG  = colors.HexColor("#E3F2FD")
GOLD      = colors.HexColor("#FFC107")
GREEN     = colors.HexColor("#2E7D32")
RED       = colors.HexColor("#C62828")
WHITE     = colors.white
GREY_LINE = colors.HexColor("#BDBDBD")


def _grade_color(grade: str) -> colors.Color:
    if grade in ("A+", "A"):
        return GREEN
    if grade in ("B+", "B"):
        return ACCENT
    if grade == "C":
        return GOLD
    return RED


def generate_grade_card(
    student: pd.Series,
    module_perf: pd.DataFrame,
    daily_perf: pd.DataFrame,
    output_dir: str,
) -> str:
    """Generate a PDF grade card for one student and return the file path."""
    os.makedirs(output_dir, exist_ok=True)
    email = student["email"]
    safe_name = "".join(c if c.isalnum() else "_" for c in student["name"])
    out_path = os.path.join(output_dir, f"grade_card_{safe_name}.pdf")

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    h_center = ParagraphStyle("hc", alignment=TA_CENTER, fontSize=11, textColor=PRIMARY)
    title_s  = ParagraphStyle("title", alignment=TA_CENTER, fontSize=18,
                               textColor=WHITE, fontName="Helvetica-Bold")
    sub_s    = ParagraphStyle("sub",   alignment=TA_CENTER, fontSize=10,
                               textColor=LIGHT_BG)
    body_s   = styles["Normal"]

    elems = []

    # ── Header banner ──────────────────────────────────────────────
    header_data = [[
        Paragraph(config["system"]["institution"], title_s),
    ], [
        Paragraph(config["system"]["training"], sub_s),
    ], [
        Paragraph("PERFORMANCE GRADE CARD", title_s),
    ]]
    header_table = Table(header_data, colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elems.append(header_table)
    elems.append(Spacer(1, 0.4 * cm))

    # ── Student info ───────────────────────────────────────────────
    info_data = [
        ["Student Name", ":", student["name"],
         "Email", ":", email],
        ["Rank", ":", f"#{student['rank']}",
         "Quizzes Attempted", ":", str(int(student["quizzes_attempted"]))],
        ["Overall Score", ":", f"{student['total_marks']:.1f} / {student['total_max']:.1f}",
         "Overall Percentage", ":", f"{student['overall_percentage']:.2f}%"],
        ["Overall Percentile", ":", f"{student['overall_percentile']:.2f}",
         "Grade", ":",
         Paragraph(f"<b>{student['grade']}</b>",
                   ParagraphStyle("g", textColor=_grade_color(student["grade"]),
                                  fontSize=13))],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 0.4*cm, 5*cm, 3.5*cm, 0.4*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.3, GREY_LINE),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(info_table)
    elems.append(Spacer(1, 0.4 * cm))

    # ── Module-wise performance ────────────────────────────────────
    elems.append(Paragraph("<b>Module-wise Performance</b>", h_center))
    elems.append(Spacer(1, 0.2 * cm))

    s_mod = module_perf[module_perf["email"] == email].copy()
    if not s_mod.empty:
        mod_rows = [["Module", "Marks", "Max", "Percentage", "Percentile"]]
        for _, row in s_mod.iterrows():
            mod_rows.append([
                row["module"],
                f"{row['module_marks']:.1f}",
                f"{row['module_max']:.1f}",
                f"{row['module_percentage']:.2f}%",
                f"{row['module_percentile']:.2f}",
            ])
        mod_table = Table(mod_rows, colWidths=[7*cm, 2*cm, 2*cm, 3*cm, 3*cm])
        mod_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.3, GREY_LINE),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elems.append(mod_table)
    else:
        elems.append(Paragraph("No module data available.", body_s))

    elems.append(Spacer(1, 0.4 * cm))

    # ── Daily quiz scores ──────────────────────────────────────────
    elems.append(Paragraph("<b>Daily Quiz Scores</b>", h_center))
    elems.append(Spacer(1, 0.2 * cm))

    s_daily = daily_perf[daily_perf["email"] == email].sort_values("quiz_number")
    if not s_daily.empty:
        day_rows = [["Quiz #", "Date", "Module", "Score", "Max", "%"]]
        for _, row in s_daily.iterrows():
            day_rows.append([
                f"Q{int(row['quiz_number'])}",
                str(row["quiz_date"]),
                row["module"],
                f"{row['raw_score']:.1f}",
                f"{row['max_score']:.1f}",
                f"{row['percentage']:.1f}%",
            ])
        day_table = Table(day_rows, colWidths=[1.5*cm, 2.5*cm, 6*cm, 1.8*cm, 1.8*cm, 2.4*cm])
        day_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.3, GREY_LINE),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 3),
        ]))
        elems.append(day_table)

    # ── Footer ─────────────────────────────────────────────────────
    elems.append(Spacer(1, 0.5 * cm))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=PRIMARY))
    elems.append(Paragraph(
        "Generated by Automated Training Performance Management System | Agentic AI Project",
        ParagraphStyle("footer", alignment=TA_CENTER, fontSize=7, textColor=GREY_LINE)
    ))

    doc.build(elems)
    logger.info(f"Grade card generated: {out_path}")
    return out_path


def generate_all_grade_cards(
    perf: pd.DataFrame,
    module_perf: pd.DataFrame,
    daily_perf: pd.DataFrame,
    output_dir: str,
) -> list[str]:
    """Generate grade cards for all students."""
    paths = []
    for _, student in perf.iterrows():
        try:
            p = generate_grade_card(student, module_perf, daily_perf, output_dir)
            paths.append(p)
        except Exception as e:
            logger.error(f"Failed grade card for {student.get('email')}: {e}")
    logger.info(f"Generated {len(paths)} grade cards.")
    return paths
