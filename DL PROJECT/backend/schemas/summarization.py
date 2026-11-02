from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SummarizeRequest(BaseModel):
    text: str = Field(..., description='Input text to summarize', min_length=5)
    model_key: str = Field('t5_small', description='Key of the model to use (t5_small, distilbart)')
    length_mode: str = Field('medium', description='Length preset: short, medium, long, detailed')
    target_word_count: Optional[int] = Field(None, description='Optional explicit target word count')
    custom_min_tokens: Optional[int] = Field(None, ge=10, le=1000, description='Custom minimum tokens')
    custom_max_tokens: Optional[int] = Field(None, ge=20, le=1500, description='Custom maximum tokens')
    custom_num_beams: Optional[int] = Field(None, ge=1, le=8, description='Beam count for beam search')
    custom_length_penalty: Optional[float] = Field(None, ge=0.5, le=4.0, description='Length penalty')
    do_sample: bool = Field(False, description='Deterministic vs stochastic generation')

class SummarizeResponse(BaseModel):
    success: bool
    summary: str
    model_key: Optional[str] = 't5_small'
    model_name: Optional[str] = 'T5-small (Falconsai/text_summarization)'
    length_mode: Optional[str] = 'medium'
    target_word_range: Optional[str] = None
    processing_time: float = 0.0
    model_load_time: float = 0.0
    inference_time: float = 0.0
    input_word_count: int = 0
    input_char_count: int = 0
    input_token_count: int = 0
    summary_word_count: int = 0
    summary_char_count: int = 0
    compression_ratio: float = 0.0
    is_chunked: bool = False
    chunks_count: int = 1
    device: str = 'CPU'
    warnings: List[str] = []
    error: Optional[str] = None

class JobCreateResponse(BaseModel):
    job_id: str
    status: str = "pending"
    message: str = "Job queued for processing"

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    message: Optional[str] = None
    result: Optional[SummarizeResponse] = None
    error: Optional[str] = None

class CompareRequest(BaseModel):
    text: str = Field(..., description='Input text to compare across models', min_length=10)
    models: List[str] = Field(default=['distilbart', 't5_small'], description='List of model keys to compare')
    length_mode: str = Field('medium', description='Preset length profile')
    reference_summary: Optional[str] = Field(None, description='Optional ground truth reference summary')

class CompareResponse(BaseModel):
    success: bool
    results: Dict[str, Any] = {}
    error: Optional[str] = None

class EvaluateRequest(BaseModel):
    generated_summary: str = Field(..., description='Generated summary to evaluate', min_length=1)
    reference_summary: str = Field(..., description='Ground truth reference summary', min_length=1)
    original_text: Optional[str] = Field(None, description='Optional source text')
    include_bertscore: bool = Field(False, description='Whether to compute BERTScore')

class EvaluateResponse(BaseModel):
    success: bool
    metrics: Optional[Dict[str, Any]] = None
    bertscore: Optional[Dict[str, Any]] = None
    summary_words: int = 0
    reference_words: int = 0
    original_words: Optional[int] = None
    compression_ratio: Optional[float] = None
    error: Optional[str] = None

class HistoryItem(BaseModel):
    id: str
    timestamp: str
    source_type: str
    filename: str
    model_name: str
    model_key: str
    length_mode: str
    input_word_count: int
    summary_word_count: int
    compression_ratio: float
    processing_time: float
    is_chunked: bool
    chunks_count: int
    summary: str
    warnings: List[str] = []

class StatsResponse(BaseModel):
    total_documents: int
    total_summaries: int
    avg_input_words: float
    avg_output_words: float
    avg_processing_time: float
    avg_compression_ratio: float
