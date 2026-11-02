"""
Download Utilities for Exporting Generated Summaries.
Supports TXT, Markdown, and JSON formats with full metadata.
"""
import json
from datetime import datetime
from typing import Dict, Any

def format_summary_txt(summary: str, metadata: Dict[str, Any]) -> str:
    """Formats summary and execution statistics as a plain text report."""
    timestamp = metadata.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    model_name = metadata.get("model", "BART")
    orig_words = metadata.get("original_words", 0)
    sum_words = metadata.get("summary_words", 0)
    ratio = metadata.get("compression_ratio", 0.0)
    duration = metadata.get("processing_time", 0.0)

    report = [
        "=" * 70,
        "ABSTRACTIVE TEXT SUMMARIZATION REPORT",
        "=" * 70,
        f"Generated At      : {timestamp}",
        f"Model Used        : {model_name}",
        f"Original Words    : {orig_words}",
        f"Summary Words     : {sum_words}",
        f"Compression Ratio : {ratio}%",
        f"Processing Time   : {duration:.2f} seconds",
        "=" * 70,
        "",
        "GENERATED ABSTRACTIVE SUMMARY:",
        "-" * 70,
        summary.strip(),
        "",
        "=" * 70,
        "Project: Abstractive Text Summarization Using Transformer Models",
        "Team Lead: CHOUDAM BHARATH REDDY",
        "=" * 70,
    ]
    return "\n".join(report)

def format_summary_markdown(summary: str, metadata: Dict[str, Any]) -> str:
    """Formats summary and execution statistics as GitHub-flavored Markdown."""
    timestamp = metadata.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    model_name = metadata.get("model", "BART")
    orig_words = metadata.get("original_words", 0)
    sum_words = metadata.get("summary_words", 0)
    ratio = metadata.get("compression_ratio", 0.0)
    duration = metadata.get("processing_time", 0.0)
    source = metadata.get("source", "Pasted Text")

    md = [
        "# Abstractive Text Summarization Report",
        "",
        f"> **Generated:** {timestamp}  ",
        f"> **Model:** `{model_name}`  ",
        f"> **Source:** {source}",
        "",
        "## Summary Statistics",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Original Words** | {orig_words} |",
        f"| **Summary Words** | {sum_words} |",
        f"| **Compression Ratio** | {ratio}% |",
        f"| **Processing Latency** | {duration:.2f} s |",
        "",
        "## Generated Summary",
        "",
        summary.strip(),
        "",
        "---",
        "*Project: Abstractive Text Summarization Using Transformer Models | Team Lead: CHOUDAM BHARATH REDDY*",
    ]
    return "\n".join(md)

def format_summary_json(summary: str, metadata: Dict[str, Any]) -> str:
    """Formats summary and full metadata as JSON."""
    payload = {
        "project": "Abstractive Text Summarization Using Transformer Models",
        "team_lead": "CHOUDAM BHARATH REDDY",
        "summary": summary.strip(),
        "metadata": metadata
    }
    return json.dumps(payload, indent=2)
