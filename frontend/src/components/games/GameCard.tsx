import { Link } from 'react-router-dom';
import type { Game } from '../../types/api';
import { Card } from '../ui/Card';

interface GameCardProps {
  game: Game;
}

export const GameCard: React.FC<GameCardProps> = ({ game }) => {
  const formatDate = (date: string | null) => {
    if (!date) return 'TBA';
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Link to={`/games/${game.id}`}>
      <Card variant="bordered" className="h-full hover:shadow-lg transition-shadow cursor-pointer">
        <div className="aspect-[3/4] bg-gray-200 rounded-lg overflow-hidden mb-3">
          {game.cover_url ? (
            <img
              src={game.cover_url}
              alt={game.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No Image
            </div>
          )}
        </div>

        <h3 className="font-semibold text-lg mb-2 line-clamp-2">{game.name}</h3>

        {game.summary && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">{game.summary}</p>
        )}

        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>{formatDate(game.release_date)}</span>
          {game.rating && (
            <div className="flex items-center gap-1">
              <span className="text-yellow-500">★</span>
              <span className="font-medium">{game.rating.toFixed(1)}</span>
            </div>
          )}
        </div>

        {game.genres && game.genres.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {game.genres.slice(0, 3).map((genre) => (
              <span
                key={genre}
                className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
              >
                {genre}
              </span>
            ))}
          </div>
        )}

        {game.user_rating !== undefined && game.user_rating_count && game.user_rating_count > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">User Rating</span>
              <div className="flex items-center gap-1">
                <span className="text-blue-500">★</span>
                <span className="font-medium">
                  {game.user_rating.toFixed(1)} ({game.user_rating_count})
                </span>
              </div>
            </div>
          </div>
        )}
      </Card>
    </Link>
  );
};
