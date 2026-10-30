import React from 'react';
import { Search, Plus, Shield, Terminal, Zap } from 'lucide-react';

export default function Header({ onStartScan, searchQuery, onSearchChange, gapCount }) {
  return (
    <header className="h-14 border-b border-[#171b23] bg-[#090b0e]/90 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Workspace Breadcrumbs & Scope Tag */}
      <div className="flex items-center gap-2.5 text-xs">
        <span className="font-display font-bold text-white flex items-center gap-1.5 text-xs tracking-tight">
          <Terminal className="w-3.5 h-3.5 text-amber-400" />
          Privexis
        </span>
        <span className="text-slate-600 font-mono">/</span>
        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#14171f] text-slate-400 border border-[#232936]">
          PS-019 Privacy Evidence Workspace
        </span>
        <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[9px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
          Technical Evidence Only
        </span>
      </div>

      {/* Global Search and Actions */}
      <div className="flex items-center gap-2.5">
        <div className="relative w-56 sm:w-64">
          <Search className="w-3 h-3 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search fields, sources, classes..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-[#0e1015] border border-[#1b202c] rounded-lg pl-8 pr-3 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500/60 font-sans"
          />
        </div>

        <button
          onClick={onStartScan}
          className="flex items-center gap-1.5 px-3 py-1 bg-amber-500 hover:bg-amber-400 text-[#07080a] font-bold text-xs rounded-lg shadow-sm transition-all active:scale-95 font-display"
        >
          <Zap className="w-3 h-3 stroke-[2.5]" />
          <span>New Scan</span>
        </button>
      </div>
    </header>
  );
}
