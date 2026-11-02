import React from 'react';
import { Sparkles, ShieldCheck, RefreshCw } from 'lucide-react';
import { HealthResponse } from '../types';

interface HeaderProps {
  pageTitle: string;
  health: HealthResponse | null;
  onRefreshHealth: () => void;
  isChecking: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  pageTitle,
  health,
  onRefreshHealth,
  isChecking,
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div>
        <h2 className="text-lg font-bold text-slate-900 tracking-tight">
          {pageTitle}
        </h2>
        <p className="text-xs text-slate-500">
          Abstractive Text Summarization using Seq2Seq Transformers
        </p>
      </div>

      <div className="flex items-center gap-3">
        {/* Model status pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700">
          <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
          <span className="font-semibold text-slate-900">{health?.active_model ? health.active_model.split(' ')[0] : 'T5-small'}</span>
          <span className="text-slate-400">|</span>
          <span className="text-slate-600 truncate max-w-[180px]">{health?.active_model || 'Falconsai/text_summarization'}</span>
        </div>

        {/* Backend health pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-medium text-emerald-700">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
          <span>API Connected</span>
          <button
            onClick={onRefreshHealth}
            disabled={isChecking}
            title="Refresh status"
            className="hover:text-emerald-900 disabled:opacity-50 ml-0.5"
          >
            <RefreshCw className={`h-3 w-3 ${isChecking ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
