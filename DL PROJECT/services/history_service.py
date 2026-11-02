"""
Session History Service.
Maintains persistent and in-memory session records of all summarization runs.
Calculates aggregate statistics for the project dashboard.
"""
import os
import json
import uuid
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "history.json")

class HistoryService:
    """Manages history records with thread-safe file persistence."""
    _lock = threading.Lock()
    _in_memory_records: List[Dict[str, Any]] = []
    _initialized = False

    @classmethod
    def _init_storage(cls):
        if not cls._initialized:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            if os.path.exists(HISTORY_FILE):
                try:
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        cls._in_memory_records = json.load(f)
                except Exception:
                    cls._in_memory_records = []
            cls._initialized = True

    @classmethod
    def _save_to_disk(cls):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._in_memory_records, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def create_record(
        cls,
        summary_result: Dict[str, Any],
        source_type: str = "Pasted Text",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates and stores a standardized history record."""
        cls._init_storage()
        record_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "id": record_id,
            "timestamp": timestamp,
            "source_type": source_type,
            "filename": filename or "N/A",
            "model_name": summary_result.get("model_name", "BART"),
            "model_key": summary_result.get("model_key", "bart"),
            "length_mode": summary_result.get("length_mode", "medium"),
            "input_word_count": summary_result.get("input_word_count", 0),
            "summary_word_count": summary_result.get("summary_word_count", 0),
            "compression_ratio": summary_result.get("compression_ratio", 0.0),
            "processing_time": summary_result.get("processing_time", 0.0),
            "is_chunked": summary_result.get("is_chunked", False),
            "chunks_count": summary_result.get("chunks_count", 1),
            "summary": summary_result.get("summary", ""),
            "warnings": summary_result.get("warnings", []),
        }

        with cls._lock:
            cls._in_memory_records.insert(0, record)
            cls._save_to_disk()

        return record

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        cls._init_storage()
        with cls._lock:
            return list(cls._in_memory_records)

    @classmethod
    def delete_record(cls, record_id: str) -> bool:
        cls._init_storage()
        with cls._lock:
            initial_len = len(cls._in_memory_records)
            cls._in_memory_records = [r for r in cls._in_memory_records if r.get("id") != record_id]
            if len(cls._in_memory_records) < initial_len:
                cls._save_to_disk()
                return True
        return False

    @classmethod
    def clear_all(cls):
        cls._init_storage()
        with cls._lock:
            cls._in_memory_records = []
            cls._save_to_disk()

    @classmethod
    def compute_aggregate_stats(cls, history_records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Calculates live aggregate statistics from actual recorded runs.
        No fabricated numbers.
        """
        if history_records is None:
            history_records = cls.get_all()

        if not history_records:
            return {
                "total_documents": 0,
                "total_summaries": 0,
                "avg_input_words": 0,
                "avg_output_words": 0,
                "avg_processing_time": 0.0,
                "avg_compression_ratio": 0.0,
            }

        total_runs = len(history_records)
        total_in_words = sum(r.get("input_word_count", 0) for r in history_records)
        total_out_words = sum(r.get("summary_word_count", 0) for r in history_records)
        total_time = sum(r.get("processing_time", 0.0) for r in history_records)
        total_comp = sum(r.get("compression_ratio", 0.0) for r in history_records)

        return {
            "total_documents": total_runs,
            "total_summaries": total_runs,
            "avg_input_words": round(total_in_words / total_runs, 1),
            "avg_output_words": round(total_out_words / total_runs, 1),
            "avg_processing_time": round(total_time / total_runs, 2),
            "avg_compression_ratio": round(total_comp / total_runs, 2),
        }
