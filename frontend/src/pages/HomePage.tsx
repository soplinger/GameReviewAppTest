/**
 * Home page
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button, Card } from '../components/ui';

const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-[calc(100vh-16rem)]">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-primary-600 to-secondary-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Your Gaming Reviews, Amplified
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              Share reviews, connect with friends, and discover your next favorite game
            </p>
            {!isAuthenticated && (
              <div className="flex justify-center gap-4">
                <Link to="/register">
                  <Button size="lg" variant="secondary">
                    Get Started
                  </Button>
                </Link>
                <Link to="/login">
                  <Button size="lg" variant="ghost" className="text-white border-white hover:bg-white/10">
                    Sign In
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Why GameReview?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card variant="bordered" padding="lg">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Write Reviews
              </h3>
              <p className="text-gray-600">
                Share your gaming experiences with detailed reviews and ratings
              </p>
            </div>
          </Card>

          <Card variant="bordered" padding="lg">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Connect with Friends
              </h3>
              <p className="text-gray-600">
                Follow friends and see what games they're playing and reviewing
              </p>
            </div>
          </Card>

          <Card variant="bordered" padding="lg">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Get Recommendations
              </h3>
              <p className="text-gray-600">
                Discover new games based on your tastes and friend recommendations
              </p>
            </div>
          </Card>
        </div>
      </div>

      {/* CTA Section */}
      {!isAuthenticated && (
        <div className="bg-gray-100 py-16">
          <div className="max-w-4xl mx-auto text-center px-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Ready to Start Reviewing?
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Join thousands of gamers sharing their experiences
            </p>
            <Link to="/register">
              <Button size="lg" variant="primary">
                Create Free Account
              </Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
