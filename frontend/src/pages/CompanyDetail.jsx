import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Building2, Calendar, FileText, ExternalLink } from 'lucide-react';
import { format } from 'date-fns';
import SourceViewer from '../components/SourceViewer';
import { mockAPI } from '../services/api';

const CompanyDetail = () => {
  const { companyName } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSource, setSelectedSource] = useState(null);

  useEffect(() => {
    loadCompanyDetails();
  }, [companyName]);

  const loadCompanyDetails = async () => {
    setLoading(true);
    try {
      // Using mock data for now
      // In production: const data = await companyAPI.getByName(companyName);
      const data = mockAPI.companyDetails;
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
          <div>
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
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Sources</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {company.sources.map((source, index) => (
            <button
              key={index}
              onClick={() => setSelectedSource(index)}
              className={`p-4 border-2 rounded-lg text-left transition ${
                selectedSource === index
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`badge ${
                    source.type === 'pdf'
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
        <SourceViewer
          source={company.sources[selectedSource]}
          documentData={{
            content: {
              raw_text: 'Sample extracted text content...',
              chunks: [{ chunk_id: '1', text: 'Sample chunk' }],
              structured: {
                headings: [{ tag: 'h1', text: 'Sample Heading' }],
                paragraphs: ['Sample paragraph 1', 'Sample paragraph 2'],
              },
            },
          }}
        />
      )}
    </div>
  );
};

export default CompanyDetail;
