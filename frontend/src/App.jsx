import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
  const [activePage, setActivePage] = useState('dashboard');
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
      const res = await axios.post('/api/scan-demo');
      setScanResult(res.data);
      setHasCustomData(false);
    } catch (err) {
      console.warn('Initial demo scan load error:', err);
    }
  };

  const handleScanComplete = (data, isCustom = false) => {
    setScanResult(data);
    setHasCustomData(isCustom);
    setActivePage('evidence');
  };

  const handleMetadataUpdated = (newData) => {
    setScanResult(newData);
  };

  const gapCount = scanResult?.summary?.gap_count || 0;

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-200 font-sans selection:bg-emerald-500/20 selection:text-emerald-300">
      {/* Left Sidebar */}
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        hasCustomData={hasCustomData}
        onReloadDemo={loadDemoScan}
        gapCount={gapCount}
      />

      {/* Main Content Area */}
      <div className="pl-60 min-h-screen flex flex-col">
        {/* Sticky Top Header */}
        <Header
          onStartScan={() => setActivePage('scan')}
          searchQuery={globalSearch}
          onSearchChange={setGlobalSearch}
          gapCount={gapCount}
        />

        {/* Dynamic Page Router */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-6">
          {activePage === 'dashboard' && (
            <DashboardPage
              data={scanResult}
              onNavigate={setActivePage}
              onOpenMetadataModal={(item) => setEditingItem(item)}
            />
          )}

          {activePage === 'scan' && (
            <ScanPage
              onScanComplete={(data, isCustom) => handleScanComplete(data, isCustom)}
            />
          )}

          {activePage === 'evidence' && (
            <EvidencePage
              data={scanResult}
              onNavigateToScan={() => setActivePage('scan')}
              onLoadDemo={loadDemoScan}
              onOpenMetadataModal={(item) => setEditingItem(item)}
            />
          )}

          {activePage === 'gaps' && (
            <GapsPage
              data={scanResult}
              onNavigateToScan={() => setActivePage('scan')}
              onLoadDemo={loadDemoScan}
              onOpenMetadataModal={(item) => setEditingItem(item)}
            />
          )}

          {activePage === 'accuracy' && <AccuracyPage />}
          {activePage === 'rules' && <RulesPage />}
          {activePage === 'demos' && <DemosPage />}
          {activePage === 'about' && <AboutPage />}
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
