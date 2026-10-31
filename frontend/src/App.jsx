import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import MetadataModal from './components/MetadataModal';
import DashboardPage from './pages/DashboardPage';
import ScanPage from './pages/ScanPage';
import EvidencePage from './pages/EvidencePage';
import GapsPage from './pages/GapsPage';
import AccuracyPage from './pages/AccuracyPage';
import RulesPage from './pages/RulesPage';
import DemosPage from './pages/DemosPage';
import AboutPage from './pages/AboutPage';

export default function App() {
  const navigate = useNavigate();
  const [scanResult, setScanResult] = useState(null);
  const [hasCustomData, setHasCustomData] = useState(false);
  const [globalSearch, setGlobalSearch] = useState('');
  const [editingItem, setEditingItem] = useState(null);

  // Auto-populate with standard synthetic demo data on first load
  useEffect(() => {
    loadDemoScan();
  }, []);

  const loadDemoScan = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${apiBase}/api/scan-demo`, { method: 'POST' });
      const data = await res.json();
      setScanResult(data);
      setHasCustomData(false);
    } catch (err) {
      console.warn('Initial demo scan load error:', err);
    }
  };

  const handleScanComplete = (data, isCustom = false) => {
    setScanResult(data);
    setHasCustomData(isCustom);
    navigate('/evidence');
  };

  const handleMetadataUpdated = (newData) => {
    setScanResult(newData);
  };

  const gapCount = scanResult?.summary?.gap_count || 0;

  return (
    <div className="min-h-screen bg-[#0b0d12] text-slate-200 font-sans selection:bg-amber-400/20 selection:text-amber-200">
      {/* Left Sidebar */}
      <Sidebar
        hasCustomData={hasCustomData}
        onReloadDemo={loadDemoScan}
        gapCount={gapCount}
      />

      {/* Main Content Area */}
      <div className="pl-60 min-h-screen flex flex-col">
        {/* Sticky Top Header */}
        <Header
          searchQuery={globalSearch}
          onSearchChange={setGlobalSearch}
          gapCount={gapCount}
        />

        {/* Dynamic Page Router */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={
              <DashboardPage
                data={scanResult}
                onOpenMetadataModal={(item) => setEditingItem(item)}
              />
            } />
            <Route path="/scan" element={
              <ScanPage
                onScanComplete={(data, isCustom) => handleScanComplete(data, isCustom)}
              />
            } />
            <Route path="/evidence" element={
              <EvidencePage
                data={scanResult}
                onLoadDemo={loadDemoScan}
                onOpenMetadataModal={(item) => setEditingItem(item)}
              />
            } />
            <Route path="/gaps" element={
              <GapsPage
                data={scanResult}
                onLoadDemo={loadDemoScan}
                onOpenMetadataModal={(item) => setEditingItem(item)}
              />
            } />
            <Route path="/accuracy" element={<AccuracyPage />} />
            <Route path="/rules" element={<RulesPage />} />
            <Route path="/demos" element={<DemosPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>

      {/* Interactive Metadata Remediation Modal */}
      {editingItem && (
        <MetadataModal
          item={editingItem}
          onClose={() => setEditingItem(null)}
          onUpdated={handleMetadataUpdated}
        />
      )}
    </div>
  );
}
