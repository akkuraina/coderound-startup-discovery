import React from 'react';
import { Company } from '../types';
import { Users, MapPin, TrendingUp, Calendar, DollarSign, Mail } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { safeParseArray } from '../lib/parsing';

interface ResultsCardProps {
  company: Company;
  onOutreach: (company: Company) => void;
}

const ResultsCard: React.FC<ResultsCardProps> = ({ company, onOutreach }) => {
  const hiringStatusLabel = {
    0: { label: 'Not Hiring', color: 'bg-gray-100 text-gray-700' },
    1: { label: 'Potentially Hiring', color: 'bg-yellow-100 text-yellow-700' },
    2: { label: 'Actively Hiring', color: 'bg-green-100 text-green-700' },
  }[company.hiring_status] || { label: 'Unknown', color: 'bg-gray-100 text-gray-700' };

  // Safe parse: handles objects, JSON strings, and plain strings
  const investors = safeParseArray(company.investors);

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6 fade-in">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800">{company.name}</h3>
          {company.country && (
            <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
              <MapPin size={14} />
              {company.country}
            </div>
          )}
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${hiringStatusLabel.color}`}>
          {hiringStatusLabel.label}
        </span>
      </div>

      {/* Description */}
      {company.description && (
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{company.description}</p>
      )}

      {/* Funding Info */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4 py-4 border-y">
        {company.funding_amount && (
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              <DollarSign size={14} />
              Amount Raised
            </div>
            <p className="font-bold text-gray-800">${(company.funding_amount / 1000000).toFixed(1)}M</p>
          </div>
        )}

        {company.funding_round && (
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              <TrendingUp size={14} />
              Funding Round
            </div>
            <p className="font-bold text-gray-800">{company.funding_round}</p>
          </div>
        )}

        {company.funding_date && (
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              <Calendar size={14} />
              Announcement
            </div>
            <p className="font-bold text-gray-800">
              {formatDistanceToNow(new Date(company.funding_date), { addSuffix: true })}
            </p>
          </div>
        )}
      </div>

      {/* Investors */}
      {investors.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
            <Users size={14} />
            Investors
          </div>
          <div className="flex flex-wrap gap-2">
            {investors.map((investor, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded border border-blue-200"
              >
                {investor}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Links */}
      <div className="flex gap-2 mb-4">
        {company.website && (
          <a
            href={company.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-500 hover:underline"
          >
            Website →
          </a>
        )}
        {company.linkedin_url && (
          <a
            href={company.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-500 hover:underline"
          >
            LinkedIn →
          </a>
        )}
      </div>

      {/* Actions */}
      <button
        onClick={() => onOutreach(company)}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-primary text-white rounded-lg hover:opacity-90 transition font-medium"
      >
        <Mail size={16} />
        Reach Out
      </button>
    </div>
  );
};

export default ResultsCard;
