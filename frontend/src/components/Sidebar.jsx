import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Search, Database, AlertTriangle,
  Sliders, BarChart3, Beaker, Info, RefreshCw
} from 'lucide-react';

// Privexis monogram — "P" wordmark
import PrivexisLogo from './PrivexisLogo';

export default function Sidebar({
  hasCustomData,
  onReloadDemo,
  gapCount = 0
}) {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { id: 'dashboard', path: '/dashboard', label: 'Command Center', icon: LayoutDashboard, tag: '01' },
    { id: 'scan', path: '/scan', label: 'Discovery Scanner', icon: Search, tag: '02' },
    { id: 'evidence', path: '/evidence', label: 'Evidence Inventory', icon: Database, tag: '03' },
    {
      id: 'gaps',
      path: '/gaps',
      label: 'Evidence Gaps',
      icon: AlertTriangle,
      badge: gapCount > 0 ? `${gapCount}` : null,
      tag: '04'
    },
    { id: 'rules', path: '/rules', label: 'Rule Engine', icon: Sliders, tag: '05' },
    { id: 'accuracy', path: '/accuracy', label: 'Accuracy & Metrics', icon: BarChart3, tag: '06' },
    { id: 'demos', path: '/demos', label: 'Try to Fool It', icon: Beaker, tag: '07' },
    { id: 'about', path: '/about', label: 'Architecture & Scope', icon: Info, tag: '08' },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-60 bg-[#0c0e14] border-r border-[#1e2433] flex flex-col z-50">
      {/* Brand Monogram Header */}
      <div className="p-4 border-b border-[#1e2433] bg-[#0c0e14]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl shadow-md shadow-amber-500/10 border border-[#1e2433] bg-[#11141d] flex items-center justify-center p-1">
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
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-2.5 py-1 text-[9px] font-mono uppercase tracking-widest text-slate-500 font-semibold">
          SYSTEM MODULES
        </div>
        {navItems.map(({ id, path, label, icon: Icon, badge, tag }) => {
          const active = location.pathname === path || (location.pathname === '/' && id === 'dashboard');
          return (
            <button
              key={id}
              onClick={() => navigate(path)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl transition-all text-xs font-medium group relative ${
                active
                  ? 'bg-[#181d2a] text-white border border-[#2a3348] shadow-md shadow-black/20'
                  : 'text-slate-400 hover:bg-[#121620] hover:text-slate-200 border border-transparent'
              }`}
            >
              {active && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-amber-400 rounded-r-full shadow-sm shadow-amber-400/50" />
              )}
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 shrink-0 transition-colors ${active ? 'text-amber-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span className={active ? 'font-semibold text-white' : ''}>{label}</span>
              </div>
              {badge ? (
                <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
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
      <div className="p-3 border-t border-[#1e2433] bg-[#090b0e] space-y-2">
        {hasCustomData && (
          <button
            onClick={onReloadDemo}
            className="w-full flex items-center justify-between gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-medium text-slate-400 hover:text-amber-300 hover:bg-amber-500/10 border border-[#1e2433] transition-all"
          >
            <RefreshCw className="w-3 h-3 text-amber-400" />
            Reset to Synthetic Data
          </button>
        )}
        <div className="p-3 rounded-xl bg-[#11141d] border border-[#1e2433] text-xs">
          <div className="flex items-center justify-between">
            <span className="font-display font-bold text-white text-[11px]">Team Infynex</span>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[9px] text-emerald-400 font-mono font-bold">READY</span>
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