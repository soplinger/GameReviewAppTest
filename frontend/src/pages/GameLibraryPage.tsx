import { useState, useEffect } from 'react';
import { oauthService, GameLibraryEntry } from '../services/oauthService';
import { FaClock, FaTrophy, FaSteam, FaPlaystation, FaXbox } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const PLATFORM_ICONS: Record<number, JSX.Element> = {
  // This would map linked_account_id to platform icons
  // For simplicity, we'll show a generic icon
};

export default function GameLibraryPage() {
  const [library, setLibrary] = useState<GameLibraryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [platformFilter, setPlatformFilter] = useState<'steam' | 'playstation' | 'xbox' | null>(null);
  const limit = 24;

  useEffect(() => {
    loadLibrary();
  }, [page, platformFilter]);

  const loadLibrary = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await oauthService.getGameLibrary(
        page * limit,
        limit,
        platformFilter || undefined
      );
      
      setLibrary(result.items);
      setTotal(result.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load game library');
    } finally {
      setLoading(false);
    }
  };

  const formatPlaytime = (hours: number): string => {
    if (hours < 1) {
      return `${Math.round(hours * 60)}m`;
    } else if (hours < 100) {
      return `${hours.toFixed(1)}h`;
    } else {
      return `${Math.round(hours)}h`;
    }
  };

  const totalPages = Math.ceil(total / limit);

  if (loading && page === 0) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          My Game Library
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {total} games imported from your linked platforms
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Platform Filter */}
      <div className="mb-6 flex space-x-2">
        <button
          onClick={() => setPlatformFilter(null)}
          className={`px-4 py-2 rounded-lg ${
            platformFilter === null
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          All Platforms
        </button>
        <button
          onClick={() => setPlatformFilter('steam')}
          className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
            platformFilter === 'steam'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          <FaSteam />
          <span>Steam</span>
        </button>
        <button
          onClick={() => setPlatformFilter('playstation')}
          className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
            platformFilter === 'playstation'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          <FaPlaystation />
          <span>PlayStation</span>
        </button>
        <button
          onClick={() => setPlatformFilter('xbox')}
          className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
            platformFilter === 'xbox'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          <FaXbox />
          <span>Xbox</span>
        </button>
      </div>

      {library.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No games found in your library
          </p>
          <Link
            to="/linked-accounts"
            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium"
          >
            Link a gaming account to import your library
          </Link>
        </div>
      ) : (
        <>
          {/* Game Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-8">
            {library.map((entry) => (
              <Link
                key={entry.id}
                to={`/games/${entry.game?.slug || entry.game_id}`}
                className="group"
              >
                <div className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                  <div className="aspect-[3/4] bg-gray-200 dark:bg-gray-700 relative">
                    {entry.game?.cover_image_url ? (
                      <img
                        src={entry.game.cover_image_url}
                        alt={entry.game.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        No Image
                      </div>
                    )}
                  </div>
                  
                  <div className="p-3">
                    <h3 className="font-semibold text-sm text-gray-900 dark:text-white mb-2 line-clamp-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      {entry.game?.name || `Game #${entry.game_id}`}
                    </h3>
                    
                    <div className="space-y-1">
                      {entry.playtime_hours > 0 && (
                        <div className="flex items-center text-xs text-gray-600 dark:text-gray-400">
                          <FaClock className="mr-1" />
                          <span>{formatPlaytime(entry.playtime_hours)}</span>
                        </div>
                      )}
                      
                      {entry.achievements_count > 0 && (
                        <div className="flex items-center text-xs text-gray-600 dark:text-gray-400">
                          <FaTrophy className="mr-1" />
                          <span>{entry.achievements_count}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Previous
              </button>
              
              <span className="text-gray-700 dark:text-gray-300">
                Page {page + 1} of {totalPages}
              </span>
              
              <button
                onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
