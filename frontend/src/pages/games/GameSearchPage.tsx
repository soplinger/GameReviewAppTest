import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  useHybridSearchGames, 
  usePopularGames,
  useSyncPopularGames,
  useSyncGamesBySearch,
  useSyncGamesByGenre,
  useSyncRecentGames
} from '../../services/gameService';
import { GameCard } from '../../components/games/GameCard';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';
import { GameSyncPanel } from '../../components/games/GameSyncPanel';

export const GameSearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [platform, setPlatform] = useState(searchParams.get('platform') || '');
  const [genre, setGenre] = useState(searchParams.get('genre') || '');
  const [showSyncPanel, setShowSyncPanel] = useState(false);
  const [autoSync, setAutoSync] = useState(true);
  const page = parseInt(searchParams.get('page') || '1');

  const query = searchParams.get('q') || undefined;
  const platformFilter = searchParams.get('platform') || undefined;
  const genreFilter = searchParams.get('genre') || undefined;

  // Use hybrid search when there's a query
  const {
    data: searchResults,
    isLoading: searchLoading,
    error: searchError,
  } = useHybridSearchGames({
    query: query || '',
    auto_sync: autoSync,
    sync_limit: 10,
    page,
    page_size: 20,
  }, { enabled: !!query });

  const {
    data: popularGames,
    isLoading: popularLoading,
    error: popularError,
  } = usePopularGames({ page, page_size: 20 });

  const syncPopularMutation = useSyncPopularGames();
  const syncSearchMutation = useSyncGamesBySearch();
  const syncGenreMutation = useSyncGamesByGenre();
  const syncRecentMutation = useSyncRecentGames();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if (platform) params.set('platform', platform);
    if (genre) params.set('genre', genre);
    params.set('page', '1');
    setSearchParams(params);
  };

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', newPage.toString());
    setSearchParams(params);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setPlatform('');
    setGenre('');
    setSearchParams({});
  };

  const data = query ? searchResults : popularGames;
  const isLoading = query ? searchLoading : popularLoading;
  const error = query ? searchError : popularError;

  const showSyncSuccess = 
    syncPopularMutation.isSuccess ||
    syncSearchMutation.isSuccess ||
    syncGenreMutation.isSuccess ||
    syncRecentMutation.isSuccess;

  const syncError = 
    syncPopularMutation.error ||
    syncSearchMutation.error ||
    syncGenreMutation.error ||
    syncRecentMutation.error;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">
          {query ? 'Game Search' : 'Popular Games'}
        </h1>
        <Button 
          variant="outline" 
          onClick={() => setShowSyncPanel(!showSyncPanel)}
        >
          {showSyncPanel ? 'Hide' : 'Show'} IGDB Sync
        </Button>
      </div>

      {/* Sync Success/Error Messages */}
      {showSyncSuccess && (
        <Alert variant="success" className="mb-4">
          Games synced successfully from IGDB!
        </Alert>
      )}
      
      {syncError && (
        <Alert variant="error" className="mb-4">
          Failed to sync games: {syncError.message}
        </Alert>
      )}

      {/* IGDB Sync Panel */}
      {showSyncPanel && (
        <GameSyncPanel
          onSyncPopular={(limit) => syncPopularMutation.mutate(limit)}
          onSyncBySearch={(query, limit) => syncSearchMutation.mutate({ query, limit })}
          onSyncByGenre={(genre, limit) => syncGenreMutation.mutate({ genre, limit })}
          onSyncRecent={(limit, daysBack) => syncRecentMutation.mutate({ limit, daysBack })}
          isLoading={
            syncPopularMutation.isPending ||
            syncSearchMutation.isPending ||
            syncGenreMutation.isPending ||
            syncRecentMutation.isPending
          }
        />
      )}

      {/* Search Form */}
      <form onSubmit={handleSearch} className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <Input
            label="Search Games"
            placeholder="Enter game name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Input
            label="Platform"
            placeholder="e.g., PlayStation 5"
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
          />
          <Input
            label="Genre"
            placeholder="e.g., Action, RPG"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            <Button type="submit">
              {query ? 'Smart Search' : 'Search'}
            </Button>
            {(searchQuery || platform || genre) && (
              <Button type="button" variant="secondary" onClick={clearFilters}>
                Clear Filters
              </Button>
            )}
          </div>
          
          {query && (
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={autoSync}
                onChange={(e) => setAutoSync(e.target.checked)}
                className="rounded border-gray-300"
              />
              Auto-sync from IGDB if no results
            </label>
          )}
        </div>
      </form>

      {/* Results */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">
          Error loading games. Please try again.
        </div>
      )}

      {data && (
        <>
          <div className="mb-4 text-gray-600 flex items-center justify-between">
            <span>
              Showing {data.games.length} of {data.total} games
              {data.is_from_igdb && (
                <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  IGDB Results
                </span>
              )}
            </span>
            {data.synced_count > 0 && (
              <span className="text-sm text-green-600">
                ✓ {data.synced_count} new games synced
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
            {data.games.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex justify-center gap-2">
              <Button
                variant="secondary"
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
              >
                Previous
              </Button>
              <span className="flex items-center px-4">
                Page {page} of {data.total_pages}
              </span>
              <Button
                variant="secondary"
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= data.total_pages}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
