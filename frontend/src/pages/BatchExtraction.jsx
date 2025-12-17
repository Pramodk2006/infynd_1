import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, Plus, X, Upload } from 'lucide-react';

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
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // In production:
      // await extractionAPI.batch({ company, sources, crawlMode });
      
      alert(`Batch extraction started for ${company} with ${sources.length} sources!`);
      navigate('/');
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to start batch extraction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Layers className="mr-3 text-blue-600" size={36} />
          Batch Extraction
        </h1>
        <p className="text-gray-600 mt-2">
          Extract data from multiple sources for a single company
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="mb-6">
            <label className="label">
              Company Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              required
              placeholder="e.g., TechCorp Inc"
              className="input-field"
            />
          </div>

          <div className="mb-6">
            <label className="label">Crawl Mode (for URLs)</label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setCrawlMode('summary')}
                className={`p-3 border-2 rounded-lg transition ${
                  crawlMode === 'summary'
                    ? 'border-blue-600 bg-blue-50 text-blue-600'
                    : 'border-gray-300'
                }`}
              >
                <div className="font-medium">Summary</div>
                <div className="text-xs text-gray-600">2 pages</div>
              </button>
              <button
                type="button"
                onClick={() => setCrawlMode('full')}
                className={`p-3 border-2 rounded-lg transition ${
                  crawlMode === 'full'
                    ? 'border-blue-600 bg-blue-50 text-blue-600'
                    : 'border-gray-300'
                }`}
              >
                <div className="font-medium">Full</div>
                <div className="text-xs text-gray-600">Entire site</div>
              </button>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="label mb-0">
                Sources <span className="text-red-500">*</span>
              </label>
              <button
                type="button"
                onClick={addSource}
                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
              >
                <Plus size={18} />
                <span>Add Source</span>
              </button>
            </div>

            <div className="space-y-4">
              {sources.map((source, index) => (
                <div key={index} className="flex space-x-3">
                  <select
                    value={source.type}
                    onChange={(e) => updateSource(index, 'type', e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                      className="input-field"
                    />
                    {source.type !== 'url' && (
                      <button
                        type="button"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        <Upload size={18} />
                      </button>
                    )}
                  </div>

                  {sources.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeSource(index)}
                      className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition"
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
            className={`flex-1 btn-primary ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing {sources.length} sources...
              </span>
            ) : (
              `Start Batch Extraction (${sources.length} sources)`
            )}
          </button>
          <button type="button" onClick={() => navigate('/')} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>

      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-semibold text-yellow-900 mb-2">📦 Batch Processing Benefits</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• Process multiple sources for one company simultaneously</li>
          <li>• All sources saved to the same company folder</li>
          <li>• Mix different source types (URL + PDF + HTML + text)</li>
          <li>• Automatic error handling - continues even if one source fails</li>
          <li>• Progress tracking for each source</li>
        </ul>
      </div>
    </div>
  );
};

export default BatchExtraction;
