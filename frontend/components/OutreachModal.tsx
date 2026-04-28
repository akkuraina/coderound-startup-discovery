import React, { useState, useEffect } from 'react';
import { Company } from '../types';
import { apiClient } from '../lib/api';
import { X, Send, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

interface OutreachModalProps {
  isOpen: boolean;
  company: Company | null;
  onClose: () => void;
  onSuccess: () => void;
}

const OutreachModal: React.FC<OutreachModalProps> = ({
  isOpen,
  company,
  onClose,
  onSuccess,
}) => {
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (company && isOpen) {
      generateEmail();
    }
  }, [isOpen, company?.id]);

  const generateEmail = async () => {
    if (!company) return;

    setIsGenerating(true);
    try {
      const result = await apiClient.generateOutreachEmail(company.id);
      setSubject(result.subject);
      setContent(result.body);
      setEmail(''); // Let user fill this
    } catch (error) {
      toast.error('Failed to generate email');
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSendEmail = async () => {
    if (!email.trim()) {
      toast.error('Please enter a recipient email');
      return;
    }

    if (!content.trim()) {
      toast.error('Please provide email content');
      return;
    }

    if (!company) return;

    setIsLoading(true);
    try {
      await apiClient.sendOutreachEmail(
        company.id,
        email,
        subject,
        content
      );
      toast.success('Email sent successfully!');
      onSuccess();
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send email');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen || !company) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 flex justify-between items-center p-6 border-b bg-white">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Reach Out to {company.name}</h2>
            <p className="text-sm text-gray-500 mt-1">Customize and send your outreach email</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {isGenerating ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="animate-spin mr-2" />
              Generating personalized email...
            </div>
          ) : (
            <>
              {/* Recipient Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Send To Email Address *
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g., founder@company.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject Line
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Content */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Content
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={10}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Feel free to edit the generated content to personalize it further
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendEmail}
                  disabled={isLoading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-primary text-white rounded-lg font-medium hover:opacity-90 transition disabled:opacity-50"
                >
                  {isLoading ? (
                    <Loader size={18} className="animate-spin" />
                  ) : (
                    <Send size={18} />
                  )}
                  {isLoading ? 'Sending...' : 'Send Email'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default OutreachModal;
