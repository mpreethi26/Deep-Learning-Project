"""
PDF Extraction Service.
Extracts clean machine-readable text from PDF files using PyMuPDF (fitz).
Detects scanned/image-only PDFs, validates file size, and provides page-level summaries.
"""
import io
import os
import logging
from typing import Dict, Any, Tuple
import fitz  # PyMuPDF
import config
from utils.text_utils import clean_text, compute_text_stats

logger = logging.getLogger(__name__)

class PDFService:
    """Service for extracting and validating text from PDF files."""

    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Parses PDF bytes, checks for machine-readable text,
        and returns clean text with metadata.
        """
        size_mb = len(file_bytes) / (1024 * 1024)
        max_allowed = config.PDF_SETTINGS["max_file_size_mb"]

        if size_mb > max_allowed:
            return {
                "success": False,
                "error": f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {max_allowed} MB.",
                "text": "",
            }

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)

            if total_pages == 0:
                return {
                    "success": False,
                    "error": "The uploaded PDF has 0 pages or is empty.",
                    "text": "",
                }

            extracted_pages = []
            pages_with_text = 0

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_text = page.get_text("text")
                cleaned_page = clean_text(page_text)
                if cleaned_page:
                    pages_with_text += 1
                    extracted_pages.append(cleaned_page)

            doc.close()

            full_text = "\n\n".join(extracted_pages).strip()

            if not full_text:
                return {
                    "success": False,
                    "error": (
                        "No machine-readable text found in the PDF. "
                        "The document appears to be scanned or contains image-only pages. "
                        "Abstractive summarization requires selectable text (OCR is required for scanned documents)."
                    ),
                    "text": "",
                    "total_pages": total_pages,
                    "pages_with_text": 0,
                    "file_size_mb": round(size_mb, 2),
                }

            stats = compute_text_stats(full_text)

            return {
                "success": True,
                "filename": filename,
                "file_size_mb": round(size_mb, 2),
                "total_pages": total_pages,
                "pages_with_text": pages_with_text,
                "text": full_text,
                "word_count": stats["word_count"],
                "char_count": stats["char_count"],
                "sentence_count": stats["sentence_count"],
            }

        except Exception as e:
            logger.error(f"Failed to extract PDF '{filename}': {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to parse PDF document: {str(e)}",
                "text": "",
            }
