/**
 * FeedCard component for displaying review with author info and game details
 */

import React from 'react';
import { ReviewResponse } from '../../services/reviewService';
import { Card } from '../ui/Card';
import { Avatar } from '../ui/Avatar';
import { StarRating } from '../ui/StarRating';
import { Badge } from '../ui/Badge';

interface FeedCardProps {
  review: ReviewResponse;
  onUserClick?: (userId: number) => void;
  onGameClick?: (gameId: number) => void;
  className?: string;
}

export const FeedCard: React.FC<FeedCardProps> = ({
  review,
  onUserClick,
  onGameClick,
  className = '',
}) => {
  const handleUserClick = () => {
    if (onUserClick) {
      onUserClick(review.user.id);
    }
  };

  const handleGameClick = () => {
    if (onGameClick) {
      onGameClick(review.game.id);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInHours = diffInMs / (1000 * 60 * 60);
    const diffInDays = diffInHours / 24;

    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInDays < 7) {
      return `${Math.floor(diffInDays)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength).trim() + '...';
  };

  return (
    <Card className={`p-6 hover:shadow-lg transition-shadow ${className}`}>
      {/* Header - User and timestamp */}
      <div className="flex items-center justify-between mb-4">
        <div 
          className="flex items-center space-x-3 cursor-pointer hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors"
          onClick={handleUserClick}
        >
          <Avatar
            src={review.user.avatar_url}
            alt={review.user.username}
            size="sm"
          />
          <div>
            <h4 className="font-medium text-gray-900">
              {review.user.username}
            </h4>
            <p className="text-xs text-gray-500">
              {formatDate(review.created_at)}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <StarRating rating={review.rating} size="sm" readonly />
          <span className="text-lg font-semibold text-gray-900">
            {review.rating}/5
          </span>
        </div>
      </div>

      {/* Game Information */}
      <div 
        className="flex items-start space-x-4 mb-4 cursor-pointer hover:bg-gray-50 rounded-lg p-3 -m-3 transition-colors"
        onClick={handleGameClick}
      >
        {review.game.cover_image_url && (
          <img
            src={review.game.cover_image_url}
            alt={review.game.title}
            className="w-16 h-20 object-cover rounded-md shadow-sm"
          />
        )}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 truncate">
            {review.game.title}
          </h3>
          
          {review.game.genres && review.game.genres.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {review.game.genres.slice(0, 3).map((genre, index) => (
                <Badge key={index} variant="secondary" size="sm">
                  {genre}
                </Badge>
              ))}
              {review.game.genres.length > 3 && (
                <Badge variant="secondary" size="sm">
                  +{review.game.genres.length - 3} more
                </Badge>
              )}
            </div>
          )}

          {review.game.platforms && review.game.platforms.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {review.game.platforms.slice(0, 4).map((platform, index) => (
                <Badge key={index} variant="outline" size="sm">
                  {platform}
                </Badge>
              ))}
              {review.game.platforms.length > 4 && (
                <Badge variant="outline" size="sm">
                  +{review.game.platforms.length - 4}
                </Badge>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Review Content */}
      <div className="space-y-3">
        {review.title && (
          <h4 className="text-lg font-medium text-gray-900">
            {review.title}
          </h4>
        )}
        
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-700 leading-relaxed">
            {truncateText(review.content, 300)}
          </p>
        </div>

        {review.content.length > 300 && (
          <button 
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            onClick={() => {
              // TODO: Implement expand/collapse or navigate to full review
            }}
          >
            Read more
          </button>
        )}
      </div>

      {/* Footer - Engagement stats */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          {review.helpful_count > 0 && (
            <span className="flex items-center space-x-1">
              <svg 
                className="w-4 h-4" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
              </svg>
              <span>{review.helpful_count} helpful</span>
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button 
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
            title="Mark as helpful"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
          </button>
          <button 
            className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-full transition-colors"
            title="Share"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
          </button>
        </div>
      </div>
    </Card>
  );
};