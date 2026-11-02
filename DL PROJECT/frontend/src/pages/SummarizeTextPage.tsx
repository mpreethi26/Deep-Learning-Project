import React, { useState } from 'react';
import {
  Sparkles,
  RotateCcw,
  Copy,
  Check,
  Download,
  Sliders,
  AlertCircle,
  FileText,
  FileUp,
  CheckCircle2,
  Clock,
  Layers,
  Edit3
} from 'lucide-react';
import { SummarizeRequest, SummarizeResponse, ModelInfo, LengthProfile } from '../types';
import { api } from '../services/api';

const SAMPLE_TEXTS = {
  ai_research: `Artificial intelligence (AI) has undergone a historic paradigm shift propelled by transformer-based neural network architectures. Originally introduced by Vaswani et al. in 2017 through the landmark work "Attention Is All You Need," transformers eschewed recurrent and convolutional dependencies in favor of multi-head self-attention mechanisms. This architectural breakthrough enabled complete parallelization during training while effectively capturing long-range semantic dependencies across extensive sequences. In modern natural language processing, text summarization stands as one of the most intellectually demanding benchmarks. Summarization tasks are categorized into extractive and abstractive paradigms. Extractive summarization identifies and stitches salient sentences directly from the raw document without grammatical alterations. In contrast, abstractive summarization requires high-level semantic comprehension, lexical rephrasing, and novel sentence synthesis to distill the overarching ideas into concise representations. The BART model, proposed by Lewis et al. in 2019, marries bidirectional encoder representations with autoregressive decoding, making it exceptionally well-suited for abstractive generation. When fine-tuned on news corpora like CNN/DailyMail, BART achieves remarkable ROUGE metrics, though real-world deployments must account for token length limits, inductive brevity biases, and domain adaptation challenges.`,
  finance_report: `Global Technology Solutions Inc. today reported its financial results for the fourth quarter and fiscal year ended December 31, 2025. Total revenue for the fourth quarter reached $4.85 billion, representing an increase of 14% year-over-year compared to $4.25 billion in the prior-year period. Cloud and cognitive intelligence services served as the primary growth catalyst, generating $2.10 billion in quarterly revenue, up 26% year-over-year. Operating income stood at $1.15 billion with an operating margin of 23.7%, compared to 21.2% in the fourth quarter of 2024. Net income for the quarter totaled $890 million, or $1.42 per diluted share, exceeding consensus estimates of $1.34 per share. Free cash flow generation remained robust at $950 million for the quarter, bringing full-year operating cash flow to $3.4 billion. Management attributed the outperformance to strong enterprise adoption of its enterprise AI agents and automated workflow intelligence suite. For the full fiscal year 2026, the company issued positive forward guidance, anticipating revenue between $20.2 billion and $20.8 billion, reflecting continued momentum across enterprise AI transformations and digital cloud migrations.`,
  healthcare_study: `Immunotherapy has transformed the oncology therapeutic paradigm over the past decade, yet clinical responses vary widely across heterogeneous patient cohorts. In this multicenter prospective cohort study, we examined the prognostic significance of tumor-infiltrating lymphocyte (TIL) spatial architectures and genomic tumor mutational burden (TMB) in 640 patients diagnosed with advanced non-small cell lung cancer (NSCLC) receiving programmed death-1 (PD-1) inhibitor monotherapy. Whole-exome sequencing and multiplex immunohistochemistry were performed on baseline pre-treatment biopsy specimens. Patients exhibiting both elevated TMB (>=10 mutations per megabase) and high stromal TIL density demonstrated significantly prolonged progression-free survival (median 14.8 months vs 4.2 months, hazard ratio 0.38, 95% confidence interval 0.28-0.51, p < 0.001) and superior overall survival rates compared to patients lacking both biomarkers. Multivariate Cox regression confirmed that the integrated composite biomarker retained independent prognostic power after adjusting for age, histology, and smoking status. Furthermore, single-cell RNA sequencing revealed an enriched subset of cytotoxic CD8+ T cells expressing tissue-resident memory signatures in exceptional responders. These findings suggest that concurrent evaluation of genomic mutational metrics and spatial immune microenvironment markers provides a superior predictive framework for optimizing immunotherapy candidate selection.`
};

interface SummarizeTextPageProps {
  models: ModelInfo[];
  lengthProfiles: Record<string, LengthProfile>;
  onNavigate: (page: string) => void;
}

export const SummarizeTextPage: React.FC<SummarizeTextPageProps> = ({
  models,
  lengthProfiles,
  onNavigate
}) => {
  const [inputText, setInputText] = useState('');
  const [selectedModel, setSelectedModel] = useState('t5_small');
  const [selectedLength, setSelectedLength] = useState<'short' | 'medium' | 'long' | 'detailed'>('medium');
  const [targetWordCount, setTargetWordCount] = useState<number | undefined>(undefined);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [numBeams, setNumBeams] = useState<number>(2);
  const [lengthPenalty, setLengthPenalty] = useState<number>(1.5);
  const [doSample, setDoSample] = useState<boolean>(false);

  const [isLoading, setIsLoading] = useState(false);
  const [jobProgress, setJobProgress] = useState<number>(0);
  const [jobMessage, setJobMessage] = useState<string>('');
  const [result, setResult] = useState<SummarizeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedSummary, setEditedSummary] = useState('');

  // Source Stats
  const cleanSource = inputText.trim();
  const wordCount = cleanSource ? cleanSource.split(/\s+/).length : 0;
  const charCount = cleanSource.length;
  const estimatedTokens = Math.round(wordCount * 1.35);

  const handleGenerate = async () => {
    if (wordCount < 10) {
      setErrorMessage('Input text is too short. Please provide at least 10 words for abstractive summarization.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setJobProgress(5);
    setJobMessage('Enqueuing summarization job...');

    const req: SummarizeRequest = {
      text: inputText,
      model_key: selectedModel,
      length_mode: selectedLength,
      target_word_count: targetWordCount || undefined,
      custom_num_beams: numBeams,
      custom_length_penalty: lengthPenalty,
      do_sample: doSample,
    };

    try {
      // Background task workflow with job ID and polling
      const job = await api.createSummarizeJob(req);
      const response = await api.pollJobUntilComplete(job.job_id, (status) => {
        setJobProgress(status.progress);
        if (status.message) setJobMessage(status.message);
      });
      setResult(response);
      setEditedSummary(response.summary);
      setIsEditing(false);
    } catch (err: any) {
      console.error('Summarization failed:', err);
      const detail = err.response?.data?.detail || err.message || 'Summarization request failed.';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    const textToCopy = isEditing ? editedSummary : result?.summary || '';
    navigator.clipboard.writeText(textToCopy);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    const text = isEditing ? editedSummary : result?.summary || '';
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `summary-${selectedLength}-${Date.now()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadMd = () => {
    const text = isEditing ? editedSummary : result?.summary || '';
    const content = `# Abstractive Summary\n\n**Model:** ${result?.model_name}\n**Preset:** ${result?.length_mode}\n**Original Words:** ${result?.input_word_count}\n**Summary Words:** ${result?.summary_word_count}\n**Compression Ratio:** ${result?.compression_ratio}%\n\n---\n\n${text}\n`;
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `summary-${selectedLength}-${Date.now()}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const loadSample = (key: keyof typeof SAMPLE_TEXTS) => {
    setInputText(SAMPLE_TEXTS[key]);
    setErrorMessage(null);
  };

  const presets = [
    { id: 'short', name: 'Short', range: '80–120 words', desc: 'Core facts & key takeaway' },
    { id: 'medium', name: 'Medium', range: '150–250 words', desc: 'Balanced synthesis' },
    { id: 'long', name: 'Long', range: '300–500 words', desc: 'Comprehensive coverage' },
    { id: 'detailed', name: 'Detailed', range: '500–800 words', desc: 'Exhaustive section coverage' },
  ] as const;

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Title & Sample buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Abstractive Text Summarization
          </h1>
          <p className="text-xs text-slate-500">
            Select a target length preset and generate high-fidelity neural summaries.
          </p>
        </div>

        {/* Sample Loaders */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">Load Sample:</span>
          <button
            onClick={() => loadSample('ai_research')}
            className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
          >
            AI Research
          </button>
          <button
            onClick={() => loadSample('finance_report')}
            className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
          >
            Financial
          </button>
          <button
            onClick={() => loadSample('healthcare_study')}
            className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
          >
            Clinical
          </button>
        </div>
      </div>

      {/* Main Two-Column Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* LEFT COLUMN: Source Editor & Controls */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="h-4 w-4 text-indigo-600" />
                Source Text
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onNavigate('summarize-pdf')}
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1"
                >
                  <FileUp className="h-3.5 w-3.5" />
                  <span>Upload PDF instead</span>
                </button>
                {inputText && (
                  <button
                    onClick={() => { setInputText(''); setResult(null); setErrorMessage(null); }}
                    className="text-xs text-slate-400 hover:text-rose-600 font-medium ml-2"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            {/* Large Text Area */}
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste long articles, academic papers, reports, or legal transcripts here..."
              className="w-full h-80 p-4 rounded-xl border border-slate-200 bg-slate-50/50 text-slate-900 text-sm font-sans focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white resize-y transition leading-relaxed"
            />

            {/* Input Live Stats */}
            <div className="flex items-center justify-between text-xs text-slate-500 pt-1 border-t border-slate-100">
              <div className="flex items-center gap-3">
                <span><strong>{wordCount}</strong> words</span>
                <span>&bull;</span>
                <span><strong>{charCount}</strong> chars</span>
                <span>&bull;</span>
                <span>~<strong>{estimatedTokens}</strong> tokens</span>
              </div>
              {estimatedTokens > 850 && (
                <span className="text-amber-600 font-medium flex items-center gap-1">
                  <Layers className="h-3 w-3" />
                  Hierarchical Chunking Active
                </span>
              )}
            </div>
          </div>

          {/* Model & Length Controls Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 space-y-5">
            {/* Model Selection */}
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
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">DistilBART</span>
                    {selectedModel === 'distilbart' && <CheckCircle2 className="h-4 w-4 text-indigo-600" />}
                  </div>
                  <div className="text-[10px] font-mono text-indigo-600 font-semibold mt-0.5">
                    sshleifer/distilbart-cnn-12-6
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">High-coherence abstractive summary, 2x faster than BART</p>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedModel('t5_small')}
                  className={`p-3 rounded-xl border text-left transition ${
                    selectedModel === 't5_small'
                      ? 'border-indigo-600 bg-indigo-50/60 ring-2 ring-indigo-500/20'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">T5-small Fine-Tuned</span>
                    {selectedModel === 't5_small' && <CheckCircle2 className="h-4 w-4 text-indigo-600" />}
                  </div>
                  <div className="text-[10px] font-mono text-indigo-600 font-semibold mt-0.5">
                    Falconsai/text_summarization
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">Lightweight 60M parameters, optimized summarization</p>
                </button>
              </div>
            </div>

            {/* Length Presets */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Summary Length Preset
                </label>
                <span className="text-[11px] text-indigo-600 font-semibold">
                  Guaranteed Length-Aware
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {presets.map((preset) => {
                  const isSelected = selectedLength === preset.id;
                  return (
                    <button
                      key={preset.id}
                      type="button"
                      onClick={() => {
                        setSelectedLength(preset.id);
                        if (preset.id === 'short') setLengthPenalty(1.2);
                        if (preset.id === 'medium') setLengthPenalty(1.8);
                        if (preset.id === 'long') setLengthPenalty(2.2);
                        if (preset.id === 'detailed') setLengthPenalty(2.5);
                      }}
                      className={`p-3 rounded-xl border text-left transition ${
                        isSelected
                          ? 'border-indigo-600 bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                          : 'border-slate-200 hover:border-slate-300 bg-white text-slate-700'
                      }`}
                    >
                      <div className="text-xs font-bold">{preset.name}</div>
                      <div className={`text-[10px] mt-0.5 font-medium ${isSelected ? 'text-indigo-200' : 'text-slate-400'}`}>
                        {preset.range}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Advanced Settings Accordion */}
            <div className="pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900"
              >
                <Sliders className="h-3.5 w-3.5" />
                <span>{showAdvanced ? 'Hide Advanced Settings' : 'Show Advanced Settings'}</span>
              </button>

              {showAdvanced && (
                <div className="mt-3 p-4 bg-slate-50 rounded-xl space-y-4 border border-slate-200 text-xs">
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">
                      Explicit Target Word Count (Optional)
                    </label>
                    <input
                      type="number"
                      value={targetWordCount || ''}
                      onChange={(e) => setTargetWordCount(e.target.value ? parseInt(e.target.value) : undefined)}
                      placeholder="e.g. 200 (overrides preset range)"
                      className="w-full p-2 rounded-lg border border-slate-300 bg-white text-xs"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">
                        Beam Search: {numBeams}
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="8"
                        value={numBeams}
                        onChange={(e) => setNumBeams(parseInt(e.target.value))}
                        className="w-full accent-indigo-600"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">
                        Length Penalty: {lengthPenalty}
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="3.0"
                        step="0.1"
                        value={lengthPenalty}
                        onChange={(e) => setLengthPenalty(parseFloat(e.target.value))}
                        className="w-full accent-indigo-600"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-1">
                    <input
                      type="checkbox"
                      id="doSampleCheck"
                      checked={doSample}
                      onChange={(e) => setDoSample(e.target.checked)}
                      className="rounded accent-indigo-600"
                    />
                    <label htmlFor="doSampleCheck" className="text-slate-700 font-medium cursor-pointer">
                      Enable Stochastic Sampling (do_sample = True)
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* Error Message */}
            {errorMessage && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={isLoading || wordCount < 10}
              className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-sm transition-all shadow-md shadow-indigo-600/20 hover:-translate-y-0.5 flex items-center justify-center gap-2 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isLoading ? (
                <>
                  <RotateCcw className="h-4 w-4 animate-spin" />
                  <span>Generating Abstractive Summary...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Generate Summary</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: Results Panel */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-5 min-h-[520px] flex flex-col justify-between">
          {!result && !isLoading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 space-y-3 my-auto">
              <div className="h-14 w-14 rounded-2xl bg-indigo-50 text-indigo-500 flex items-center justify-center">
                <Sparkles className="h-7 w-7" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">No Summary Generated Yet</h3>
              <p className="text-xs text-slate-500 max-w-sm">
                Paste your text on the left, pick your preferred target length, and click <span className="font-semibold text-indigo-600">Generate Summary</span>.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 space-y-4 my-auto">
              <div className="h-14 w-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center animate-pulse">
                <Sparkles className="h-7 w-7 animate-spin" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">
                {jobMessage || 'Synthesizing Text via Seq2Seq Transformer...'}
              </h3>
              <p className="text-xs text-slate-500 max-w-xs">
                Background worker executing token-bounded attention, beam search, and sentence completion.
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
              {/* Telemetry Pills Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700">
                    {result.summary_word_count} words
                  </span>
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700">
                    {result.compression_ratio}% reduction
                  </span>
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700" title="Total processing duration">
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
                  {result.is_chunked && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700">
                      Hierarchical ({result.chunks_count} chunks)
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setIsEditing(!isEditing)}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium flex items-center gap-1"
                    title="Toggle Edit"
                  >
                    <Edit3 className="h-3.5 w-3.5" />
                    <span>{isEditing ? 'View' : 'Edit'}</span>
                  </button>
                  <button
                    onClick={handleCopy}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium flex items-center gap-1"
                    title="Copy to Clipboard"
                  >
                    {isCopied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{isCopied ? 'Copied' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={handleDownloadTxt}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium flex items-center gap-1"
                    title="Download as TXT"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>TXT</span>
                  </button>
                  <button
                    onClick={handleDownloadMd}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-medium flex items-center gap-1"
                    title="Download as Markdown"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>MD</span>
                  </button>
                </div>
              </div>

              {/* Warnings Banner if any */}
              {result.warnings && result.warnings.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs space-y-1">
                  {result.warnings.map((w, idx) => (
                    <div key={idx} className="flex items-start gap-1.5">
                      <AlertCircle className="h-3.5 w-3.5 mt-0.5 shrink-0 text-amber-600" />
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Summary Display Box */}
              <div className="flex-1">
                {isEditing ? (
                  <textarea
                    value={editedSummary}
                    onChange={(e) => setEditedSummary(e.target.value)}
                    className="w-full h-96 p-4 rounded-xl border border-slate-200 text-slate-900 text-sm font-sans focus:outline-none focus:ring-2 focus:ring-indigo-500 leading-relaxed resize-y"
                  />
                ) : (
                  <div className="prose prose-slate max-w-none text-slate-800 text-sm leading-relaxed p-4 bg-slate-50/70 rounded-xl border border-slate-100 min-h-[360px] whitespace-pre-wrap">
                    {result.summary}
                  </div>
                )}
              </div>

              {/* Footer specs */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Model: <strong>{result.model_name}</strong></span>
                <span>Preset target: <strong>{result.target_word_range || selectedLength}</strong></span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
