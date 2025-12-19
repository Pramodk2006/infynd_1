import React, { useState, useEffect } from 'react';
import { Search, RefreshCw } from 'lucide-react';
import CompanyCard from './CompanyCard';
import { companyAPI } from '../services/api';

const CompanyList = () => {
  const [companies, setCompanies] = useState([]);
  const [filteredCompanies, setFilteredCompanies] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompanies();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = companies.filter((company) =>
        company.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredCompanies(filtered);
    } else {
      setFilteredCompanies(companies);
    }
  }, [searchTerm, companies]);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const data = await companyAPI.getAll();
      setCompanies(data);
      setFilteredCompanies(data);
    } catch (error) {
      console.error('Error loading companies:', error);
      setCompanies([]);
      setFilteredCompanies([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8 flex flex-col md:flex-row items-center gap-4">
        <div className="flex-1 relative w-full">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <input
            type="text"
            placeholder="Search companies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent shadow-sm text-slate-900 dark:text-white placeholder-slate-400 transition-all duration-200"
          />
        </div>
        <button
          onClick={loadCompanies}
          className="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 active:bg-primary-800 transition-all duration-200 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          <span className="font-medium">Refresh Data</span>
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-primary-600">
              <div className="h-2 w-2 bg-primary-600 rounded-full"></div>
            </div>
          </div>
        </div>
      ) : filteredCompanies.length === 0 ? (
        <div className="text-center py-24 bg-white dark:bg-infynd-card-dark rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-700">
          <div className="mx-auto h-24 w-24 bg-slate-50 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
            <RefreshCw size={32} className="text-slate-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">No companies found</h3>
          <p className="text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            {searchTerm ? `We couldn't find any companies matching "${searchTerm}"` : 'Start your journey by creating a new data extraction!'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCompanies.map((company, index) => (
            <CompanyCard key={index} company={company} />
          ))}
        </div>
      )}

      {!loading && filteredCompanies.length > 0 && (
        <div className="mt-8 text-center">
          <span className="inline-flex items-center px-4 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-sm font-medium text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
            Showing {filteredCompanies.length} of {companies.length} entries
          </span>
        </div>
      )}
    </div>
  );
};

export default CompanyList;
