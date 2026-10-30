import React from 'react';
import {
  ShieldCheck, AlertOctagon, CheckCircle2,
  FileText, ExternalLink, HelpCircle, Sparkles
} from 'lucide-react';

export default function AboutPage() {
  const requirements = [
    {
      req: 'Support CSV and one SQL database',
      status: 'Implemented',
      detail: 'Read-only connectors for CSV and SQLite with reservoir sampling (50 rows/col).'
    },
    {
      req: 'Identify 5 predefined data classes',
      status: 'Implemented',
      detail: 'NAME, EMAIL, PHONE, GOVT_ID (Aadhaar & PAN), and DOB.'
    },
    {
      req: 'Small manually labelled test set for evaluation',
      status: 'Implemented',
      detail: '22 hand-labelled columns in data/labels.csv and 21 in data/holdout/labels.csv.'
    },
    {
      req: 'Detect candidate personal-data fields using configurable rules',
      status: 'Implemented',
      detail: 'Externalized in config/rules.yaml with column hints, negative blockers, regex, and checksums.'
    },
    {
      req: 'Link discovered fields to purpose and retention metadata',
      status: 'Implemented',
      detail: 'Joined with config/metadata.yaml via source:table:column composite keys.'
    },
    {
      req: 'Flag missing purpose or retention information',
      status: 'Implemented',
      detail: 'Checklist evaluator flags MISSING_PURPOSE, MISSING_RETENTION, MISSING_OWNER.'
    },
    {
      req: 'Report per-class precision and recall',
      status: 'Implemented',
      detail: 'Calculated and displayed per class with TP/FP/FN counts on main and holdout sets.'
    },
    {
      req: 'Clearly distinguish technical evidence from legal interpretation',
      status: 'Enforced',
      detail: 'All outputs labeled Candidate Fields for Human Review. No legal assertions.'
    },
    {
      req: 'No automatic lawful-basis determination or universal data-flow inference',
      status: 'Enforced',
      detail: 'Strict architectural boundary: neither lawful basis nor data-flow inference is performed.'
    }
  ];

  return (
    <div className="space-y-7 animate-in fade-in duration-500 max-w-4xl">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider mb-2">
          <Sparkles className="w-3 h-3" />
          Team Infynex • AIORI-3 (PS-019)
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          System Architecture & Scope Boundaries
        </h1>
        <p className="text-slate-400 mt-1 text-xs leading-relaxed">
          Privexis by Team Infynex addresses Problem Statement PS-019: Personal-Data Discovery and Privacy Evidence Inventory in structured datasets.
        </p>
      </div>

      {/* Scope Disclaimer Callout */}
      <div className="p-5 bg-emerald-950/20 border border-emerald-500/30 rounded-2xl space-y-2">
        <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-wide">
          <AlertOctagon className="w-4 h-4" />
          Technical Evidence vs. Legal Compliance Boundary
        </div>
        <p className="text-slate-300 text-xs leading-relaxed">
          The system produces an objective technical evidence inventory for human review. It does not make legal compliance decisions, does not determine lawful bases, and does not infer inter-system data flows.
        </p>
      </div>

      {/* Requirements Table */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-[#182035] bg-[#090d16]">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">PS-019 Deliverable Coverage</h3>
        </div>

        <div className="divide-y divide-[#182035]">
          {requirements.map((r, i) => (
            <div key={i} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
              <div className="space-y-1 max-w-lg">
                <div className="font-bold text-white text-xs">{r.req}</div>
                <div className="text-slate-400 text-[11px]">{r.detail}</div>
              </div>
              <span className="shrink-0 px-2.5 py-0.5 bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold rounded-md self-start md:self-center font-mono text-[10px]">
                {r.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* References */}
      <div className="bg-[#0c101d] border border-[#182035] rounded-2xl p-5 space-y-3">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Official References & Standards
        </h3>
        <ul className="space-y-2 text-xs text-slate-400">
          <li className="flex items-center gap-2">
            <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
            <a
              href="https://www.meity.gov.in/data-protection-framework"
              target="_blank"
              rel="noreferrer"
              className="text-cyan-400 hover:underline"
            >
              MeitY — Data Protection Framework (Digital Personal Data Protection Act)
            </a>
          </li>
          <li className="flex items-center gap-2">
            <FileText className="w-3.5 h-3.5 text-slate-500" />
            <span>Algorithm R Reservoir Sampling (Vitter, 1985) for O(k) bounded memory scanning</span>
          </li>
          <li className="flex items-center gap-2">
            <FileText className="w-3.5 h-3.5 text-slate-500" />
            <span>Verhoeff Checksum Dihedral Group D5 for Aadhaar identification validation</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
