import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, FileText, ExternalLink } from 'lucide-react';
import { format } from 'date-fns';

const CompanyCard = ({ company }) => {
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  return (
    <Link to={`/company/${encodeURIComponent(company.name)}`}>
      <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-all duration-300 card-hover border border-gray-100">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
              {company.name}
              <ExternalLink size={16} className="ml-2 text-gray-400" />
            </h3>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center text-gray-600">
            <FileText size={18} className="mr-2 text-blue-500" />
            <span className="text-sm">
              <span className="font-semibold text-gray-900">{company.totalSources || 0}</span> {(company.totalSources === 1) ? 'source' : 'sources'}
            </span>
          </div>

          <div className="flex items-center text-gray-600">
            <Calendar size={18} className="mr-2 text-green-500" />
            <span className="text-sm">
              Updated: <span className="font-medium">{formatDate(company.lastUpdated)}</span>
            </span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-100">
          <button className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center">
            View Details →
          </button>
        </div>
      </div>
    </Link>
  );
};

export default CompanyCard;
