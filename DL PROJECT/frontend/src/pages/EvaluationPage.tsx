import React, { useState } from 'react';
import { BarChart3, RotateCcw, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { EvaluateResponse } from '../types';
import { api } from '../services/api';

export const EvaluationPage: React.FC = () => {
  const [generatedSummary, setGeneratedSummary] = useState(
    'BART is a sequence-to-sequence model designed for generative language tasks. ' +
    'Pretrained with diverse noise transformations, BART excels at abstractive text summarization ' +
    'when fine-tuned on CNN/DailyMail benchmarks.'
  );
  const [referenceSummary, setReferenceSummary] = useState(
    'BART is an encoder-decoder sequence-to-sequence neural network model for text generation and summarization. ' +
    'It corrupts source sequences with denoising objectives and achieves state-of-the-art results on CNN/DailyMail.'
  );
  const [originalText, setOriginalText] = useState('');
  const [includeBertScore, setIncludeBertScore] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<EvaluateResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleEvaluate = async () => {
    if (!generatedSummary.trim()) {
      setErrorMessage('Please provide a generated summary to evaluate.');
      return;
    }
    if (!referenceSummary.trim()) {
      setErrorMessage('A ground-truth reference summary is strictly required to compute reference-based NLP metrics.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await api.evaluateSummary({
        generated_summary: generatedSummary,
        reference_summary: referenceSummary,
        original_text: originalText.trim() || undefined,
        include_bertscore: includeBertScore
      });
      setResult(res);
    } catch (err: any) {
      console.error('Evaluation failed:', err);
      setErrorMessage(err.response?.data?.detail || err.message || 'Evaluation computation failed.');
    } finally {
      setIsLoading(false);
    }
  };

  // Prepare chart data from ROUGE metrics
  const chartData = result?.metrics ? [
    {
      metric: 'ROUGE-1 (Unigram)',
      Precision: Number((result.metrics.rouge1.precision * 100).toFixed(1)),
      Recall: Number((result.metrics.rouge1.recall * 100).toFixed(1)),
      F1: Number((result.metrics.rouge1.fmeasure * 100).toFixed(1)),
    },
    {
      metric: 'ROUGE-2 (Bigram)',
      Precision: Number((result.metrics.rouge2.precision * 100).toFixed(1)),
      Recall: Number((result.metrics.rouge2.recall * 100).toFixed(1)),
      F1: Number((result.metrics.rouge2.fmeasure * 100).toFixed(1)),
    },
    {
      metric: 'ROUGE-L (Longest Subseq)',
      Precision: Number((result.metrics.rougeL.precision * 100).toFixed(1)),
      Recall: Number((result.metrics.rougeL.recall * 100).toFixed(1)),
      F1: Number((result.metrics.rougeL.fmeasure * 100).toFixed(1)),
    },
  ] : [];

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-indigo-600" />
          <span>NLP Summary Evaluation Dashboard</span>
        </h1>
        <p className="text-xs text-slate-500">
          Compute genuine academic evaluation metrics (ROUGE-1, ROUGE-2, ROUGE-L) against verified reference ground truths.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Input Panel */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Candidate (Generated) Summary
            </label>
            <textarea
              value={generatedSummary}
              onChange={(e) => setGeneratedSummary(e.target.value)}
              className="w-full h-32 p-3 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
              placeholder="Paste generated model output..."
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Reference (Ground-Truth) Summary
            </label>
            <textarea
              value={referenceSummary}
              onChange={(e) => setReferenceSummary(e.target.value)}
              className="w-full h-32 p-3 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
              placeholder="Paste human expert reference summary..."
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Original Source Text (Optional &bull; For Compression Ratio)
            </label>
            <textarea
              value={originalText}
              onChange={(e) => setOriginalText(e.target.value)}
              className="w-full h-20 p-3 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
              placeholder="Optional source document..."
            />
          </div>

          {errorMessage && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <button
            onClick={handleEvaluate}
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-200 text-white font-semibold text-xs transition shadow-md shadow-indigo-600/20 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <RotateCcw className="h-4 w-4 animate-spin" />
                <span>Computing ROUGE Metrics...</span>
              </>
            ) : (
              <>
                <BarChart3 className="h-4 w-4" />
                <span>Calculate ROUGE Evaluation</span>
              </>
            )}
          </button>
        </div>

        {/* Evaluation Visualizations */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 space-y-5 min-h-[460px]">
          {!result && !isLoading && (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-3">
              <div className="h-12 w-12 rounded-xl bg-indigo-50 text-indigo-500 flex items-center justify-center">
                <BarChart3 className="h-6 w-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">No Evaluation Computed Yet</h3>
              <p className="text-xs text-slate-500 max-w-xs">
                Provide both the generated candidate summary and reference ground truth to calculate genuine ROUGE overlap.
              </p>
            </div>
          )}

          {result && !isLoading && (
            <div className="space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="text-sm font-bold text-slate-900">ROUGE Benchmark Metrics (%)</h3>
                <div className="text-xs text-slate-500">
                  Candidate: <strong>{result.summary_words}w</strong> &bull; Ref: <strong>{result.reference_words}w</strong>
                </div>
              </div>

              {/* Recharts Bar Chart */}
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                    <XAxis dataKey="metric" tick={{ fontSize: 11 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
                    <Tooltip formatter={(value: any) => [`${value}%`]} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    <Bar dataKey="Precision" fill="#6366F1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Recall" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="F1" fill="#10B981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Metric Breakdown Cards */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <span className="block text-[11px] font-semibold text-slate-500">ROUGE-1 F1</span>
                  <span className="text-xl font-black text-slate-900">
                    {result.metrics?.rouge1.fmeasure ? (result.metrics.rouge1.fmeasure * 100).toFixed(1) : 0}%
                  </span>
                  <span className="block text-[10px] text-slate-400 mt-0.5">Unigram Co-occurrence</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <span className="block text-[11px] font-semibold text-slate-500">ROUGE-2 F1</span>
                  <span className="text-xl font-black text-slate-900">
                    {result.metrics?.rouge2.fmeasure ? (result.metrics.rouge2.fmeasure * 100).toFixed(1) : 0}%
                  </span>
                  <span className="block text-[10px] text-slate-400 mt-0.5">Bigram Overlap</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <span className="block text-[11px] font-semibold text-slate-500">ROUGE-L F1</span>
                  <span className="text-xl font-black text-slate-900">
                    {result.metrics?.rougeL.fmeasure ? (result.metrics.rougeL.fmeasure * 100).toFixed(1) : 0}%
                  </span>
                  <span className="block text-[10px] text-slate-400 mt-0.5">Longest Common Subsequence</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Metric Interpretations Guide */}
      <div className="bg-slate-50 rounded-xl p-6 border border-slate-200 space-y-3">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
          <Info className="h-4 w-4 text-indigo-600" />
          <span>Understanding Academic Summarization Metrics</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-600 leading-relaxed">
          <div>
            <strong className="text-slate-900 block mb-1">ROUGE-1 (Unigrams):</strong>
            Measures the percentage of single words from the human reference present in the generated summary. Reflects informational completeness and vocabulary alignment.
          </div>
          <div>
            <strong className="text-slate-900 block mb-1">ROUGE-2 (Bigrams):</strong>
            Measures consecutive word pair matches. Higher scores indicate superior phrase-level fluency, localized coherence, and syntactic structure preservation.
          </div>
          <div>
            <strong className="text-slate-900 block mb-1">ROUGE-L (LCS):</strong>
            Identifies the longest common subsequence of words without requiring consecutive matches. Captures sentence-level structural and narrative flow.
          </div>
        </div>
      </div>
    </div>
  );
};
