/**
 * Test script for IGDB integration in React Game Review App
 * Run this to verify frontend IGDB sync functionality
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { GameSearchPage } from '../pages/games/GameSearchPage';
import { GameSyncPanel } from '../components/games/GameSyncPanel';

// Mock gameService for testing
jest.mock('../services/gameService', () => ({
  useHybridSearchGames: jest.fn(),
  usePopularGames: jest.fn(),
  useSyncPopularGames: jest.fn(),
  useSyncGamesBySearch: jest.fn(),
  useSyncGamesByGenre: jest.fn(),
  useSyncRecentGames: jest.fn(),
}));

describe('IGDB Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  const renderWithProviders = (component: React.ReactNode) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {component}
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  describe('GameSyncPanel', () => {
    const mockProps = {
      onSyncPopular: jest.fn(),
      onSyncBySearch: jest.fn(),
      onSyncByGenre: jest.fn(),
      onSyncRecent: jest.fn(),
      isLoading: false,
    };

    it('renders sync controls correctly', () => {
      renderWithProviders(<GameSyncPanel {...mockProps} />);
      
      expect(screen.getByText('🎮 IGDB Game Sync Center')).toBeInTheDocument();
      expect(screen.getByText('📈 Sync Popular Games')).toBeInTheDocument();
      expect(screen.getByText('🔍 Sync by Search')).toBeInTheDocument();
      expect(screen.getByText('🎯 Sync by Genre')).toBeInTheDocument();
      expect(screen.getByText('📅 Sync Recent Releases')).toBeInTheDocument();
    });

    it('handles popular games sync', async () => {
      renderWithProviders(<GameSyncPanel {...mockProps} />);
      
      const syncButton = screen.getByText('Sync Popular');
      fireEvent.click(syncButton);
      
      expect(mockProps.onSyncPopular).toHaveBeenCalledWith(20);
    });

    it('handles search-based sync with query input', async () => {
      renderWithProviders(<GameSyncPanel {...mockProps} />);
      
      const searchInput = screen.getByPlaceholderText('zelda, mario, etc.');
      fireEvent.change(searchInput, { target: { value: 'zelda' } });
      
      const syncButton = screen.getByText('Sync Search');
      fireEvent.click(syncButton);
      
      expect(mockProps.onSyncBySearch).toHaveBeenCalledWith('zelda', 10);
    });

    it('handles genre sync with selection', async () => {
      renderWithProviders(<GameSyncPanel {...mockProps} />);
      
      const genreSelect = screen.getByDisplayValue('');
      fireEvent.change(genreSelect, { target: { value: 'Action' } });
      
      const syncButton = screen.getByText('Sync Genre');
      fireEvent.click(syncButton);
      
      expect(mockProps.onSyncByGenre).toHaveBeenCalledWith('Action', 15);
    });

    it('shows loading state during sync', () => {
      const loadingProps = { ...mockProps, isLoading: true };
      renderWithProviders(<GameSyncPanel {...loadingProps} />);
      
      expect(screen.getByText('Syncing games from IGDB...')).toBeInTheDocument();
    });

    it('handles quick action buttons', () => {
      renderWithProviders(<GameSyncPanel {...mockProps} />);
      
      const actionButton = screen.getByText('Action (10)');
      fireEvent.click(actionButton);
      
      expect(mockProps.onSyncByGenre).toHaveBeenCalledWith('Action', 10);
    });
  });

  describe('GameSearchPage IGDB Integration', () => {
    const mockGameService = require('../services/gameService');

    beforeEach(() => {
      mockGameService.useHybridSearchGames.mockReturnValue({
        data: { games: [], total: 0, is_from_igdb: false, synced_count: 0 },
        isLoading: false,
        error: null,
      });
      
      mockGameService.usePopularGames.mockReturnValue({
        data: { games: [], total: 0 },
        isLoading: false,
        error: null,
      });

      const mockMutation = {
        mutate: jest.fn(),
        isPending: false,
        isSuccess: false,
        error: null,
      };

      mockGameService.useSyncPopularGames.mockReturnValue(mockMutation);
      mockGameService.useSyncGamesBySearch.mockReturnValue(mockMutation);
      mockGameService.useSyncGamesByGenre.mockReturnValue(mockMutation);
      mockGameService.useSyncRecentGames.mockReturnValue(mockMutation);
    });

    it('renders sync panel toggle button', () => {
      renderWithProviders(<GameSearchPage />);
      
      expect(screen.getByText('Show IGDB Sync')).toBeInTheDocument();
    });

    it('shows sync panel when toggled', () => {
      renderWithProviders(<GameSearchPage />);
      
      const toggleButton = screen.getByText('Show IGDB Sync');
      fireEvent.click(toggleButton);
      
      expect(screen.getByText('🎮 IGDB Game Sync Center')).toBeInTheDocument();
      expect(screen.getByText('Hide IGDB Sync')).toBeInTheDocument();
    });

    it('shows auto-sync checkbox when searching', () => {
      // Mock search params
      delete window.location;
      window.location = { search: '?q=zelda' } as any;
      
      renderWithProviders(<GameSearchPage />);
      
      expect(screen.getByLabelText('Auto-sync from IGDB if no results')).toBeInTheDocument();
    });

    it('displays IGDB badge for IGDB results', () => {
      mockGameService.useHybridSearchGames.mockReturnValue({
        data: { games: [], total: 0, is_from_igdb: true, synced_count: 0 },
        isLoading: false,
        error: null,
      });

      renderWithProviders(<GameSearchPage />);
      
      expect(screen.getByText('IGDB Results')).toBeInTheDocument();
    });

    it('displays sync count when games are synced', () => {
      mockGameService.useHybridSearchGames.mockReturnValue({
        data: { games: [], total: 0, is_from_igdb: false, synced_count: 5 },
        isLoading: false,
        error: null,
      });

      renderWithProviders(<GameSearchPage />);
      
      expect(screen.getByText('✓ 5 new games synced')).toBeInTheDocument();
    });

    it('shows success alert after sync operations', () => {
      const mockMutation = {
        mutate: jest.fn(),
        isPending: false,
        isSuccess: true,
        error: null,
      };

      mockGameService.useSyncPopularGames.mockReturnValue(mockMutation);

      renderWithProviders(<GameSearchPage />);
      
      expect(screen.getByText('Games synced successfully from IGDB!')).toBeInTheDocument();
    });
  });
});

// Integration test helper functions
export const testIGDBIntegration = {
  // Test hybrid search with auto-sync
  async testHybridSearch(query: string, expectAutoSync: boolean = false) {
    console.log(`Testing hybrid search for: "${query}"`);
    console.log(`Auto-sync expected: ${expectAutoSync}`);
    
    // This would be used in actual integration tests
    // with a running frontend and backend
  },

  // Test sync operations
  async testSyncOperations() {
    console.log('Testing all sync operations...');
    
    const operations = [
      { name: 'Popular Games', limit: 10 },
      { name: 'Search: "mario"', query: 'mario', limit: 5 },
      { name: 'Genre: Action', genre: 'Action', limit: 8 },
      { name: 'Recent Games', limit: 15, daysBack: 30 },
    ];

    for (const op of operations) {
      console.log(`  Testing ${op.name}...`);
      // Actual sync calls would go here
    }
  },

  // Test error handling
  async testErrorHandling() {
    console.log('Testing error scenarios...');
    
    const errorCases = [
      'Invalid IGDB credentials',
      'Network timeout',
      'Rate limit exceeded',
      'Invalid search query',
    ];

    for (const errorCase of errorCases) {
      console.log(`  Testing: ${errorCase}`);
      // Error simulation would go here
    }
  },
};

console.log('IGDB Integration Test Suite Ready');
console.log('Run tests with: npm test src/__tests__/igdb-integration.test.tsx');