import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CompanyDetail from './pages/CompanyDetail';
import NewExtraction from './pages/NewExtraction';
import BatchExtraction from './pages/BatchExtraction';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/company/:companyName" element={<CompanyDetail />} />
            <Route path="/extract" element={<NewExtraction />} />
            <Route path="/batch" element={<BatchExtraction />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
