import React from 'react';
import Link from 'next/link';
import { Zap, Users, Mail, TrendingUp, ArrowRight } from 'lucide-react';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-light pt-20">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="gradient-text">Discover & Recruit</span>
            <br />
            Funded Startups Instantly
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            CodeRound Startup Discovery Radar automatically identifies startups that raised capital
            in the last 30 days and are actively hiring. Reach out at the perfect time.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/signup"
              className="px-8 py-4 bg-gradient-primary text-white rounded-lg font-bold hover:shadow-lg transition transform hover:-translate-y-1"
            >
              Get Started Free
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 border-2 border-primary text-primary rounded-lg font-bold hover:bg-primary hover:text-white transition"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-16 gradient-text">How It Works</h2>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {/* Feature 1 */}
          <div className="glass-effect p-8 rounded-xl hover:shadow-lg transition">
            <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center mb-4">
              <Zap className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-3">Automated Discovery</h3>
            <p className="text-gray-600">
              Our system continuously scans the web for startups that raised seed funding in the
              last 30 days.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="glass-effect p-8 rounded-xl hover:shadow-lg transition">
            <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center mb-4">
              <Users className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-3">Hiring Insights</h3>
            <p className="text-gray-600">
              AI analyzes company data to identify which startups are actively hiring or planning to
              hire soon.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="glass-effect p-8 rounded-xl hover:shadow-lg transition">
            <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center mb-4">
              <Mail className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-bold mb-3">AI-Powered Outreach</h3>
            <p className="text-gray-600">
              Generate personalized emails in seconds, then send them directly from our platform.
            </p>
          </div>
        </div>

        {/* Workflow */}
        <div className="bg-white rounded-xl p-8 shadow-md">
          <h3 className="text-2xl font-bold mb-8 text-center">Your Workflow</h3>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-10 h-10 bg-gradient-primary text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                1
              </div>
              <p className="font-semibold text-gray-800">Sign Up</p>
              <p className="text-sm text-gray-600 mt-1">Create your free account</p>
            </div>

            <div className="flex items-center justify-center">
              <ArrowRight className="text-primary hidden md:block" size={24} />
            </div>

            <div className="text-center">
              <div className="w-10 h-10 bg-gradient-primary text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                2
              </div>
              <p className="font-semibold text-gray-800">Discover</p>
              <p className="text-sm text-gray-600 mt-1">Run automated discovery</p>
            </div>

            <div className="flex items-center justify-center">
              <ArrowRight className="text-primary hidden md:block" size={24} />
            </div>

            <div className="text-center">
              <div className="w-10 h-10 bg-gradient-primary text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                3
              </div>
              <p className="font-semibold text-gray-800">Reach Out</p>
              <p className="text-sm text-gray-600 mt-1">Send personalized emails</p>
            </div>

            <div className="flex items-center justify-center">
              <ArrowRight className="text-primary hidden md:block" size={24} />
            </div>

            <div className="text-center">
              <div className="w-10 h-10 bg-gradient-primary text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                4
              </div>
              <p className="font-semibold text-gray-800">Track</p>
              <p className="text-sm text-gray-600 mt-1">Monitor responses</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <p className="text-4xl font-bold gradient-text mb-2">1000+</p>
            <p className="text-gray-600">Startups Tracked</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold gradient-text mb-2">30 days</p>
            <p className="text-gray-600">Data Window</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold gradient-text mb-2">100%</p>
            <p className="text-gray-600">AI-Powered</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="bg-gradient-primary rounded-xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Find Your Next Hires?</h2>
          <p className="text-lg mb-8 opacity-90">
            Join CodeRound and discover funded startups before your competitors do.
          </p>
          <Link
            href="/signup"
            className="inline-block px-8 py-4 bg-white text-primary font-bold rounded-lg hover:shadow-lg transition"
          >
            Start Free Trial
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 py-8 mt-20">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2026 CodeRound AI. All rights reserved.</p>
          <p className="text-sm mt-2">Fullstack AI Recruiter for Fast Growing Startups</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
