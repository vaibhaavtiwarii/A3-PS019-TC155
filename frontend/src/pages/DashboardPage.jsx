import React from 'react';
import {
  Database, ShieldCheck, AlertTriangle, CheckCircle2,
  TrendingUp, ArrowRight, Layers, FileText, ChevronRight,
  ExternalLink, Sparkles, Terminal, Activity, Eye
} from 'lucide-react';

const CLASS_COLORS = {
  NAME: '#f59e0b',    // Amber
  EMAIL: '#38bdf8',   // Sky
  PHONE: '#a78bfa',   // Purple
  GOVT_ID: '#f43f5e', // Rose
  DOB: '#10b981',     // Emerald
};

export default function DashboardPage({ data, onNavigate, onOpenMetadataModal }) {
  if (!data) return null;

  const { summary, findings, review } = data;
  const classBreakdown = summary.class_breakdown || {};
  const totalFindings = summary.pii_detected || findings.length || 1;

  // Donut chart computations
  const donutSegments = [];
  let cumulative = 0;
  Object.entries(classBreakdown).forEach(([cls, count]) => {
    const fraction = count / totalFindings;
    const dashLength = fraction * 283;
    const dashOffset = -cumulative * 283;
    donutSegments.push({
      cls,
      count,
      pct: Math.round(fraction * 100),
      color: CLASS_COLORS[cls] || '#94a3b8',
      dashLength,
      dashOffset,
    });
    cumulative += fraction;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#171b23] pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold uppercase">
              Privexis
            </span>
            <span className="text-[10px] font-mono text-slate-500">
              AUDIT RUN // SYNTHETIC TARGET
            </span>
          </div>
          <h1 className="text-xl font-bold font-display text-white tracking-tight">
            Privacy Evidence Command Center
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Technical personal-data discovery & metadata linkage registry. No automated lawful-basis determinations.
          </p>
        </div>

        <button
          onClick={() => onNavigate('scan')}
          className="self-start sm:self-center flex items-center gap-1.5 px-3 py-1.5 bg-[#14171f] hover:bg-amber-500 hover:text-[#07080a] text-slate-300 font-bold text-xs rounded-md border border-[#232936] transition-all font-display"
        >
          <span>Run Custom Scan</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 5 Compact Telemetry Metric Panels */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {/* Metric 1 */}
        <div className="bg-[#0c0e12] border border-[#1a1f29] p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 uppercase tracking-wider">
            <span>Sources</span>
            <Database className="w-3 h-3 text-slate-500" />
          </div>
          <div className="text-2xl font-bold text-white mt-1 font-display">{summary.files_scanned}</div>
          <div className="text-[10px] text-slate-500 font-mono mt-0.5">{summary.total_columns} columns</div>
        </div>

        {/* Metric 2 */}
        <div className="bg-[#0c0e12] border border-[#1a1f29] p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 uppercase tracking-wider">
            <span>PII Candidates</span>
            <Activity className="w-3 h-3 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-1 font-display">{summary.pii_detected}</div>
          <div className="text-[10px] text-slate-500 font-mono mt-0.5">5 Predefined classes</div>
        </div>

        {/* Metric 3 */}
        <div className="bg-[#0c0e12] border border-[#1a1f29] p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 uppercase tracking-wider">
            <span>Documented</span>
            <FileText className="w-3 h-3 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-1 font-display">{summary.metadata_linked}</div>
          <div className="w-full bg-[#171b23] h-1 rounded-full overflow-hidden mt-1.5">
            <div
              className="h-full bg-emerald-400 rounded-full"
              style={{ width: `${summary.evidence_coverage}%` }}
            />
          </div>
        </div>

        {/* Metric 4 */}
        <div className="bg-[#0c0e12] border border-[#1a1f29] p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 uppercase tracking-wider">
            <span>Evidence Gaps</span>
            <AlertTriangle className="w-3 h-3 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400 mt-1 font-display">{summary.gap_count}</div>
          <div className="text-[10px] text-rose-400/80 font-mono mt-0.5">
            {summary.pii_detected > 0 ? Math.round((summary.gap_count / summary.pii_detected) * 100) : 0}% of candidates
          </div>
        </div>

        {/* Metric 5 */}
        <div className="bg-[#0c0e12] border border-[#1a1f29] p-3.5 rounded-lg">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 uppercase tracking-wider">
            <span>Coverage</span>
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-1 font-display">
            {summary.evidence_coverage}%
          </div>
          <div className="text-[10px] text-slate-500 font-mono mt-0.5">
            {summary.metadata_linked}/{summary.pii_detected} mapped
          </div>
        </div>
      </div>

      {/* 2 Middle Data Visualizations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left: Donut Chart */}
        <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-xs font-bold font-display text-white uppercase tracking-wider">
                PII Distribution by Class
              </h3>
              <p className="text-[11px] text-slate-400">Classified candidate personal-data fields</p>
            </div>
            <span className="text-[10px] font-mono font-bold text-slate-300 bg-[#14171f] px-2 py-0.5 rounded border border-[#232936]">
              {totalFindings} TOTAL
            </span>
          </div>

          <div className="flex items-center justify-around py-2">
            <div className="relative w-32 h-32 flex items-center justify-center">
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="transparent" stroke="#171b23" strokeWidth="8" />
                {donutSegments.map((seg, i) => (
                  <circle
                    key={i}
                    cx="50"
                    cy="50"
                    r="45"
                    fill="transparent"
                    stroke={seg.color}
                    strokeWidth="8"
                    strokeDasharray={`${seg.dashLength} 283`}
                    strokeDashoffset={seg.dashOffset}
                  />
                ))}
              </svg>
              <div className="absolute text-center">
                <span className="text-xl font-bold text-white font-display">{totalFindings}</span>
                <span className="text-[8px] text-slate-500 block uppercase font-mono tracking-widest">FIELDS</span>
              </div>
            </div>

            <div className="space-y-1.5 text-xs font-mono">
              {donutSegments.map((seg, i) => (
                <div key={i} className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-sm" style={{ backgroundColor: seg.color }} />
                    <span className="text-slate-300 text-[11px]">{seg.cls}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-white text-[11px]">{seg.count}</span>
                    <span className="text-slate-500 text-[10px] ml-1">({seg.pct}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Trend Chart */}
        <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-xs font-bold font-display text-white uppercase tracking-wider">
                Discovery Growth vs. Open Gaps
              </h3>
              <p className="text-[11px] text-slate-400">Audit trajectory across scanning iterations</p>
            </div>
            <div className="flex items-center gap-3 text-[10px] font-mono">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-sm bg-amber-400" />
                <span className="text-slate-300">Candidates</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-sm bg-rose-400" />
                <span className="text-slate-300">Gaps</span>
              </div>
            </div>
          </div>

          <div className="h-36 w-full pt-2">
            <svg className="w-full h-full overflow-visible" viewBox="0 0 300 100">
              <line x1="0" y1="20" x2="300" y2="20" stroke="#171b23" strokeDasharray="3 3" />
              <line x1="0" y1="50" x2="300" y2="50" stroke="#171b23" strokeDasharray="3 3" />
              <line x1="0" y1="80" x2="300" y2="80" stroke="#171b23" strokeDasharray="3 3" />

              <polyline
                fill="none"
                stroke="#f59e0b"
                strokeWidth="2"
                points="10,75 80,60 160,40 240,30 290,25"
              />
              <circle cx="290" cy="25" r="3" fill="#f59e0b" />

              <polyline
                fill="none"
                stroke="#f43f5e"
                strokeWidth="2"
                strokeDasharray="4 2"
                points="10,85 80,75 160,65 240,60 290,55"
              />
              <circle cx="290" cy="55" r="3" fill="#f43f5e" />
            </svg>
            <div className="flex justify-between text-[9px] text-slate-500 font-mono mt-2">
              <span>Baseline</span>
              <span>Run 2</span>
              <span>Run 3</span>
              <span>Current</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Inventory Table */}
      <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-lg overflow-hidden">
        <div className="p-3.5 border-b border-[#171b23] bg-[#090b0e] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-bold font-display text-white uppercase tracking-wider">
              Discovered Inventory Snapshot
            </h3>
            <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-[#14171f] text-slate-400 font-bold">
              {findings.length}
            </span>
          </div>

          <button
            onClick={() => onNavigate('evidence')}
            className="flex items-center gap-1 text-xs font-bold text-amber-400 hover:text-amber-300 transition-colors font-display"
          >
            <span>Full Inventory Board</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#090b0e] text-slate-400 text-[10px] font-mono uppercase tracking-wider border-b border-[#171b23]">
                <th className="px-4 py-2.5 font-bold">Field</th>
                <th className="px-4 py-2.5 font-bold">Class</th>
                <th className="px-4 py-2.5 font-bold">Source</th>
                <th className="px-4 py-2.5 font-bold">Purpose</th>
                <th className="px-4 py-2.5 font-bold">Retention</th>
                <th className="px-4 py-2.5 font-bold">Status</th>
                <th className="px-4 py-2.5 font-bold text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#171b23]">
              {findings.slice(0, 6).map((f, i) => (
                <tr key={i} className="hover:bg-[#11141a] transition-colors">
                  <td className="px-4 py-2.5 font-mono font-bold text-white text-[11px]">
                    {f.column}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-[#14171f] text-amber-400 border border-[#232936]">
                      {f.cls}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-slate-400 font-mono text-[10px]">
                    {f.source}
                  </td>
                  <td className="px-4 py-2.5 text-slate-300 text-[11px]">
                    {f.purpose || (
                      <span className="text-rose-400 font-mono text-[9px] bg-rose-500/10 px-1 py-0.5 rounded">
                        MISSING
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-slate-300 text-[11px]">
                    {f.retention || (
                      <span className="text-rose-400 font-mono text-[9px] bg-rose-500/10 px-1 py-0.5 rounded">
                        MISSING
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5">
                    {f.gaps.length > 0 ? (
                      <span className="inline-flex items-center gap-1 text-rose-400 text-[10px] font-mono">
                        <AlertTriangle className="w-3 h-3" /> GAP
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-emerald-400 text-[10px] font-mono">
                        <CheckCircle2 className="w-3 h-3" /> OK
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <button
                      onClick={() => onOpenMetadataModal(f)}
                      className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#14171f] hover:bg-amber-500 hover:text-[#07080a] text-slate-300 border border-[#232936] transition-all"
                    >
                      {f.gaps.length > 0 ? 'Fix Gap' : 'Edit'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
