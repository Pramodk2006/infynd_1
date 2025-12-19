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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Company not found</p>
        <button onClick={() => navigate('/')} className="mt-4 btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6 transition"
      >
        <ArrowLeft size={20} className="mr-2" />
        Back to Dashboard
      </button>

      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 flex items-center mb-4">
              <Building2 className="mr-3 text-blue-600" size={36} />
              {company.name}
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center text-gray-600">
                <FileText size={18} className="mr-2 text-blue-500" />
                <span>
                  <span className="font-semibold">{company.totalSources}</span> sources
                </span>
              </div>
              <div className="flex items-center text-gray-600">
                <Calendar size={18} className="mr-2 text-green-500" />
                <span>Created: {formatDate(company.created)}</span>
              </div>
              <div className="flex items-center text-gray-600">
                <Calendar size={18} className="mr-2 text-orange-500" />
                <span>Updated: {formatDate(company.lastUpdated)}</span>
              </div>
            </div>
          </div>
          <div className="ml-4 flex gap-3">
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
                  ? 'bg-gray-400 cursor-not-allowed'
                  : summaryStatus === 'ready'
                    ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white'
                    : 'bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 text-white'
                }`}
            >
              <Sparkles size={20} className={summaryStatus === 'preparing' ? 'animate-spin' : ''} />
              {summaryStatus === 'preparing' ? 'Preparing...' : summaryStatus === 'ready' ? 'View Summary' : 'Prepare Summary'}
            </button>
            <button
              onClick={() => navigate(`/compare/${encodeURIComponent(company.name)}`)}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all shadow-md hover:shadow-lg"
            >
              <TrendingUp size={20} />
              Compare Classifiers
            </button>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Sources</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {company.sources.map((source, index) => (
            <button
              key={index}
              onClick={() => setSelectedSource(index)}
              className={`p-4 border-2 rounded-lg text-left transition ${selectedSource === index
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
                }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`badge ${source.type === 'pdf'
                      ? 'badge-pdf'
                      : source.type === 'html'
                        ? 'badge-html'
                        : source.type === 'url'
                          ? 'badge-url'
                          : 'badge-text'
                    }`}
                >
                  {source.type.toUpperCase()}
                </span>
                {selectedSource === index && <ExternalLink size={16} className="text-blue-600" />}
              </div>
              <div className="font-medium text-gray-900 text-sm truncate">{source.title}</div>
              <div className="text-xs text-gray-500 mt-1">{formatDate(source.extracted_at)}</div>
            </button>
          ))}
        </div>
      </div>

      {selectedSource !== null && company.sources[selectedSource] && (
        <div>
          {loadingDocument ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : documentData ? (
            <SourceViewer
              source={company.sources[selectedSource]}
              documentData={documentData}
            />
          ) : (
            <div className="text-center py-12 text-gray-500">
              Failed to load document data
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CompanyDetail;
