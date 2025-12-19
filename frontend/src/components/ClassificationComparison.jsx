import React, { useState } from 'react';
import { AlertCircle, CheckCircle, Loader, TrendingUp } from 'lucide-react';

const ClassificationComparison = ({ companyName }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runComparison = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`http://localhost:5000/api/classify_compare/${companyName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const ResultCard = ({ title, data, success, error: methodError, color }) => (
    <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${color}`}>
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      
      {methodError && (
        <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
            <div className="text-sm text-red-700">{methodError}</div>
          </div>
        </div>
      )}

      {success && data && data.final_prediction && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="text-green-500" size={20} />
            <span className="text-green-600 font-medium">Classification Complete</span>
          </div>

          <div className="space-y-2">
            <div className="bg-gray-50 p-3 rounded">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Sector</div>
              <div className="font-semibold text-lg">{data.final_prediction.sector}</div>
            </div>

            <div className="bg-gray-50 p-3 rounded">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Industry</div>
              <div className="font-semibold">{data.final_prediction.industry}</div>
            </div>

            <div className="bg-gray-50 p-3 rounded">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Sub-Industry</div>
              <div className="font-semibold">{data.final_prediction.sub_industry}</div>
            </div>

            <div className="bg-blue-50 p-3 rounded flex items-center justify-between">
              <div className="text-xs text-gray-500 uppercase tracking-wide">Confidence</div>
              <div className="font-bold text-blue-600">
                {(data.final_prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>

            {data.final_prediction.sic_code && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">SIC Code</div>
                <div className="font-mono text-sm">{data.final_prediction.sic_code}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {success && data && data.sector && (
        // Ollama format
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="text-green-500" size={20} />
            <span className="text-green-600 font-medium">Classification Complete</span>
          </div>

          <div className="space-y-2">
            <div className="bg-gray-50 p-3 rounded">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Sector</div>
              <div className="font-semibold text-lg">{data.sector}</div>
            </div>

            <div className="bg-gray-50 p-3 rounded">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Industry</div>
              <div className="font-semibold">{data.industry}</div>
            </div>

            <div className="bg-gray-50 p-3 rounded">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Sub-Industry</div>
              <div className="font-semibold">{data.sub_industry}</div>
            </div>

            <div className="bg-blue-50 p-3 rounded flex items-center justify-between">
              <div className="text-xs text-gray-500 uppercase tracking-wide">Confidence</div>
              <div className="font-bold text-blue-600">
                {(data.confidence * 100).toFixed(1)}%
              </div>
            </div>

            {data.alternatives && data.alternatives.length > 0 && (
              <div className="mt-4">
                <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Top Alternatives</div>
                <div className="space-y-1">
                  {data.alternatives.slice(0, 3).map((alt, idx) => (
                    <div key={idx} className="text-sm bg-gray-50 p-2 rounded flex justify-between">
                      <span>{alt.sub_industry}</span>
                      <span className="text-gray-500">{(alt.similarity * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!success && !methodError && (
        <div className="text-gray-400 text-center py-8">
          Click "Run Comparison" to classify
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-3xl font-bold mb-2">Classification Comparison</h2>
        <p className="text-gray-600">
          Compare Top-K Hierarchical and Ollama (Embedding + LLM) classifiers for <span className="font-semibold">{companyName}</span>
        </p>
      </div>

      <div className="mb-6">
        <button
          onClick={runComparison}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors"
        >
          {loading ? (
            <>
              <Loader className="animate-spin" size={20} />
              Running Classification...
            </>
          ) : (
            <>
              <TrendingUp size={20} />
              Run Comparison
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-2">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <div className="font-semibold text-red-700">Error</div>
              <div className="text-sm text-red-600">{error}</div>
            </div>
          </div>
        </div>
      )}

      {result && (
        <>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="text-sm">
              <div className="font-semibold mb-2">Company Text</div>
              <div className="text-gray-700">
                <span className="font-mono text-xs text-gray-500">{result.text_length} characters</span>
                <div className="mt-2 text-sm bg-white p-3 rounded border">
                  {result.text_preview}...
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResultCard
              title="Top-K Hierarchical Classifier"
              data={result.topk.result}
              success={result.topk.success}
              error={result.topk.error}
              color="border-purple-500"
            />

            <ResultCard
              title="Ollama (Embedding + LLM)"
              data={result.ollama.result}
              success={result.ollama.success}
              error={result.ollama.error}
              color="border-green-500"
            />
          </div>

          <div className="mt-6 bg-gray-50 rounded-lg p-4 text-xs text-gray-500">
            <div className="font-semibold mb-1">Classification completed at:</div>
            <div className="font-mono">{new Date(result.timestamp).toLocaleString()}</div>
          </div>
        </>
      )}
    </div>
  );
};

export default ClassificationComparison;
