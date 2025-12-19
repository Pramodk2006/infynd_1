import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Clock, CheckCircle, AlertCircle, Loader, Download, Search } from 'lucide-react';
import { format } from 'date-fns';

const Summaries = () => {
  const navigate = useNavigate();
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [stats, setStats] = useState({ ready: 0, preparing: 0, total: 0 });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadSummaries();
    // Only poll if there are preparing items
    const interval = setInterval(() => {
      // We can relax this condition or check local state if needed
      if (stats.preparing > 0) {
        loadSummaries();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [stats.preparing]);

  const loadSummaries = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const [summariesRes, statsRes] = await Promise.all([
        fetch('http://localhost:5000/api/summaries', { signal: controller.signal }),
        fetch('http://localhost:5000/api/cache/stats', { signal: controller.signal })
      ]);

      clearTimeout(timeoutId);

      if (summariesRes.ok && statsRes.ok) {
        const summariesData = await summariesRes.json();
        const statsData = await statsRes.json();

        setSummaries(summariesData.summaries || []);
        setStats({
          ready: statsData.ready || 0,
          preparing: statsData.preparing || 0,
          total: statsData.total_cached || 0
        });
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Error loading summaries:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="text-infynd-success" size={20} />;
      case 'preparing':
        return <Loader className="text-orange-500 animate-spin" size={20} />;
      case 'error':
        return <AlertCircle className="text-infynd-warning" size={20} />;
      default:
        return <Clock className="text-slate-400" size={20} />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'ready': return 'Ready';
      case 'preparing': return 'Preparing...';
      case 'error': return 'Error';
      default: return 'Not Started';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'preparing':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300';
    }
  };

  const filteredSummaries = summaries.filter(s =>
    s.company_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const downloadAllCSV = async () => {
    setDownloading(true);
    try {
      // Get only ready summaries
      const readySummaries = summaries.filter(s => s.status === 'ready');

      if (readySummaries.length === 0) {
        alert('No ready summaries to download');
        return;
      }

      // Fetch all enhanced data
      const allData = await Promise.all(
        readySummaries.map(async (summary) => {
          try {
            const response = await fetch(`http://localhost:5000/api/companies/${summary.company_name}/enhanced`);
            if (response.ok) {
              return await response.json();
            }
            return null;
          } catch (err) {
            console.error(`Error fetching ${summary.company_name}:`, err);
            return null;
          }
        })
      );

      // Filter out null results
      const validData = allData.filter(d => d !== null);

      if (validData.length === 0) {
        alert('Failed to fetch any summary data');
        return;
      }

      // Create CSV with all companies
      const csvRows = [];

      // Header row
      const headers = [
        'Company Name', 'Acronym', 'Domain', 'Domain Status', 'Logo URL',
        'Short Description', 'Long Description',
        'Sector', 'Industry', 'Sub-Industry', 'SIC Code', 'SIC Description',
        'Tags', 'Registration Number', 'VAT Number',
        'Full Address', 'Phone', 'Sales Phone', 'Email', 'All Emails',
        'Other Numbers', 'Hours of Operation', 'HQ Indicator',
        'Certifications', 'Team Members', 'Services',
        'Extraction Timestamp', 'Text Length'
      ];
      csvRows.push(headers.join(','));

      // Data rows
      validData.forEach(data => {
        // Helper to extract value from enhanced data structure
        const getVal = (item) => {
          if (item !== null && typeof item === 'object' && 'value' in item) {
            return item.value;
          }
          return item;
        };

        const escapeCSV = (val) => {
          if (!val || val === '-') return '';
          const str = String(val).replace(/"/g, '""');
          return str.includes(',') || str.includes('\n') || str.includes('"') ? `"${str}"` : str;
        };

        // Extract values handling both flat and enhanced structures
        const company_name = getVal(data.company_name);
        const acronym = getVal(data.acronym);
        const domain = getVal(data.domain);
        const domain_status = getVal(data.domain_status);
        const logo_url = getVal(data.logo_url);
        const short_description = getVal(data.short_description);
        const long_description = getVal(data.long_description);
        const sector = getVal(data.sector);
        const industry = getVal(data.industry);
        const sub_industry = getVal(data.sub_industry);
        const sic_code = getVal(data.sic_code);
        const sic_text = getVal(data.sic_text);
        const tags = getVal(data.tags);
        const company_registration_number = getVal(data.company_registration_number);
        const vat_number = getVal(data.vat_number);
        const full_address = getVal(data.full_address);
        const phone = getVal(data.phone);
        const sales_phone = getVal(data.sales_phone);
        const email = getVal(data.email);
        const all_emails = getVal(data.all_emails);
        const other_numbers = getVal(data.other_numbers);
        const hours_of_operation = getVal(data.hours_of_operation);
        const hq_indicator = getVal(data.hq_indicator);
        const certifications = getVal(data.certifications);
        const people = getVal(data.people);
        const services = getVal(data.services);
        const extraction_timestamp = getVal(data.extraction_timestamp);
        const text_length = getVal(data.text_length);

        const row = [
          escapeCSV(company_name),
          escapeCSV(acronym),
          escapeCSV(domain),
          escapeCSV(domain_status),
          escapeCSV(logo_url),
          escapeCSV(short_description),
          escapeCSV(long_description),
          escapeCSV(sector),
          escapeCSV(industry),
          escapeCSV(sub_industry),
          escapeCSV(sic_code),
          escapeCSV(sic_text),
          escapeCSV(tags?.join('; ')),
          escapeCSV(company_registration_number),
          escapeCSV(vat_number),
          escapeCSV(full_address),
          escapeCSV(phone),
          escapeCSV(sales_phone),
          escapeCSV(email),
          escapeCSV(all_emails?.join('; ')),
          escapeCSV(other_numbers?.join('; ')),
          escapeCSV(hours_of_operation),
          escapeCSV(hq_indicator ? 'Yes' : 'No'),
          escapeCSV(certifications?.join('; ')),
          escapeCSV(people?.filter(p => p.name !== '-').map(p => `${p.name} (${p.title})`).join('; ')),
          escapeCSV(services?.filter(s => s.service !== '-').map(s => `${s.service} [${s.type}]`).join('; ')),
          escapeCSV(new Date(extraction_timestamp).toLocaleString()),
          escapeCSV(text_length + ' characters')
        ];
        csvRows.push(row.join(','));
      });

      // Create and download file
      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);

      link.setAttribute('href', url);
      link.setAttribute('download', `all_company_summaries_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      alert(`Successfully downloaded ${validData.length} company summaries`);
    } catch (error) {
      console.error('Error downloading CSV:', error);
      alert('Failed to download CSV: ' + error.message);
    } finally {
      setDownloading(false);
    }
  };

  const SummaryCard = ({ summary }) => (
    <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento hover:shadow-bento-hover transition-all duration-300 border border-slate-100 dark:border-slate-700 p-5 group flex flex-col justify-between h-full">
      <div>
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg text-primary-600 dark:text-primary-400">
              <FileText size={20} />
            </div>
            <h3 className="font-bold text-slate-800 dark:text-white line-clamp-1">{summary.company_name}</h3>
          </div>
          <div className={`px-2 py-1 rounded text-xs font-semibold flex items-center gap-1 ${getStatusClass(summary.status)}`}>
            {getStatusIcon(summary.status)}
            <span className="hidden sm:inline">{getStatusText(summary.status)}</span>
          </div>
        </div>

        <div className="space-y-2 text-sm text-slate-500 dark:text-slate-400 mb-4">
          <div className="flex justify-between">
            <span>Created:</span>
            <span className="font-medium text-slate-700 dark:text-slate-300">{format(new Date(summary.created_at), 'MMM dd, HH:mm')}</span>
          </div>
          <div className="flex justify-between">
            <span>Updated:</span>
            <span className="font-medium text-slate-700 dark:text-slate-300">{format(new Date(summary.updated_at), 'MMM dd, HH:mm')}</span>
          </div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
        {summary.status === 'ready' ? (
          <button
            onClick={() => navigate(`/company/${encodeURIComponent(summary.company_name)}/enhanced`)}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white py-2 rounded-lg text-sm font-medium transition-colors shadow-sm"
          >
            View Summary
          </button>
        ) : summary.status === 'preparing' ? (
          <div className="w-full bg-slate-100 dark:bg-slate-700 text-slate-400 py-2 rounded-lg text-sm font-medium text-center cursor-not-allowed">
            Processing...
          </div>
        ) : (
          <button
            onClick={() => navigate(`/company/${encodeURIComponent(summary.company_name)}`)}
            className="w-full text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Go to Company
          </button>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">Enhanced Summaries</h1>
          <p className="text-slate-600 dark:text-slate-400">
            View all prepared company summaries in one place
          </p>
        </div>
        {stats.ready > 0 && (
          <button
            onClick={downloadAllCSV}
            disabled={downloading}
            className="bg-infynd-success hover:bg-emerald-600 disabled:bg-slate-400 text-white px-6 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2 transform active:scale-95"
          >
            {downloading ? (
              <>
                <Loader className="animate-spin" size={20} />
                Downloading...
              </>
            ) : (
              <>
                <Download size={20} />
                Download All CSV
              </>
            )}
          </button>
        )}
      </div>

      {/* Stats Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento p-6 border border-slate-100 dark:border-slate-700 relative overflow-hidden group">
          <div className="absolute right-0 top-0 h-full w-24 bg-gradient-to-l from-blue-50 to-transparent dark:from-blue-900/10 opacity-50 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative z-10">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Total Summaries</p>
                <p className="text-4xl font-bold text-slate-900 dark:text-white">{stats.total}</p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
                <FileText size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento p-6 border border-slate-100 dark:border-slate-700 relative overflow-hidden group">
          <div className="absolute right-0 top-0 h-full w-24 bg-gradient-to-l from-green-50 to-transparent dark:from-green-900/10 opacity-50 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative z-10">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Ready to View</p>
                <p className="text-4xl font-bold text-infynd-success">{stats.ready}</p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
                <CheckCircle size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento p-6 border border-slate-100 dark:border-slate-700 relative overflow-hidden group">
          <div className="absolute right-0 top-0 h-full w-24 bg-gradient-to-l from-orange-50 to-transparent dark:from-orange-900/10 opacity-50 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative z-10">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Preparing</p>
                <p className="text-4xl font-bold text-orange-500">{stats.preparing}</p>
              </div>
              <div className="p-3 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-lg">
                <Loader size={24} className={stats.preparing > 0 ? "animate-spin" : ""} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
        <input
          type="text"
          placeholder="Search summaries..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-11 pr-4 py-3 bg-white dark:bg-infynd-card-dark border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm text-slate-900 dark:text-white"
        />
      </div>

      {/* Grid of Summaries */}
      {filteredSummaries.length === 0 ? (
        <div className="bg-white dark:bg-infynd-card-dark rounded-2xl shadow-bento p-16 text-center border border-dashed border-slate-200 dark:border-slate-700">
          <div className="mx-auto h-24 w-24 bg-slate-50 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6">
            <FileText className="text-slate-300 dark:text-slate-600" size={48} />
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">No Summaries Found</h2>
          <p className="text-slate-500 dark:text-slate-400 mb-8 max-w-md mx-auto">
            {searchTerm ? 'No results match your search term.' : 'Start preparing enhanced summaries from the company detail pages to see them here.'}
          </p>
          {!searchTerm && (
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-xl font-semibold transition shadow-lg hover:shadow-primary-500/25"
            >
              Go to Dashboard
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredSummaries.map((summary) => (
            <SummaryCard key={summary.company_name} summary={summary} />
          ))}
        </div>
      )}
    </div>
  );
};
export default Summaries;
