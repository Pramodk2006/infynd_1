import React from 'react';
import { BrowserRouter as Router, Routes, Route, useParams } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CompanyDetail from './pages/CompanyDetail';
import NewExtraction from './pages/NewExtraction';
import BatchExtraction from './pages/BatchExtraction';
import ClassificationComparison from './components/ClassificationComparison';
import EnhancedSummaryCard from './components/EnhancedSummaryCard';
import Summaries from './pages/Summaries';
import './App.css';

// Wrapper component to get params
const ComparisonWrapper = () => {
  const { companyName } = useParams();
  return <ClassificationComparison companyName={companyName} />;
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/company/:companyName" element={<CompanyDetail />} />
            <Route path="/company/:companyName/enhanced" element={<EnhancedSummaryCard />} />
            <Route path="/summaries" element={<Summaries />} />
            <Route path="/extract" element={<NewExtraction />} />
            <Route path="/batch" element={<BatchExtraction />} />
            <Route path="/compare/:companyName" element={<ComparisonWrapper />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
