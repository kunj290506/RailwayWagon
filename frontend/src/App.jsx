import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProLanding from './pages/ProLanding';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import FrameComparison from './components/FrameComparison';
import SimulatedLiveDashboard from './pages/SimulatedLiveDashboard';
import HistoryPage from './pages/History';
import BatchProcess from './pages/BatchProcess';
import './styles/design-system.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<ProLanding />} />

        {/* Dashboard with nested routes */}
        <Route path="/dashboard" element={<Dashboard />}>
          <Route index element={<UploadPage />} />
          <Route path="results" element={<SimulatedLiveDashboard />} />
          <Route path="comparison" element={<FrameComparison />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="batch" element={<BatchProcess />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
