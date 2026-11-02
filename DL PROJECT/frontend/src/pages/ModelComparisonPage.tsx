import React, { useState } from 'react';
import { Columns, Sparkles, RotateCcw, AlertCircle, Copy, Check, Table } from 'lucide-react';
import { api } from '../services/api';

export const ModelComparisonPage: React.FC = () => {
  const [inputText, setInputText] = useState(
    'Artificial intelligence and transformer architectures have revolutionized computational linguistics. ' +
    'The DistilBART model by sshleifer uses a distilled 12-encoder 6-decoder architecture pretrained as a ' +
    'denoising autoencoder for high-coherence abstractive summarization. In contrast, T5-small fine-tuned by ' +
    'Falconsai frames summarization into a lightweight, highly efficient Seq2Seq format with 60M parameters. ' +
    'When evaluating both models on identical source documents, comparing output compression, latency, and ROUGE ' +
    'overlap highlights the architectural trade-offs between distilled BART and specialized T5.'
  );
  const [referenceSummary, setReferenceSummary] = useState(
    'DistilBART and T5-small represent prominent transformer Seq2Seq architectures for abstractive summarization. ' +
    'DistilBART offers rich news-style coherence, while T5-small provides ultra-fast lightweight generation.'
  );
  const [selectedLength, setSelectedLength] = useState('medium');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<Record<string, any> | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [copiedModel, setCopiedModel] = useState<string | null>(null);

  const handleCompare = async () => {
    if (inputText.trim().split(/\s+/).length < 10) {
      setErrorMessage('Input text must have at least 10 words for comparative evaluation.');
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await api.compareModels({
        text: inputText,
        models: ['distilbart', 't5_small'],
        length_mode: selectedLength,
        reference_summary: referenceSummary.trim() || undefined
      });
      setResults(res.results);
    } catch (err: any) {
      console.error('Comparison failed:', err);
      setErrorMessage(err.response?.data?.detail || err.message || 'Model comparison failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedModel(key);
    setTimeout(() => setCopiedModel(null), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
          <Columns className="h-6 w-6 text-indigo-600" />
          <span>Model Architecture Comparison</span>
        </h1>
        <p className="text-xs text-slate-500">
          Run comparative inference on the same source text using <span className="font-semibold text-slate-700">DistilBART</span> (<code>sshleifer/distilbart-cnn-12-6</code>) and <span className="font-semibold text-slate-700">T5-small Fine-Tuned</span> (<code>Falconsai/text_summarization</code>) to observe synthesis styles, length control, and ROUGE scores.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 space-y-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
            Source Text
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="w-full h-36 p-3 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
            placeholder="Enter text to compare models across..."
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
            Reference Ground Truth Summary (Optional &bull; Enables ROUGE Calculation)
          </label>
          <textarea
            value={referenceSummary}
            onChange={(e) => setReferenceSummary(e.target.value)}
            className="w-full h-20 p-3 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50/50"
            placeholder="Optional reference summary to calculate precision, recall, and F1..."
          />
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-600">Preset:</span>
            {(['short', 'medium', 'long'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setSelectedLength(mode)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                  selectedLength === mode
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>

          <button
            onClick={handleCompare}
            disabled={isLoading}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-xs transition shadow-md shadow-indigo-600/20 flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <RotateCcw className="h-4 w-4 animate-spin" />
                <span>Running Comparative Inference...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Run Model Comparison</span>
              </>
            )}
          </button>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {results && (() => {
        const bartRes = results.distilbart || results.bart;
        const t5Res = results.t5_small || results.t5;
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
            {/* DistilBART Card */}
            <div className="bg-white rounded-xl border border-indigo-200 shadow-card p-5 flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div>
                    <h3 className="font-extrabold text-sm text-slate-900">DistilBART</h3>
                    <p className="text-[11px] text-indigo-600 font-medium">sshleifer/distilbart-cnn-12-6</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold text-xs">
                      {bartRes?.summary_word_count || 0} words
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold text-xs">
                      {bartRes?.processing_time || 0}s
                    </span>
                  </div>
                </div>

                <div className="mt-4 p-4 rounded-xl bg-slate-50/70 text-slate-800 text-xs leading-relaxed min-h-[160px] whitespace-pre-wrap">
                  {bartRes?.summary || (bartRes?.error ? `Error: ${bartRes.error}` : 'No output generated')}
                </div>

                {/* ROUGE Table if reference supplied */}
                {bartRes?.evaluation && (
                  <div className="mt-4 p-3 bg-indigo-50/40 rounded-xl border border-indigo-100">
                    <h4 className="text-[11px] font-bold text-indigo-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Table className="h-3.5 w-3.5" />
                      <span>DistilBART ROUGE Scores vs Reference</span>
                    </h4>
                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                      <div className="p-2 bg-white rounded border border-indigo-100">
                        <span className="block text-[10px] text-slate-400 font-medium">ROUGE-1 F1</span>
                        <span className="font-extrabold text-indigo-700">
                          {bartRes.evaluation.rouge1?.fmeasure || '0.00'}
                        </span>
                      </div>
                      <div className="p-2 bg-white rounded border border-indigo-100">
                        <span className="block text-[10px] text-slate-400 font-medium">ROUGE-2 F1</span>
                        <span className="font-extrabold text-indigo-700">
                          {bartRes.evaluation.rouge2?.fmeasure || '0.00'}
                        </span>
                      </div>
                      <div className="p-2 bg-white rounded border border-indigo-100">
                        <span className="block text-[10px] text-slate-400 font-medium">ROUGE-L F1</span>
                        <span className="font-extrabold text-indigo-700">
                          {bartRes.evaluation.rougeL?.fmeasure || '0.00'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400">Compression: {bartRes?.compression_ratio || 0}%</span>
                <button
                  onClick={() => handleCopy('distilbart', bartRes?.summary || '')}
                  className="px-3 py-1 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-semibold flex items-center gap-1"
                >
                  {copiedModel === 'distilbart' ? <Check className="h-3 w-3 text-emerald-600" /> : <Copy className="h-3 w-3" />}
                  <span>{copiedModel === 'distilbart' ? 'Copied' : 'Copy DistilBART'}</span>
                </button>
              </div>
            </div>

            {/* T5-small Fine-Tuned Card */}
            <div className="bg-white rounded-xl border border-violet-200 shadow-card p-5 flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div>
                    <h3 className="font-extrabold text-sm text-slate-900">T5-small Fine-Tuned</h3>
                    <p className="text-[11px] text-violet-600 font-medium">Falconsai/text_summarization</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-violet-50 text-violet-700 font-bold text-xs">
                      {t5Res?.summary_word_count || 0} words
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold text-xs">
                      {t5Res?.processing_time || 0}s
                    </span>
                  </div>
                </div>

                <div className="mt-4 p-4 rounded-xl bg-slate-50/70 text-slate-800 text-xs leading-relaxed min-h-[160px] whitespace-pre-wrap">
                  {t5Res?.summary || (t5Res?.error ? `Error: ${t5Res.error}` : 'No output generated')}
                </div>

                {/* ROUGE Table if reference supplied */}
                {t5Res?.evaluation && (
                  <div className="mt-4 p-3 bg-violet-50/40 rounded-xl border border-violet-100">
                    <h4 className="text-[11px] font-bold text-violet-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Table className="h-3.5 w-3.5" />
                      <span>T5-small ROUGE Scores vs Reference</span>
                    </h4>
                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                      <div className="p-2 bg-white rounded border border-violet-100">
                        <span className="block text-[10px] text-slate-400 font-medium">ROUGE-1 F1</span>
                        <span className="font-extrabold text-violet-700">
                          {t5Res.evaluation.rouge1?.fmeasure || '0.00'}
                        </span>
                      </div>
                      <div className="p-2 bg-white rounded border border-violet-100">
                        <span className="block text-[10px] text-slate-400 font-medium">ROUGE-2 F1</span>
                        <span className="font-extrabold text-violet-700">
                          {t5Res.evaluation.rouge2?.fmeasure || '0.00'}
                        </span>
                      </div>
                      <div className="p-2 bg-white rounded border border-violet-100">
                        <span className="block text-[10px] text-slate-400 font-medium">ROUGE-L F1</span>
                        <span className="font-extrabold text-violet-700">
                          {t5Res.evaluation.rougeL?.fmeasure || '0.00'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400">Compression: {t5Res?.compression_ratio || 0}%</span>
                <button
                  onClick={() => handleCopy('t5_small', t5Res?.summary || '')}
                  className="px-3 py-1 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-semibold flex items-center gap-1"
                >
                  {copiedModel === 't5_small' ? <Check className="h-3 w-3 text-emerald-600" /> : <Copy className="h-3 w-3" />}
                  <span>{copiedModel === 't5_small' ? 'Copied' : 'Copy T5-small'}</span>
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};
