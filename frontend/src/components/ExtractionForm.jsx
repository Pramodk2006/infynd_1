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
      navigate('/dashboard');
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
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Company Name */}
      <div>
        <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
          Company Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="company"
          value={formData.company}
          onChange={handleChange}
          required
          placeholder="e.g., Acme Corporation"
          className="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm text-slate-900 dark:text-white transition-colors"
        />
      </div>

      {/* Source Type */}
      <div>
        <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Source Type</label>
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
              className={`flex flex-col items-center justify-center p-4 border-2 rounded-xl transition-all duration-200 ${formData.sourceType === type.value
                ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 shadow-md transform scale-105'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
            >
              <type.icon size={28} className={`mb-3 ${formData.sourceType === type.value ? 'text-primary-600 dark:text-primary-400' : 'text-slate-400'}`} />
              <span className="text-sm font-bold">{type.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Source Input */}
      <div>
        <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
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
            className="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm text-slate-900 dark:text-white transition-colors pl-4 pr-10"
          />
          {formData.sourceType !== 'url' && (
            <div
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 pointer-events-none"
            >
              <Upload size={20} />
            </div>
          )}
        </div>
      </div>

      {/* Crawl Mode (only for URLs) */}
      {formData.sourceType === 'url' && (
        <div className="animate-fade-in-up">
          <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Crawl Mode</label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setFormData({ ...formData, crawlMode: 'summary' })}
              className={`p-4 border-2 rounded-xl transition-all duration-200 text-left ${formData.crawlMode === 'summary'
                ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-800'
                }`}
            >
              <div className={`font-bold mb-1 ${formData.crawlMode === 'summary' ? 'text-primary-700 dark:text-primary-300' : 'text-slate-800 dark:text-white'}`}>Summary Mode</div>
              <div className={`text-sm ${formData.crawlMode === 'summary' ? 'text-primary-600/80 dark:text-primary-300/80' : 'text-slate-500 dark:text-slate-400'}`}>Homepage + 1 key page</div>
            </button>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, crawlMode: 'full' })}
              className={`p-4 border-2 rounded-xl transition-all duration-200 text-left ${formData.crawlMode === 'full'
                ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-800'
                }`}
            >
              <div className={`font-bold mb-1 ${formData.crawlMode === 'full' ? 'text-primary-700 dark:text-primary-300' : 'text-slate-800 dark:text-white'}`}>Full Crawl</div>
              <div className={`text-sm ${formData.crawlMode === 'full' ? 'text-primary-600/80 dark:text-primary-300/80' : 'text-slate-500 dark:text-slate-400'}`}>Entire website</div>
            </button>
          </div>
        </div>
      )}

      {/* Max Pages (only for full crawl) */}
      {formData.sourceType === 'url' && formData.crawlMode === 'full' && (
        <div className="animate-fade-in-up">
          <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Maximum Pages</label>
          <input
            type="number"
            name="maxPages"
            value={formData.maxPages}
            onChange={handleChange}
            min="1"
            max="500"
            className="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm text-slate-900 dark:text-white transition-colors"
          />
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Limit the number of pages to crawl (1-500)</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-300 animate-fade-in">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <div className="flex space-x-4 pt-4">
        <button
          type="submit"
          disabled={loading}
          className={`flex-1 bg-primary-600 hover:bg-primary-700 text-white font-bold py-4 px-6 rounded-xl transition duration-300 shadow-lg hover:shadow-primary-500/30 transform active:scale-[0.98] ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
          onClick={() => navigate('/dashboard')}
          className="px-6 py-4 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 font-semibold rounded-xl transition duration-300"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default ExtractionForm;
