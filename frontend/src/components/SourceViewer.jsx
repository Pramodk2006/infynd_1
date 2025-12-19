import React, { useState } from 'react';
import { FileText, Download, Eye, Calendar, Tag } from 'lucide-react';
import { format } from 'date-fns';

const SourceViewer = ({ source, documentData }) => {
  const [showJson, setShowJson] = useState(false);

  const getTypeClasses = (type) => {
    const classes = {
      pdf: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
      html: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      url: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      text: 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-slate-300',
    };
    return classes[type] || 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300';
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm:ss');
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento border border-slate-100 dark:border-slate-700 p-6">
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <FileText size={20} className="mr-2 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">{source.title}</h3>
          </div>
          <div className="flex items-center space-x-3 text-sm text-slate-600 dark:text-slate-400">
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getTypeClasses(source.type)}`}>
              {source.type.toUpperCase()}
            </span>
            <span className="flex items-center">
              <Calendar size={14} className="mr-1" />
              {formatDate(source.extracted_at)}
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <div className="text-sm">
          <span className="font-medium text-slate-700 dark:text-slate-300">Source URI:</span>
          <p className="text-slate-600 dark:text-slate-400 mt-1 break-all font-mono text-xs bg-slate-50 dark:bg-slate-800/50 p-2 rounded">{source.uri}</p>
        </div>

        {source.document_id && (
          <div className="text-sm">
            <span className="font-medium text-slate-700 dark:text-slate-300">Document ID:</span>
            <p className="text-slate-600 dark:text-slate-400 mt-1 font-mono text-xs">{source.document_id}</p>
          </div>
        )}
      </div>

      {documentData && (
        <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {documentData.content?.raw_text?.length || 0}
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">Characters</div>
            </div>
            <div className="text-center p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
              <div className="text-2xl font-bold text-infynd-success">
                {documentData.content?.chunks?.length || 0}
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">Chunks</div>
            </div>
            {documentData.content?.structured && (
              <>
                <div className="text-center p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                  <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {documentData.content.structured.headings?.length || 0}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">Headings</div>
                </div>
                <div className="text-center p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                  <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    {documentData.content.structured.paragraphs?.length || 0}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">Paragraphs</div>
                </div>
              </>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              onClick={() => setShowJson(!showJson)}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition shadow-sm hover:shadow"
            >
              <Eye size={18} />
              <span>{showJson ? 'Hide' : 'View'} JSON</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition">
              <Download size={18} />
              <span>Download</span>
            </button>
          </div>

          {showJson && (
            <div className="mt-4 p-4 bg-slate-900 rounded-lg overflow-auto max-h-96 shadow-inner">
              <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono">
                {JSON.stringify(documentData, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SourceViewer;
