import React, { useState, useEffect } from 'react';
import {
  Sliders, CheckCircle2, Shield,
  FileCode, Loader2, AlertCircle, Sparkles
} from 'lucide-react';

export default function RulesPage() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${apiBase}/api/rules`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setConfig(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch rules config');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-400 mb-3" />
        <p className="text-xs">Loading rule and checklist configuration...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-5 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-xs">
        <AlertCircle className="w-4 h-4 mb-1.5 text-red-400" />
        {error}
      </div>
    );
  }

  const { rules, checklist } = config || {};
  const scoring = rules?.scoring || {};
  const classes = rules?.classes || {};

  return (
    <div className="space-y-7 animate-in fade-in duration-500">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider mb-2">
          <Sparkles className="w-3 h-3" />
          Infynex Transparent Engine
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          Configurable Detection Rules & Checklist
        </h1>
        <p className="text-slate-400 mt-1 text-xs max-w-2xl leading-relaxed">
          PS-019 requires detecting candidate fields using configurable rules without black-box inference. All rules are externalized in YAML.
        </p>
      </div>

      {/* Scoring Weights */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl p-6">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
          <Sliders className="w-3.5 h-3.5 text-emerald-400" />
          Scoring Formulation
        </h3>
        <p className="text-xs text-emerald-300/90 mb-5 font-mono bg-[#070a12] p-3 rounded-xl border border-[#182035]">
          confidence = (name_weight × hint_matched) + (value_weight × fraction_valid_values)
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-[#070a12] border border-[#182035] rounded-xl">
            <span className="text-[10px] text-slate-500 font-bold uppercase">Name Hint Weight</span>
            <div className="text-2xl font-extrabold text-emerald-400 mt-1 font-mono">{scoring.name_weight}</div>
          </div>
          <div className="p-4 bg-[#070a12] border border-[#182035] rounded-xl">
            <span className="text-[10px] text-slate-500 font-bold uppercase">Value Pattern Weight</span>
            <div className="text-2xl font-extrabold text-cyan-400 mt-1 font-mono">{scoring.value_weight}</div>
          </div>
          <div className="p-4 bg-[#070a12] border border-[#182035] rounded-xl">
            <span className="text-[10px] text-slate-500 font-bold uppercase">Candidate Threshold</span>
            <div className="text-2xl font-extrabold text-white mt-1 font-mono">{scoring.threshold}</div>
          </div>
          <div className="p-4 bg-[#070a12] border border-[#182035] rounded-xl">
            <span className="text-[10px] text-slate-500 font-bold uppercase">Review Floor</span>
            <div className="text-2xl font-extrabold text-amber-400 mt-1 font-mono">{scoring.review_floor}</div>
          </div>
        </div>
      </div>

      {/* Predefined Classes Definition */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-[#182035] bg-[#090d16]">
          <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            Class Rule Specifications (<code className="text-cyan-300 font-mono">config/rules.yaml</code>)
          </h3>
        </div>

        <div className="divide-y divide-[#182035]">
          {Object.entries(classes).map(([cls, spec]) => (
            <div key={cls} className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold rounded-lg text-xs font-mono">
                  {cls}
                </span>
                <span className="text-[11px] text-slate-400 italic">
                  Check: {spec.check}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs pt-1">
                <div>
                  <div className="text-slate-500 text-[10px] font-bold uppercase mb-1">Column Name Hints</div>
                  <div className="flex flex-wrap gap-1">
                    {spec.name_hints?.map((h, i) => (
                      <span key={i} className="px-2 py-0.5 bg-[#070a12] border border-[#182035] rounded text-slate-300 font-mono text-[11px]">
                        {h}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-slate-500 text-[10px] font-bold uppercase mb-1">Negative Blockers</div>
                  <div className="flex flex-wrap gap-1">
                    {spec.negative_hints && spec.negative_hints.length > 0 ? (
                      spec.negative_hints.map((nh, i) => (
                        <span key={i} className="px-2 py-0.5 bg-rose-950/40 border border-rose-900/40 rounded text-rose-300 font-mono text-[11px]">
                          {nh}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-600 italic text-[11px]">None configured</span>
                    )}
                  </div>
                </div>

                <div>
                  <div className="text-slate-500 text-[10px] font-bold uppercase mb-1">Validators & Patterns</div>
                  <div className="space-y-1 font-mono text-[11px] text-slate-300">
                    {spec.validator && (
                      <div className="text-emerald-400">Validator: {spec.validator}</div>
                    )}
                    {spec.value_patterns?.map((p, i) => (
                      <div key={i} className="text-slate-400 truncate" title={p}>
                        {p}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Checklist Configuration */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl p-5">
        <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          Evidence Checklist Definition (<code className="text-xs text-cyan-300 font-mono">config/checklist.yaml</code>)
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Defines what constitutes an evidence gap for each candidate finding.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 bg-[#070a12] border border-[#182035] rounded-xl space-y-2">
            <span className="text-slate-500 text-[10px] font-bold uppercase">Required Items (Missing = Evidence Gap)</span>
            <div className="flex flex-wrap gap-2 pt-1">
              {checklist?.required?.map((item, i) => (
                <span key={i} className="px-2.5 py-1 bg-amber-500/10 text-amber-300 border border-amber-500/20 rounded-md font-mono text-xs">
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div className="p-4 bg-[#070a12] border border-[#182035] rounded-xl space-y-2">
            <span className="text-slate-500 text-[10px] font-bold uppercase">Advisory Checks</span>
            <div className="flex flex-wrap gap-2 pt-1">
              {checklist?.advisory?.map((item, i) => (
                <span key={i} className="px-2.5 py-1 bg-[#131d33] text-slate-300 border border-[#1f2c4a] rounded-md font-mono text-xs">
                  {item}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
