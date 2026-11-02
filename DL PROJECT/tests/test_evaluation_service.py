"""
Unit Tests for Evaluation Service.
"""
import pytest
from services.evaluation_service import EvaluationService

def test_evaluation_success():
    gen = "Apollo 11 landed humans on the Moon in 1969."
    ref = "In 1969, NASA landed the first humans on the Moon."
    res = EvaluationService.evaluate(gen, ref, original_text="Long Apollo text here.")

    assert res["success"] is True
    assert "rouge1" in res["metrics"]
    assert "rouge2" in res["metrics"]
    assert "rougeL" in res["metrics"]
    assert res["metrics"]["rouge1"]["fmeasure"] > 0.0

def test_evaluation_missing_reference():
    res = EvaluationService.evaluate("Some generated summary.", "")
    assert res["success"] is False
    assert "reference" in res["error"].lower()

def test_evaluation_empty_candidate():
    res = EvaluationService.evaluate("", "Some reference text.")
    assert res["success"] is False
    assert "empty" in res["error"].lower()
