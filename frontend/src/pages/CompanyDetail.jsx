import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Building2, Calendar, FileText, ExternalLink, TrendingUp, Sparkles } from 'lucide-react';
import { format } from 'date-fns';
import SourceViewer from '../components/SourceViewer';
import { companyAPI, sourceAPI } from '../services/api';

const CompanyDetail = () => {
  const { companyName } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSource, setSelectedSource] = useState(null);
  const [documentData, setDocumentData] = useState(null);
  const [loadingDocument, setLoadingDocument] = useState(false);
  const [summaryStatus, setSummaryStatus] = useState('not_started');

  useEffect(() => {
    loadCompanyDetails();
    // Check summary status in background, don't block UI
    setTimeout(() => checkSummaryStatus(), 100);
  }, [companyName]);

  useEffect(() => {
    if (selectedSource !== null && company?.sources[selectedSource]) {
      loadDocumentData(company.sources[selectedSource].document_id);
    }
  }, [selectedSource, company]);

  const loadDocumentData = async (documentId) => {
    setLoadingDocument(true);
    setDocumentData(null);
    try {
      const data = await sourceAPI.getDocument(documentId);
      setDocumentData(data);
    } catch (error) {
      console.error('Error loading document:', error);
    } finally {
      setLoadingDocument(false);
    }
  };

  const loadCompanyDetails = async () => {
    setLoading(true);
    try {
      const data = await companyAPI.getByName(decodeURIComponent(companyName));
      setCompany(data);
      if (data.sources && data.sources.length > 0) {
        setSelectedSource(0);
      }
    } catch (error) {
      console.error('Error loading company details:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkSummaryStatus = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000); // 1 second timeout

      const response = await fetch(`http://localhost:5000/api/companies/${companyName}/enhanced/status`, {
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        setSummaryStatus(data.status || 'not_started');
      }
    } catch (error) {
      // Silently fail - status will remain 'not_started'
    }
  };

  const handlePrepareSummary = async () => {
    try {
      setSummaryStatus('preparing');
      const response = await fetch(`http://localhost:5000/api/companies/${companyName}/enhanced/prepare`, {
        method: 'POST'
      });

      if (!response.ok) {
        setSummaryStatus('error');
        return;
      }

      // Poll for completion (max 300 polls * 2s = 600s = 10 minutes)
      let pollCount = 0;
      const pollInterval = setInterval(async () => {
        pollCount++;
        if (pollCount > 300) {
          clearInterval(pollInterval);
          setSummaryStatus('error');
          return;
        }

        try {
          const statusRes = await fetch(`http://localhost:5000/api/companies/${companyName}/enhanced/status`);
          if (statusRes.ok) {
            const data = await statusRes.json();
            setSummaryStatus(data.status);

            if (data.status === 'ready') {
              clearInterval(pollInterval);
              navigate(`/company/${encodeURIComponent(company.name)}/enhanced`);
            } else if (data.status === 'error') {
              clearInterval(pollInterval);
            }
          }
        } catch (err) {
          // Continue polling on errors
        }
      }, 2000);
    } catch (error) {
      console.error('Error preparing summary:', error);
      setSummaryStatus('error');
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 dark:text-slate-400 text-lg">Company not found</p>
        <button onClick={() => navigate('/dashboard')} className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white mb-6 transition"
      >
        <ArrowLeft size={20} className="mr-2" />
        Back to Dashboard
      </button>

      {/* Header Section */}
      <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento p-6 mb-8 border border-slate-100 dark:border-slate-700">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center mb-4">
              <Building2 className="mr-3 text-primary-600 dark:text-primary-400" size={36} />
              {company.name}
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center text-slate-600 dark:text-slate-400">
                <FileText size={18} className="mr-2 text-primary-500" />
                <span>
                  <span className="font-semibold text-slate-900 dark:text-slate-200">{company.totalSources}</span> sources
                </span>
              </div>
              <div className="flex items-center text-slate-600 dark:text-slate-400">
                <Calendar size={18} className="mr-2 text-infynd-success" />
                <span>Created: {formatDate(company.created)}</span>
              </div>
              <div className="flex items-center text-slate-600 dark:text-slate-400">
                <Calendar size={18} className="mr-2 text-orange-500" />
                <span>Updated: {formatDate(company.lastUpdated)}</span>
              </div>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => {
                if (summaryStatus === 'ready') {
                  navigate(`/company/${encodeURIComponent(company.name)}/enhanced`);
                } else if (summaryStatus === 'not_started' || summaryStatus === 'error') {
                  handlePrepareSummary();
                }
              }}
              disabled={summaryStatus === 'preparing'}
              className={`px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all shadow-md hover:shadow-lg ${summaryStatus === 'preparing'
                ? 'bg-slate-400 cursor-not-allowed text-white'
                : summaryStatus === 'ready'
                  ? 'bg-infynd-success text-white hover:bg-emerald-600'
                  : 'bg-orange-500 text-white hover:bg-orange-600'
                }`}
            >
              <Sparkles size={20} className={summaryStatus === 'preparing' ? 'animate-spin' : ''} />
              {summaryStatus === 'preparing' ? 'Preparing...' : summaryStatus === 'ready' ? 'View Summary' : 'Prepare Summary'}
            </button>
            <button
              onClick={() => navigate(`/compare/${encodeURIComponent(company.name)}`)}
              className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all shadow-md hover:shadow-lg"
            >
              <TrendingUp size={20} />
              Compare Classifiers
            </button>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Sources</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {company.sources.map((source, index) => (
            <button
              key={index}
              onClick={() => setSelectedSource(index)}
              className={`p-4 border rounded-xl text-left transition-all duration-200 ${selectedSource === index
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 ring-1 ring-primary-500'
                : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-infynd-card-dark hover:border-primary-300 dark:hover:border-slate-600'
                }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium ${source.type === 'pdf'
                    ? 'bg-red-100 text-red-800'
                    : source.type === 'html'
                      ? 'bg-orange-100 text-orange-800'
                      : source.type === 'url'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                >
                  {source.type.toUpperCase()}
                </span>
                {selectedSource === index && <ExternalLink size={16} className="text-primary-600 dark:text-primary-400" />}
              </div>
              <div className="font-medium text-slate-900 dark:text-white text-sm truncate">{source.title}</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">{formatDate(source.extracted_at)}</div>
            </button>
          ))}
        </div>
      </div>

      {selectedSource !== null && company.sources[selectedSource] && (
        <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento border border-slate-100 dark:border-slate-700 overflow-hidden">
          {loadingDocument ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : documentData ? (
            <SourceViewer
              source={company.sources[selectedSource]}
              documentData={documentData}
            />
          ) : (
            <div className="text-center py-12 text-slate-500">
              Failed to load document data
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CompanyDetail;
