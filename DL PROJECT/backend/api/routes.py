import os
import sys
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from services.model_manager import ModelManager
from services.summarization_service import SummarizationService
from services.pdf_service import PDFService
from services.evaluation_service import EvaluationService
from services.history_service import HistoryService
from services.job_service import JobManager
from backend.schemas.summarization import (
    SummarizeRequest,
    SummarizeResponse,
    JobCreateResponse,
    JobStatusResponse,
    CompareRequest,
    CompareResponse,
    EvaluateRequest,
    EvaluateResponse,
    StatsResponse
)

router = APIRouter(prefix="/api")
model_manager = ModelManager()
summarizer = SummarizationService()
evaluator = EvaluationService()
pdf_service = PDFService()
history_service = HistoryService()
job_manager = JobManager()

@router.get("/health", tags=["Health"])
async def health_check():
    """Non-blocking health and device status probe."""
    loaded_info = model_manager.get_loaded_model_info()
    return {
        "status": "healthy",
        "application": config.PROJECT_TITLE,
        "team_lead": config.TEAM_LEAD,
        "device": model_manager.device_name,
        "active_model": loaded_info["display_name"] if loaded_info else "None (Lazy load on demand)",
        "active_model_key": loaded_info["key"] if loaded_info else None,
        "supported_models": list(config.SUPPORTED_MODELS.keys())
    }

@router.get("/models", tags=["Models"])
async def get_models():
    """Returns supported Transformer models and length profiles."""
    models_list = []
    loaded_key = model_manager._loaded_model_key
    for key, val in config.SUPPORTED_MODELS.items():
        m_dict = dict(val)
        m_dict["key"] = key
        m_dict["is_loaded"] = (key == loaded_key)
        models_list.append(m_dict)
    
    return {
        "models": models_list,
        "default_model": config.DEFAULT_MODEL_KEY,
        "length_profiles": config.LENGTH_PROFILES
    }

@router.post("/summarize", response_model=SummarizeResponse, tags=["Summarization"])
async def summarize_text(req: SummarizeRequest):
    """Generates abstractive text summary using Transformer models."""
    result = summarizer.generate_summary(
        text=req.text,
        model_key=req.model_key,
        length_mode=req.length_mode,
        custom_min_tokens=req.custom_min_tokens,
        custom_max_tokens=req.custom_max_tokens,
        custom_num_beams=req.custom_num_beams,
        custom_length_penalty=req.custom_length_penalty,
        target_word_count=req.target_word_count,
        do_sample=req.do_sample,
    )

    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Summarization failed")
        )

    # Persist in session history
    history_service.create_record(
        summary_result=result,
        source_type="Pasted Text",
        filename=None
    )

    return result

@router.post("/jobs/summarize", response_model=JobCreateResponse, tags=["Jobs"])
async def create_summarize_job(req: SummarizeRequest):
    """Enqueues an asynchronous text summarization job and returns a job_id for polling."""
    job_id = job_manager.create_text_job(
        text=req.text,
        model_key=req.model_key,
        length_mode=req.length_mode,
        custom_min_tokens=req.custom_min_tokens,
        custom_max_tokens=req.custom_max_tokens,
        custom_num_beams=req.custom_num_beams,
        custom_length_penalty=req.custom_length_penalty,
        target_word_count=req.target_word_count,
        do_sample=req.do_sample,
    )
    return {"job_id": job_id, "status": "pending", "message": "Text summarization job enqueued"}

@router.post("/jobs/summarize/pdf", response_model=JobCreateResponse, tags=["Jobs"])
async def create_summarize_pdf_job(
    file: UploadFile = File(...),
    model_key: str = Form("t5_small"),
    length_mode: str = Form("medium"),
    target_word_count: Optional[int] = Form(None),
    custom_min_tokens: Optional[int] = Form(None),
    custom_max_tokens: Optional[int] = Form(None),
    custom_num_beams: Optional[int] = Form(None),
    custom_length_penalty: Optional[float] = Form(None),
    do_sample: bool = Form(False)
):
    """Enqueues an asynchronous PDF summarization job and returns a job_id for polling."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported."
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF file is empty (0 bytes)."
        )

    job_id = job_manager.create_pdf_job(
        file_bytes=contents,
        filename=file.filename,
        model_key=model_key,
        length_mode=length_mode,
        custom_min_tokens=custom_min_tokens,
        custom_max_tokens=custom_max_tokens,
        custom_num_beams=custom_num_beams,
        custom_length_penalty=custom_length_penalty,
        target_word_count=target_word_count,
        do_sample=do_sample,
    )
    return {"job_id": job_id, "status": "pending", "message": "PDF summarization job enqueued"}

@router.get("/jobs/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
async def get_job_status(job_id: str):
    """Polls status, progress, and result of an asynchronous summarization job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found."
        )
    return job

@router.post("/summarize/pdf", tags=["Summarization"])
async def summarize_pdf(
    file: UploadFile = File(...),
    model_key: str = Form("t5_small"),
    length_mode: str = Form("medium"),
    target_word_count: Optional[int] = Form(None),
    custom_min_tokens: Optional[int] = Form(None),
    custom_max_tokens: Optional[int] = Form(None),
    custom_num_beams: Optional[int] = Form(None),
    custom_length_penalty: Optional[float] = Form(None),
    do_sample: bool = Form(False)
):
    """Extracts text from uploaded PDF and generates an abstractive summary."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported."
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF file is empty (0 bytes)."
        )

    pdf_res = pdf_service.extract_text_from_bytes(contents, filename=file.filename)
    if not pdf_res.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pdf_res.get("error", "Failed to extract text from PDF")
        )

    extracted_text = pdf_res["text"]

    result = summarizer.generate_summary(
        text=extracted_text,
        model_key=model_key,
        length_mode=length_mode,
        custom_min_tokens=custom_min_tokens,
        custom_max_tokens=custom_max_tokens,
        custom_num_beams=custom_num_beams,
        custom_length_penalty=custom_length_penalty,
        target_word_count=target_word_count,
        do_sample=do_sample,
    )

    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Summarization of PDF text failed")
        )

    # Add PDF metadata to result
    result["pdf_metadata"] = {
        "filename": file.filename,
        "file_size_mb": pdf_res.get("file_size_mb"),
        "total_pages": pdf_res.get("total_pages"),
        "pages_with_text": pdf_res.get("pages_with_text"),
        "extracted_char_count": pdf_res.get("char_count"),
    }

    # Persist in session history
    history_service.create_record(
        summary_result=result,
        source_type="PDF Document",
        filename=file.filename
    )

    return result

@router.post("/compare", response_model=CompareResponse, tags=["Comparison"])
async def compare_models(req: CompareRequest):
    """Runs comparative inference across DistilBART and T5-small sequentially."""
    req_models = req.models or ["distilbart", "t5_small"]
    resolved_models = []
    for m in req_models:
        res_key = model_manager.resolve_model_key(m)
        if res_key in config.SUPPORTED_MODELS and res_key not in resolved_models:
            resolved_models.append(res_key)
    if not resolved_models:
        resolved_models = ["distilbart", "t5_small"]

    results = {}
    for m_key in resolved_models:
        res = summarizer.generate_summary(
            text=req.text,
            model_key=m_key,
            length_mode=req.length_mode,
            custom_num_beams=2,  # 2 beams for fast comparative response and timeout prevention
        )
        if res.get("success", False):
            if req.reference_summary and req.reference_summary.strip():
                ev = evaluator.evaluate(res["summary"], req.reference_summary)
                res["evaluation"] = ev.get("metrics", {})
            results[m_key] = res
            if m_key == "distilbart":
                results["bart"] = res
            elif m_key == "t5_small":
                results["t5"] = res
        else:
            err_dict = {"success": False, "error": res.get("error", "Inference failed")}
            results[m_key] = err_dict
            if m_key == "distilbart":
                results["bart"] = err_dict
            elif m_key == "t5_small":
                results["t5"] = err_dict

    return {"success": True, "results": results}

@router.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
async def evaluate_summary(req: EvaluateRequest):
    """Evaluates generated summary against reference ground truth via ROUGE and BERTScore."""
    res = evaluator.evaluate(
        generated_summary=req.generated_summary,
        reference_summary=req.reference_summary,
        original_text=req.original_text,
        include_bertscore=req.include_bertscore
    )

    if not res.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("error", "Evaluation failed")
        )

    return res

@router.get("/history", tags=["History"])
async def get_history():
    """Retrieves all recorded summarization runs."""
    records = history_service.get_all()
    return {"records": records, "total": len(records)}

@router.delete("/history/{record_id}", tags=["History"])
async def delete_history_item(record_id: str):
    """Deletes a specific history record by ID."""
    success = history_service.delete_record(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record {record_id} not found"
        )
    return {"success": True, "id": record_id}

@router.delete("/history", tags=["History"])
async def clear_all_history():
    """Clears all history records."""
    history_service.clear_all()
    return {"success": True, "message": "History cleared"}

@router.get("/stats", response_model=StatsResponse, tags=["Dashboard"])
async def get_stats():
    """Computes real-time aggregate statistics from recorded session operations."""
    stats = history_service.compute_aggregate_stats()
    return stats
