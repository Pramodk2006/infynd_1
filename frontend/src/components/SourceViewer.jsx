import React, { useState } from 'react';
import { FileText, Download, Eye, Calendar, Tag } from 'lucide-react';
import ReactJson from 'react-json-view';
import { format } from 'date-fns';

const SourceViewer = ({ source, documentData }) => {
  const [showJson, setShowJson] = useState(false);

  const getTypeColor = (type) => {
    const colors = {
      pdf: 'badge-pdf',
      html: 'badge-html',
      url: 'badge-url',
      text: 'badge-text',
    };
    return colors[type] || 'badge bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm:ss');
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <FileText size={20} className="mr-2 text-blue-600" />
            <h3 className="text-lg font-bold text-gray-900">{source.title}</h3>
          </div>
          <div className="flex items-center space-x-3 text-sm text-gray-600">
            <span className={`badge ${getTypeColor(source.type)}`}>{source.type.toUpperCase()}</span>
            <span className="flex items-center">
              <Calendar size={14} className="mr-1" />
              {formatDate(source.extracted_at)}
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div className="text-sm">
          <span className="font-medium text-gray-700">Source URI:</span>
          <p className="text-gray-600 mt-1 break-all">{source.uri}</p>
        </div>
        
        {source.document_id && (
          <div className="text-sm">
            <span className="font-medium text-gray-700">Document ID:</span>
            <p className="text-gray-600 mt-1 font-mono text-xs">{source.document_id}</p>
          </div>
        )}
      </div>

      {documentData && (
        <div className="border-t border-gray-200 pt-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {documentData.content?.raw_text?.length || 0}
              </div>
              <div className="text-xs text-gray-600">Characters</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {documentData.content?.chunks?.length || 0}
              </div>
              <div className="text-xs text-gray-600">Chunks</div>
            </div>
            {documentData.content?.structured && (
              <>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {documentData.content.structured.headings?.length || 0}
                  </div>
                  <div className="text-xs text-gray-600">Headings</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {documentData.content.structured.paragraphs?.length || 0}
                  </div>
                  <div className="text-xs text-gray-600">Paragraphs</div>
                </div>
              </>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              onClick={() => setShowJson(!showJson)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Eye size={18} />
              <span>{showJson ? 'Hide' : 'View'} JSON</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition">
              <Download size={18} />
              <span>Download</span>
            </button>
          </div>

          {showJson && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg overflow-auto max-h-96">
              <ReactJson
                src={documentData}
                theme="rjv-default"
                collapsed={2}
                displayDataTypes={false}
                displayObjectSize={true}
                enableClipboard={true}
                name="document"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SourceViewer;
