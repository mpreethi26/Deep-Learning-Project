import React, { useEffect, useState } from 'react';
import {
  History,
  Trash2,
  Copy,
  Check,
  Download,
  Search,
  FileText,
  Clock,
  Layers,
  Sparkles,
  AlertTriangle
} from 'lucide-react';
import { HistoryItem } from '../types';
import { api } from '../services/api';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<string>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const res = await api.getHistory();
      setHistory(res.records);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteHistoryItem(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Failed to delete item:', err);
    }
  };

  const handleClearAll = async () => {
    if (window.confirm('Are you sure you want to clear all history records?')) {
      try {
        await api.clearHistory();
        setHistory([]);
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDownloadTxt = (item: HistoryItem) => {
    const content = `Abstractive Summary (${item.model_name})\nDate: ${item.timestamp}\nPreset: ${item.length_mode}\nWords: ${item.summary_word_count}\n\n${item.summary}\n`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `summary-${item.id}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      item.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.model_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.source_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPreset = selectedPreset === 'all' || item.length_mode === selectedPreset;
    return matchesSearch && matchesPreset;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <History className="h-6 w-6 text-indigo-600" />
            <span>Summary Run History</span>
          </h1>
          <p className="text-xs text-slate-500">
            Audit trail of all abstractive summarization runs executed in the active session.
          </p>
        </div>

        {history.length > 0 && (
          <button
            onClick={handleClearAll}
            className="px-3.5 py-1.5 rounded-lg border border-rose-200 text-rose-600 hover:bg-rose-50 text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear All History</span>
          </button>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-4 flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="relative w-full sm:w-96">
          <Search className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search summaries, models, sources..."
            className="w-full pl-9 pr-4 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs font-semibold text-slate-500">Preset:</span>
          {['all', 'short', 'medium', 'long', 'detailed'].map((preset) => (
            <button
              key={preset}
              onClick={() => setSelectedPreset(preset)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium capitalize transition ${
                selectedPreset === preset
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* Records List */}
      {filteredHistory.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-slate-200 text-center space-y-3">
          <div className="h-12 w-12 rounded-xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
            <FileText className="h-6 w-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-800">No records found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {searchTerm
              ? 'No history matches your search filter.'
              : 'Execute a text or PDF summarization to record operational runs.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHistory.map((item) => {
            const isExpanded = expandedId === item.id;
            return (
              <div
                key={item.id}
                className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 space-y-3 hover:shadow-card transition"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{item.model_name}</span>
                    <span className="text-slate-300">&bull;</span>
                    <span className="px-2 py-0.5 rounded font-semibold bg-indigo-50 text-indigo-700 capitalize">
                      {item.length_mode}
                    </span>
                    <span className="text-slate-300">&bull;</span>
                    <span className="text-slate-500">{item.source_type}</span>
                  </div>
                  <div className="flex items-center gap-3 text-slate-400 text-[11px]">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {item.timestamp}
                    </span>
                  </div>
                </div>

                {/* Summary Snippet or Full */}
                <div className="text-xs text-slate-700 leading-relaxed bg-slate-50/70 p-3.5 rounded-lg border border-slate-100 whitespace-pre-wrap">
                  {isExpanded ? item.summary : item.summary.slice(0, 240) + (item.summary.length > 240 ? '...' : '')}
                </div>

                {/* Actions & Metrics */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                  <div className="flex items-center gap-3 text-slate-500 text-[11px]">
                    <span>Output: <strong>{item.summary_word_count}</strong> words</span>
                    <span>&bull;</span>
                    <span>Reduction: <strong className="text-emerald-600">{item.compression_ratio}%</strong></span>
                    <span>&bull;</span>
                    <span>Latency: <strong>{item.processing_time}s</strong></span>
                    {item.is_chunked && (
                      <>
                        <span>&bull;</span>
                        <span className="text-amber-600 font-medium">Hierarchical ({item.chunks_count} chunks)</span>
                      </>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {item.summary.length > 240 && (
                      <button
                        onClick={() => setExpandedId(isExpanded ? null : item.id)}
                        className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold"
                      >
                        {isExpanded ? 'Show Less' : 'Expand'}
                      </button>
                    )}
                    <button
                      onClick={() => handleCopy(item.id, item.summary)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
                      title="Copy"
                    >
                      {copiedId === item.id ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                    </button>
                    <button
                      onClick={() => handleDownloadTxt(item)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
                      title="Download TXT"
                    >
                      <Download className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-rose-50 text-slate-400 hover:text-rose-600"
                      title="Delete"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
