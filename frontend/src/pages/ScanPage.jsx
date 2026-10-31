import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload, Database, Zap, FileText, CheckCircle2,
  AlertCircle, Loader2, ArrowRight, ShieldCheck, Sparkles, Terminal,
  Check, RefreshCw
} from 'lucide-react';

export default function ScanPage({ onScanComplete }) {
  const navigate = useNavigate();
  const [sourceType, setSourceType] = useState('demo'); // 'demo', 'files'
  const [files, setFiles] = useState([]);
  const [metadataFile, setMetadataFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Console output
  const [consoleLogs, setConsoleLogs] = useState([
    '// Privexis Discovery Engine v2.4 initialized',
    '// Synthetic data connectors ready for CSV & SQLite',
    '// Select a source to launch an audit scan...'
  ]);
  const [scanProgress, setScanProgress] = useState(0);

  const fileInputRef = useRef(null);
  const metaInputRef = useRef(null);

  const addLog = (msg) => {
    setConsoleLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  const runScan = async () => {
    setLoading(true);
    setError(null);
    setScanProgress(15);
    setConsoleLogs([
      `[${new Date().toLocaleTimeString()}] Initializing scan job...`,
      `[${new Date().toLocaleTimeString()}] Loading detection rules from config/rules.yaml...`,
    ]);

    try {
      let res;
      if (sourceType === 'demo') {
        setTimeout(() => setScanProgress(45), 100);
        setTimeout(() => addLog('Streaming bounded reservoir samples (k=50) across active tables...'), 150);
        setTimeout(() => setScanProgress(75), 250);
        setTimeout(() => addLog('Applying Verhoeff Dihedral checksum & regex pattern evaluators...'), 300);

        const apiBase = import.meta.env.VITE_API_BASE_URL || '';
        const response = await fetch(`${apiBase}/api/scan-demo`, { method: 'POST' });
        if (!response.ok) throw new Error(await response.text());
        res = await response.json();
      } else {
        if (files.length === 0) {
          setError('Please select at least one file to scan.');
          setLoading(false);
          return;
        }

        const formData = new FormData();
        files.forEach((file) => formData.append('files', file));
        if (metadataFile) {
          formData.append('metadata_file', metadataFile);
        }

        setTimeout(() => setScanProgress(50), 100);
        addLog(`Uploading and inspecting ${files.length} structured file(s)...`);

        const apiBase = import.meta.env.VITE_API_BASE_URL || '';
        const response = await fetch(`${apiBase}/api/scan`, { method: 'POST', body: formData });
        if (!response.ok) throw new Error(await response.text());
        res = await response.json();
      }

      setScanProgress(100);
      addLog(`[COMPLETE] Discovered ${res.findings.length} PII candidate fields in ${res.summary.execution_time}s`);
      addLog(`[LINKER] Joined findings with policy metadata. ${res.summary.gap_count} evidence gaps flagged.`);

      setTimeout(() => {
        onScanComplete(res, sourceType !== 'demo');
      }, 500);
    } catch (err) {
      setError(err.message || 'Scan execution failed');
      addLog(`[FATAL] Scan halted: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-7 animate-in fade-in duration-500">
      {/* Title */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider mb-2">
          <Sparkles className="w-3 h-3" />
          Infynex Discovery Scanner
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          Personal-Data Discovery Scanner
        </h1>
        <p className="text-slate-400 mt-1 text-xs max-w-2xl leading-relaxed">
          Scan structured SQL databases, an uploaded SQLite database, or CSV exports for candidate personal-data fields across the 5 predefined classes.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2.5 p-3.5 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid: Left Setup Options vs Right Execution Console */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: Source Selection and Configuration */}
        <div className="lg:col-span-7 space-y-4">
          {/* Step 1: Select Source Type */}
          <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-lg p-4 space-y-2.5">
            <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">
              1. SELECT DATA SOURCE TARGET
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setSourceType('demo')}
                className={`p-3 rounded-lg border text-left transition-all ${
                  sourceType === 'demo'
                    ? 'bg-[#14171f] border-amber-500/50 text-white'
                    : 'bg-[#07080a] border-[#171b23] text-slate-400 hover:text-white hover:bg-[#101217]'
                }`}
              >
                <Database className="w-3.5 h-3.5 text-amber-400 mb-1.5" />
                <div className="font-display font-bold text-xs">Synthetic Target</div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">SQLite & CSV tables</div>
              </button>

              <button
                type="button"
                onClick={() => setSourceType('files')}
                className={`p-3 rounded-lg border text-left transition-all ${
                  sourceType === 'files'
                    ? 'bg-[#14171f] border-amber-500/50 text-white'
                    : 'bg-[#07080a] border-[#171b23] text-slate-400 hover:text-white hover:bg-[#101217]'
                }`}
              >
                <Upload className="w-3.5 h-3.5 text-amber-400 mb-1.5" />
                <div className="font-display font-bold text-xs">Upload Files</div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">.csv, .sqlite, .db</div>
              </button>
            </div>
          </div>

          {/* Step 2: Specific Configuration Panel */}
          {sourceType === 'files' && (
            <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-lg p-4 space-y-3">
              <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">
                2. UPLOAD STRUCTURED DATASETS
              </span>
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border border-dashed border-[#1f2533] hover:border-amber-500/70 bg-[#07080a] rounded-lg p-5 text-center cursor-pointer transition-all"
              >
                <Upload className="w-6 h-6 text-slate-500 mx-auto mb-1.5" />
                <p className="text-slate-300 text-xs font-medium">Select .csv or .sqlite data files</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".csv,.sqlite,.db,.sqlite3"
                  onChange={(e) => e.target.files && setFiles(Array.from(e.target.files))}
                  className="hidden"
                />
              </div>

              {files.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {files.map((f, i) => (
                    <span key={i} className="px-2 py-0.5 bg-[#14171f] border border-[#232936] rounded text-[11px] text-slate-300 font-mono">
                      {f.name} ({(f.size / 1024).toFixed(1)} KB)
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {sourceType === 'demo' && (
            <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-lg p-4 space-y-2">
              <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">
                2. SYNTHETIC VERIFICATION SUITE
              </span>
              <p className="text-xs text-slate-300 leading-relaxed">
                Applies reservoir sampling to standard synthetic benchmark tables:
              </p>
              <div className="flex flex-wrap gap-1.5 pt-1 font-mono text-xs">
                <span className="px-2 py-0.5 bg-[#07080a] border border-[#171b23] rounded text-amber-300 text-[11px]">
                  onboarding.csv (7 cols)
                </span>
                <span className="px-2 py-0.5 bg-[#07080a] border border-[#171b23] rounded text-amber-300 text-[11px]">
                  users.sqlite (6 cols)
                </span>
                <span className="px-2 py-0.5 bg-[#07080a] border border-[#171b23] rounded text-amber-300 text-[11px]">
                  hard_cases.csv (5 cols)
                </span>
              </div>
            </div>
          )}

          {/* Step 3: Evidence Checklist Flags */}
          <div className="bg-[#0c0e12] border border-[#1a1f29] rounded-lg p-4 space-y-2.5">
            <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">
              3. CHECKLIST VERIFICATION TARGETS
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs font-mono">
              <div className="p-2.5 bg-[#07080a] rounded-lg border border-[#171b23] flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-slate-300 text-[11px]">Purpose</span>
              </div>
              <div className="p-2.5 bg-[#07080a] rounded-lg border border-[#171b23] flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-slate-300 text-[11px]">Retention</span>
              </div>
              <div className="p-2.5 bg-[#07080a] rounded-lg border border-[#171b23] flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-slate-300 text-[11px]">Owner</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Execution Console */}
        <div className="lg:col-span-5 bg-[#0c0e12] border border-[#1a1f29] rounded-lg p-4 space-y-3 sticky top-20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-amber-400" />
              <h3 className="text-xs font-bold font-display text-white uppercase tracking-wider">Telemetry Console</h3>
            </div>
            <span className="text-xs font-mono font-bold text-amber-400">{scanProgress}%</span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-[#171b23] h-1 rounded-full overflow-hidden">
            <div
              className="h-full bg-amber-500 transition-all duration-300 rounded-full"
              style={{ width: `${scanProgress}%` }}
            />
          </div>

          {/* Terminal Screen */}
          <div className="bg-[#07080a] border border-[#171b23] rounded-lg p-3.5 h-60 overflow-y-auto font-mono text-[10px] space-y-1 text-slate-300">
            {consoleLogs.map((log, idx) => (
              <div key={idx} className={log.includes('[SUCCESS]') || log.includes('[COMPLETE]') ? 'text-emerald-400' : log.includes('[ERROR]') ? 'text-rose-400' : log.includes('//') ? 'text-slate-600' : 'text-slate-400'}>
                {log}
              </div>
            ))}
          </div>

          {/* Launch Scan Action */}
          <button
            type="button"
            onClick={runScan}
            disabled={loading}
            className="w-full py-2.5 bg-amber-500 hover:bg-amber-400 disabled:bg-slate-800 disabled:text-slate-500 text-[#07080a] font-bold font-display text-xs rounded-lg shadow-sm transition-all flex items-center justify-center gap-1.5 active:scale-98"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin text-[#07080a]" /> : <Zap className="w-3.5 h-3.5 stroke-[2.5]" />}
            <span>{loading ? 'Processing scan...' : 'Launch Scan Execution'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
