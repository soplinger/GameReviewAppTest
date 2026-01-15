import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSearchGames, usePopularGames } from '../../services/gameService';
import { GameCard } from '../../components/games/GameCard';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Spinner } from '../../components/ui/Spinner';

export const GameSearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [platform, setPlatform] = useState(searchParams.get('platform') || '');
  const [genre, setGenre] = useState(searchParams.get('genre') || '');
  const page = parseInt(searchParams.get('page') || '1');

  const query = searchParams.get('q') || undefined;
  const platformFilter = searchParams.get('platform') || undefined;
  const genreFilter = searchParams.get('genre') || undefined;

  const {
    data: searchResults,
    isLoading: searchLoading,
    error: searchError,
  } = useSearchGames({
    query,
    platform: platformFilter,
    genre: genreFilter,
    page,
    page_size: 20,
  });

  const {
    data: popularGames,
    isLoading: popularLoading,
    error: popularError,
  } = usePopularGames({ page, page_size: 20 });

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

  const data = query || platformFilter || genreFilter ? searchResults : popularGames;
  const isLoading = query || platformFilter || genreFilter ? searchLoading : popularLoading;
  const error = query || platformFilter || genreFilter ? searchError : popularError;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">
        {query || platformFilter || genreFilter ? 'Search Results' : 'Popular Games'}
      </h1>

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
        <div className="flex gap-2">
          <Button type="submit">Search</Button>
          {(searchQuery || platform || genre) && (
            <Button type="button" variant="secondary" onClick={clearFilters}>
              Clear Filters
            </Button>
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
          <div className="mb-4 text-gray-600">
            Showing {data.games.length} of {data.total} games
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
