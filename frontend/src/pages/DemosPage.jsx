import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Beaker, CheckCircle2, XCircle, AlertCircle,
  Loader2, ArrowRight, ShieldCheck, Zap, Sparkles
} from 'lucide-react';

export default function DemosPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDemos();
  }, []);

  const fetchDemos = async () => {
    try {
      const res = await axios.get('/api/demos');
      setCases(res.data.cases || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch demo cases');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-400 mb-3" />
        <p className="text-xs">Evaluating adversarial column conflict cases...</p>
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

  return (
    <div className="space-y-7 animate-in fade-in duration-500">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[10px] font-bold uppercase tracking-wider mb-2">
          <Sparkles className="w-3 h-3" />
          Infynex Adversarial Sandbox
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          "Try to Fool It" Benchmark
        </h1>
        <p className="text-slate-400 mt-1 text-xs max-w-2xl leading-relaxed">
          Demonstrating how Privexis resolves conflicts where column names contradict actual values, contrasting our hybrid engine against naive name-only inspection tools.
        </p>
      </div>

      {/* Grid of Cases */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {cases.map((c, i) => (
          <div
            key={i}
            className="bg-[#0c101d] border border-[#182035] rounded-2xl p-5 space-y-3.5 shadow-xl hover:border-[#223050] transition-all"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h4 className="font-bold text-white text-xs">{c.title}</h4>
                <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                  Column name: <code className="text-cyan-300 font-bold bg-[#070a12] px-1.5 py-0.5 rounded border border-[#182035]">{c.column}</code>
                </div>
              </div>
              {c.correct ? (
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full font-mono">
                  <CheckCircle2 className="w-3 h-3" /> Correct
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-full font-mono">
                  <XCircle className="w-3 h-3" /> Misclassified
                </span>
              )}
            </div>

            {/* Value Samples */}
            <div className="p-2.5 bg-[#070a12] border border-[#182035] rounded-xl">
              <span className="text-[9px] text-slate-500 font-bold uppercase block mb-1">
                Sample Values (Masked)
              </span>
              <div className="flex flex-wrap gap-1.5">
                {c.values.map((v, idx) => (
                  <span key={idx} className="font-mono text-[11px] text-slate-300 bg-[#0c101d] px-2 py-0.5 rounded border border-[#182035]">
                    {v}
                  </span>
                ))}
              </div>
            </div>

            {/* Comparison row */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs pt-1">
              <div className="p-2 bg-[#070a12] rounded-xl border border-[#182035]">
                <span className="text-[9px] text-slate-500 uppercase block font-bold">True Class</span>
                <span className="font-mono font-bold text-slate-200 mt-0.5 block text-xs">{c.truth}</span>
              </div>

              <div className="p-2 bg-emerald-950/20 rounded-xl border border-emerald-500/30">
                <span className="text-[9px] text-emerald-400 uppercase block font-bold">Infynex Engine</span>
                <span className="font-mono font-bold text-emerald-300 mt-0.5 block text-xs">{c.predicted}</span>
              </div>

              <div className="p-2 bg-[#070a12] rounded-xl border border-[#182035]">
                <span className="text-[9px] text-slate-500 uppercase block font-bold">Naive Name Tool</span>
                <span className={`font-mono font-bold mt-0.5 block text-xs ${c.name_only_guess !== c.truth ? 'text-amber-400' : 'text-slate-400'}`}>
                  {c.name_only_guess}
                </span>
              </div>
            </div>

            <p className="text-[11px] text-slate-400 italic">
              Evidence: {c.evidence} (Confidence: {Math.round(c.confidence * 100)}%)
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
