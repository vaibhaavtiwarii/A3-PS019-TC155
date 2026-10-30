import React, { useState } from 'react';
import {
  ShieldAlert, Database, FileText, Download, CheckCircle2,
  XCircle, Filter, Search, Zap, AlertTriangle, ChevronDown, ChevronRight,
  Sparkles, RefreshCw
} from 'lucide-react';

export default function EvidencePage({ data, onNavigateToScan, onLoadDemo, onOpenMetadataModal }) {
  const [filterClass, setFilterClass] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedRow, setExpandedRow] = useState(null);

  if (!data) {
    return (
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl p-12 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mx-auto">
          <Database className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-white">No Scan Results Loaded Yet</h3>
        <p className="text-slate-400 text-xs max-w-md mx-auto">
          Load the built-in synthetic test dataset or scan custom files to generate the technical evidence inventory.
        </p>
        <div className="flex justify-center gap-3 pt-2">
          <button
            onClick={onLoadDemo}
            className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-[#070a12] font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition-all"
          >
            Load Synthetic Demo
          </button>
          <button
            onClick={onNavigateToScan}
            className="px-4 py-2 bg-[#131d33] hover:bg-[#182542] text-slate-300 font-semibold text-xs rounded-xl border border-slate-700/60 transition-all"
          >
            Upload Custom Files
          </button>
        </div>
      </div>
    );
  }

  const { summary, findings, review } = data;

  const filteredFindings = findings.filter((f) => {
    const matchesClass = filterClass === 'ALL' || f.cls === filterClass;
    const matchesSearch =
      f.column.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.table.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesClass && matchesSearch;
  });

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'infynex_privacy_evidence_inventory.json';
    a.click();
  };

  const exportCSV = () => {
    const headers = [
      'source', 'table', 'column', 'class', 'confidence',
      'purpose', 'retention', 'owner', 'gaps', 'status'
    ];
    const rows = findings.map((f) => [
      f.source,
      f.table,
      f.column,
      f.cls,
      f.confidence,
      `"${f.purpose || ''}"`,
      `"${f.retention || ''}"`,
      `"${f.owner || ''}"`,
      `"${f.gaps.join(';')}"`,
      `"${f.review_status}"`
    ]);
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'infynex_privacy_evidence_inventory.csv';
    a.click();
  };

  return (
    <div className="space-y-7 animate-in fade-in duration-500">
      {/* Header with Export */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[10px] font-mono uppercase tracking-wider mb-1.5">
            <Sparkles className="w-3 h-3" />
            Privexis Registry
          </div>
          <h1 className="text-xl font-bold font-display text-white tracking-tight">
            Privacy Evidence Inventory
          </h1>
          <p className="text-slate-400 mt-0.5 text-xs">
            Discovered candidate personal-data fields mapped to declared business purposes and retention schedules.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={exportCSV}
            className="flex items-center gap-1.5 px-3 py-1 bg-[#14171f] hover:bg-[#1c212c] text-slate-300 text-xs font-mono font-medium rounded-lg border border-[#232936] transition-all"
          >
            <Download className="w-3 h-3 text-amber-400" />
            Export CSV
          </button>
          <button
            onClick={exportJSON}
            className="flex items-center gap-1.5 px-3 py-1 bg-[#14171f] hover:bg-[#1c212c] text-slate-300 text-xs font-mono font-medium rounded-lg border border-[#232936] transition-all"
          >
            <Download className="w-3 h-3 text-amber-400" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="text-slate-500 text-[11px] font-bold uppercase tracking-wider">Total Columns</div>
          <div className="text-2xl font-extrabold text-white mt-1 font-mono">{summary.total_columns}</div>
          <div className="text-[11px] text-slate-500 mt-1">{summary.files_scanned} files inspected</div>
        </div>

        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl relative overflow-hidden group hover:border-emerald-500/40 transition-all">
          <div className="text-slate-500 text-[11px] font-bold uppercase tracking-wider">Candidate PII Fields</div>
          <div className="text-2xl font-extrabold text-emerald-400 mt-1 font-mono">{summary.pii_detected}</div>
          <div className="text-[11px] text-slate-500 mt-1">Detected across 5 classes</div>
        </div>

        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl relative overflow-hidden group hover:border-amber-500/40 transition-all">
          <div className="text-slate-500 text-[11px] font-bold uppercase tracking-wider">Evidence Gaps</div>
          <div className="text-2xl font-extrabold text-amber-400 mt-1 font-mono">{summary.gap_count}</div>
          <div className="text-[11px] text-slate-500 mt-1">Missing purpose / retention</div>
        </div>

        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl relative overflow-hidden group hover:border-cyan-500/40 transition-all">
          <div className="text-slate-500 text-[11px] font-bold uppercase tracking-wider">Execution Time</div>
          <div className="text-2xl font-extrabold text-cyan-400 mt-1 font-mono">{summary.execution_time}s</div>
          <div className="text-[11px] text-slate-500 mt-1">Reservoir sample (k=50)</div>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-[#0c101d] p-3.5 rounded-xl border border-[#182035]">
        <div className="flex flex-wrap gap-1.5">
          {['ALL', 'NAME', 'EMAIL', 'PHONE', 'GOVT_ID', 'DOB'].map((cls) => (
            <button
              key={cls}
              onClick={() => setFilterClass(cls)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filterClass === cls
                  ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-[#070a12] font-bold shadow-md shadow-emerald-500/20'
                  : 'bg-[#131d33] text-slate-400 hover:text-white hover:bg-[#192744]'
              }`}
            >
              {cls}
            </button>
          ))}
        </div>

        <div className="relative w-full md:w-64">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search column or source..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#070a12] border border-[#182035] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/60"
          />
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#070a12] text-slate-400 text-[11px] uppercase tracking-wider border-b border-[#182035]">
                <th className="px-5 py-3.5 font-bold">Column & Location</th>
                <th className="px-5 py-3.5 font-bold">Class & Tier</th>
                <th className="px-5 py-3.5 font-bold">Confidence</th>
                <th className="px-5 py-3.5 font-bold">Declared Purpose</th>
                <th className="px-5 py-3.5 font-bold">Retention</th>
                <th className="px-5 py-3.5 font-bold">Review Status</th>
                <th className="px-5 py-3.5 font-bold text-center">Action</th>
                <th className="px-5 py-3.5 font-bold text-center">Detail</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#182035]">
              {filteredFindings.map((f, i) => {
                const isExpanded = expandedRow === i;
                const hasGaps = f.gaps.length > 0;
                return (
                  <React.Fragment key={i}>
                    <tr
                      onClick={() => setExpandedRow(isExpanded ? null : i)}
                      className="hover:bg-[#131d33]/50 cursor-pointer transition-colors"
                    >
                      <td className="px-5 py-3.5">
                        <div className="font-bold text-white text-xs">{f.column}</div>
                        <div className="text-[11px] text-slate-500 font-mono">
                          {f.source} {f.table !== '-' && `→ ${f.table}`}
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-1.5">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                            {f.cls}
                          </span>
                          <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono ${f.cls === 'GOVT_ID' ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20' : 'bg-slate-800 text-slate-400'}`}>
                            {f.tier || 'Tier 2'}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-[#182035] h-1.5 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full"
                              style={{ width: `${Math.round(f.confidence * 100)}%` }}
                            />
                          </div>
                          <span className="text-[11px] font-mono font-bold text-slate-300">
                            {Math.round(f.confidence * 100)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        {f.purpose ? (
                          <span className="text-slate-300">{f.purpose}</span>
                        ) : (
                          <span className="text-amber-400 font-medium bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 text-[10px]">
                            Missing
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3.5">
                        {f.retention ? (
                          <span className="text-slate-300">{f.retention}</span>
                        ) : (
                          <span className="text-amber-400 font-medium bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 text-[10px]">
                            Missing
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3.5">
                        {hasGaps ? (
                          <span className="inline-flex items-center gap-1 text-amber-400 font-semibold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded text-[10px]">
                            <AlertTriangle className="w-3 h-3" />
                            Evidence Gap
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px]">
                            <CheckCircle2 className="w-3 h-3" />
                            Candidate Complete
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3.5 text-center" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => onOpenMetadataModal && onOpenMetadataModal(f)}
                          className="px-2.5 py-1 rounded-lg text-[10px] font-bold font-mono bg-[#131d33] hover:bg-emerald-500 hover:text-[#070a12] text-slate-300 border border-[#1f2c4a] transition-all"
                        >
                          {hasGaps ? 'Fix Gap' : 'Edit'}
                        </button>
                      </td>
                      <td className="px-5 py-3.5 text-center text-slate-500">
                        {isExpanded ? <ChevronDown className="w-4 h-4 mx-auto text-emerald-400" /> : <ChevronRight className="w-4 h-4 mx-auto" />}
                      </td>
                    </tr>

                    {/* Expandable Evidence Drawer */}
                    {isExpanded && (
                      <tr className="bg-[#090e1c]">
                        <td colSpan={7} className="px-6 py-4">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-xs">
                            <div>
                              <div className="text-slate-500 text-[10px] font-bold uppercase tracking-wider mb-1">
                                Technical Evidence Log
                              </div>
                              <p className="text-slate-300 bg-[#070a12] p-3 rounded-xl border border-[#182035] font-mono text-[11px] leading-relaxed">
                                {f.evidence}
                              </p>
                              <div className="mt-2 text-[11px] text-slate-400">
                                Name score: <span className="text-emerald-300 font-mono">{f.name_score}</span> | Value score: <span className="text-cyan-300 font-mono">{f.value_score}</span>
                              </div>
                            </div>

                            <div>
                              <div className="text-slate-500 text-[10px] font-bold uppercase tracking-wider mb-1">
                                Masked Value Samples
                              </div>
                              <div className="bg-[#070a12] p-3 rounded-xl border border-[#182035] space-y-1 font-mono text-[11px] text-slate-300">
                                {f.sample_values && f.sample_values.length > 0 ? (
                                  f.sample_values.map((v, idx) => (
                                    <div key={idx} className="text-cyan-300/90">{v}</div>
                                  ))
                                ) : (
                                  <span className="text-slate-500">No samples available</span>
                                )}
                              </div>
                            </div>

                            <div>
                              <div className="text-slate-500 text-[10px] font-bold uppercase tracking-wider mb-1">
                                Checklist Items Breakdown
                              </div>
                              <div className="bg-[#070a12] p-3 rounded-xl border border-[#182035] space-y-1.5">
                                {f.checklist && f.checklist.map((item, idx) => (
                                  <div key={idx} className="flex items-center justify-between text-[11px]">
                                    <span className="text-slate-300">{item.label}</span>
                                    {item.present ? (
                                      <span className="text-emerald-400 flex items-center gap-1 font-medium font-mono text-[10px]">
                                        <CheckCircle2 className="w-3 h-3" /> Present
                                      </span>
                                    ) : (
                                      <span className={`flex items-center gap-1 font-medium font-mono text-[10px] ${item.required ? 'text-amber-400' : 'text-slate-500'}`}>
                                        <XCircle className="w-3 h-3" /> {item.required ? 'Missing' : 'Absent'}
                                      </span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review Section */}
      {review && review.length > 0 && (
        <div className="bg-[#0c101d] border border-[#182035] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-bold text-white">Needs a Closer Look (Below Threshold)</h3>
          </div>
          <p className="text-slate-400 text-xs mb-3">
            Columns displaying partial evidence exceeding the review floor ({0.1}) but falling below the candidate threshold.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {review.map((r, i) => (
              <div key={i} className="p-3 bg-[#070a12] border border-[#182035] rounded-xl text-xs flex justify-between items-center">
                <div>
                  <span className="font-bold text-white">{r.column}</span>
                  <span className="text-slate-500 ml-2 font-mono">({r.source}:{r.table})</span>
                  <p className="text-slate-400 mt-0.5 text-[11px]">{r.evidence}</p>
                </div>
                <span className="px-2 py-0.5 bg-[#182035] text-slate-300 rounded font-mono font-bold text-[11px]">
                  {Math.round(r.confidence * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
