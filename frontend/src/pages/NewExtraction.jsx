import React from 'react';
import { PlusCircle } from 'lucide-react';
import ExtractionForm from '../components/ExtractionForm';

const NewExtraction = () => {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <PlusCircle className="mr-3 text-blue-600" size={36} />
          New Extraction
        </h1>
        <p className="text-gray-600 mt-2">
          Extract company data from a single source (URL, PDF, HTML, or text file)
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <ExtractionForm mode="single" />
      </div>

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">💡 Tips</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• <strong>Summary mode</strong> extracts homepage + 1 key page (faster)</li>
          <li>• <strong>Full crawl</strong> mode extracts the entire website (comprehensive)</li>
          <li>• PDFs are extracted with full metadata (author, date, page count)</li>
          <li>• HTML files preserve structure (headings, tables, lists)</li>
          <li>• All outputs are vector-DB ready with pre-chunked content</li>
        </ul>
      </div>
    </div>
  );
};

export default NewExtraction;
