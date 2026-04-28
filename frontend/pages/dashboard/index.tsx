import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import { apiClient } from '../../lib/api';
import { authUtils } from '../../lib/auth';
import toast from 'react-hot-toast';
import { Loader, Zap } from 'lucide-react';

const Dashboard: React.FC = () => {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);

  useEffect(() => {
    // Redirect if not authenticated
    if (!authUtils.isAuthenticated()) {
      router.push('/login');
      return;
    }

    const user = authUtils.getCurrentUser();
    setUser(user);
  }, []);

  const handleDiscoverStartups = async () => {
    setIsDiscovering(true);

    try {
      const result = await apiClient.discoverStartups();
      toast.success(`Discovered ${result.total_found} startups!`);
      router.push('/results');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Discovery failed');
      console.error(error);
    } finally {
      setIsDiscovering(false);
    }
  };

  if (!user) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader className="animate-spin" size={32} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Welcome Section */}
        <div className="glass-effect rounded-xl p-8 mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Welcome, <span className="gradient-text">{user.name}!</span>
          </h1>
          <p className="text-gray-600 text-lg">
            Ready to discover newly funded startups? Click the button below to run your first scan.
          </p>
        </div>

        {/* Main CTA */}
        <div className="bg-gradient-primary rounded-xl p-12 text-white text-center">
          <Zap size={48} className="mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Start Discovering Startups</h2>
          <p className="text-lg mb-8 opacity-90 max-w-xl mx-auto">
            Our AI will scan the web for startups that raised seed funding in the last 30 days and
            identify which ones are actively hiring.
          </p>

          <button
            onClick={handleDiscoverStartups}
            disabled={isDiscovering}
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary font-bold rounded-lg hover:shadow-lg transition disabled:opacity-50 text-lg"
          >
            {isDiscovering && <Loader size={20} className="animate-spin" />}
            {isDiscovering ? 'Discovering...' : 'Discover Startups'}
          </button>
        </div>

        {/* Info Grid */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="glass-effect rounded-lg p-6">
            <h3 className="font-bold text-lg mb-2">🔍 Automated Search</h3>
            <p className="text-gray-600 text-sm">
              Scans 1000+ sources for recent funding announcements
            </p>
          </div>

          <div className="glass-effect rounded-lg p-6">
            <h3 className="font-bold text-lg mb-2">🤖 AI Analysis</h3>
            <p className="text-gray-600 text-sm">
              Claude AI extracts key details and hiring signals
            </p>
          </div>

          <div className="glass-effect rounded-lg p-6">
            <h3 className="font-bold text-lg mb-2">📧 Smart Outreach</h3>
            <p className="text-gray-600 text-sm">
              Generate personalized emails and track responses
            </p>
          </div>
        </div>

        {/* Quick Start */}
        <div className="mt-12 glass-effect rounded-xl p-8">
          <h2 className="text-2xl font-bold mb-6">Quick Start Guide</h2>
          <ol className="space-y-4">
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-gradient-primary text-white rounded-full flex items-center justify-center font-bold">
                1
              </span>
              <div>
                <p className="font-semibold text-gray-800">Click "Discover Startups"</p>
                <p className="text-gray-600 text-sm">
                  The system will automatically scan for recently funded startups
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-gradient-primary text-white rounded-full flex items-center justify-center font-bold">
                2
              </span>
              <div>
                <p className="font-semibold text-gray-800">View Results</p>
                <p className="text-gray-600 text-sm">
                  See all discovered companies with hiring status and funding details
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-gradient-primary text-white rounded-full flex items-center justify-center font-bold">
                3
              </span>
              <div>
                <p className="font-semibold text-gray-800">Send Outreach Emails</p>
                <p className="text-gray-600 text-sm">
                  Click "Reach Out" on any company to generate and send a personalized email
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-gradient-primary text-white rounded-full flex items-center justify-center font-bold">
                4
              </span>
              <div>
                <p className="font-semibold text-gray-800">Track Responses</p>
                <p className="text-gray-600 text-sm">
                  Monitor your outreach history and update response statuses
                </p>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
