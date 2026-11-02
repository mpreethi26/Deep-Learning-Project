export interface ModelInfo {
  key: string;
  display_name: string;
  model_id: string;
  architecture: string;
  framework: string;
  max_input_tokens: number;
  is_encoder_decoder: boolean;
  notes: string;
  is_loaded?: boolean;
}

export interface LengthProfile {
  label: string;
  description: string;
  target_word_min: number;
  target_word_max: number;
  min_tokens: number;
  max_tokens: number;
  num_beams: number;
  length_penalty: number;
  chunk_intermediate_tokens?: number;
}

export interface SummarizeRequest {
  text: string;
  model_key: string;
  length_mode: 'short' | 'medium' | 'long' | 'detailed';
  target_word_count?: number;
  custom_min_tokens?: number;
  custom_max_tokens?: number;
  custom_num_beams?: number;
  custom_length_penalty?: number;
  do_sample?: boolean;
}

export interface SummarizeResponse {
  success: boolean;
  summary: string;
  model_key: string;
  model_name: string;
  length_mode: string;
  target_word_range?: string;
  processing_time: number;
  model_load_time?: number;
  inference_time?: number;
  input_word_count: number;
  input_char_count: number;
  input_token_count: number;
  summary_word_count: number;
  summary_char_count: number;
  compression_ratio: number;
  is_chunked: boolean;
  chunks_count: number;
  device: string;
  warnings?: string[];
  error?: string;
  pdf_metadata?: {
    filename: string;
    file_size_mb: number;
    total_pages: number;
    pages_with_text: number;
    extracted_char_count: number;
  };
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: SummarizeResponse;
  error?: string;
}

export interface MetricDetail {
  precision: number;
  recall: number;
  fmeasure: number;
}

export interface EvaluateResponse {
  success: boolean;
  metrics?: {
    rouge1: MetricDetail;
    rouge2: MetricDetail;
    rougeL: MetricDetail;
  };
  bertscore?: {
    precision: number;
    recall: number;
    f1: number;
  };
  summary_words: number;
  reference_words: number;
  original_words?: number;
  compression_ratio?: number;
  error?: string;
}

export interface HistoryItem {
  id: string;
  timestamp: string;
  source_type: string;
  filename: string;
  model_name: string;
  model_key: string;
  length_mode: string;
  input_word_count: number;
  summary_word_count: number;
  compression_ratio: number;
  processing_time: number;
  is_chunked: boolean;
  chunks_count: number;
  summary: string;
  warnings?: string[];
}

export interface StatsResponse {
  total_documents: number;
  total_summaries: number;
  avg_input_words: number;
  avg_output_words: number;
  avg_processing_time: number;
  avg_compression_ratio: number;
}

export interface HealthResponse {
  status: string;
  application: string;
  team_lead: string;
  device: string;
  active_model: string;
  active_model_key: string | null;
  supported_models: string[];
}
