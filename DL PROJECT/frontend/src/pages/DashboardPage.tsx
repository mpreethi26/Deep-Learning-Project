import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  FileText,
  FileUp,
  BarChart2,
  Clock,
  Zap,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Layers,
  Copy,
  Check
} from 'lucide-react';
import { StatsResponse, HistoryItem, ModelInfo } from '../types';
import { api } from '../services/api';

interface DashboardPageProps {
  onNavigate: (page: string) => void;
  models: ModelInfo[];
  device: string;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigate,
  models,
  device
}) => {
  const [stats, setStats] = useState<StatsResponse>({
    total_documents: 0,
    total_summaries: 0,
    avg_input_words: 0,
    avg_output_words: 0,
    avg_processing_time: 0,
    avg_compression_ratio: 0,
  });
  const [recentHistory, setRecentHistory] = useState<HistoryItem[]>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const statsRes = await api.getStats();
      setStats(statsRes);
      const histRes = await api.getHistory();
      setRecentHistory(histRes.records.slice(0, 4));
    } catch (err) {
      console.error('Error loading dashboard stats:', err);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-8 sm:p-10 shadow-premium border border-slate-800">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-semibold tracking-wide">
            <Sparkles className="h-3.5 w-3.5 text-indigo-300" />
            <span>AI-Powered Abstractive NLP Workspace</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            High-Fidelity Abstractive Text Summarization
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Harness pretrained sequence-to-sequence Transformer architectures (<span className="text-indigo-300 font-semibold">DistilBART</span> and <span className="text-indigo-300 font-semibold">T5-small Fine-Tuned</span>) with length-aware token budgeting, hierarchical document chunking, and verified ROUGE evaluation.
          </p>

          <div className="pt-2 flex flex-wrap gap-4">
            <button
              onClick={() => onNavigate('summarize-text')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-all shadow-lg shadow-indigo-600/30 hover:-translate-y-0.5"
            >
              <FileText className="h-4 w-4" />
              <span>New Text Summary</span>
              <ArrowRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => onNavigate('summarize-pdf')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold border border-slate-700 transition-all hover:-translate-y-0.5"
            >
              <FileUp className="h-4 w-4" />
              <span>Upload PDF Document</span>
            </button>
          </div>
        </div>

        {/* Ambient background blur */}
        <div className="absolute right-0 top-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Live Session Statistics */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <BarChart2 className="h-5 w-5 text-indigo-600" />
            <span>Active Session Telemetry</span>
          </h2>
          <span className="text-xs text-slate-500 font-medium">
            Calculated live from real user operations
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-subtle hover:shadow-card transition-shadow">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Documents</p>
            <p className="mt-2 text-2xl font-extrabold text-slate-900">{stats.total_documents}</p>
            <p className="text-[11px] text-slate-400 mt-1">Processed in session</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-subtle hover:shadow-card transition-shadow">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Summaries</p>
            <p className="mt-2 text-2xl font-extrabold text-indigo-600">{stats.total_summaries}</p>
            <p className="text-[11px] text-slate-400 mt-1">Generated</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-subtle hover:shadow-card transition-shadow">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Input</p>
            <p className="mt-2 text-2xl font-extrabold text-slate-900">
              {stats.avg_input_words > 0 ? `${stats.avg_input_words}w` : '0w'}
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Mean source length</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-subtle hover:shadow-card transition-shadow">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Output</p>
            <p className="mt-2 text-2xl font-extrabold text-slate-900">
              {stats.avg_output_words > 0 ? `${stats.avg_output_words}w` : '0w'}
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Mean summary length</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-subtle hover:shadow-card transition-shadow">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Compression</p>
            <p className="mt-2 text-2xl font-extrabold text-emerald-600">
              {stats.avg_compression_ratio > 0 ? `${stats.avg_compression_ratio}%` : '0%'}
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Volume reduction</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-subtle hover:shadow-card transition-shadow">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Latency</p>
            <p className="mt-2 text-2xl font-extrabold text-indigo-600">
              {stats.avg_processing_time > 0 ? `${stats.avg_processing_time}s` : '0s'}
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Inference turnaround</p>
          </div>
        </div>
      </div>

      {/* Model Architecture & Features Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model Card: DistilBART */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">DistilBART CNN 12-6</h3>
                <p className="text-xs text-slate-500 font-mono">sshleifer/distilbart-cnn-12-6</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-indigo-100 text-indigo-700">
              Primary Model
            </span>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Distilled 12-encoder 6-decoder BART checkpoint initialized from bart-large-cnn. Preserves 95%+ of full BART performance with over 2x CPU inference speed and half the memory footprint.
          </p>

          <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-400 block text-[11px]">Architecture</span>
              <span className="font-semibold text-slate-800">Distilled Seq2Seq</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[11px]">Context Window</span>
              <span className="font-semibold text-slate-800">1024 Tokens</span>
            </div>
          </div>
        </div>

        {/* Model Card: T5-small */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center">
                <Cpu className="h-5 w-5 text-violet-600" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">T5-small Fine-Tuned</h3>
                <p className="text-xs text-slate-500 font-mono">Falconsai/text_summarization</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700">
              Comparative
            </span>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Specialized 60M parameter T5 model specifically fine-tuned for high-speed text summarization. Generates crisp, focused summaries with minimal latency on commodity CPU hardware.
          </p>

          <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-400 block text-[11px]">Architecture</span>
              <span className="font-semibold text-slate-800">Fine-Tuned T5 (60M)</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[11px]">Context Window</span>
              <span className="font-semibold text-slate-800">512 Tokens</span>
            </div>
          </div>
        </div>

        {/* System & Pipeline Highlights */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-subtle space-y-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center">
              <Layers className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Length &amp; Pipeline Engine</h3>
              <p className="text-xs text-slate-500">Fixed Length Calibration</p>
            </div>
          </div>

          <ul className="text-xs text-slate-600 space-y-2">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />
              <span><strong>4 Length Presets:</strong> Short (80-120w), Medium (150-250w), Long (300-500w), Detailed (500-800w).</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />
              <span><strong>Hierarchical Chunking:</strong> Seamless summarization of lengthy manuscripts and multi-page PDFs.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />
              <span><strong>Hardware:</strong> {device}</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Recent Summaries Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Clock className="h-5 w-5 text-indigo-600" />
            <span>Recent Summaries</span>
          </h2>
          {recentHistory.length > 0 && (
            <button
              onClick={() => onNavigate('history')}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
            >
              <span>View All History</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          )}
        </div>

        {recentHistory.length === 0 ? (
          <div className="bg-white rounded-xl p-8 border border-slate-200 text-center space-y-3">
            <div className="h-12 w-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
              <FileText className="h-6 w-6" />
            </div>
            <h4 className="text-sm font-bold text-slate-800">No summaries generated yet</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Ready to summarize? Paste an article or upload a PDF to see your generated abstractive summaries and analytics.
            </p>
            <button
              onClick={() => onNavigate('summarize-text')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-xs"
            >
              <span>Create First Summary</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentHistory.map((item) => (
              <div
                key={item.id}
                className="bg-white p-5 rounded-xl border border-slate-200 shadow-subtle hover:shadow-card transition-shadow space-y-3"
              >
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded font-semibold bg-slate-100 text-slate-700 capitalize">
                      {item.length_mode}
                    </span>
                    <span className="text-slate-400">|</span>
                    <span className="text-slate-600 font-medium">{item.model_name.split(' ')[0]}</span>
                  </div>
                  <span className="text-slate-400 text-[11px]">{item.timestamp}</span>
                </div>

                <p className="text-xs text-slate-700 line-clamp-3 leading-relaxed">
                  {item.summary}
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px]">
                  <div className="flex items-center gap-3 text-slate-500">
                    <span>{item.summary_word_count} words</span>
                    <span>&bull;</span>
                    <span className="text-emerald-600 font-medium">{item.compression_ratio}% reduction</span>
                    <span>&bull;</span>
                    <span>{item.processing_time}s</span>
                  </div>
                  <button
                    onClick={() => handleCopy(item.id, item.summary)}
                    className="p-1 text-slate-400 hover:text-slate-700"
                    title="Copy Summary"
                  >
                    {copiedId === item.id ? (
                      <Check className="h-3.5 w-3.5 text-emerald-600" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
