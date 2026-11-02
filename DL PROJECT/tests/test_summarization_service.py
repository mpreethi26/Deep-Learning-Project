"""
Integration / Unit Tests for Summarization Service.
"""
import pytest
from services.summarization_service import SummarizationService
from services.history_service import HistoryService

def test_summarization_validation():
    service = SummarizationService()
    res = service.generate_summary("")
    assert res["success"] is False
    assert "empty" in res["error"].lower()

    res_short = service.generate_summary("Too short")
    assert res_short["success"] is False

def test_history_service_aggregations():
    rec1 = {
        "id": "1",
        "input_word_count": 100,
        "summary_word_count": 25,
        "compression_ratio": 75.0,
        "processing_time": 2.0,
    }
    rec2 = {
        "id": "2",
        "input_word_count": 200,
        "summary_word_count": 50,
        "compression_ratio": 75.0,
        "processing_time": 4.0,
    }
    stats = HistoryService.compute_aggregate_stats([rec1, rec2])
    assert stats["total_documents"] == 2
    assert stats["avg_input_words"] == 150.0
    assert stats["avg_output_words"] == 37.5
    assert stats["avg_processing_time"] == 3.0
