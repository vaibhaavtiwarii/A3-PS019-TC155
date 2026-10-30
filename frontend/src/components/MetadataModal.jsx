import React, { useState } from 'react';
import axios from 'axios';
import { X, ShieldAlert, Check, Loader2, Sparkles } from 'lucide-react';

const PURPOSE_PRESETS = [
  'Customer identification & KYC',
  'Two-factor authentication (2FA)',
  'Service communication & support',
  'Employment & payroll compliance',
  'Statutory tax compliance'
];

const RETENTION_PRESETS = [
  'Account closure + 1 year',
  'Account closure + 7 years',
  'Statutory requirement (7 years)',
  'Account closure + 180 days',
  'Duration of active employment'
];

export default function MetadataModal({ item, onClose, onUpdated }) {
  const [purpose, setPurpose] = useState(item.purpose || '');
  const [retention, setRetention] = useState(item.retention || '');
  const [owner, setOwner] = useState(item.owner || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await axios.post('/api/metadata/update', {
        source: item.source,
        table: item.table || '-',
        column: item.column,
        purpose,
        retention,
        owner,
      });
      onUpdated(res.data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to update metadata');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-xl w-full max-w-lg shadow-2xl overflow-hidden font-sans">
        {/* Modal Header */}
        <div className="p-4 border-b border-[#171b23] flex items-center justify-between bg-[#07080a]">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <ShieldAlert className="w-3.5 h-3.5" />
            </div>
            <div>
              <h3 className="text-xs font-bold font-display text-white">Review & Link Privacy Metadata</h3>
              <p className="text-[10px] text-slate-400 font-mono">
                {item.source} {item.table !== '-' && `→ ${item.table}`} → <span className="text-amber-400 font-bold">{item.column}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-500 hover:text-white hover:bg-[#14171f] transition-all"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-3.5 text-xs">
          {error && (
            <div className="p-2.5 bg-red-950/40 border border-red-800/60 rounded-lg text-red-300 text-xs">
              {error}
            </div>
          )}

          {/* Declared Purpose */}
          <div>
            <label className="block text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">
              Declared Business Purpose
            </label>
            <input
              type="text"
              placeholder="e.g. Identity verification for KYC onboarding"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              className="w-full bg-[#07080a] border border-[#171b23] rounded-lg px-2.5 py-1.5 text-white placeholder-slate-600 focus:outline-none focus:border-amber-500/60 font-sans text-xs"
              required
            />
            <div className="flex flex-wrap gap-1 mt-1">
              {PURPOSE_PRESETS.map((p, i) => (
                <button
                  type="button"
                  key={i}
                  onClick={() => setPurpose(p)}
                  className="text-[9px] text-slate-400 bg-[#07080a] hover:text-amber-300 hover:border-amber-500/40 border border-[#171b23] px-1.5 py-0.5 rounded transition-all font-mono"
                >
                  + {p}
                </button>
              ))}
            </div>
          </div>

          {/* Retention Schedule */}
          <div>
            <label className="block text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">
              Retention Schedule Period
            </label>
            <input
              type="text"
              placeholder="e.g. Account closure + 7 years (statutory)"
              value={retention}
              onChange={(e) => setRetention(e.target.value)}
              className="w-full bg-[#07080a] border border-[#171b23] rounded-lg px-2.5 py-1.5 text-white placeholder-slate-600 focus:outline-none focus:border-amber-500/60 font-sans text-xs"
              required
            />
            <div className="flex flex-wrap gap-1 mt-1">
              {RETENTION_PRESETS.map((r, i) => (
                <button
                  type="button"
                  key={i}
                  onClick={() => setRetention(r)}
                  className="text-[9px] text-slate-400 bg-[#07080a] hover:text-amber-300 hover:border-amber-500/40 border border-[#171b23] px-1.5 py-0.5 rounded transition-all font-mono"
                >
                  + {r}
                </button>
              ))}
            </div>
          </div>

          {/* Data Owner */}
          <div>
            <label className="block text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">
              Responsible Data Owner / Department
            </label>
            <input
              type="text"
              placeholder="e.g. Compliance Team, Security Operations"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              className="w-full bg-[#07080a] border border-[#171b23] rounded-lg px-2.5 py-1.5 text-white placeholder-slate-600 focus:outline-none focus:border-amber-500/60 font-sans text-xs"
            />
          </div>

          {/* Footer Actions */}
          <div className="pt-3 border-t border-[#171b23] flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 bg-[#14171f] hover:bg-[#1a1f29] text-slate-400 hover:text-white font-medium rounded-lg border border-[#232936] transition-all text-xs font-mono"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-1.5 bg-amber-500 hover:bg-amber-400 text-[#07080a] font-bold font-display rounded-lg shadow-sm transition-all flex items-center gap-1.5 text-xs"
            >
              {saving ? <Loader2 className="w-3 h-3 animate-spin text-[#07080a]" /> : <Check className="w-3 h-3 stroke-[3]" />}
              {saving ? 'Updating...' : 'Save & Resolve Gap'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

