import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, Plus, X, Upload, CheckCircle, Loader } from 'lucide-react';
import { extractionAPI } from '../services/api';

const BatchExtraction = () => {
  const navigate = useNavigate();
  const [company, setCompany] = useState('');
  const [sources, setSources] = useState([{ type: 'url', value: '' }]);
  const [crawlMode, setCrawlMode] = useState('summary');
  const [loading, setLoading] = useState(false);

  const addSource = () => {
    setSources([...sources, { type: 'url', value: '' }]);
  };

  const removeSource = (index) => {
    setSources(sources.filter((_, i) => i !== index));
  };

  const updateSource = (index, field, value) => {
    const updated = [...sources];
    updated[index][field] = value;
    setSources(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await extractionAPI.batch({
        company,
        sources: sources.map(s => ({ value: s.value })),
        crawlMode,
      });

      const successCount = result.successful || 0;
      const failedCount = result.failed || 0;

      if (successCount > 0) {
        alert(`Batch extraction completed!\n✅ Success: ${successCount}\n❌ Failed: ${failedCount}`);
      } else {
        alert(`Batch extraction failed!\nAll ${failedCount} sources failed to extract.`);
      }

      navigate('/dashboard');
    } catch (error) {
      console.error('Error:', error);
      alert(error.response?.data?.error || 'Failed to start batch extraction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center mb-2">
          <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-xl mr-4 text-primary-600 dark:text-primary-400">
            <Layers size={32} />
          </div>
          Batch Extraction
        </h1>
        <p className="text-slate-600 dark:text-slate-400 text-lg ml-16">
          Extract data from multiple sources for a single company
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento border border-slate-100 dark:border-slate-700 p-8">
          <div className="mb-8">
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
              Company Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              required
              placeholder="e.g., TechCorp Inc"
              className="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm text-slate-900 dark:text-white transition-colors"
            />
          </div>

          <div className="mb-8">
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Crawl Mode (for URLs)</label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setCrawlMode('summary')}
                className={`p-4 border-2 rounded-xl transition text-left relative overflow-hidden group ${crawlMode === 'summary'
                  ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                  : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 bg-white dark:bg-slate-800'
                  }`}
              >
                <div className="font-bold mb-1">Summary</div>
                <div className="text-xs opacity-80">2 pages</div>
                {crawlMode === 'summary' && <div className="absolute top-2 right-2 text-primary-600 dark:text-primary-400"><CheckCircle size={16} /></div>}
              </button>
              <button
                type="button"
                onClick={() => setCrawlMode('full')}
                className={`p-4 border-2 rounded-xl transition text-left relative overflow-hidden group ${crawlMode === 'full'
                  ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                  : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 bg-white dark:bg-slate-800'
                  }`}
              >
                <div className="font-bold mb-1">Full</div>
                <div className="text-xs opacity-80">Entire site</div>
                {crawlMode === 'full' && <div className="absolute top-2 right-2 text-primary-600 dark:text-primary-400"><CheckCircle size={16} /></div>}
              </button>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-0">
                Sources <span className="text-red-500">*</span>
              </label>
              <button
                type="button"
                onClick={addSource}
                className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium text-sm px-3 py-1.5 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                title="Add another source"
              >
                <Plus size={18} />
                <span>Add Source</span>
              </button>
            </div>

            <div className="space-y-4">
              {sources.map((source, index) => (
                <div key={index} className="flex space-x-3 items-start animate-fade-in-up">
                  <select
                    value={source.type}
                    onChange={(e) => updateSource(index, 'type', e.target.value)}
                    className="px-4 py-3 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm text-slate-900 dark:text-white transition-colors w-32"
                  >
                    <option value="url">URL</option>
                    <option value="pdf">PDF</option>
                    <option value="html">HTML</option>
                    <option value="text">Text</option>
                  </select>

                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={source.value}
                      onChange={(e) => updateSource(index, 'value', e.target.value)}
                      required
                      placeholder={
                        source.type === 'url'
                          ? 'https://example.com'
                          : './path/to/file.' + source.type
                      }
                      className="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm text-slate-900 dark:text-white transition-colors pl-4 pr-10"
                    />
                    {source.type !== 'url' && (
                      <div
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 pointer-events-none"
                      >
                        <Upload size={18} />
                      </div>
                    )}
                  </div>

                  {sources.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeSource(index)}
                      className="p-3 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
                      title="Remove source"
                    >
                      <X size={20} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loading}
            className={`flex-1 bg-primary-600 hover:bg-primary-700 text-white font-bold py-4 px-6 rounded-xl transition duration-300 shadow-lg hover:shadow-primary-500/30 transform active:scale-[0.98] ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader className="animate-spin" size={20} />
                Processing {sources.length} sources...
              </span>
            ) : (
              `Start Batch Extraction (${sources.length} sources)`
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

      <div className="mt-8 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6">
        <h3 className="font-semibold text-amber-900 dark:text-amber-100 mb-3 flex items-center gap-2">
          <span role="img" aria-label="package">📦</span> Batch Processing Benefits
        </h3>
        <ul className="text-sm text-amber-900 dark:text-amber-200 space-y-2">
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0"></span>
            <span>Process multiple sources for one company simultaneously</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0"></span>
            <span>All sources saved to the same company folder</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0"></span>
            <span>Mix different source types (URL + PDF + HTML + text)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0"></span>
            <span>Automatic error handling - continues even if one source fails</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0"></span>
            <span>Progress tracking for each source</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default BatchExtraction;
