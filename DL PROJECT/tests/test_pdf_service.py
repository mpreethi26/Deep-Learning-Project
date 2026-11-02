"""
Unit Tests for PDF Service.
"""
import pytest
import fitz
from services.pdf_service import PDFService

def create_sample_pdf_bytes(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_extract_valid_pdf():
    sample_text = "This is a machine readable academic document page."
    pdf_bytes = create_sample_pdf_bytes(sample_text)
    result = PDFService.extract_text_from_bytes(pdf_bytes, filename="test.pdf")

    assert result["success"] is True
    assert result["total_pages"] == 1
    assert result["word_count"] > 0
    assert "academic" in result["text"]

def test_extract_empty_pdf():
    # PDF with no text on page
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    result = PDFService.extract_text_from_bytes(pdf_bytes, filename="empty.pdf")
    assert result["success"] is False
    assert "scanned" in result["error"].lower() or "no machine-readable text" in result["error"].lower()

def test_extract_corrupted_pdf():
    corrupted_bytes = b"NOT_A_VALID_PDF_HEADER_OR_CONTENT"
    result = PDFService.extract_text_from_bytes(corrupted_bytes, filename="corrupt.pdf")
    assert result["success"] is False
    assert "failed" in result["error"].lower()
