/**
 * Main application with routing
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Header, Footer } from './components/layout';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import { GameSearchPage } from './pages/games/GameSearchPage';
import { GameDetailPage } from './pages/games/GameDetailPage';
import { ProfilePage } from './pages/profile/ProfilePage';
import { FeedPage } from './pages/feed/FeedPage';
import { FriendsPage } from './pages/social/FriendsPage';
import LinkedAccountsPage from './pages/LinkedAccountsPage';
import GameLibraryPage from './pages/GameLibraryPage';
import { ProtectedRoute } from './components/ProtectedRoute';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <div className="flex flex-col min-h-screen bg-gray-50">
              <Header />
              <main className="flex-1">
                <Routes>
                {/* Home */}
                <Route path="/" element={<HomePage />} />
                
                {/* Auth Routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                
                {/* Game Routes */}
                <Route path="/games" element={<GameSearchPage />} />
                <Route path="/games/:slug" element={<GameDetailPage />} />
                
                {/* Protected Routes */}
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <ProfilePage />
                    </ProtectedRoute>
                  }
                />
                
                {/* Social Routes - Protected */}
                <Route
                  path="/feed"
                  element={
                    <ProtectedRoute>
                      <FeedPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/friends"
                  element={
                    <ProtectedRoute>
                      <FriendsPage />
                    </ProtectedRoute>
                  }
                />
                
                {/* OAuth & Library Routes - Protected */}
                <Route
                  path="/linked-accounts"
                  element={
                    <ProtectedRoute>
                      <LinkedAccountsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/library"
                  element={
                    <ProtectedRoute>
                      <GameLibraryPage />
                    </ProtectedRoute>
                  }
                />
                
                {/* 404 */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
