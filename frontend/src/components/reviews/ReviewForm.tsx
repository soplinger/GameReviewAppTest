import { useState } from 'react';
import type { ReviewCreate, ReviewUpdate } from '../../types/api';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

interface ReviewFormProps {
  initialData?: {
    rating: number;
    title: string;
    content: string;
    playtime_hours?: number;
    platform?: string;
    is_recommended: boolean;
  };
  gameId: number;
  onSubmit: (data: ReviewCreate | ReviewUpdate) => Promise<void>;
  onCancel?: () => void;
  isEditing?: boolean;
}

export const ReviewForm: React.FC<ReviewFormProps> = ({
  initialData,
  gameId,
  onSubmit,
  onCancel,
  isEditing = false,
}) => {
  const [rating, setRating] = useState(initialData?.rating || 0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [title, setTitle] = useState(initialData?.title || '');
  const [content, setContent] = useState(initialData?.content || '');
  const [playtimeHours, setPlaytimeHours] = useState(
    initialData?.playtime_hours?.toString() || ''
  );
  const [platform, setPlatform] = useState(initialData?.platform || '');
  const [isRecommended, setIsRecommended] = useState(
    initialData?.is_recommended ?? true
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (rating < 1 || rating > 5) {
      setError('Please select a rating between 1 and 5 stars');
      return;
    }

    if (title.trim().length < 5) {
      setError('Title must be at least 5 characters');
      return;
    }

    if (content.trim().length < 50) {
      setError('Review content must be at least 50 characters');
      return;
    }

    setIsSubmitting(true);

    try {
      const data: ReviewCreate | ReviewUpdate = {
        ...(isEditing ? {} : { game_id: gameId }),
        rating,
        title: title.trim(),
        content: content.trim(),
        playtime_hours: playtimeHours ? parseFloat(playtimeHours) : undefined,
        platform: platform.trim() || undefined,
        is_recommended: isRecommended,
      };

      await onSubmit(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save review');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStars = () => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className="text-3xl focus:outline-none transition-colors"
            onMouseEnter={() => setHoveredRating(star)}
            onMouseLeave={() => setHoveredRating(0)}
            onClick={() => setRating(star)}
          >
            <span
              className={
                star <= (hoveredRating || rating)
                  ? 'text-yellow-400'
                  : 'text-gray-300'
              }
            >
              ★
            </span>
          </button>
        ))}
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
      )}

      {/* Rating */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Rating <span className="text-red-500">*</span>
        </label>
        {renderStars()}
        {rating > 0 && (
          <p className="text-sm text-gray-600 mt-1">{rating} out of 5 stars</p>
        )}
      </div>

      {/* Recommendation */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="recommended"
          checked={isRecommended}
          onChange={(e) => setIsRecommended(e.target.checked)}
          className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
        />
        <label htmlFor="recommended" className="text-sm font-medium text-gray-700">
          I recommend this game
        </label>
      </div>

      {/* Title */}
      <Input
        label="Review Title"
        required
        placeholder="Sum up your experience in a few words"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        helperText="Minimum 5 characters"
      />

      {/* Content */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Review Content <span className="text-red-500">*</span>
        </label>
        <textarea
          required
          placeholder="Share your thoughts about the game... (minimum 50 characters)"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        <p className="text-sm text-gray-500 mt-1">
          {content.length} / 50 characters minimum
        </p>
      </div>

      {/* Optional Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Playtime (hours)"
          type="number"
          step="0.5"
          min="0"
          placeholder="e.g., 25.5"
          value={playtimeHours}
          onChange={(e) => setPlaytimeHours(e.target.value)}
        />
        <Input
          label="Platform"
          placeholder="e.g., PlayStation 5, PC"
          value={platform}
          onChange={(e) => setPlatform(e.target.value)}
        />
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-4">
        <Button type="submit" disabled={isSubmitting} loading={isSubmitting}>
          {isEditing ? 'Update Review' : 'Publish Review'}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};
