import React, { useState, useRef } from 'react';
import {
  FileUp,
  FileText,
  Sparkles,
  RotateCcw,
  Copy,
  Check,
  Download,
  AlertCircle,
  CheckCircle2,
  Layers,
  FileCheck
} from 'lucide-react';
import { SummarizeResponse } from '../types';
import { api } from '../services/api';

export const SummarizePdfPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [selectedModel, setSelectedModel] = useState('t5_small');
  const [selectedLength, setSelectedLength] = useState<'short' | 'medium' | 'long' | 'detailed'>('medium');
  const [isLoading, setIsLoading] = useState(false);
  const [jobProgress, setJobProgress] = useState<number>(0);
  const [jobMessage, setJobMessage] = useState<string>('');
  const [result, setResult] = useState<SummarizeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.toLowerCase().endsWith('.pdf')) {
        setErrorMessage('Please select a valid PDF file.');
        return;
      }
      setFile(selected);
      setErrorMessage(null);
      setResult(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (!dropped.name.toLowerCase().endsWith('.pdf')) {
        setErrorMessage('Please drop a valid PDF file.');
        return;
      }
      setFile(dropped);
      setErrorMessage(null);
      setResult(null);
    }
  };

  const handleSummarize = async () => {
    if (!file) {
      setErrorMessage('Please upload a PDF file first.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setJobProgress(5);
    setJobMessage('Uploading and queuing PDF for processing...');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_key', selectedModel);
    formData.append('length_mode', selectedLength);

    try {
      const job = await api.createSummarizePdfJob(formData);
      const res = await api.pollJobUntilComplete(job.job_id, (status) => {
        setJobProgress(status.progress);
        if (status.message) setJobMessage(status.message);
      });
      setResult(res);
    } catch (err: any) {
      console.error('PDF summarization error:', err);
      const detail = err.response?.data?.detail || err.message || 'Failed to summarize PDF.';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result?.summary) return;
    navigator.clipboard.writeText(result.summary);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    if (!result?.summary) return;
    const blob = new Blob([result.summary], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${file?.name.replace('.pdf', '') || 'pdf'}-summary.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const presets = [
    { id: 'short', name: 'Short', range: '80–120 words' },
    { id: 'medium', name: 'Medium', range: '150–250 words' },
    { id: 'long', name: 'Long', range: '300–500 words' },
    { id: 'detailed', name: 'Detailed', range: '500–800 words' },
  ] as const;

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          PDF Document Summarization
        </h1>
        <p className="text-xs text-slate-500">
          Upload multi-page research manuscripts or corporate PDFs for automated PyMuPDF extraction and hierarchical abstractive synthesis.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Upload & Controls */}
        <div className="space-y-4">
          {/* Dropzone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
              file
                ? 'border-indigo-400 bg-indigo-50/40'
                : 'border-slate-300 hover:border-indigo-500 hover:bg-slate-50/60 bg-white'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf"
              className="hidden"
            />
            <div className="h-12 w-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mx-auto mb-3">
              {file ? <FileCheck className="h-6 w-6" /> : <FileUp className="h-6 w-6" />}
            </div>
            {file ? (
              <div className="space-y-1">
                <p className="text-sm font-bold text-slate-900">{file.name}</p>
                <p className="text-xs text-slate-500">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB &bull; Ready to extract
                </p>
                <span className="inline-block mt-2 text-xs font-semibold text-indigo-600 hover:underline">
                  Click to choose different file
                </span>
              </div>
            ) : (
              <div className="space-y-1">
                <p className="text-sm font-bold text-slate-800">
                  Drag and drop your PDF here, or <span className="text-indigo-600">browse</span>
                </p>
                <p className="text-xs text-slate-400">
                  Supports up to 25 MB documents &bull; Selectable text required
                </p>
              </div>
            )}
          </div>

          {/* Model & Length Controls */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Transformer Model
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedModel('distilbart')}
                  className={`p-3 rounded-xl border text-left transition ${
                    selectedModel === 'distilbart'
                      ? 'border-indigo-600 bg-indigo-50/60 ring-2 ring-indigo-500/20'
                      : 'border-slate-200 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">DistilBART</span>
                    {selectedModel === 'distilbart' && <CheckCircle2 className="h-4 w-4 text-indigo-600" />}
                  </div>
                  <div className="text-[10px] font-mono text-indigo-600 font-semibold mt-0.5">
                    sshleifer/distilbart-cnn-12-6
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">Recommended for dense PDF documents</p>
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedModel('t5_small')}
                  className={`p-3 rounded-xl border text-left transition ${
                    selectedModel === 't5_small'
                      ? 'border-indigo-600 bg-indigo-50/60 ring-2 ring-indigo-500/20'
                      : 'border-slate-200 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">T5-small Fine-Tuned</span>
                    {selectedModel === 't5_small' && <CheckCircle2 className="h-4 w-4 text-indigo-600" />}
                  </div>
                  <div className="text-[10px] font-mono text-indigo-600 font-semibold mt-0.5">
                    Falconsai/text_summarization
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">Fast 60M fine-tuned Seq2Seq model</p>
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Summary Preset
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {presets.map((preset) => (
                  <button
                    key={preset.id}
                    type="button"
                    onClick={() => setSelectedLength(preset.id)}
                    className={`p-2.5 rounded-xl border text-left transition ${
                      selectedLength === preset.id
                        ? 'border-indigo-600 bg-indigo-600 text-white'
                        : 'border-slate-200 bg-white text-slate-700'
                    }`}
                  >
                    <div className="text-xs font-bold">{preset.name}</div>
                    <div className={`text-[10px] ${selectedLength === preset.id ? 'text-indigo-200' : 'text-slate-400'}`}>
                      {preset.range}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {errorMessage && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <button
              onClick={handleSummarize}
              disabled={isLoading || !file}
              className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-sm transition shadow-md shadow-indigo-600/20 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <RotateCcw className="h-4 w-4 animate-spin" />
                  <span>Extracting &amp; Summarizing PDF...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Summarize PDF Document</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 min-h-[520px] flex flex-col justify-between">
          {!result && !isLoading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 space-y-3 my-auto">
              <div className="h-14 w-14 rounded-2xl bg-indigo-50 text-indigo-500 flex items-center justify-center">
                <FileUp className="h-7 w-7" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">No PDF Summarized Yet</h3>
              <p className="text-xs text-slate-500 max-w-sm">
                Upload a PDF on the left and select your length preset to run PyMuPDF extraction and hierarchical Transformer inference.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 space-y-4 my-auto">
              <div className="h-14 w-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center animate-pulse">
                <RotateCcw className="h-7 w-7 animate-spin" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">
                {jobMessage || 'Processing Multi-Page Document...'}
              </h3>
              <p className="text-xs text-slate-500 max-w-xs">
                Extracting textual streams, chunking long sections, and synthesizing abstractive insights.
              </p>
              <div className="w-64 space-y-1.5">
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(5, Math.min(100, jobProgress))}%` }}
                  />
                </div>
                <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                  <span>Progress</span>
                  <span className="font-semibold text-indigo-600">{jobProgress}%</span>
                </div>
              </div>
            </div>
          )}

          {result && !isLoading && (
            <div className="flex-1 flex flex-col space-y-4">
              {/* Telemetry Pills */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700">
                    {result.summary_word_count} words
                  </span>
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700">
                    {result.compression_ratio}% reduction
                  </span>
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                    Total: {result.processing_time}s
                  </span>
                  {result.model_load_time !== undefined && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700" title="Model Load & Tokenizer Initialization Time">
                      Load: {result.model_load_time}s
                    </span>
                  )}
                  {result.inference_time !== undefined && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-violet-50 text-violet-700" title="Pure Neural Inference Time">
                      Infer: {result.inference_time}s
                    </span>
                  )}
                  {result.pdf_metadata && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-600">
                      {result.pdf_metadata.total_pages} Pages ({result.pdf_metadata.pages_with_text} with text)
                    </span>
                  )}
                  {result.is_chunked && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700">
                      Hierarchical ({result.chunks_count} chunks)
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={handleCopy}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium flex items-center gap-1"
                  >
                    {isCopied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{isCopied ? 'Copied' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={handleDownloadTxt}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium flex items-center gap-1"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>TXT</span>
                  </button>
                </div>
              </div>

              {/* Summary Text Box */}
              <div className="prose prose-slate max-w-none text-slate-800 text-sm leading-relaxed p-4 bg-slate-50/70 rounded-xl border border-slate-100 min-h-[380px] whitespace-pre-wrap">
                {result.summary}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Source: <strong>{result.pdf_metadata?.filename || file?.name}</strong></span>
                <span>Preset: <strong>{result.length_mode}</strong></span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
