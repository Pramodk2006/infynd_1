import React from 'react';
import { PlusCircle } from 'lucide-react';
import ExtractionForm from '../components/ExtractionForm';

const NewExtraction = () => {
  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center mb-2">
          <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-xl mr-4 text-primary-600 dark:text-primary-400">
            <PlusCircle size={32} />
          </div>
          New Extraction
        </h1>
        <p className="text-slate-600 dark:text-slate-400 text-lg ml-16">
          Extract company data from a single source (URL, PDF, HTML, or text file)
        </p>
      </div>

      <div className="bg-white dark:bg-infynd-card-dark rounded-xl shadow-bento border border-slate-100 dark:border-slate-700 p-8 mb-8">
        <ExtractionForm mode="single" />
      </div>

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-3 flex items-center gap-2">
          <span role="img" aria-label="lightbulb">💡</span> Pro Tips
        </h3>
        <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-2">
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span>
            <span><strong>Summary mode</strong> extracts homepage + 1 key page (faster)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span>
            <span><strong>Full crawl</strong> mode extracts the entire website (comprehensive)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span>
            <span>PDFs are extracted with full metadata (author, date, page count)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span>
            <span>HTML files preserve structure (headings, tables, lists)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span>
            <span>All outputs are vector-DB ready with pre-chunked content</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default NewExtraction;
