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

  const StatCard = ({ label, value, description, icon: Icon, colorClass }) => (
    <div className="bg-white dark:bg-infynd-card-dark rounded-xl p-6 shadow-bento hover:shadow-bento-hover transition-all duration-300 border border-slate-100 dark:border-slate-700 group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">{label}</p>
          <h3 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">{value}</h3>
          <p className="text-xs text-slate-400 dark:text-slate-500">{description}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClass} bg-opacity-10 group-hover:scale-110 transition-transform duration-300`}>
          <Icon className={colorClass.replace('bg-', 'text-')} size={24} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center tracking-tight">
            <Building2 className="mr-3 text-primary-600 dark:text-primary-400" size={32} />
            Company Dashboard
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2 text-lg">
            Overview of your data extraction workflow
          </p>
        </div>
        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-infynd-success/10 text-infynd-success rounded-full border border-infynd-success/20">
          <Sparkles size={16} />
          <span className="text-sm font-semibold">System Operational</span>
        </div>
      </div>

      {/* Stats Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          label="Total Companies"
          value={stats.companies}
          description="Active entities in database"
          icon={Building2}
          colorClass="bg-blue-600 text-blue-600"
        />
        <StatCard
          label="Total Sources"
          value={stats.sources}
          description="Documents & URLs processed"
          icon={Sparkles}
          colorClass="bg-purple-600 text-purple-600"
        />
        <StatCard
          label="Source Types"
          value={stats.types}
          description="Supported ingestion formats"
          icon={Building2} // You might want a different icon here
          colorClass="bg-emerald-500 text-emerald-500"
        />
      </div>

      {/* Main Content Area */}
      <div className="bg-slate-50 dark:bg-slate-900/50 rounded-2xl">
        <CompanyList />
      </div>
    </div>
  );
};

export default Dashboard;
