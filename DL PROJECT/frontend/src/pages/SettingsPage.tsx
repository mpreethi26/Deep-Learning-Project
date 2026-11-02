import React, { useState } from 'react';
import { Settings, Cpu, HardDrive, ShieldCheck, RefreshCw, Check } from 'lucide-react';
import { HealthResponse } from '../types';
import { api } from '../services/api';

interface SettingsPageProps {
  health: HealthResponse | null;
  onRefreshHealth: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  health,
  onRefreshHealth
}) => {
  const [clearing, setClearing] = useState(false);
  const [clearedMsg, setClearedMsg] = useState(false);

  const handleClearHistory = async () => {
    setClearing(true);
    try {
      await api.clearHistory();
      setClearedMsg(true);
      setTimeout(() => setClearedMsg(false), 2500);
    } catch (err) {
      console.error(err);
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
          <Settings className="h-6 w-6 text-indigo-600" />
          <span>System Settings &amp; Infrastructure</span>
        </h1>
        <p className="text-xs text-slate-500">
          Backend connectivity, PyTorch execution parameters, and model configuration.
        </p>
      </div>

      {/* Backend Status Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-sm text-slate-900">FastAPI Backend Service</h3>
            <p className="text-xs text-slate-500">REST API connected at http://localhost:8000</p>
          </div>
          <button
            onClick={onRefreshHealth}
            className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center gap-1.5 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Probe Status</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-3 bg-slate-50 rounded-lg">
            <span className="text-slate-400 block text-[11px]">API Health</span>
            <span className="font-bold text-emerald-600 capitalize">{health?.status || 'Active'}</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <span className="text-slate-400 block text-[11px]">Execution Engine</span>
            <span className="font-bold text-slate-800">{health?.device || 'PyTorch Inference'}</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <span className="text-slate-400 block text-[11px]">Active Model</span>
            <span className="font-bold text-indigo-600">{health?.active_model || 'BART Large CNN'}</span>
          </div>
        </div>
      </div>

      {/* Cache Management */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-subtle p-6 space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Storage &amp; Session Management</h3>
        <p className="text-xs text-slate-500">
          History records are safely persisted locally in <code className="bg-slate-100 px-1 py-0.5 rounded">data/history.json</code> with in-memory caching.
        </p>

        <div className="flex items-center justify-between pt-2">
          <button
            onClick={handleClearHistory}
            disabled={clearing}
            className="px-4 py-2 rounded-lg bg-rose-50 border border-rose-200 hover:bg-rose-100 text-rose-700 text-xs font-semibold transition flex items-center gap-2"
          >
            {clearing ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : null}
            <span>Purge Session History Data</span>
          </button>
          {clearedMsg && (
            <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
              <Check className="h-3.5 w-3.5" />
              History successfully purged!
            </span>
          )}
        </div>
      </div>

      {/* Project Lead & Credits */}
      <div className="bg-slate-900 text-slate-100 rounded-xl p-6 space-y-3 shadow-premium">
        <h3 className="font-bold text-sm text-white flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-indigo-400" />
          <span>Project Credits &amp; Attribution</span>
        </h3>
        <p className="text-xs text-slate-300">
          <strong>Project:</strong> Abstractive Text Summarization Using Transformer Models
        </p>
        <p className="text-xs text-slate-300">
          <strong>Team Lead:</strong> CHOUDAM BHARATH REDDY
        </p>
        <p className="text-xs text-slate-400">
          Built with PyTorch, Hugging Face Transformers (sshleifer/distilbart-cnn-12-6 & Falconsai/text_summarization), FastAPI, React, TypeScript, and Tailwind CSS.
        </p>
      </div>
    </div>
  );
};
