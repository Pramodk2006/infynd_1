import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Link as LinkIcon, FileText, File } from 'lucide-react';
import { extractionAPI } from '../services/api';

const ExtractionForm = ({ mode = 'single' }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    company: '',
    sourceType: 'url',
    source: '',
    crawlMode: 'summary',
    maxPages: 50,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await extractionAPI.extract({
        company: formData.company,
        source: formData.source,
        crawlMode: formData.crawlMode,
        maxPages: formData.maxPages,
      });
      
      alert(`Extraction successful! Document ID: ${result.document_id}`);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to start extraction');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Company Name */}
      <div>
        <label className="label">
          Company Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="company"
          value={formData.company}
          onChange={handleChange}
          required
          placeholder="e.g., Acme Corporation"
          className="input-field"
        />
      </div>

      {/* Source Type */}
      <div>
        <label className="label">Source Type</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { value: 'url', icon: LinkIcon, label: 'Website URL' },
            { value: 'pdf', icon: FileText, label: 'PDF File' },
            { value: 'html', icon: File, label: 'HTML File' },
            { value: 'text', icon: File, label: 'Text File' },
          ].map((type) => (
            <button
              key={type.value}
              type="button"
              onClick={() => setFormData({ ...formData, sourceType: type.value })}
              className={`flex flex-col items-center justify-center p-4 border-2 rounded-lg transition ${
                formData.sourceType === type.value
                  ? 'border-blue-600 bg-blue-50 text-blue-600'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <type.icon size={24} className="mb-2" />
              <span className="text-sm font-medium">{type.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Source Input */}
      <div>
        <label className="label">
          {formData.sourceType === 'url' ? 'Website URL' : 'File Path'} <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <input
            type={formData.sourceType === 'url' ? 'url' : 'text'}
            name="source"
            value={formData.source}
            onChange={handleChange}
            required
            placeholder={
              formData.sourceType === 'url'
                ? 'https://example.com'
                : formData.sourceType === 'pdf'
                ? './documents/company-brochure.pdf'
                : './documents/about.html'
            }
            className="input-field"
          />
          {formData.sourceType !== 'url' && (
            <button
              type="button"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <Upload size={20} />
            </button>
          )}
        </div>
      </div>

      {/* Crawl Mode (only for URLs) */}
      {formData.sourceType === 'url' && (
        <div>
          <label className="label">Crawl Mode</label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setFormData({ ...formData, crawlMode: 'summary' })}
              className={`p-4 border-2 rounded-lg transition ${
                formData.crawlMode === 'summary'
                  ? 'border-blue-600 bg-blue-50 text-blue-600'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-medium mb-1">Summary Mode</div>
              <div className="text-sm text-gray-600">Homepage + 1 key page</div>
            </button>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, crawlMode: 'full' })}
              className={`p-4 border-2 rounded-lg transition ${
                formData.crawlMode === 'full'
                  ? 'border-blue-600 bg-blue-50 text-blue-600'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-medium mb-1">Full Crawl</div>
              <div className="text-sm text-gray-600">Entire website</div>
            </button>
          </div>
        </div>
      )}

      {/* Max Pages (only for full crawl) */}
      {formData.sourceType === 'url' && formData.crawlMode === 'full' && (
        <div>
          <label className="label">Maximum Pages</label>
          <input
            type="number"
            name="maxPages"
            value={formData.maxPages}
            onChange={handleChange}
            min="1"
            max="500"
            className="input-field"
          />
          <p className="text-sm text-gray-500 mt-1">Limit the number of pages to crawl (1-500)</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <div className="flex space-x-4">
        <button
          type="submit"
          disabled={loading}
          className={`flex-1 btn-primary ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            'Start Extraction'
          )}
        </button>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="btn-secondary"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default ExtractionForm;
