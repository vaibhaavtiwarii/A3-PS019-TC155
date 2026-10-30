import React, { useState } from 'react';
import {
  AlertTriangle, CheckCircle2, XCircle, FileWarning,
  Download, Database, ShieldAlert, Check, Sparkles,
  ArrowRight, Shield, AlertOctagon, HelpCircle
} from 'lucide-react';

export default function GapsPage({ data, onNavigateToScan, onLoadDemo, onOpenMetadataModal }) {
  const [activeTab, setActiveTab] = useState('cards'); // 'cards' or 'matrix'

  if (!data) return null;

  const { findings, gap_tally, orphaned_metadata, summary } = data;
  const gapFindings = findings.filter((f) => f.gaps && f.gaps.length > 0);
  const severity = summary.severity || { critical: 0, high: gapFindings.length, medium: 0 };

  const downloadMarkdownReport = () => {
    let md = `# Infynex Privacy Evidence Gap Report\n\n`;
    md += `*Team Infynex | AIORI-3 (PS-019)*\n`;
    md += `*Technical evidence for human review. Does not constitute legal compliance determination.*\n\n`;
    md += `## Summary\n`;
    md += `- **Flagged candidate fields:** ${findings.length}\n`;
    md += `- **Fields with missing metadata/evidence:** ${gapFindings.length}\n`;
    md += `- **Orphaned metadata entries:** ${orphaned_metadata.length}\n\n`;

    md += `## Gap Breakdown Tally\n`;
    Object.entries(gap_tally).forEach(([k, v]) => {
      md += `- **${k}**: ${v}\n`;
    });
    md += `\n`;

    md += `## Missing Metadata Audit Details\n\n`;
    md += `| Source | Table | Column | Class | Missing Items |\n`;
    md += `|---|---|---|---|---|\n`;
    gapFindings.forEach((f) => {
      md += `| ${f.source} | ${f.table} | ${f.column} | ${f.cls} | ${f.gaps.join(', ')} |\n`;
    });
    md += `\n`;

    if (orphaned_metadata.length > 0) {
      md += `## Orphaned Declared Metadata\n\n`;
      orphaned_metadata.forEach((k) => {
        md += `- \`${k}\`\n`;
      });
    }

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'infynex_privacy_gap_report.md';
    a.click();
  };

  return (
    <div className="space-y-7 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[10px] font-mono uppercase tracking-wider mb-1.5">
            <Sparkles className="w-3 h-3" />
            Infynex Verification Radar
          </div>
          <h1 className="text-xl font-bold font-display text-white tracking-tight">
            Missing-Metadata & Evidence Gap Audit
          </h1>
          <p className="text-slate-400 mt-0.5 text-xs">
            Auditing candidate fields against declared purpose, retention schedules, and verification checks.
          </p>
        </div>
        <button
          onClick={downloadMarkdownReport}
          className="flex items-center gap-1.5 px-3 py-1 bg-amber-500 hover:bg-amber-400 text-[#07080a] font-bold text-xs rounded-lg shadow-sm transition-all font-display"
        >
          <Download className="w-3 h-3" />
          Export Gap Report (.md)
        </button>
      </div>

      {/* Top 3 Gap Severity Metric Cards (from PriVista Screenshot 5) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Critical Gaps */}
        <div className="bg-[#0c101d] border border-rose-500/30 p-5 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400">Critical Gaps</span>
            <div className="text-3xl font-extrabold text-rose-400 font-mono mt-1">{severity.critical}</div>
            <span className="text-[10px] text-slate-500 mt-0.5 block">Government / Identity identifiers</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <AlertOctagon className="w-6 h-6" />
          </div>
        </div>

        {/* High Gaps */}
        <div className="bg-[#0c101d] border border-amber-500/30 p-5 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">High Gaps</span>
            <div className="text-3xl font-extrabold text-amber-400 font-mono mt-1">{severity.high}</div>
            <span className="text-[10px] text-slate-500 mt-0.5 block">Purpose or retention missing</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        {/* Medium Gaps */}
        <div className="bg-[#0c101d] border border-[#182035] p-5 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">Medium Gaps</span>
            <div className="text-3xl font-extrabold text-cyan-400 font-mono mt-1">{severity.medium}</div>
            <span className="text-[10px] text-slate-500 mt-0.5 block">Advisory checklist attributes</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <HelpCircle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* View Switcher: Interactive Remediation Cards vs Full Compliance Matrix */}
      <div className="flex gap-2.5 border-b border-[#182035] pb-3">
        <button
          onClick={() => setActiveTab('cards')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'cards'
              ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-[#070a12] shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-[#131d33]'
          }`}
        >
          Remediation Cards ({gapFindings.length})
        </button>
        <button
          onClick={() => setActiveTab('matrix')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'matrix'
              ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-[#070a12] shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-[#131d33]'
          }`}
        >
          Checklist Compliance Matrix
        </button>
      </div>

      {/* TAB 1: Remediation Cards (PriVista Screenshot 5 Feature) */}
      {activeTab === 'cards' && (
        <div className="space-y-4">
          {gapFindings.length > 0 ? (
            gapFindings.map((f, i) => (
              <div
                key={i}
                className="bg-[#0c101d] border border-[#182035] rounded-2xl p-5 space-y-4 shadow-xl hover:border-[#223050] transition-all"
              >
                {/* Card Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-white text-sm font-mono">{f.column}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${f.cls === 'GOVT_ID' ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30' : 'bg-amber-500/10 text-amber-300 border border-amber-500/30'}`}>
                        {f.tier || 'High tier'}
                      </span>
                      <span className="text-slate-400 text-xs font-mono">
                        {f.cls} · {Math.round(f.confidence * 100)}% conf
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                      {f.source} {f.table !== '-' && `· ${f.table}`}
                    </div>
                  </div>

                  <button
                    onClick={() => onOpenMetadataModal(f)}
                    className="self-start sm:self-center px-3.5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-[#070a12] shadow-md shadow-emerald-500/15 transition-all flex items-center gap-1.5 active:scale-95"
                  >
                    <span>Review & Add Metadata</span>
                    <ArrowRight className="w-3.5 h-3.5 stroke-[2.5]" />
                  </button>
                </div>

                {/* 3 Detail Columns inside Card */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 text-xs pt-1">
                  {/* Missing Attributes */}
                  <div className="p-3 bg-[#070a12] rounded-xl border border-[#182035]">
                    <span className="text-[10px] text-slate-500 font-bold uppercase block mb-1.5">
                      Missing Checklist Attributes
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {f.gaps.map((g, gIdx) => (
                        <span key={gIdx} className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/10 text-rose-300 border border-rose-500/20">
                          ✗ {g.replace('MISSING_', '').toLowerCase()}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Currently Declared */}
                  <div className="p-3 bg-[#070a12] rounded-xl border border-[#182035]">
                    <span className="text-[10px] text-slate-500 font-bold uppercase block mb-1.5">
                      Currently Declared
                    </span>
                    <div className="space-y-0.5 text-[11px] font-mono text-slate-300">
                      <div>Purpose: <span className="text-slate-400">{f.purpose || '—'}</span></div>
                      <div>Retention: <span className="text-slate-400">{f.retention || '—'}</span></div>
                      <div>Owner: <span className="text-slate-400">{f.owner || '—'}</span></div>
                    </div>
                  </div>

                  {/* Suggested Next Step */}
                  <div className="p-3 bg-[#070a12] rounded-xl border border-[#182035]">
                    <span className="text-[10px] text-slate-500 font-bold uppercase block mb-1.5">
                      Suggested Next Step
                    </span>
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      {f.suggested_next_step}
                    </p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-emerald-400 text-xs bg-[#0c101d] rounded-2xl border border-emerald-500/20">
              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-400" />
              All candidate personal-data fields have complete purpose and retention documentation!
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Full Checklist Compliance Matrix */}
      {activeTab === 'matrix' && (
        <div className="bg-[#0c101d] border border-[#182035] rounded-2xl overflow-hidden shadow-2xl">
          <div className="p-4 border-b border-[#182035] bg-[#090d16]">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Checklist Compliance Matrix
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Comprehensive verification audit per candidate field.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#070a12] text-slate-400 text-[11px] uppercase tracking-wider border-b border-[#182035]">
                  <th className="px-5 py-3 font-bold">Field</th>
                  <th className="px-5 py-3 font-bold">Class</th>
                  <th className="px-5 py-3 font-bold text-center">Declared Purpose</th>
                  <th className="px-5 py-3 font-bold text-center">Retention Schedule</th>
                  <th className="px-5 py-3 font-bold text-center">Data Owner</th>
                  <th className="px-5 py-3 font-bold text-center">Value Verification</th>
                  <th className="px-5 py-3 font-bold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#182035]">
                {findings.map((f, i) => {
                  const getCheck = (itemKey) => f.checklist?.find((c) => c.item === itemKey);
                  const purposeCheck = getCheck('purpose');
                  const retentionCheck = getCheck('retention');
                  const ownerCheck = getCheck('owner');
                  const valCheck = getCheck('value_check');

                  return (
                    <tr key={i} className="hover:bg-[#131d33]/50 transition-colors">
                      <td className="px-5 py-3">
                        <div className="font-bold text-white">{f.column}</div>
                        <div className="text-[11px] text-slate-500 font-mono">{f.source}</div>
                      </td>
                      <td className="px-5 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                          {f.cls}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-center">
                        {purposeCheck?.present ? (
                          <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                        ) : (
                          <span className="text-rose-400 font-bold text-[10px] font-mono bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                            MISSING
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3 text-center">
                        {retentionCheck?.present ? (
                          <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                        ) : (
                          <span className="text-rose-400 font-bold text-[10px] font-mono bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                            MISSING
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3 text-center">
                        {ownerCheck?.present ? (
                          <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                        ) : (
                          <span className="text-amber-400 font-bold text-[10px] font-mono bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                            MISSING
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3 text-center">
                        {valCheck?.present ? (
                          <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                        ) : (
                          <span className="text-slate-500 text-[10px] font-mono">
                            {valCheck?.required ? 'FAIL' : '—'}
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3">
                        <button
                          onClick={() => onOpenMetadataModal(f)}
                          className="px-2.5 py-1 rounded-lg text-[10px] font-bold font-mono bg-[#131d33] hover:bg-emerald-500 hover:text-[#070a12] text-slate-300 border border-[#1f2c4a] transition-all"
                        >
                          {f.gaps.length > 0 ? 'Fix Gap' : 'Edit'}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Orphaned Metadata */}
      {orphaned_metadata && orphaned_metadata.length > 0 && (
        <div className="bg-[#0c101d] border border-[#182035] rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-1.5">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-bold text-white">Orphaned Declared Metadata</h3>
          </div>
          <p className="text-slate-400 text-xs mb-3">
            Policy definitions in <code className="text-cyan-300 font-mono">config/metadata.yaml</code> where no corresponding personal-data field was detected:
          </p>
          <div className="flex flex-wrap gap-2">
            {orphaned_metadata.map((key, i) => (
              <span key={i} className="px-3 py-1 bg-[#070a12] border border-[#182035] text-slate-300 font-mono text-[11px] rounded-lg">
                {key}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
