import React, { useState, useEffect } from 'react';
import {
  BarChart3, CheckCircle2, AlertCircle, Loader2,
  TrendingUp, Award, Layers, Sparkles
} from 'lucide-react';

export default function AccuracyPage() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [datasetView, setDatasetView] = useState('main'); // 'main' or 'holdout'

  useEffect(() => {
    fetchAccuracy();
  }, []);

  const fetchAccuracy = async () => {
    setLoading(true);
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${apiBase}/api/accuracy`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setMetrics(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch evaluation metrics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-400 mb-3" />
        <p className="text-xs">Evaluating scanner against hand-labelled ground truth sets...</p>
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

  const activeMetrics = metrics ? metrics[datasetView] : null;
  const perClass = activeMetrics?.per_class || {};
  const overall = activeMetrics?.overall || {};

  return (
    <div className="space-y-7 animate-in fade-in duration-500">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider mb-2">
          <Award className="w-3 h-3" />
          Infynex Benchmark Evaluation
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          Per-Class Precision & Recall Evaluation
        </h1>
        <p className="text-slate-400 mt-1 text-xs max-w-2xl leading-relaxed">
          PS-019 requires reporting per-class precision and recall against small manually labelled ground truth sets.
        </p>
      </div>

      {/* Dataset Toggle */}
      <div className="flex gap-2.5 border-b border-[#182035] pb-3.5">
        <button
          onClick={() => setDatasetView('main')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl font-bold text-xs transition-all ${
            datasetView === 'main'
              ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-[#070a12] shadow-lg shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-[#131d33]'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Main Ground Truth Set (22 columns)
        </button>
        <button
          onClick={() => setDatasetView('holdout')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl font-bold text-xs transition-all ${
            datasetView === 'holdout'
              ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-[#070a12] shadow-lg shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-[#131d33]'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Fresh Holdout Set (21 columns)
        </button>
      </div>

      {/* Summary Scorecards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl">
          <div className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Overall Precision</div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-1 font-mono">
            {Math.round((overall.precision || 0) * 100)}%
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">True Positives / (TP + False Positives)</p>
        </div>

        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl">
          <div className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Overall Recall</div>
          <div className="text-3xl font-extrabold text-cyan-400 mt-1 font-mono">
            {Math.round((overall.recall || 0) * 100)}%
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">True Positives / (TP + False Negatives)</p>
        </div>

        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl">
          <div className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Micro F1 Score</div>
          <div className="text-3xl font-extrabold text-purple-400 mt-1 font-mono">
            {Math.round((overall.f1 || 0) * 100)}%
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">Harmonic balance of precision & recall</p>
        </div>
      </div>

      {/* Per Class Table & Visual Meters */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-[#182035] bg-[#090d16]">
          <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
            <BarChart3 className="w-3.5 h-3.5 text-emerald-400" />
            Per-Class Accuracy Audit
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#070a12] text-slate-400 text-[11px] uppercase tracking-wider border-b border-[#182035]">
                <th className="px-5 py-3.5 font-bold">Data Class</th>
                <th className="px-5 py-3.5 font-bold">Precision</th>
                <th className="px-5 py-3.5 font-bold">Recall</th>
                <th className="px-5 py-3.5 font-bold">F1 Score</th>
                <th className="px-5 py-3.5 font-bold text-center">TP</th>
                <th className="px-5 py-3.5 font-bold text-center">FP</th>
                <th className="px-5 py-3.5 font-bold text-center">FN</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#182035]">
              {Object.entries(perClass).map(([cls, stat]) => {
                const precPct = stat.precision !== null ? Math.round(stat.precision * 100) : 0;
                const recPct = stat.recall !== null ? Math.round(stat.recall * 100) : 0;
                const f1Pct = stat.f1 !== null ? Math.round(stat.f1 * 100) : 0;

                return (
                  <tr key={cls} className="hover:bg-[#131d33]/50 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-white">
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                        {cls}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-[#182035] h-1.5 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-400 rounded-full"
                            style={{ width: `${precPct}%` }}
                          />
                        </div>
                        <span className="text-[11px] font-mono font-bold text-slate-200">
                          {stat.precision !== null ? `${precPct}%` : 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-[#182035] h-1.5 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-cyan-400 rounded-full"
                            style={{ width: `${recPct}%` }}
                          />
                        </div>
                        <span className="text-[11px] font-mono font-bold text-slate-200">
                          {stat.recall !== null ? `${recPct}%` : 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-mono font-bold text-[11px] text-purple-400">
                      {stat.f1 !== null ? `${f1Pct}%` : 'N/A'}
                    </td>
                    <td className="px-5 py-3.5 text-center font-mono text-[11px] text-emerald-400 font-bold">
                      {stat.tp}
                    </td>
                    <td className="px-5 py-3.5 text-center font-mono text-[11px] text-amber-400 font-bold">
                      {stat.fp}
                    </td>
                    <td className="px-5 py-3.5 text-center font-mono text-[11px] text-rose-400 font-bold">
                      {stat.fn}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Methodology Note */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-xl p-4 text-[11px] text-slate-400 leading-relaxed">
        <strong className="text-white">Ground Truth Standard:</strong> Hand-annotated ground-truth labels across both the primary synthetic dataset and a separate, uncalibrated holdout set (<code className="text-cyan-300 font-mono">data/holdout/labels.csv</code>). Column-level evaluation unit.
      </div>
    </div>
  );
}
