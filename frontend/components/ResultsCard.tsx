import React from 'react';
import { Company } from '../types';
import { Users, MapPin, TrendingUp, Calendar, DollarSign, Mail, ExternalLink } from 'lucide-react';
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
  const decisionMakers = company.decision_makers?.decision_makers || [];

  return (
    <div className={`bg-white rounded-lg shadow-md hover:shadow-lg transition overflow-hidden fade-in ${
      company.is_tech ? 'border-l-4 border-l-purple-500' : 'border-l-4 border-l-gray-300'
    }`}>
      {/* Header Section */}
      <div className="p-6 pb-4 border-b">
        {/* Title & Badges */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-xl font-bold text-gray-800">{company.name}</h3>
            {company.is_tech && (
              <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-bold rounded">
                🔧 TECH
              </span>
            )}
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ${hiringStatusLabel.color}`}>
            {hiringStatusLabel.label}
          </span>
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-gray-600 flex-wrap mb-3">
          {company.country && (
            <div className="flex items-center gap-1">
              <MapPin size={14} />
              {company.country}
            </div>
          )}
          {company.sector && (
            <div className="text-purple-600 font-medium">
              {company.sector}
            </div>
          )}
        </div>

        {/* Description */}
        {company.description && (
          <p className="text-gray-600 text-sm">{company.description}</p>
        )}
      </div>

      {/* Funding & Investors Section */}
      <div className="px-6 py-4 border-b bg-gray-50">
        {/* Funding Info Grid */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {company.funding_amount && (
            <div>
              <div className="text-xs text-gray-500 font-semibold mb-1">Raised</div>
              <p className="font-bold text-gray-800">${(company.funding_amount / 1000000).toFixed(1)}M</p>
            </div>
          )}

          {company.funding_round && (
            <div>
              <div className="text-xs text-gray-500 font-semibold mb-1">Round</div>
              <p className="font-bold text-gray-800">{company.funding_round}</p>
            </div>
          )}

          {company.funding_date && (
            <div>
              <div className="text-xs text-gray-500 font-semibold mb-1">Announced</div>
              <p className="font-bold text-gray-800 text-xs">
                {formatDistanceToNow(new Date(company.funding_date), { addSuffix: true })}
              </p>
            </div>
          )}
        </div>

        {/* Investors */}
        {investors.length > 0 && (
          <div>
            <div className="text-xs text-gray-500 font-semibold mb-2">Investors</div>
            <div className="flex flex-wrap gap-2">
              {investors.slice(0, 3).map((investor, idx) => (
                <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded border border-blue-200">
                  {investor}
                </span>
              ))}
              {investors.length > 3 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">+{investors.length - 3} more</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Decision Makers Section */}
      {decisionMakers.length > 0 && (
        <div className="px-6 py-4 border-b bg-blue-50">
          <div className="flex items-center gap-2 mb-3">
            <Users size={16} className="text-blue-600" />
            <h4 className="font-semibold text-gray-800 text-sm">Leadership</h4>
          </div>
          <div className="space-y-2">
            {decisionMakers.map((maker, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-white rounded border border-blue-100">
                <div>
                  <p className="font-medium text-sm text-gray-800">{maker.name}</p>
                  <p className="text-xs text-gray-600">{maker.title}</p>
                </div>
                {maker.linkedin_url && (
                  <a
                    href={maker.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                    title="View on LinkedIn"
                  >
                    <ExternalLink size={14} />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Links Section */}
      {(company.website || company.linkedin_url) && (
        <div className="px-6 py-4 border-b flex gap-3">
          {company.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded text-sm font-medium transition"
            >
              🌐 Website
              <ExternalLink size={12} />
            </a>
          )}
          {company.linkedin_url && (
            <a
              href={company.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded text-sm font-medium transition"
            >
              💼 LinkedIn
              <ExternalLink size={12} />
            </a>
          )}
        </div>
      )}

      {/* Action Button */}
      <div className="p-6 pt-4">
        <button
          onClick={() => onOutreach(company)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition font-medium shadow-sm"
        >
          <Mail size={16} />
          Reach Out
        </button>
      </div>
    </div>
  );
};

export default ResultsCard;
