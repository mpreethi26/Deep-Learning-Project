import React from 'react';
import {
  LayoutDashboard,
  FileText,
  FileUp,
  Columns,
  BarChart3,
  History,
  Settings,
  Sparkles,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onSelectPage: (page: string) => void;
  activeDevice: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onSelectPage,
  activeDevice
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'summarize-text', label: 'Summarize Text', icon: FileText },
    { id: 'summarize-pdf', label: 'Summarize PDF', icon: FileUp },
    { id: 'comparison', label: 'Model Comparison', icon: Columns },
    { id: 'evaluation', label: 'Evaluation Metrics', icon: BarChart3 },
    { id: 'history', label: 'Summary History', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col h-screen sticky top-0 border-r border-slate-800 shadow-xl select-none z-30">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
              Neural Summarizer
            </h1>
            <p className="text-xs text-indigo-300 font-medium tracking-wide">
              Transformer NLP Studio
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
          Core Modules
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Hardware / Engine Status */}
      <div className="p-4 mx-3 mb-4 bg-slate-800/70 border border-slate-700/60 rounded-xl">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-1">
          <Cpu className="h-3.5 w-3.5 text-indigo-400" />
          <span>Inference Engine</span>
        </div>
        <p className="text-[11px] text-slate-400 truncate">
          {activeDevice || 'Detecting hardware...'}
        </p>
        <div className="mt-2 flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-[10px] font-medium text-emerald-400">Model Ready (PyTorch)</span>
        </div>
      </div>
    </aside>
  );
};
