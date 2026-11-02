"""
Background Job Execution Service for Asynchronous Summarization.
Enables polling workflow with progress tracking to eliminate HTTP timeouts.
"""
import uuid
import time
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from services.summarization_service import SummarizationService
from services.pdf_service import PDFService
from services.history_service import HistoryService

logger = logging.getLogger(__name__)

class JobManager:
    _instance = None
    _jobs: Dict[str, Dict[str, Any]] = {}
    _executor: Optional[ThreadPoolExecutor] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
            cls._instance._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="summarize-job")
            cls._instance.summarizer = SummarizationService()
            cls._instance.pdf_service = PDFService()
            cls._instance.history_service = HistoryService()
        return cls._instance

    def create_text_job(
        self,
        text: str,
        model_key: str = "t5_small",
        length_mode: str = "medium",
        custom_min_tokens: Optional[int] = None,
        custom_max_tokens: Optional[int] = None,
        custom_num_beams: Optional[int] = None,
        custom_length_penalty: Optional[float] = None,
        target_word_count: Optional[int] = None,
        do_sample: bool = False,
    ) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "message": "Queued in background...",
            "created_at": time.time(),
            "result": None,
            "error": None,
        }

        self._executor.submit(
            self._execute_text_job,
            job_id,
            text,
            model_key,
            length_mode,
            custom_min_tokens,
            custom_max_tokens,
            custom_num_beams,
            custom_length_penalty,
            target_word_count,
            do_sample,
        )
        return job_id

    def _execute_text_job(
        self,
        job_id: str,
        text: str,
        model_key: str,
        length_mode: str,
        custom_min_tokens: Optional[int],
        custom_max_tokens: Optional[int],
        custom_num_beams: Optional[int],
        custom_length_penalty: Optional[float],
        target_word_count: Optional[int],
        do_sample: bool,
    ):
        def progress_cb(pct: int, msg: str):
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "processing"
                self._jobs[job_id]["progress"] = pct
                self._jobs[job_id]["message"] = msg

        try:
            progress_cb(5, "Starting summarization job...")
            result = self.summarizer.generate_summary(
                text=text,
                model_key=model_key,
                length_mode=length_mode,
                custom_min_tokens=custom_min_tokens,
                custom_max_tokens=custom_max_tokens,
                custom_num_beams=custom_num_beams,
                custom_length_penalty=custom_length_penalty,
                target_word_count=target_word_count,
                do_sample=do_sample,
                progress_callback=progress_cb,
            )

            if result.get("success", False):
                self.history_service.create_record(
                    summary_result=result,
                    source_type="Pasted Text (Background Job)",
                    filename=None
                )
                self._jobs[job_id]["status"] = "completed"
                self._jobs[job_id]["progress"] = 100
                self._jobs[job_id]["message"] = "Summary completed."
                self._jobs[job_id]["result"] = result
            else:
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["error"] = result.get("error", "Summarization failed")
                self._jobs[job_id]["message"] = "Inference failed."
        except Exception as e:
            logger.error(f"Job {job_id} encountered exception: {e}", exc_info=True)
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["error"] = str(e)
                self._jobs[job_id]["message"] = f"Error: {str(e)}"

    def create_pdf_job(
        self,
        file_bytes: bytes,
        filename: str,
        model_key: str = "t5_small",
        length_mode: str = "medium",
        custom_min_tokens: Optional[int] = None,
        custom_max_tokens: Optional[int] = None,
        custom_num_beams: Optional[int] = None,
        custom_length_penalty: Optional[float] = None,
        target_word_count: Optional[int] = None,
        do_sample: bool = False,
    ) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "message": "PDF received, queuing for extraction...",
            "created_at": time.time(),
            "result": None,
            "error": None,
        }

        self._executor.submit(
            self._execute_pdf_job,
            job_id,
            file_bytes,
            filename,
            model_key,
            length_mode,
            custom_min_tokens,
            custom_max_tokens,
            custom_num_beams,
            custom_length_penalty,
            target_word_count,
            do_sample,
        )
        return job_id

    def _execute_pdf_job(
        self,
        job_id: str,
        file_bytes: bytes,
        filename: str,
        model_key: str,
        length_mode: str,
        custom_min_tokens: Optional[int],
        custom_max_tokens: Optional[int],
        custom_num_beams: Optional[int],
        custom_length_penalty: Optional[float],
        target_word_count: Optional[int],
        do_sample: bool,
    ):
        def progress_cb(pct: int, msg: str):
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "processing"
                self._jobs[job_id]["progress"] = pct
                self._jobs[job_id]["message"] = msg

        try:
            progress_cb(10, f"Extracting text from {filename} with PyMuPDF...")
            pdf_res = self.pdf_service.extract_text_from_bytes(file_bytes, filename=filename)
            if not pdf_res.get("success", False):
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["error"] = pdf_res.get("error", "PDF extraction failed")
                return

            extracted_text = pdf_res["text"]
            progress_cb(20, f"Extracted {pdf_res.get('char_count', 0)} characters across {pdf_res.get('total_pages', 1)} pages.")

            result = self.summarizer.generate_summary(
                text=extracted_text,
                model_key=model_key,
                length_mode=length_mode,
                custom_min_tokens=custom_min_tokens,
                custom_max_tokens=custom_max_tokens,
                custom_num_beams=custom_num_beams,
                custom_length_penalty=custom_length_penalty,
                target_word_count=target_word_count,
                do_sample=do_sample,
                progress_callback=progress_cb,
            )

            if result.get("success", False):
                result["pdf_metadata"] = {
                    "filename": filename,
                    "file_size_mb": pdf_res.get("file_size_mb"),
                    "total_pages": pdf_res.get("total_pages"),
                    "pages_with_text": pdf_res.get("pages_with_text"),
                    "extracted_char_count": pdf_res.get("char_count"),
                }
                self.history_service.create_record(
                    summary_result=result,
                    source_type="PDF Document (Background Job)",
                    filename=filename
                )
                self._jobs[job_id]["status"] = "completed"
                self._jobs[job_id]["progress"] = 100
                self._jobs[job_id]["message"] = "PDF summarization completed."
                self._jobs[job_id]["result"] = result
            else:
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["error"] = result.get("error", "PDF summarization failed")
                self._jobs[job_id]["message"] = "Inference failed."
        except Exception as e:
            logger.error(f"Job {job_id} encountered exception: {e}", exc_info=True)
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["error"] = str(e)
                self._jobs[job_id]["message"] = f"Error: {str(e)}"

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)
