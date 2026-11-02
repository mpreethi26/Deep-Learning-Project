import React from 'react';
import { BookOpen, ExternalLink, Cpu, GitBranch, Layers, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const ResearchPage: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto space-y-10 pb-16">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-indigo-600" />
          <span>Research Methodology &amp; IEEE Alignment</span>
        </h1>
        <p className="text-xs text-slate-500">
          Theoretical foundations, mathematical formulations, and IEEE Xplore literature alignment for Seq2Seq abstractive summarization.
        </p>
      </div>

      {/* IEEE Paper Card */}
      <div className="bg-white rounded-2xl border-2 border-indigo-100 shadow-premium p-6 sm:p-8 space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
            IEEE Xplore Alignment
          </span>
          <span className="text-xs font-semibold text-slate-500">Natural Language Processing</span>
        </div>

        <div>
          <h2 className="text-xl font-bold text-slate-900 leading-snug">
            Abstractive Text Summarization using Sequence-to-Sequence BART with Hierarchical Section Modeling
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Required Research Publisher: <strong className="text-slate-800">IEEE Xplore</strong> &bull; Keywords: <code className="bg-slate-100 px-1 py-0.5 rounded text-indigo-600">abstractive text summarization transformer</code>
          </p>
        </div>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 text-xs text-slate-700 space-y-2 leading-relaxed">
          <p>
            <strong>Research Problem:</strong> Standard encoder-decoder transformers (such as DistilBART and T5-small) suffer from fixed positional encoding bottlenecks (1024 / 512 tokens) and news-dataset inductive brevity biases, resulting in premature summary truncation on lengthy documents and technical manuscripts.
          </p>
          <p>
            <strong>Core Methodology:</strong> A hierarchical sliding-window token chunking pipeline coupled with length-aware token budgeting and bounded multi-stage synthesis. Sentence boundary preservation prevents fragmentation artifacts.
          </p>
          <p>
            <strong>Evaluated Models:</strong> Primary <code className="bg-slate-200 px-1 py-0.5 rounded text-indigo-700">sshleifer/distilbart-cnn-12-6</code> and comparative fine-tuned <code className="bg-slate-200 px-1 py-0.5 rounded text-indigo-700">Falconsai/text_summarization</code>.
          </p>
        </div>
      </div>

      {/* Mathematical & Architectural Foundations */}
      <div className="space-y-6">
        <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2">
          1. Transformer Architecture &amp; Self-Attention
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          The core mechanism driving transformer models is the Scaled Dot-Product Attention, defined mathematically as:
        </p>
        <div className="p-4 bg-slate-900 text-indigo-300 font-mono text-xs rounded-xl overflow-x-auto shadow-inner text-center">
          Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          In Multi-Head Attention, queries, keys, and values are linearly projected $h$ times with distinct learned parameter matrices, permitting the model to attend jointly to contextual representations at disparate subspace positions:
        </p>
        <div className="p-4 bg-slate-900 text-indigo-300 font-mono text-xs rounded-xl overflow-x-auto shadow-inner text-center">
          MultiHead(Q, K, V) = Concat(head_1, ..., head_h) * W^O
        </div>
      </div>

      {/* Extractive vs Abstractive */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2">
          2. Extractive vs. Abstractive Summarization
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border border-slate-200 rounded-xl overflow-hidden bg-white">
            <thead className="bg-slate-100 text-slate-700 uppercase font-bold text-[11px]">
              <tr>
                <th className="p-3 border-b border-slate-200">Dimension</th>
                <th className="p-3 border-b border-slate-200">Extractive Summarization</th>
                <th className="p-3 border-b border-slate-200">Abstractive Summarization (Implemented)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-600">
              <tr>
                <td className="p-3 font-semibold text-slate-900">Vocabulary</td>
                <td className="p-3">Strictly identical to source sentences</td>
                <td className="p-3">Synthesizes novel tokens, paraphrases, and idioms</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-900">Mechanism</td>
                <td className="p-3">Sentence scoring and ranking (TextRank, LexRank)</td>
                <td className="p-3">Autoregressive Seq2Seq decoding with cross-attention</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-900">Cohesion</td>
                <td className="p-3">Often abrupt, redundant, or disjointed transitions</td>
                <td className="p-3">Fluent, human-like narrative flow and synthesis</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-900">Failure Modes</td>
                <td className="p-3">Includes irrelevant source details verbatim</td>
                <td className="p-3">Potential hallucination without length/beam grounding</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* BART Denoising Autoencoder Mechanics */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2">
          3. BART (Bidirectional &amp; Auto-Regressive Transformers)
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          BART uses a standard sequence-to-sequence architecture with a bidirectional encoder (like BERT) and a left-to-right autoregressive decoder (like GPT). It is pretrained by corrupting document text using 5 distinct stochastic transformations:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-white rounded-xl border border-slate-200">
            <strong className="text-indigo-600 block mb-1">1. Token Masking</strong>
            Arbitrary tokens are sampled and replaced with [MASK] tokens (akin to BERT).
          </div>
          <div className="p-3 bg-white rounded-xl border border-slate-200">
            <strong className="text-indigo-600 block mb-1">2. Token Deletion</strong>
            Random tokens are erased from the sequence; the model learns to identify absent positions.
          </div>
          <div className="p-3 bg-white rounded-xl border border-slate-200">
            <strong className="text-indigo-600 block mb-1">3. Text Infilling</strong>
            Single spans of text are replaced with single [MASK] tokens, teaching the model span lengths.
          </div>
          <div className="p-3 bg-white rounded-xl border border-slate-200">
            <strong className="text-indigo-600 block mb-1">4. Sentence Permutation</strong>
            Document sentences are randomly shuffled; the model restores chronological order.
          </div>
          <div className="p-3 bg-white rounded-xl border border-slate-200 sm:col-span-2">
            <strong className="text-indigo-600 block mb-1">5. Document Rotation</strong>
            A token is chosen uniformly at random and the document is rotated to begin at that token.
          </div>
        </div>
      </div>

      {/* End-to-End Pipeline Workflow */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2">
          4. Implemented End-to-End Execution Pipeline
        </h3>
        <div className="p-5 bg-white rounded-xl border border-slate-200 space-y-3 text-xs text-slate-700">
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">1</div>
            <div><strong>Input Ingestion:</strong> Raw pasted text or PyMuPDF binary stream extraction.</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">2</div>
            <div><strong>Subword Tokenization:</strong> BPE encoding with context limit validation (&le; 1024 tokens).</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">3</div>
            <div><strong>Hierarchical Chunking:</strong> Sliding window (900 token max, 75 token overlap) on paragraph boundaries.</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">4</div>
            <div><strong>Length-Aware Generation:</strong> Beam search (beams=4) with calibrated min_new_tokens and length_penalty.</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">5</div>
            <div><strong>Sentence Boundary Trimming:</strong> Trims incomplete trailing fragments cleanly.</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">6</div>
            <div><strong>ROUGE Evaluation:</strong> Unigram, bigram, and LCS overlap computation against references.</div>
          </div>
        </div>
      </div>
    </div>
  );
};
