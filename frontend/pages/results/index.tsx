import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import ResultsCard from '../../components/ResultsCard';
import OutreachModal from '../../components/OutreachModal';
import { apiClient } from '../../lib/api';
import { authUtils } from '../../lib/auth';
import { Company, Outreach } from '../../types';
import toast from 'react-hot-toast';
import { Loader, Filter, History } from 'lucide-react';

const Results: React.FC = () => {
  const router = useRouter();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [outreach, setOutreach] = useState<Outreach[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [hiringFilter, setHiringFilter] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'discover' | 'outreach'>('discover');

  useEffect(() => {
    if (!authUtils.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadData();
  }, [hiringFilter]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // Load companies
      const companiesData = await apiClient.getCompanies(hiringFilter);
      setCompanies(companiesData);

      // Load outreach history
      const outreachData = await apiClient.getOutreachHistory(0, 100);
      setOutreach(outreachData);
    } catch (error: any) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOutreach = (company: Company) => {
    setSelectedCompany(company);
    setIsModalOpen(true);
  };

  const handleOutreachSuccess = () => {
    loadData();
  };

  const handleUpdateOutreachStatus = async (
    outreachId: number,
    status: number,
    notes: string = ''
  ) => {
    try {
      await apiClient.updateOutreachStatus(outreachId, status, notes);
      toast.success('Status updated');
      loadData();
    } catch (error: any) {
      toast.error('Failed to update status');
      console.error(error);
    }
  };

  const getHiringLabel = (status: number) => {
    return {
      0: 'Not Hiring',
      1: 'Potentially Hiring',
      2: 'Actively Hiring',
    }[status] || 'Unknown';
  };

  const getResponseLabel = (status: number) => {
    return {
      0: 'Pending',
      1: 'Positive Response',
      2: 'Negative Response',
      3: 'No Response',
    }[status] || 'Unknown';
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Startup Discovery Results</h1>
          <p className="text-gray-600">
            {companies.length} startups found • Last 30 days
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b">
          <button
            onClick={() => setActiveTab('discover')}
            className={`px-6 py-3 font-semibold transition border-b-2 ${
              activeTab === 'discover'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="flex items-center gap-2">
              <Filter size={18} />
              Discovered Startups ({companies.length})
            </span>
          </button>
          <button
            onClick={() => setActiveTab('outreach')}
            className={`px-6 py-3 font-semibold transition border-b-2 ${
              activeTab === 'outreach'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="flex items-center gap-2">
              <History size={18} />
              Outreach History ({outreach.length})
            </span>
          </button>
        </div>

        {/* Discovered Startups Tab */}
        {activeTab === 'discover' && (
          <>
            {/* Filters */}
            <div className="flex gap-2 mb-6 flex-wrap">
              <button
                onClick={() => setHiringFilter(null)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  hiringFilter === null
                    ? 'bg-primary text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setHiringFilter(0)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  hiringFilter === 0
                    ? 'bg-gray-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Not Hiring
              </button>
              <button
                onClick={() => setHiringFilter(1)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  hiringFilter === 1
                    ? 'bg-yellow-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Potentially Hiring
              </button>
              <button
                onClick={() => setHiringFilter(2)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  hiringFilter === 2
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Actively Hiring
              </button>
            </div>

            {/* Loading State */}
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader className="animate-spin mr-2" size={24} />
                <span>Loading startups...</span>
              </div>
            ) : companies.length === 0 ? (
              <div className="text-center py-12 glass-effect rounded-lg">
                <p className="text-gray-600 text-lg mb-4">
                  No startups found matching your criteria.
                </p>
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-6 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition"
                >
                  Back to Dashboard
                </button>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-6">
                {companies.map((company) => (
                  <ResultsCard
                    key={company.id}
                    company={company}
                    onOutreach={handleOutreach}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* Outreach History Tab */}
        {activeTab === 'outreach' && (
          <>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader className="animate-spin mr-2" size={24} />
                <span>Loading outreach history...</span>
              </div>
            ) : outreach.length === 0 ? (
              <div className="text-center py-12 glass-effect rounded-lg">
                <p className="text-gray-600 text-lg mb-4">
                  No outreach emails sent yet.
                </p>
                <button
                  onClick={() => setActiveTab('discover')}
                  className="px-6 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition"
                >
                  Start Outreach
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {outreach.map((item) => (
                  <div key={item.id} className="glass-effect p-6 rounded-lg fade-in">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold text-lg">
                          {companies.find((c) => c.id === item.company_id)?.name ||
                            'Unknown Company'}
                        </h3>
                        <p className="text-sm text-gray-500">{item.email_sent_to}</p>
                      </div>
                      <select
                        value={item.response_status}
                        onChange={(e) =>
                          handleUpdateOutreachStatus(item.id, parseInt(e.target.value))
                        }
                        className={`px-3 py-1 rounded-lg text-sm font-medium border-0 ${
                          {
                            0: 'bg-blue-100 text-blue-700',
                            1: 'bg-green-100 text-green-700',
                            2: 'bg-red-100 text-red-700',
                            3: 'bg-gray-100 text-gray-700',
                          }[item.response_status] || 'bg-gray-100'
                        }`}
                      >
                        <option value={0}>Pending</option>
                        <option value={1}>Positive Response</option>
                        <option value={2}>Negative Response</option>
                        <option value={3}>No Response</option>
                      </select>
                    </div>

                    <p className="text-sm text-gray-600 mb-3">{item.email_subject}</p>

                    <div className="bg-gray-50 p-3 rounded text-sm text-gray-700 mb-3 max-h-24 overflow-y-auto">
                      {item.email_content}
                    </div>

                    <div className="text-xs text-gray-500">
                      <p>
                        Sent:{' '}
                        {new Date(item.sent_at).toLocaleDateString()}{' '}
                        {new Date(item.sent_at).toLocaleTimeString()}
                      </p>
                      {item.response_received_at && (
                        <p>
                          Response:{' '}
                          {new Date(item.response_received_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>

                    {item.response_notes && (
                      <div className="mt-3 p-3 bg-yellow-50 rounded text-sm text-yellow-700 border border-yellow-200">
                        <p className="font-semibold">Notes:</p>
                        <p>{item.response_notes}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Outreach Modal */}
      <OutreachModal
        isOpen={isModalOpen}
        company={selectedCompany}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedCompany(null);
        }}
        onSuccess={handleOutreachSuccess}
      />
    </Layout>
  );
};

export default Results;
