import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GameSearchPage } from './GameSearchPage';
import * as gameService from '../../services/gameService';

// Mock the game service
vi.mock('../../services/gameService');

const mockGames = {
  games: [
    {
      id: 1,
      name: 'Test Game 1',
      slug: 'test-game-1',
      summary: 'A great action game',
      cover_url: 'https://example.com/cover1.jpg',
      release_date: '2023-01-15',
      rating: 85.5,
      platforms: ['PC', 'PlayStation 5'],
      genres: ['Action', 'Adventure'],
    },
    {
      id: 2,
      name: 'Test Game 2',
      slug: 'test-game-2',
      summary: 'An amazing RPG',
      cover_url: 'https://example.com/cover2.jpg',
      release_date: '2023-06-20',
      rating: 90.0,
      platforms: ['PC', 'Xbox Series X'],
      genres: ['RPG', 'Adventure'],
    },
  ],
  total: 2,
  page: 1,
  page_size: 20,
  total_pages: 1,
};

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('GameSearchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders popular games by default', async () => {
    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: mockGames,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Popular Games')).toBeInTheDocument();
    });

    expect(screen.getByText('Test Game 1')).toBeInTheDocument();
    expect(screen.getByText('Test Game 2')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    // Should show spinner or loading indicator
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state', () => {
    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to load'),
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    expect(screen.getByText(/error loading games/i)).toBeInTheDocument();
  });

  it('displays search form with all filter inputs', () => {
    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: mockGames,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    expect(screen.getByPlaceholderText(/enter game name/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/playstation/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/action, rpg/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });

  it('shows game count', async () => {
    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: mockGames,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/showing 2 of 2 games/i)).toBeInTheDocument();
    });
  });

  it('renders game cards with correct information', async () => {
    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: mockGames,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Test Game 1')).toBeInTheDocument();
      expect(screen.getByText('A great action game')).toBeInTheDocument();
      expect(screen.getByText('85.5')).toBeInTheDocument();
    });
  });

  it('shows pagination when multiple pages exist', async () => {
    const multiPageData = {
      ...mockGames,
      total_pages: 3,
      page: 1,
    };

    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: multiPageData,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/page 1 of 3/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /previous/i })).toBeInTheDocument();
    });
  });

  it('disables previous button on first page', async () => {
    vi.mocked(gameService.usePopularGames).mockReturnValue({
      data: { ...mockGames, total_pages: 3, page: 1 },
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(gameService.useSearchGames).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);

    render(<GameSearchPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      const prevButton = screen.getByRole('button', { name: /previous/i });
      expect(prevButton).toBeDisabled();
    });
  });
});
