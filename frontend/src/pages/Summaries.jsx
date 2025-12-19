import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { format } from 'date-fns';

const Summaries = () => {
  const navigate = useNavigate();
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [stats, setStats] = useState({ ready: 0, preparing: 0, total: 0 });

  useEffect(() => {
    loadSummaries();
    // Only poll if there are preparing items
    const interval = setInterval(() => {
      if (stats.preparing > 0) {
        loadSummaries();
      }
    }, 5000); // Reduced to 5 seconds and conditional
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
        return <CheckCircle className="text-green-500" size={20} />;
      case 'preparing':
        return <Loader className="text-yellow-500 animate-spin" size={20} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={20} />;
      default:
        return <Clock className="text-gray-400" size={20} />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'ready':
        return 'Ready';
      case 'preparing':
        return 'Preparing...';
      case 'error':
        return 'Error';
      default:
        return 'Not Started';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800';
      case 'preparing':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
        const escapeCSV = (val) => {
          if (!val || val === '-') return '';
          const str = String(val).replace(/"/g, '""');
          return str.includes(',') || str.includes('\n') || str.includes('"') ? `"${str}"` : str;
        };

        const row = [
          escapeCSV(data.company_name),
          escapeCSV(data.acronym),
          escapeCSV(data.domain),
          escapeCSV(data.domain_status),
          escapeCSV(data.logo_url),
          escapeCSV(data.short_description),
          escapeCSV(data.long_description),
          escapeCSV(data.sector),
          escapeCSV(data.industry),
          escapeCSV(data.sub_industry),
          escapeCSV(data.sic_code),
          escapeCSV(data.sic_text),
          escapeCSV(data.tags?.join('; ')),
          escapeCSV(data.company_registration_number),
          escapeCSV(data.vat_number),
          escapeCSV(data.full_address),
          escapeCSV(data.phone),
          escapeCSV(data.sales_phone),
          escapeCSV(data.email),
          escapeCSV(data.all_emails?.join('; ')),
          escapeCSV(data.other_numbers?.join('; ')),
          escapeCSV(data.hours_of_operation),
          escapeCSV(data.hq_indicator ? 'Yes' : 'No'),
          escapeCSV(data.certifications?.join('; ')),
          escapeCSV(data.people?.filter(p => p.name !== '-').map(p => `${p.name} (${p.title})`).join('; ')),
          escapeCSV(data.services?.filter(s => s.service !== '-').map(s => `${s.service} [${s.type}]`).join('; ')),
          escapeCSV(new Date(data.extraction_timestamp).toLocaleString()),
          escapeCSV(data.text_length + ' characters')
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Enhanced Summaries</h1>
          <p className="text-gray-600">
            View all prepared company summaries in one place
          </p>
        </div>
        {stats.ready > 0 && (
          <button
            onClick={downloadAllCSV}
            disabled={downloading}
            className="bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
          >
            {downloading ? (
              <>
                <Loader className="animate-spin" size={20} />
                Downloading...
              </>
            ) : (
              <>
                📥 Download All CSV
              </>
            )}
          </button>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Summaries</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <FileText className="text-blue-500" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Ready to View</p>
              <p className="text-3xl font-bold text-green-600">{stats.ready}</p>
            </div>
            <CheckCircle className="text-green-500" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Preparing</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.preparing}</p>
            </div>
            <Loader className="text-yellow-500" size={40} />
          </div>
        </div>
      </div>

      {/* Summaries List */}
      {summaries.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="mx-auto text-gray-400 mb-4" size={64} />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Summaries Yet</h2>
          <p className="text-gray-600 mb-6">
            Start preparing enhanced summaries from the company detail pages
          </p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition"
          >
            View Companies
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {summaries.map((summary) => (
                <tr key={summary.company_name} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="text-gray-400 mr-3" size={20} />
                      <span className="font-medium text-gray-900">{summary.company_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(summary.status)}
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(summary.status)}`}>
                        {getStatusText(summary.status)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(summary.created_at), 'MMM dd, yyyy HH:mm')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(summary.updated_at), 'MMM dd, yyyy HH:mm')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {summary.status === 'ready' ? (
                      <button
                        onClick={() => navigate(`/company/${encodeURIComponent(summary.company_name)}/enhanced`)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
                      >
                        View Summary
                      </button>
                    ) : summary.status === 'preparing' ? (
                      <span className="text-gray-400">Processing...</span>
                    ) : (
                      <button
                        onClick={() => navigate(`/company/${encodeURIComponent(summary.company_name)}`)}
                        className="text-blue-600 hover:text-blue-700 font-semibold"
                      >
                        View Company
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Summaries;
