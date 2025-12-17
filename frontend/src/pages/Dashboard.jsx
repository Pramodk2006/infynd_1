import React, { useState, useEffect } from 'react';
import { Building2, Sparkles } from 'lucide-react';
import CompanyList from '../components/CompanyList';
import { companyAPI } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({ companies: 0, sources: 0, types: 4 });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const companies = await companyAPI.getAll();
      const totalSources = companies.reduce((sum, c) => sum + (c.totalSources || 0), 0);
      setStats({
        companies: companies.length,
        sources: totalSources,
        types: 4
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Building2 className="mr-3 text-blue-600" size={36} />
              Company Dashboard
            </h1>
            <p className="text-gray-600 mt-2">
              Manage and view all extracted company data in one place
            </p>
          </div>
          <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg">
            <Sparkles size={18} />
            <span className="text-sm font-medium">Stage 1: Data Extraction Complete</span>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 mb-8 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold mb-1">{stats.companies}</div>
            <div className="text-blue-100">Total Companies</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold mb-1">{stats.sources}</div>
            <div className="text-blue-100">Total Sources</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold mb-1">{stats.types}</div>
            <div className="text-blue-100">Source Types</div>
          </div>
        </div>
      </div>

      <CompanyList />
    </div>
  );
};

export default Dashboard;
