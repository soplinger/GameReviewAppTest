import { Link } from 'react-router-dom';
import type { Review } from '../../types/api';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { useAuth } from '../../contexts/AuthContext';

interface ReviewCardProps {
  review: Review;
  onEdit?: () => void;
  onDelete?: () => void;
  onMarkHelpful?: () => void;
  showGameInfo?: boolean;
}

export const ReviewCard: React.FC<ReviewCardProps> = ({
  review,
  onEdit,
  onDelete,
  onMarkHelpful,
  showGameInfo = false,
}) => {
  const { user } = useAuth();
  const isOwner = user?.id === review.user_id;

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={star <= rating ? 'text-yellow-400' : 'text-gray-300'}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <Card variant="bordered" className="hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            {review.user_avatar_url ? (
              <img
                src={review.user_avatar_url}
                alt={review.username || 'User'}
                className="w-10 h-10 rounded-full"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 font-medium">
                {review.username?.charAt(0).toUpperCase() || 'U'}
              </div>
            )}
            <div>
              <p className="font-medium">{review.username || 'Anonymous'}</p>
              <p className="text-sm text-gray-500">{formatDate(review.created_at)}</p>
            </div>
          </div>

          {showGameInfo && review.game_name && (
            <Link
              to={`/games/${review.game?.slug || review.game_id}`}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              {review.game_name}
            </Link>
          )}
        </div>

        {isOwner && (onEdit || onDelete) && (
          <div className="flex gap-2">
            {onEdit && (
              <Button size="sm" variant="secondary" onClick={onEdit}>
                Edit
              </Button>
            )}
            {onDelete && (
              <Button size="sm" variant="danger" onClick={onDelete}>
                Delete
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Rating and Recommendation */}
      <div className="flex items-center gap-4 mb-3">
        {renderStars(review.rating)}
        {review.is_recommended && (
          <span className="text-sm text-green-600 font-medium">✓ Recommended</span>
        )}
      </div>

      {/* Title */}
      <h3 className="font-bold text-lg mb-2">{review.title}</h3>

      {/* Content */}
      <p className="text-gray-700 mb-4 whitespace-pre-wrap">{review.content}</p>

      {/* Metadata */}
      <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
        {review.playtime_hours && (
          <span>⏱️ {review.playtime_hours} hours played</span>
        )}
        {review.platform && <span>🎮 {review.platform}</span>}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <button
            onClick={onMarkHelpful}
            disabled={!onMarkHelpful}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>👍</span>
            <span>Helpful ({review.helpful_count})</span>
          </button>
        </div>

        {review.updated_at !== review.created_at && (
          <p className="text-xs text-gray-500">
            Edited {formatDate(review.updated_at)}
          </p>
        )}
      </div>
    </Card>
  );
};
