"""
Agent 7: Email Agent
Sends personalised grade card PDFs to each student via Gmail SMTP.
Set SEND_EMAILS=true in .env to activate.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
import pandas as pd
from utils.logger import get_logger
from utils.config_loader import load_config, get_env

logger = get_logger("EmailAgent")
config = load_config()


def _build_html_body(student: pd.Series) -> str:
    grade_emoji = {"A+": "🏆", "A": "⭐", "B+": "👍", "B": "✅", "C": "📘", "D": "📗", "F": "📕"}
    emoji = grade_emoji.get(student["grade"], "📄")
    return f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width:600px; margin:auto; border:1px solid #e0e0e0; border-radius:8px; overflow:hidden;">
      <div style="background:#1A237E; padding:20px; text-align:center;">
        <h2 style="color:white; margin:0;">{config['system']['institution']}</h2>
        <p style="color:#E3F2FD; margin:4px 0;">{config['system']['training']}</p>
      </div>
      <div style="padding:20px;">
        <p>Dear <b>{student['name']}</b>,</p>
        <p>Your performance grade card has been updated. Here is a summary:</p>
        <table style="width:100%; border-collapse:collapse;">
          <tr style="background:#E3F2FD;">
            <td style="padding:8px; border:1px solid #ddd;"><b>Overall Score</b></td>
            <td style="padding:8px; border:1px solid #ddd;">
              {student['total_marks']:.1f} / {student['total_max']:.1f}
            </td>
          </tr>
          <tr>
            <td style="padding:8px; border:1px solid #ddd;"><b>Overall Percentage</b></td>
            <td style="padding:8px; border:1px solid #ddd;">{student['overall_percentage']:.2f}%</td>
          </tr>
          <tr style="background:#E3F2FD;">
            <td style="padding:8px; border:1px solid #ddd;"><b>Overall Percentile</b></td>
            <td style="padding:8px; border:1px solid #ddd;">{student['overall_percentile']:.2f}</td>
          </tr>
          <tr>
            <td style="padding:8px; border:1px solid #ddd;"><b>Rank</b></td>
            <td style="padding:8px; border:1px solid #ddd;">#{student['rank']}</td>
          </tr>
          <tr style="background:#E3F2FD;">
            <td style="padding:8px; border:1px solid #ddd;"><b>Grade</b></td>
            <td style="padding:8px; border:1px solid #ddd; font-size:20px;">
              {emoji} {student['grade']}
            </td>
          </tr>
        </table>
        <p style="margin-top:16px;">Please find your detailed grade card attached.</p>
        <p>Keep up the great work! 🚀</p>
      </div>
      <div style="background:#f5f5f5; padding:10px; text-align:center; font-size:11px; color:#888;">
        Automated Training Performance Management System | Agentic AI Project
      </div>
    </div>
    </body></html>
    """


def send_grade_card(student: pd.Series, pdf_path: str) -> bool:
    """Send one grade card email. Returns True on success."""
    sender = get_env("EMAIL_SENDER")
    password = get_env("EMAIL_PASSWORD")
    if not sender or not password:
        logger.warning("EMAIL_SENDER or EMAIL_PASSWORD not set. Skipping email.")
        return False

    recipient = student["email"]
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = (
        f"[{config['system']['training']}] Your Updated Grade Card – "
        f"{student['grade']} | Rank #{student['rank']}"
    )

    msg.attach(MIMEText(_build_html_body(student), "html"))

    # Attach PDF
    if pdf_path and Path(pdf_path).exists():
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{Path(pdf_path).name}"',
        )
        msg.attach(part)

    try:
        with smtplib.SMTP(config["email"]["smtp_host"], config["email"]["smtp_port"]) as srv:
            srv.ehlo()
            srv.starttls()
            srv.login(sender, password)
            srv.sendmail(sender, recipient, msg.as_string())
        logger.info(f"Email sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Email failed for {recipient}: {e}")
        return False


def send_all_emails(perf: pd.DataFrame, grade_card_paths: dict[str, str]) -> dict:
    """
    Send emails to all students.
    grade_card_paths: {email: pdf_path}
    """
    if get_env("SEND_EMAILS", "false").lower() != "true":
        logger.info("Email sending disabled (SEND_EMAILS != true). Skipping.")
        return {"sent": 0, "failed": 0, "skipped": len(perf)}

    results = {"sent": 0, "failed": 0, "skipped": 0}
    for _, student in perf.iterrows():
        pdf = grade_card_paths.get(student["email"], "")
        ok = send_grade_card(student, pdf)
        if ok:
            results["sent"] += 1
        else:
            results["failed"] += 1
    logger.info(f"Email results: {results}")
    return results
