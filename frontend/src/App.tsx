import { Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import TopologyPage from './pages/TopologyPage';
import AssetsPage from './pages/AssetsPage';
import AssetDetailPage from './pages/AssetDetailPage';
import ScansPage from './pages/ScansPage';
import IntelligencePage from './pages/IntelligencePage';
import DriftPage from './pages/DriftPage';
import CredentialsPage from './pages/CredentialsPage';
import ExportsPage from './pages/ExportsPage';

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/topology" element={<TopologyPage />} />
        <Route path="/assets" element={<AssetsPage />} />
        <Route path="/assets/:id" element={<AssetDetailPage />} />
        <Route path="/scans" element={<ScansPage />} />
        <Route path="/intelligence" element={<IntelligencePage />} />
        <Route path="/drift" element={<DriftPage />} />
        <Route path="/credentials" element={<CredentialsPage />} />
        <Route path="/exports" element={<ExportsPage />} />
      </Routes>
    </AppLayout>
  );
}
