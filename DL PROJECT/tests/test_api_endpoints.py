"""
Comprehensive FastAPI Backend Integration Tests.
Tests health, model catalog, text summarization, evaluation, history, and stats endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "Abstractive Text Summarization" in data["title"]
    assert data["health"] == "/api/health"

def test_health_check_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "device" in data
    assert "distilbart" in data["supported_models"]
    assert "t5_small" in data["supported_models"]

def test_get_models_endpoint():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert len(data["models"]) >= 2
    keys = [m["key"] for m in data["models"]]
    assert "distilbart" in keys
    assert "t5_small" in keys
    assert "length_profiles" in data
    assert "short" in data["length_profiles"]
    assert "detailed" in data["length_profiles"]

def test_summarize_empty_validation():
    resp = client.post("/api/summarize", json={"text": "", "model_key": "bart"})
    assert resp.status_code in [400, 422]

def test_summarize_too_short_validation():
    resp = client.post("/api/summarize", json={"text": "Hello world", "model_key": "bart"})
    assert resp.status_code in [400, 422]

def test_summarize_valid_text():
    sample_text = (
        "Artificial intelligence and deep neural networks have fundamentally transformed "
        "computational linguistics and abstractive text summarization. Sequence to sequence models "
        "equipped with multi-head self-attention mechanisms can synthesize long documents and retain "
        "salient contextual semantic representations across diverse paragraphs and domains."
    )
    resp = client.post("/api/summarize", json={
        "text": sample_text,
        "model_key": "bart",
        "length_mode": "short"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["summary"]) > 0
    assert data["summary_word_count"] > 0
    assert data["input_word_count"] > 0
    assert "compression_ratio" in data

def test_evaluate_endpoint():
    generated = "BART is a sequence-to-sequence model designed for generative language tasks."
    reference = "BART is a sequence-to-sequence neural network model for text generation and summarization."
    
    resp = client.post("/api/evaluate", json={
        "generated_summary": generated,
        "reference_summary": reference
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "metrics" in data
    assert "rouge1" in data["metrics"]
    assert "fmeasure" in data["metrics"]["rouge1"]
    assert data["metrics"]["rouge1"]["fmeasure"] > 0.0

def test_evaluate_missing_reference():
    resp = client.post("/api/evaluate", json={
        "generated_summary": "Some generated text.",
        "reference_summary": ""
    })
    assert resp.status_code in [400, 422]

def test_history_and_stats_flow():
    # 1. Fetch stats
    stats_resp = client.get("/api/stats")
    assert stats_resp.status_code == 200
    initial_stats = stats_resp.json()
    
    # 2. Fetch history
    hist_resp = client.get("/api/history")
    assert hist_resp.status_code == 200
    records = hist_resp.json()["records"]
    assert isinstance(records, list)

    if records:
        target_id = records[0]["id"]
        # Delete first record
        del_resp = client.delete(f"/api/history/{target_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["id"] == target_id

def test_pdf_invalid_format():
    resp = client.post(
        "/api/summarize/pdf",
        files={"file": ("test.txt", b"not a pdf", "text/plain")}
    )
    assert resp.status_code == 400
    assert "Invalid file format" in resp.json()["detail"]

def test_create_job_and_poll():
    sample_text = (
        "Artificial intelligence and deep neural networks have fundamentally transformed "
        "computational linguistics and abstractive text summarization. Sequence to sequence models "
        "equipped with multi-head self-attention mechanisms can synthesize long documents and retain "
        "salient contextual semantic representations across diverse paragraphs and domains."
    )
    # Enqueue job
    resp = client.post("/api/jobs/summarize", json={
        "text": sample_text,
        "model_key": "t5_small",
        "length_mode": "short"
    })
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]
    assert job_id is not None

    # Check status endpoint
    status_resp = client.get(f"/api/jobs/{job_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["job_id"] == job_id
    assert data["status"] in ["pending", "processing", "completed"]
