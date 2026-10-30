import React from 'react';
import {
  LayoutDashboard, Search, Database, AlertTriangle,
  Sliders, BarChart3, Beaker, Info, ShieldCheck, RefreshCw, Cpu
} from 'lucide-react';

// Privexis monogram — "P" wordmark
const PrivexisLogo = () => (
  <svg
    width="32"
    height="32"
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-label="Privexis"
  >
    <defs>
      <linearGradient id="pGrad" x1="0" y1="0" x2="1" y2="1" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stop-color="#fbbf24" />
        <stop offset="100%" stop-color="#b45309" />
      </linearGradient>
    </defs>
    <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#pGrad)" />
    <path
      d="M9 9.5 H19.5 C21.3 9.5 22.7 10.9 22.7 12.7 C22.7 14.5 21.3 15.9 19.5 15.9 H13.5 V22.5 H9 V9.5 Z"
      fill="#07080a"
    />
    <path
      d="M13.5 12.7 H19 C19.9 12.7 20.6 12 20.6 11.1 C20.6 10.2 19.9 9.5 19 9.5 H13.5 V12.7 Z"
      fill="url(#pGrad)"
    />
  </svg>
);

export default function Sidebar({
  activePage,
  onNavigate,
  hasCustomData,
  onReloadDemo,
  gapCount = 0
}) {
  const navItems = [
    { id: 'dashboard', label: 'Command Center', icon: LayoutDashboard, tag: '01' },
    { id: 'scan', label: 'Discovery Scanner', icon: Search, tag: '02' },
    { id: 'evidence', label: 'Evidence Inventory', icon: Database, tag: '03' },
    {
      id: 'gaps',
      label: 'Evidence Gaps',
      icon: AlertTriangle,
      badge: gapCount > 0 ? `${gapCount}` : null,
      tag: '04'
    },
    { id: 'rules', label: 'Rule Engine', icon: Sliders, tag: '05' },
    { id: 'accuracy', label: 'Accuracy & Metrics', icon: BarChart3, tag: '06' },
    { id: 'demos', label: 'Try to Fool It', icon: Beaker, tag: '07' },
    { id: 'about', label: 'Architecture & Scope', icon: Info, tag: '08' },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-60 bg-[#090b0e] border-r border-[#171b23] flex flex-col z-50">
      {/* Brand Monogram Header */}
      <div className="p-4 border-b border-[#171b23]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg shadow-md shadow-amber-500/20">
            <PrivexisLogo />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-display font-bold text-white text-sm tracking-tight">PRIVEXIS</span>
            </div>
            <div className="text-[10px] text-slate-500 font-mono tracking-wide">
              Team Infynex // PS-019
            </div>
          </div>
        </div>
      </div>

      {/* Nav links */}
      <nav className="flex-1 p-2.5 space-y-1 overflow-y-auto">
        <div className="px-2.5 py-1 text-[9px] font-mono uppercase tracking-widest text-slate-500">
          SYSTEM MODULES
        </div>
        {navItems.map(({ id, label, icon: Icon, badge, tag }) => {
          const active = activePage === id;
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className={`w-full flex items-center justify-between px-2.5 py-2 rounded-lg transition-all text-xs font-medium group relative ${
                active
                  ? 'bg-[#14171f] text-white border border-[#232936] shadow-sm'
                  : 'text-slate-400 hover:bg-[#101217] hover:text-slate-200 border border-transparent'
              }`}
            >
              {active && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-amber-400 rounded-r" />
              )}
              <div className="flex items-center gap-2.5">
                <Icon className={`w-3.5 h-3.5 shrink-0 ${active ? 'text-amber-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span className={active ? 'font-semibold text-white' : ''}>{label}</span>
              </div>
              {badge ? (
                <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                  {badge}
                </span>
              ) : (
                <span className="text-[9px] font-mono text-slate-600 group-hover:text-slate-500">
                  {tag}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-3 border-t border-[#171b23] bg-[#07080a] space-y-2">
        {hasCustomData && (
          <button
            onClick={onReloadDemo}
            className="w-full flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-md text-[11px] font-medium text-slate-400 hover:text-amber-300 hover:bg-amber-500/10 border border-[#1a1f29] transition-all"
          >
            <RefreshCw className="w-3 h-3 text-amber-400" />
            Reset to Synthetic Data
          </button>
        )}

        <div className="p-2.5 rounded-lg bg-[#0e1015] border border-[#171b23] text-xs">
          <div className="flex items-center justify-between">
            <span className="font-display font-bold text-white text-[11px]">Team Infynex Engine</span>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[9px] text-emerald-400 font-mono">READY</span>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-0.5">
            Reservoir Sampling (k=50)
          </p>
        </div>
      </div>
    </aside>
  );
}
