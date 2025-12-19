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

  const ResultCard = ({ title, data, success, error: methodError, color, badgeColor }) => (
    <div className={`bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento border-l-4 ${color} p-6 border-t border-r border-b border-slate-100 dark:border-slate-700 h-full flex flex-col`}>
      <h3 className="text-xl font-bold mb-6 text-slate-800 dark:text-white flex items-center justify-between">
        {title}
        {success && data && <span className={`text-xs px-2 py-1 rounded-full ${badgeColor} bg-opacity-20 text-opacity-100`}>Active</span>}
      </h3>

      {methodError && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
            <div className="text-sm text-red-700 dark:text-red-300">{methodError}</div>
          </div>
        </div>
      )}

      {success && data && data.final_prediction && (
        <div className="space-y-4 flex-1">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="text-infynd-success" size={20} />
            <span className="text-infynd-success font-medium">Classification Complete</span>
          </div>

          <div className="space-y-3">
            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl">
              <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5 font-semibold">Sector</div>
              <div className="font-bold text-lg text-slate-900 dark:text-white">{data.final_prediction.sector}</div>
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl">
              <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5 font-semibold">Industry</div>
              <div className="font-semibold text-slate-800 dark:text-slate-200">{data.final_prediction.industry}</div>
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl">
              <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5 font-semibold">Sub-Industry</div>
              <div className="font-semibold text-slate-800 dark:text-slate-200">{data.final_prediction.sub_industry}</div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-xl flex items-center justify-between border border-blue-100 dark:border-blue-800">
              <div className="text-xs text-blue-600 dark:text-blue-300 uppercase tracking-wide font-semibold">Confidence</div>
              <div className="font-bold text-blue-600 dark:text-blue-300 text-lg">
                {(data.final_prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>

            {data.final_prediction.sic_code && (
              <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl">
                <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5 font-semibold">SIC Code</div>
                <div className="font-mono text-sm text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 px-2 py-1 rounded inline-block border border-slate-200 dark:border-slate-700">
                  {data.final_prediction.sic_code}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {success && data && data.sector && (
        // Ollama format
        <div className="space-y-4 flex-1">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="text-infynd-success" size={20} />
            <span className="text-infynd-success font-medium">Classification Complete</span>
          </div>

          <div className="space-y-3">
            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl">
              <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5 font-semibold">Sector</div>
              <div className="font-bold text-lg text-slate-900 dark:text-white">{data.sector}</div>
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl">
              <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5 font-semibold">Industry</div>
              <div className="font-semibold text-slate-800 dark:text-slate-200">{data.industry}</div>
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl">
              <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5 font-semibold">Sub-Industry</div>
              <div className="font-semibold text-slate-800 dark:text-slate-200">{data.sub_industry}</div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-xl flex items-center justify-between border border-blue-100 dark:border-blue-800">
              <div className="text-xs text-blue-600 dark:text-blue-300 uppercase tracking-wide font-semibold">Confidence</div>
              <div className="font-bold text-blue-600 dark:text-blue-300 text-lg">
                {(data.confidence * 100).toFixed(1)}%
              </div>
            </div>

            {data.alternatives && data.alternatives.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
                <div className="text-xs text-slate-400 dark:text-slate-500 uppercase tracking-wide mb-3 font-semibold">Top Alternatives</div>
                <div className="space-y-2">
                  {data.alternatives.slice(0, 3).map((alt, idx) => (
                    <div key={idx} className="text-sm bg-slate-50 dark:bg-slate-800/30 p-2.5 rounded-lg flex justify-between items-center">
                      <span className="text-slate-700 dark:text-slate-300">{alt.sub_industry}</span>
                      <span className="text-xs font-mono text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                        {(alt.similarity * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!success && !methodError && (
        <div className="text-slate-400 dark:text-slate-500 text-center py-12 flex-1 flex flex-col justify-center items-center">
          <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-full mb-3">
            <TrendingUp size={24} className="opacity-50" />
          </div>
          Click "Run Comparison" to classify
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold mb-2 text-slate-900 dark:text-white tracking-tight">Classification Comparison</h2>
          <p className="text-slate-600 dark:text-slate-400">
            Compare Top-K Hierarchical and Ollama (Embedding + LLM) classifiers for <span className="font-bold text-primary-600 dark:text-primary-400">{companyName}</span>
          </p>
        </div>

        <button
          onClick={runComparison}
          disabled={loading}
          className="bg-primary-600 hover:bg-primary-700 disabled:bg-slate-400 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg hover:shadow-primary-500/25 active:scale-95"
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
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 animate-fade-in">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <div className="font-bold text-red-700 dark:text-red-400">Error</div>
              <div className="text-sm text-red-600 dark:text-red-300">{error}</div>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="animate-fade-in-up space-y-8">
          <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
            <div className="text-sm">
              <div className="font-bold text-blue-900 dark:text-blue-100 mb-2 flex items-center justify-between">
                <span>Analyzed Text Content</span>
                <span className="font-mono text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                  {result.text_length} characters
                </span>
              </div>
              <div className="mt-2 text-sm bg-white dark:bg-slate-900 p-4 rounded-lg border border-blue-100 dark:border-slate-700 text-slate-600 dark:text-slate-300 leading-relaxed font-mono">
                {result.text_preview}...
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
            <ResultCard
              title="Top-K Hierarchical Classifier"
              data={result.topk.result}
              success={result.topk.success}
              error={result.topk.error}
              color="border-purple-500"
              badgeColor="bg-purple-500 text-purple-700"
            />

            <ResultCard
              title="Ollama (Embedding + LLM)"
              data={result.ollama.result}
              success={result.ollama.success}
              error={result.ollama.error}
              color="border-emerald-500"
              badgeColor="bg-emerald-500 text-emerald-700"
            />
          </div>

          <div className="bg-slate-50 dark:bg-slate-800/30 rounded-lg p-3 text-xs text-slate-400 dark:text-slate-500 flex justify-end items-center gap-2">
            <Clock size={14} />
            <span className="font-medium">Classification completed at:</span>
            <span className="font-mono">{new Date(result.timestamp).toLocaleString()}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClassificationComparison;
