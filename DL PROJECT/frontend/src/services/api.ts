import axios from 'axios';
import {
  HealthResponse,
  ModelInfo,
  LengthProfile,
  SummarizeRequest,
  SummarizeResponse,
  JobStatusResponse,
  EvaluateResponse,
  HistoryItem,
  StatsResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 minutes timeout with background safety bounds
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  checkHealth: async (): Promise<HealthResponse> => {
    const res = await client.get<HealthResponse>('/api/health');
    return res.data;
  },

  getModels: async (): Promise<{ models: ModelInfo[]; default_model: string; length_profiles: Record<string, LengthProfile> }> => {
    const res = await client.get('/api/models');
    return res.data;
  },

  summarizeText: async (req: SummarizeRequest): Promise<SummarizeResponse> => {
    const res = await client.post<SummarizeResponse>('/api/summarize', req);
    return res.data;
  },

  createSummarizeJob: async (req: SummarizeRequest): Promise<{ job_id: string }> => {
    const res = await client.post<{ job_id: string }>('/api/jobs/summarize', req);
    return res.data;
  },

  summarizePdf: async (formData: FormData): Promise<SummarizeResponse> => {
    const res = await client.post<SummarizeResponse>('/api/summarize/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  createSummarizePdfJob: async (formData: FormData): Promise<{ job_id: string }> => {
    const res = await client.post<{ job_id: string }>('/api/jobs/summarize/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  getJobStatus: async (jobId: string): Promise<JobStatusResponse> => {
    const res = await client.get<JobStatusResponse>(`/api/jobs/${jobId}`);
    return res.data;
  },

  pollJobUntilComplete: async (
    jobId: string,
    onProgress?: (status: JobStatusResponse) => void
  ): Promise<SummarizeResponse> => {
    const maxPollTimeMs = 180000;
    const intervalMs = 1000;
    const startTime = Date.now();

    while (Date.now() - startTime < maxPollTimeMs) {
      const statusRes = await api.getJobStatus(jobId);
      if (onProgress) {
        onProgress(statusRes);
      }

      if (statusRes.status === 'completed' && statusRes.result) {
        return statusRes.result;
      }

      if (statusRes.status === 'failed') {
        throw new Error(statusRes.error || 'Summarization job failed.');
      }

      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }

    throw new Error('Summarization job timed out while polling.');
  },

  compareModels: async (data: {
    text: string;
    models: string[];
    length_mode: string;
    reference_summary?: string;
  }): Promise<{ success: boolean; results: Record<string, any> }> => {
    const res = await client.post('/api/compare', data);
    return res.data;
  },

  evaluateSummary: async (data: {
    generated_summary: string;
    reference_summary: string;
    original_text?: string;
    include_bertscore?: boolean;
  }): Promise<EvaluateResponse> => {
    const res = await client.post<EvaluateResponse>('/api/evaluate', data);
    return res.data;
  },

  getHistory: async (): Promise<{ records: HistoryItem[]; total: number }> => {
    const res = await client.get('/api/history');
    return res.data;
  },

  deleteHistoryItem: async (id: string): Promise<{ success: boolean; id: string }> => {
    const res = await client.delete(`/api/history/${id}`);
    return res.data;
  },

  clearHistory: async (): Promise<{ success: boolean; message: string }> => {
    const res = await client.delete('/api/history');
    return res.data;
  },

  getStats: async (): Promise<StatsResponse> => {
    const res = await client.get<StatsResponse>('/api/stats');
    return res.data;
  },
};
